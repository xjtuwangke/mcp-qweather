import asyncio
from datetime import datetime
import httpx
import time
import logging
import re
from pathlib import Path
from typing import Optional

import jwt

from config import settings

logger = logging.getLogger(__name__)


class QWeatherAPIError(Exception):
    """Exception raised when QWeather API returns an error code.

    References:
        https://dev.qweather.com/docs/resource/error-code/
    """

    def __init__(self, code: str, message: Optional[str] = None):
        self.code = code
        self.message = message or self._default_message(code)
        super().__init__(f"QWeather API error: {self.code} - {self.message}")

    @staticmethod
    def _default_message(code: str) -> str:
        # QWeather uses two error code versions (v1 and v2).
        # v1: code field in response body (200=ok, 204=no data, 400+=error)
        # v2: HTTP status codes with error object in response body
        # See: https://dev.qweather.com/docs/resource/error-code/
        error_messages = {
            "200": "Request successful",
            "204": "No data for the requested location",
            "400": "Bad request — invalid or missing parameter, unsupported location, or data unavailable",
            "401": "Authentication failed — check API key/credentials",
            "402": "Over quota — API call limit exceeded",
            "403": "Access denied — no permission, no credit, overdue payment, security restriction, or invalid host",
            "404": "Unknown location or endpoint",
            "429": "Too many requests — rate limited (QPM exceeded or monthly limit reached)",
            "500": "Internal server error — QWeather service unavailable",
        }
        return error_messages.get(code, f"Unknown error (code: {code})")


QWEATHER_VALID_DAYS = ("3d", "7d", "10d", "15d", "30d")
QWEATHER_VALID_HOURS = ("24h", "72h", "168h")
QWEATHER_VALID_GRID_DAYS = ("3d", "7d")
QWEATHER_VALID_GRID_HOURS = ("24h", "72h")
QWEATHER_VALID_INDICES_DAYS = ("1d", "3d")

LOCATION_ID_DOC = (
    "LocationID (unique place identifier, e.g. '101010100' for Beijing, "
    "obtained from city_lookup tool). "
)

COORDINATES_DOC = (
    "Coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. '116.41,39.92'). "
)

ADM_DOC = (
    "Upper administrative district (adm1=province/state, adm2=city). "
    "Example: 'Beijing', 'Guangdong', 'Shaanxi'. "
    "Note: QWeather's admin levels may not match actual administrative divisions. "
)

RANGE_DOC = (
    "Country code (ISO 3166 alpha-2). Example: 'cn', 'us', 'jp'. "
)


def validate_lang(lang: Optional[str] = None) -> Optional[str]:
    """Validate and normalize language parameter."""
    if lang is None:
        return None
    lang_lower = lang.lower()
    if lang_lower in ("zh-hans", "zh-hant", "zh"):
        return "zh"
    return "en"


def validate_coordinates(value: str) -> tuple[float, float]:
    """Validate coordinates in 'lon,lat' format. Returns (lon, lat)."""
    pattern = r"^(-?\d{1,3}(?:\.\d{1,2})?),(-?\d{1,2}(?:\.\d{1,2})?)$"
    match = re.match(pattern, value.strip())
    if not match:
        raise ValueError(
            f"Invalid coordinates format: '{value}'. Expected 'lon,lat' (e.g. '116.41,39.92')"
        )
    lon, lat = float(match.group(1)), float(match.group(2))
    if not (-180 <= lon <= 180):
        raise ValueError(f"Longitude must be between -180 and 180, got {lon}")
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
    return lon, lat


def validate_location_id(value: str) -> str:
    """Validate LocationID - numeric or alphanumeric (e.g. '101010100', 'P53763', '10101010007A')."""
    if not value or not re.match(r"^[A-Za-z0-9]+$", value.strip()):
        raise ValueError(f"Invalid LocationID: '{value}'. Expected alphanumeric ID (e.g. '101010100', 'P53763')")
    return value.strip()


