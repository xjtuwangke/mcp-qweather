import httpx
import time
import base64
import json
from pathlib import Path

from config import settings


class GeoAPI:
    """
    QWeather GeoAPI - City search and POI search services.
    Docs: https://dev.qweather.com/docs/api/geoapi/
    """

    def __init__(self):
        self.api_host = settings.qweather_api_host

    def generate_jwt(self) -> str:
        private_key_bytes = Path(settings.private_key_path).read_bytes()
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        pk = load_pem_private_key(private_key_bytes, password=None)

        header_dict = {"alg": "EdDSA", "kid": settings.key_id}
        header_base64 = base64.urlsafe_b64encode(json.dumps(header_dict).encode()).decode().rstrip("=")

        payload_dict = {
            "iat": int(time.time()) - 30,
            "exp": int(time.time()) + 900,
            "sub": settings.project_id
        }
        body_base64 = base64.urlsafe_b64encode(json.dumps(payload_dict).encode()).decode().rstrip("=")

        signing_input = f"{header_base64}.{body_base64}"
        signature = pk.sign(signing_input.encode())
        signature_base64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

        return f"{signing_input}.{signature_base64}"

    async def _request(self, path: str, params: dict) -> dict:
        url = f"{self.api_host}{path}"
        headers = {
            "Authorization": f"Bearer {self.generate_jwt()}",
            "Accept-Encoding": "gzip"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

    async def city_lookup(self, location: str, adm: str = None, range: str = None, number: int = 10, lang: str = None) -> dict:
        """
        City search by name or coordinates.
        Docs: https://dev.qweather.com/docs/api/geoapi/city-lookup/

        Args:
            location: City name or coordinates (required). Example: "Beijing", "116.41,39.92"
            adm: Upper administrative district. Example: "Beijing", "Shaanxi"
            range: Country code (ISO 3166). Example: "cn", "us", "jp"
            number: Number of results (1-20, default 10). Example: 5, 10
            lang: Language. Example: "en", "zh-Hans"

        Returns:
            dict: {"code": "200", "location": [{"name": "Beijing", "id": "101010100", "lat": "39.91", "lon": "116.39", "adm2": "Beijing", "adm1": "Beijing", "country": "China"}]}
        """
        params = {"location": location}
        if adm:
            params["adm"] = adm
        if range:
            params["range"] = range
        if number:
            params["number"] = number
        if lang:
            params["lang"] = lang
        return await self._request("/geo/v2/city/lookup", params)

    async def poi_lookup(self, location: str, type: str, city: str = None, number: int = 10, lang: str = None) -> dict:
        """
        POI (Points of Interest) search by keyword or coordinates.
        Docs: https://dev.qweather.com/docs/api/geoapi/poi-lookup/

        Args:
            location: Location name or coordinates (required). Example: "Beijing", "116.41,39.92"
            type: POI type (required). Example: "scenic", "TSTA" (tide station), "ARPT" (airport)
            city: Limit search to specific city. Example: "Beijing", "101010100"
            number: Number of results (1-20, default 10). Example: 5, 10
            lang: Language. Example: "en", "zh-Hans"

        Returns:
            dict: {"code": "200", "poi": [{"name": "Beijing Temple", "id": "10101010007A", "lat": "39.94", "lon": "116.41", "type": "scenic", "adm2": "Beijing", "adm1": "Beijing", "country": "China"}]}
        """
        params = {"location": location, "type": type}
        if city:
            params["city"] = city
        if number:
            params["number"] = number
        if lang:
            params["lang"] = lang
        return await self._request("/geo/v2/poi/lookup", params)

    async def poi_range(self, location: str, type: str, radius: int = 5, number: int = 10, lang: str = None) -> dict:
        """
        POI search within a radius of specified coordinates.
        Docs: https://dev.qweather.com/docs/api/geoapi/poi-range/

        Args:
            location: Coordinates (required). Example: "116.40528,39.90498" (longitude,latitude)
            type: POI type (required). Example: "scenic", "TSTA"
            radius: Search radius in km (1-50, default 5). Example: 5, 10, 20
            number: Number of results (1-20, default 10). Example: 5, 10
            lang: Language. Example: "en", "zh-Hans"

        Returns:
            dict: {"code": "200", "poi": [{"name": "Zhongshan Park", "id": "10101010016A", "lat": "39.91", "lon": "116.39", "type": "scenic", "adm2": "Beijing", "adm1": "Beijing", "country": "China"}]}
        """
        params = {"location": location, "type": type, "radius": radius}
        if number:
            params["number"] = number
        if lang:
            params["lang"] = lang
        return await self._request("/geo/v2/poi/range", params)
