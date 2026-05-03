import os
os.environ.setdefault("TZ", os.environ.get("TZ", "Asia/Shanghai"))

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.handlers.clear()
uvicorn_handler = logging.StreamHandler(sys.stdout)
uvicorn_handler.setFormatter(logging.Formatter(
    fmt="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
uvicorn_logger.addHandler(uvicorn_handler)
uvicorn_logger.setLevel(logging.INFO)

from fastmcp import FastMCP

from apis.geo import GeoAPI
from apis.weather import WeatherAPI
from apis.minutely import MinutelyAPI

logger = logging.getLogger(__name__)


mcp = FastMCP("Weather MCP")
geo_api = GeoAPI()
weather_api = WeatherAPI()
minutely_api = MinutelyAPI()

# =============================================================================
# TOOLS - Geo lookups as tools for consistency
# =============================================================================


@mcp.tool()
async def city_lookup(location: str, adm: str = None, range: str = None, number: int = 10, lang: str = None) -> dict:
    """
    City search by name or coordinates.

    Args:
        location: City name (e.g. "Beijing") or coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. "116.41,39.92").
        adm: Upper administrative district. Example: "Beijing", "Shaanxi"
        range: Country code (ISO 3166). Example: "cn", "us", "jp"
        number: Number of results (1-20, default 10). Example: 5, 10
        lang: Language. Example: "en", "zh"

    Returns:
        dict: {"code": "200", "location": [{"name": "Beijing", "id": "101010100", "lat": "39.91", "lon": "116.39", "adm2": "Beijing", "adm1": "Beijing", "country": "China"}]}
    """
    logger.info(f"[tool] city_lookup(location={location!r}, adm={adm!r}, range={range!r}, number={number!r}, lang={lang!r})")
    return await geo_api.city_lookup(location, adm, range, number, lang)


@mcp.tool()
async def poi_lookup(location: str, type: str = "scenic", city: str = None, number: int = 10, lang: str = None) -> dict:
    """
    POI (Points of Interest) search by keyword or coordinates.

    Args:
        location: Location name (e.g. "Beijing") or coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. "116.41,39.92").
        type: POI type (default: "scenic"). Example: "scenic", "TSTA" (tide station), "ARPT" (airport)
        city: Limit search to specific city. Example: "Beijing", "101010100"
        number: Number of results (1-20, default 10). Example: 5, 10
        lang: Language. Example: "en", "zh"

    Returns:
        dict: {"code": "200", "poi": [{"name": "Beijing Temple", "id": "10101010007A", "lat": "39.94", "lon": "116.41", "type": "scenic", "adm2": "Beijing", "adm1": "Beijing", "country": "China"}]}
    """
    logger.info(f"[tool] poi_lookup(location={location!r}, type={type!r}, city={city!r}, number={number!r}, lang={lang!r})")
    return await geo_api.poi_lookup(location, type, city, number, lang)


@mcp.tool()
async def poi_range(location: str, type: str = "scenic", radius: int = 5, number: int = 10, lang: str = None) -> dict:
    """
    POI search within a radius of specified coordinates.

    Args:
        location: Coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. "116.40528,39.90498").
        type: POI type (default: "scenic"). Example: "scenic", "TSTA" (tide station)
        radius: Search radius in km (1-50, default 5). Example: 5, 10, 20
        number: Number of results (1-20, default 10). Example: 5, 10
        lang: Language. Example: "en", "zh"

    Returns:
        dict: {"code": "200", "poi": [{"name": "Zhongshan Park", "id": "10101010016A", "lat": "39.91", "lon": "116.39", "type": "scenic", "adm2": "Beijing", "adm1": "Beijing", "country": "China"}]}
    """
    logger.info(f"[tool] poi_range(location={location!r}, type={type!r}, radius={radius!r}, number={number!r}, lang={lang!r})")
    return await geo_api.poi_range(location, type, radius, number, lang)


# =============================================================================
# TOOLS - Dynamic/semantic operations (Weather, Air Quality, Astronomy)
# =============================================================================


@mcp.tool()
async def weather_now(location: str, lang: str = None, unit: str = None) -> dict:
    """
    Get current weather for a location using QWeather API.

    Args:
        location: LocationID (e.g. "101010100", obtained from geo://city/ endpoint) or coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. "116.41,39.92").
        lang: Language. Example: "en", "zh"
        unit: Unit system - "m" for metric, "i" for imperial (default: metric). Example: "m", "i"

    Returns:
        dict: {"code": "200", "now": {"obsTime": "2026-05-01T19:00+08:00", "temp": "20", "feelsLike": "17", "icon": "104", "text": "Cloudy", "windDir": "Southeast", "windScale": "2", "windSpeed": "7", "humidity": "36", "precip": "0.0", "pressure": "1005", "vis": "18"}}
    """
    logger.info(f"[tool] weather_now(location={location!r}, lang={lang!r}, unit={unit!r})")
    return await weather_api.weather_now(location, lang, unit)


@mcp.tool()
async def weather_daily(location: str, days: str = "7d", lang: str = None, unit: str = None) -> dict:
    """
    Get daily weather forecast for a location using QWeather API.

    Args:
        location: LocationID (e.g. "101010100", obtained from geo://city/ endpoint) or coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. "116.41,39.92").
        days: Forecast days (required). Example: "3d", "7d", "10d", "15d", "30d"
        lang: Language. Example: "en", "zh"
        unit: Unit system - "m" for metric, "i" for imperial (default: metric). Example: "m", "i"

    Returns:
        dict: {"code": "200", "daily": [{"fxDate": "2026-05-01", "sunrise": "05:16", "sunset": "19:08", "moonrise": "19:04", "moonset": "04:40", "moonPhase": "Waxing Gibbous", "tempMax": "26", "tempMin": "14", "iconDay": "101", "textDay": "Cloudy", "iconNight": "104", "textNight": "Cloudy", "windDirDay": "East", "windScaleDay": "1-3", "precip": "0.0", "uvIndex": "8"}]}
    """
    logger.info(f"[tool] weather_daily(location={location!r}, days={days!r}, lang={lang!r}, unit={unit!r})")
    return await weather_api.weather_daily(location, days, lang, unit)


@mcp.tool()
async def weather_hourly(location: str, hours: str = "24h", lang: str = None, unit: str = None) -> dict:
    """
    Get hourly weather forecast for a location using QWeather API.

    Args:
        location: LocationID (e.g. "101010100", obtained from geo://city/ endpoint) or coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. "116.41,39.92").
        hours: Forecast hours (required). Example: "24h", "72h", "168h"
        lang: Language. Example: "en", "zh"
        unit: Unit system - "m" for metric, "i" for imperial (default: metric). Example: "m", "i"

    Returns:
        dict: {"code": "200", "hourly": [{"fxTime": "2026-05-01T20:00+08:00", "temp": "20", "icon": "104", "text": "Cloudy", "windDir": "Southeast", "windScale": "1-3", "windSpeed": "14", "humidity": "31", "pop": "0", "precip": "0.0"}]}
    """
    logger.info(f"[tool] weather_hourly(location={location!r}, hours={hours!r}, lang={lang!r}, unit={unit!r})")
    return await weather_api.weather_hourly(location, hours, lang, unit)


@mcp.tool()
async def grid_weather_now(location: str, lang: str = None, unit: str = None) -> dict:
    """
    Get grid-based current weather using numerical weather prediction model (3-5km resolution).

    Args:
        location: Coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. "116.41,39.92").
        lang: Language. Example: "en", "zh"
        unit: Unit system - "m" for metric, "i" for imperial (default: metric). Example: "m", "i"

    Returns:
        dict: {"code": "200", "now": {"obsTime": "2026-05-01T11:00+00:00", "temp": "20", "feelsLike": "18", "icon": "151", "text": "Few Clouds", "windDir": "Southeast", "windScale": "2", "windSpeed": "11", "humidity": "31", "precip": "0.0", "pressure": "1004"}}
    """
    logger.info(f"[tool] grid_weather_now(location={location!r}, lang={lang!r}, unit={unit!r})")
    return await weather_api.grid_weather_now(location, lang, unit)


@mcp.tool()
async def grid_weather_daily(location: str, days: str = "7d", lang: str = None, unit: str = None) -> dict:
    """
    Get grid-based daily weather forecast using numerical weather prediction model (3-5km resolution).

    Args:
        location: Coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. "116.41,39.92").
        days: Forecast days (required). Example: "3d", "7d"
        lang: Language. Example: "en", "zh"
        unit: Unit system - "m" for metric, "i" for imperial (default: metric). Example: "m", "i"

    Returns:
        dict: {"code": "200", "daily": [{"fxDate": "2026-05-01", "tempMax": "27", "tempMin": "14", "iconDay": "102", "textDay": "Few Clouds", "iconNight": "152", "textNight": "Few Clouds", "windDirDay": "Southeast", "windScaleDay": "2", "precip": "0.00"}]}
    """
    logger.info(f"[tool] grid_weather_daily(location={location!r}, days={days!r}, lang={lang!r}, unit={unit!r})")
    return await weather_api.grid_weather_daily(location, days, lang, unit)


@mcp.tool()
async def grid_weather_hourly(location: str, hours: str = "24h", lang: str = None, unit: str = None) -> dict:
    """
    Get grid-based hourly weather forecast using numerical weather prediction model (3-5km resolution).

    Args:
        location: Coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. "116.41,39.92").
        hours: Forecast hours (required). Example: "24h", "72h"
        lang: Language. Example: "en", "zh"
        unit: Unit system - "m" for metric, "i" for imperial (default: metric). Example: "m", "i"

    Returns:
        dict: {"code": "200", "hourly": [{"fxTime": "2026-05-01T12:00+00:00", "temp": "19", "icon": "151", "text": "Few Clouds", "windDir": "Southeast", "windScale": "2", "windSpeed": "9", "humidity": "33", "precip": "0.0"}]}
    """
    logger.info(f"[tool] grid_weather_hourly(location={location!r}, hours={hours!r}, lang={lang!r}, unit={unit!r})")
    return await weather_api.grid_weather_hourly(location, hours, lang, unit)


@mcp.tool()
async def minutely_precipitation(location: str, lang: str = None) -> dict:
    """
    Get minutely precipitation forecast (next 2 hours, 5-min intervals) for China.

    Args:
        location: Coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. "116.41,39.92").
        lang: Language. Example: "en", "zh"

    Returns:
        dict: {"code": "200", "summary": "No precipitation in the next 2 hours", "minutely": [{"fxTime": "2026-05-01T19:05+08:00", "precip": "0.00", "type": "rain"}]}
    """
    logger.info(f"[tool] minutely_precipitation(location={location!r}, lang={lang!r})")
    return await minutely_api.minutely_precipitation(location, lang)


@mcp.tool()
async def indices_forecast(location: str, type: str, days: str = "1d", lang: str = None) -> dict:
    """
    Get weather indices forecast (car wash, clothing, UV, etc.).

    Args:
        location: LocationID (e.g. "101010100", obtained from geo://city/ endpoint) or coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. "116.41,39.92").
        type: Index type IDs (required, comma-separated). Example: "1,2,3"
              Types: 1=Sports, 2=Car Wash, 3=Clothing, 4=Cold, 5=Exercise, 6=Tourism,
              7=UV Index, 8=Air Pollution Diffusion, 9=AC, 10=Allergy,
              11=Sunglasses, 12=Makeup, 13=Drying, 14=Traffic, 15=Fishing, 16=Sunscreen
        days: Forecast days. Example: "1d", "3d"
        lang: Language. Example: "en", "zh"

    Returns:
        dict: {"code": "200", "daily": [{"date": "2026-05-01", "type": "3", "name": "Clothing Index", "level": "4", "category": "Moderate", "text": "Wear a light jacket."}]}
    """
    logger.info(f"[tool] indices_forecast(location={location!r}, type={type!r}, days={days!r}, lang={lang!r})")
    return await minutely_api.indices_forecast(location, type, days, lang)


@mcp.tool()
async def air_now(lat: float, lon: float, lang: str = None) -> dict:
    """
    Get current air quality index (AQI) for coordinates.

    Args:
        lat: Latitude (decimal, up to 2 decimal places). Example: 39.92
        lon: Longitude (decimal, up to 2 decimal places). Example: 116.41
        lang: Language. Example: "en", "zh"

    Returns:
        dict: {"code": "200", "indexes": [{"code": "cn-mee", "name": "AQI (CN)", "aqi": 78, "level": "2", "category": "Good"}], "pollutants": [{"code": "pm2p5", "name": "PM2.5", "concentration": {"value": 46.14, "unit": "μg/m³"}}], "stations": [{"id": "P58655", "name": "Wanshou Xigong"}]}
    """
    logger.info(f"[tool] air_now(lat={lat!r}, lon={lon!r}, lang={lang!r})")
    return await minutely_api.air_now(lat, lon, lang)


@mcp.tool()
async def air_hourly(lat: float, lon: float, local_time: bool = None, lang: str = None) -> dict:
    """
    Get hourly air quality forecast (next 24 hours).

    Args:
        lat: Latitude (decimal, up to 2 decimal places). Example: 39.92
        lon: Longitude (decimal, up to 2 decimal places). Example: 116.41
        local_time: Return local time (true/false, default false). Example: True, False
        lang: Language. Example: "en", "zh"

    Returns:
        dict: {"code": "200", "hours": [{"forecastTime": "2026-05-01T12:00Z", "indexes": [{"code": "cn-mee", "name": "AQI (CN)", "aqi": 63, "level": "2", "category": "Good"}], "pollutants": []}]}
    """
    logger.info(f"[tool] air_hourly(lat={lat!r}, lon={lon!r}, local_time={local_time!r}, lang={lang!r})")
    return await minutely_api.air_hourly(lat, lon, local_time, lang)


@mcp.tool()
async def air_daily(lat: float, lon: float, local_time: bool = None, lang: str = None) -> dict:
    """
    Get daily air quality forecast (next 3 days).

    Args:
        lat: Latitude (decimal, up to 2 decimal places). Example: 39.92
        lon: Longitude (decimal, up to 2 decimal places). Example: 116.41
        local_time: Return local time (true/false, default false). Example: True, False
        lang: Language. Example: "en", "zh"

    Returns:
        dict: {"code": "200", "days": [{"forecastStartTime": "2026-04-30T16:00Z", "forecastEndTime": "2026-05-01T16:00Z", "indexes": [{"code": "cn-mee", "name": "AQI (CN)", "aqi": 78, "level": "2", "category": "Good"}], "pollutants": []}]}
    """
    logger.info(f"[tool] air_daily(lat={lat!r}, lon={lon!r}, local_time={local_time!r}, lang={lang!r})")
    return await minutely_api.air_daily(lat, lon, local_time, lang)


@mcp.tool()
async def air_station(location_id: str, lang: str = None) -> dict:
    """
    Get air quality data for a specific monitoring station.

    Args:
        location_id: Station LocationID (required). Example: "P53763"
        lang: Language. Example: "en", "zh"

    Returns:
        dict: {"code": "200", "pollutants": [{"code": "pm2p5", "name": "PM2.5", "fullName": "Particulate Matter (≤2.5μm)", "concentration": {"value": 27.0, "unit": "μg/m³"}}]}
    """
    logger.info(f"[tool] air_station(location_id={location_id!r}, lang={lang!r})")
    return await minutely_api.air_station(location_id, lang)


@mcp.tool()
async def astronomy_sun(location: str, date: str, lang: str = None) -> dict:
    """
    Get sunrise and sunset times for a location.

    Args:
        location: LocationID (e.g. "101010100", obtained from geo://city/ endpoint) or coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. "116.41,39.92").
        date: Date (required). Example: "20260201" (yyyyMMdd format)
        lang: Language. Example: "en", "zh"

    Returns:
        dict: {"code": "200", "sunrise": "2026-05-01T05:16+08:00", "sunset": "2026-05-01T19:08+08:00"}
    """
    logger.info(f"[tool] astronomy_sun(location={location!r}, date={date!r}, lang={lang!r})")
    return await minutely_api.astronomy_sun(location, date, lang)


@mcp.tool()
async def astronomy_moon(location: str, date: str, lang: str = None) -> dict:
    """
    Get moonrise, moonset and hourly moon phase for a location.

    Args:
        location: LocationID (e.g. "101010100", obtained from geo://city/ endpoint) or coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. "116.41,39.92").
        date: Date (required). Example: "20260201" (yyyyMMdd format)
        lang: Language. Example: "en", "zh"

    Returns:
        dict: {"code": "200", "moonrise": "2026-05-01T19:04+08:00", "moonset": "2026-05-01T04:40+08:00", "moonPhase": [{"fxTime": "2026-05-01T00:00+08:00", "value": "0.47", "name": "Waxing Gibbous", "illumination": "99", "icon": "803"}]}
    """
    logger.info(f"[tool] astronomy_moon(location={location!r}, date={date!r}, lang={lang!r})")
    return await minutely_api.astronomy_moon(location, date, lang)


@mcp.tool()
async def solar_elevation_angle(location: str, date: str, time: str, tz: str, alt: float, lang: str = None) -> dict:
    """
    Get solar elevation and azimuth angles for any time point.

    Args:
        location: Coordinates in longitude,latitude format (decimal, up to 2 decimal places, e.g. "116.41,39.92").
        date: Date (required). Example: "20260201" (yyyyMMdd)
        time: Time (required). Example: "1230" (HHmm, 24-hour)
        tz: Timezone (required). Example: "0800", "-0530"
        alt: Altitude in meters (required). Example: 43
        lang: Language. Example: "en", "zh"

    Returns:
        dict: {"code": "200", "solarElevationAngle": "64.83", "solarAzimuthAngle": "190.55", "solarHour": "1218", "hourAngle": "-4.63"}
    """
    logger.info(f"[tool] solar_elevation_angle(location={location!r}, date={date!r}, time={time!r}, tz={tz!r}, alt={alt!r}, lang={lang!r})")
    return await minutely_api.solar_elevation_angle(location, date, time, tz, alt, lang)


if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8000, show_banner=True)
    else:
        mcp.run(transport="stdio")