def validate_country_code(value: str) -> str:
    """Validate ISO 3166 alpha-2 country code."""
    if not re.match(r"^[A-Za-z]{2}$", value.strip()):
        raise ValueError(f"Invalid country code: '{value}'. Expected ISO 3166 alpha-2 code (e.g. 'cn', 'us', 'jp')")
    return value.strip().lower()


def validate_days(value: str, valid: tuple = QWEATHER_VALID_DAYS) -> str:
    """Validate forecast days parameter."""
    if value not in valid:
        raise ValueError(f"Invalid days value: '{value}'. Must be one of {valid}")
    return value


def validate_hours(value: str, valid: tuple = QWEATHER_VALID_HOURS) -> str:
    """Validate forecast hours parameter."""
    if value not in valid:
        raise ValueError(f"Invalid hours value: '{value}'. Must be one of {valid}")
    return value


def validate_date(value: str) -> str:
    """Validate date in yyyyMMdd format."""
    if not re.match(r"^\d{8}$", value):
        raise ValueError(f"Invalid date format: '{value}'. Expected 'yyyyMMdd' (e.g. '20260201')")
    try:
        datetime.strptime(value, "%Y%m%d")
    except ValueError:
        raise ValueError(f"Invalid date: '{value}'. Not a valid calendar date")
    return value


def validate_time(value: str) -> str:
    """Validate time in HHmm format (24-hour)."""
    if not re.match(r"^\d{4}$", value):
        raise ValueError(f"Invalid time format: '{value}'. Expected 'HHmm' (e.g. '1230')")
    hours, minutes = int(value[:2]), int(value[2:])
    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        raise ValueError(f"Invalid time: '{value}'. Hours must be 0-23, minutes 0-59")
    return value


def validate_timezone(value: str) -> str:
    """Validate timezone in ±HHmm format."""
    match = re.match(r"^([+-])?(\d{4})$", value.strip())
    if not match:
        raise ValueError(f"Invalid timezone format: '{value}'. Expected '±HHmm' (e.g. '+0800', '-0530')")
    sign = match.group(1)
    digits = match.group(2)
    hours, minutes = int(digits[:2]), int(digits[2:])
    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        raise ValueError(f"Invalid timezone: '{value}'. Hours must be 0-23, minutes 0-59")
    if sign == "-" and hours == 0 and minutes == 0:
        raise ValueError(f"Invalid timezone: '{value}'. Negative zero is not valid")
    return value.strip()


def validate_number(value: int, min_val: int = 1, max_val: int = 20) -> int:
    """Validate result number parameter."""
    if not (min_val <= value <= max_val):
        raise ValueError(f"Number must be between {min_val} and {max_val}, got {value}")
    return value


def validate_radius(value: int, min_val: int = 1, max_val: int = 50) -> int:
    """Validate search radius in km."""
    if not (min_val <= value <= max_val):
        raise ValueError(f"Radius must be between {min_val}km and {max_val}km, got {value}km")
    return value


def validate_unit(value: str) -> str:
    """Validate unit system parameter."""
    value_lower = value.lower()
    if value_lower not in ("m", "i"):
        raise ValueError(f"Invalid unit: '{value}'. Must be 'm' (metric) or 'i' (imperial)")
    return value_lower


def validate_altitude(value: float) -> float:
    """Validate altitude in meters."""
    if not (-500 <= value <= 10000):
        raise ValueError(f"Altitude must be between -500m and 10000m, got {value}m")
    return value


def is_coordinate_location(value: str) -> bool:
    """Check if a location value is in coordinate format."""
    try:
        validate_coordinates(value)
        return True
    except ValueError:
        return False


def validate_latitude(lat: float) -> float:
    """Validate latitude value."""
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude must be between -90 and 90, got {lat}")
    return lat


