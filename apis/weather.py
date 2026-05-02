import logging

from apis.base import QWeatherAPI, validate_lang

logger = logging.getLogger(__name__)


class WeatherAPI(QWeatherAPI):
    """
    QWeather Weather API - Current, daily, and hourly weather forecasts.
    Docs: https://dev.qweather.com/docs/api/weather/
    """

    async def weather_now(self, location: str, lang: str = None, unit: str = None) -> dict:
        """
        Get current weather for a location.
        Docs: https://dev.qweather.com/docs/api/weather/weather-now/

        Args:
            location: LocationID or coordinates (required). Example: "101010100", "116.41,39.92"
            lang: Language. Example: "en", "zh"
            unit: Unit system - "m" for metric, "i" for imperial (default: metric). Example: "m", "i"

        Returns:
            dict: {"code": "200", "now": {"obsTime": "2026-05-01T19:00+08:00", "temp": "20", "feelsLike": "17", "icon": "104", "text": "Cloudy", "windDir": "Southeast", "windScale": "2", "windSpeed": "7", "humidity": "36", "precip": "0.0", "pressure": "1005", "vis": "18"}}
        """
        params = {"location": location}
        lang = validate_lang(lang)
        if lang:
            params["lang"] = lang
        if unit:
            params["unit"] = unit
        return await self._request("/v7/weather/now", params)

    async def weather_daily(self, location: str, days: str = "7d", lang: str = None, unit: str = None) -> dict:
        """
        Get daily weather forecast (3-30 days).
        Docs: https://dev.qweather.com/docs/api/weather/weather-daily-forecast/

        Args:
            location: LocationID or coordinates (required). Example: "101010100", "116.41,39.92"
            days: Forecast days (required). Example: "3d", "7d", "10d", "15d", "30d"
            lang: Language. Example: "en", "zh"
            unit: Unit system - "m" for metric, "i" for imperial (default: metric). Example: "m", "i"

        Returns:
            dict: {"code": "200", "daily": [{"fxDate": "2026-05-01", "sunrise": "05:16", "sunset": "19:08", "moonrise": "19:04", "moonset": "04:40", "moonPhase": "Waxing Gibbous", "tempMax": "26", "tempMin": "14", "iconDay": "101", "textDay": "Cloudy", "iconNight": "104", "textNight": "Cloudy", "windDirDay": "East", "windScaleDay": "1-3", "precip": "0.0", "uvIndex": "8"}]}
        """
        params = {"location": location}
        lang = validate_lang(lang)
        if lang:
            params["lang"] = lang
        if unit:
            params["unit"] = unit
        return await self._request(f"/v7/weather/{days}", params)

    async def weather_hourly(self, location: str, hours: str = "24h", lang: str = None, unit: str = None) -> dict:
        """
        Get hourly weather forecast (24-168 hours).
        Docs: https://dev.qweather.com/docs/api/weather/weather-hourly-forecast/

        Args:
            location: LocationID or coordinates (required). Example: "101010100", "116.41,39.92"
            hours: Forecast hours (required). Example: "24h", "72h", "168h"
            lang: Language. Example: "en", "zh"
            unit: Unit system - "m" for metric, "i" for imperial (default: metric). Example: "m", "i"

        Returns:
            dict: {"code": "200", "hourly": [{"fxTime": "2026-05-01T20:00+08:00", "temp": "20", "icon": "104", "text": "Cloudy", "windDir": "Southeast", "windScale": "1-3", "windSpeed": "14", "humidity": "31", "pop": "0", "precip": "0.0"}]}
        """
        params = {"location": location}
        lang = validate_lang(lang)
        if lang:
            params["lang"] = lang
        if unit:
            params["unit"] = unit
        return await self._request(f"/v7/weather/{hours}", params)

    async def grid_weather_now(self, location: str, lang: str = None, unit: str = None) -> dict:
        """
        Get grid-based current weather using numerical weather prediction (3-5km resolution).
        Docs: https://dev.qweather.com/docs/api/weather/grid-weather-now/

        Args:
            location: Coordinates (required). Example: "116.41,39.92" (longitude,latitude)
            lang: Language. Example: "en", "zh"
            unit: Unit system - "m" for metric, "i" for imperial (default: metric). Example: "m", "i"

        Returns:
            dict: {"code": "200", "now": {"obsTime": "2026-05-01T11:00+00:00", "temp": "20", "feelsLike": "18", "icon": "151", "text": "Few Clouds", "windDir": "Southeast", "windScale": "2", "windSpeed": "11", "humidity": "31", "precip": "0.0", "pressure": "1004"}}
        """
        params = {"location": location}
        lang = validate_lang(lang)
        if lang:
            params["lang"] = lang
        if unit:
            params["unit"] = unit
        return await self._request("/v7/grid-weather/now", params)

    async def grid_weather_daily(self, location: str, days: str = "7d", lang: str = None, unit: str = None) -> dict:
        """
        Get grid-based daily weather forecast using numerical weather prediction (3-5km resolution).
        Docs: https://dev.qweather.com/docs/api/weather/grid-weather-daily-forecast/

        Args:
            location: Coordinates (required). Example: "116.41,39.92"
            days: Forecast days (required). Example: "3d", "7d"
            lang: Language. Example: "en", "zh"
            unit: Unit system - "m" for metric, "i" for imperial (default: metric). Example: "m", "i"

        Returns:
            dict: {"code": "200", "daily": [{"fxDate": "2026-05-01", "tempMax": "27", "tempMin": "14", "iconDay": "102", "textDay": "Few Clouds", "iconNight": "152", "textNight": "Few Clouds", "windDirDay": "Southeast", "windScaleDay": "2", "precip": "0.00"}]}
        """
        params = {"location": location}
        lang = validate_lang(lang)
        if lang:
            params["lang"] = lang
        if unit:
            params["unit"] = unit
        return await self._request(f"/v7/grid-weather/{days}", params)

    async def grid_weather_hourly(self, location: str, hours: str = "24h", lang: str = None, unit: str = None) -> dict:
        """
        Get grid-based hourly weather forecast using numerical weather prediction (3-5km resolution).
        Docs: https://dev.qweather.com/docs/api/weather/grid-weather-hourly-forecast/

        Args:
            location: Coordinates (required). Example: "116.41,39.92"
            hours: Forecast hours (required). Example: "24h", "72h"
            lang: Language. Example: "en", "zh"
            unit: Unit system - "m" for metric, "i" for imperial (default: metric). Example: "m", "i"

        Returns:
            dict: {"code": "200", "hourly": [{"fxTime": "2026-05-01T12:00+00:00", "temp": "19", "icon": "151", "text": "Few Clouds", "windDir": "Southeast", "windScale": "2", "windSpeed": "9", "humidity": "33", "precip": "0.0"}]}
        """
        params = {"location": location}
        lang = validate_lang(lang)
        if lang:
            params["lang"] = lang
        if unit:
            params["unit"] = unit
        return await self._request(f"/v7/grid-weather/{hours}", params)