def validate_longitude(lon: float) -> float:
    """Validate longitude value."""
    if not (-180 <= lon <= 180):
        raise ValueError(f"Longitude must be between -180 and 180, got {lon}")
    return lon


class QWeatherAPI:
    """
    Base class for QWeather API clients.
    Provides JWT generation and HTTP request handling.

    Best Practices (implemented):
      - JWT token cached for 15 min, refreshed before expiry
      - Gzip compression enabled on all requests
      - Shared httpx client with connection pooling and timeout
      - Both v1 and v2 error code formats handled

    References:
      https://dev.qweather.com/docs/configuration/authentication/
      https://dev.qweather.com/docs/best-practices/cache/
      https://dev.qweather.com/docs/best-practices/no-assumptions/
      https://dev.qweather.com/docs/resource/error-code/
    """

    _jwt_token: str = None
    _jwt_expiry: float = 0

    def __init__(self, api_host: str = None):
        self.api_host = api_host or settings.qweather_api_host
        self._private_key = None
        self._http_client = None

    def _load_private_key(self):
        """Load private key once and cache it."""
        if self._private_key is None:
            from cryptography.hazmat.primitives.serialization import load_pem_private_key
            private_key_bytes = Path(settings.private_key_path).read_bytes()
            self._private_key = load_pem_private_key(private_key_bytes, password=None)

    async def generate_jwt(self) -> str:
        """Generate JWT token for QWeather API authentication.

        Uses EdDSA (Ed25519) signing with PyJWT. Token expires in 15 minutes,
        cached until 60 seconds before expiry.

        Note: PyJWT automatically adds 'typ: JWT' to the header, which is
        compliant with QWeather's JWT spec but is a reserved field that may
        be used for authentication in the future.

        References:
            https://dev.qweather.com/docs/configuration/authentication/#json-web-token
        """
        now = time.time()
        if self._jwt_token and now < self._jwt_expiry - 60:
            return self._jwt_token

        self._load_private_key()

        def _build_token():
            return jwt.encode(
                {"iat": int(now) - 30, "exp": int(now) + 900, "sub": settings.project_id},
                self._private_key,
                algorithm="EdDSA",
                headers={"alg": "EdDSA", "kid": settings.key_id},
            )

        self._jwt_token = await asyncio.to_thread(_build_token)
        self._jwt_expiry = int(now) + 900
        return self._jwt_token

    def _get_http_client(self) -> httpx.AsyncClient:
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                headers={"Accept-Encoding": "gzip"},
                timeout=10.0,
            )
        return self._http_client

    async def close(self):
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    async def _request(self, path: str, params: dict) -> dict:
        url = f"{self.api_host}{path}"
        token = await self.generate_jwt()
        headers = {"Authorization": f"Bearer {token}"}
        logger.info(f"GET {url} params={params}")
        client = self._get_http_client()
        response = await client.get(url, headers=headers, params=params)
        logger.info(f"GET {response.request.url} status={response.status_code}")

        if response.status_code != 200:
            self._raise_error(response)

        data = response.json()
        code = data.get("code", "")
        if code and code != "200":
            detail = data.get("status", data.get("message", str(data)[:200]))
            raise QWeatherAPIError(code=code, message=detail)

        return data

    @staticmethod
    def _raise_error(response):
        # Try to extract v2 error format: { "error": { "title", "detail", "status" } }
        # See: https://dev.qweather.com/docs/resource/error-code/
        try:
            body = response.json()
            error_obj = body.get("error", {})
            title = error_obj.get("title", "")
            detail = error_obj.get("detail", "")
            if title and detail:
                raise QWeatherAPIError(
                    code=str(response.status_code),
                    message=f"{title}: {detail}",
                )
            if title:
                raise QWeatherAPIError(
                    code=str(response.status_code),
                    message=title,
                )
        except (ValueError, AttributeError):
            pass
        raise QWeatherAPIError(
            code=str(response.status_code),
            message=f"HTTP {response.status_code}: {response.text[:200]}",
        )
