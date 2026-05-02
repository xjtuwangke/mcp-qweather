import logging

from apis.base import QWeatherAPI

logger = logging.getLogger(__name__)


class MinutelyAPI(QWeatherAPI):
    """
    QWeather Minutely Precipitation, Air Quality, and Astronomy APIs.
    Docs: https://dev.qweather.com/docs/api/
    """

    async def minutely_precipitation(self, location: str, lang: str = None) -> dict:
        """
        Get minutely precipitation forecast (next 2 hours, 5-min intervals) for China.
        Docs: https://dev.qweather.com/docs/api/minutely/minutely-precipitation/

        Args:
            location: Coordinates (required). Example: "116.41,39.92" (longitude,latitude)
            lang: Language. Example: "en", "zh-Hans"

        Returns:
            dict: {"code": "200", "summary": "No precipitation in the next 2 hours", "minutely": [{"fxTime": "2026-05-01T19:05+08:00", "precip": "0.00", "type": "rain"}]}
        """
        params = {"location": location}
        if lang:
            params["lang"] = lang
        return await self._request("/v7/minutely/5m", params)

    async def indices_forecast(self, location: str, type: str, days: str = "1d", lang: str = None) -> dict:
        """
        Get weather indices forecast (car wash, clothing, UV, etc.).
        Docs: https://dev.qweather.com/docs/api/indices/indices-forecast/

        Args:
            location: LocationID or coordinates (required). Example: "101010100", "116.41,39.92"
            type: Index type IDs (required, comma-separated). Example: "1,2,3"
                  Types: 1=Sports, 2=Car Wash, 3=Clothing, 4=Cold, 5=Exercise, 6=Tourism,
                  7=UV Index, 8=Air Pollution Diffusion, 9=AC, 10=Allergy,
                  11=Sunglasses, 12=Makeup, 13=Drying, 14=Traffic, 15=Fishing, 16=Sunscreen
            days: Forecast days. Example: "1d", "3d"
            lang: Language. Example: "en", "zh-Hans"

        Returns:
            dict: {"code": "200", "daily": [{"date": "2026-05-01", "type": "3", "name": "Clothing Index", "level": "4", "category": "Moderate", "text": "Wear a light jacket."}]}
        """
        params = {"location": location, "type": type}
        if days:
            path = f"/v7/indices/{days}"
        else:
            path = "/v7/indices/1d"
        if lang:
            params["lang"] = lang
        return await self._request(path, params)

    async def air_now(self, lat: float, lon: float, lang: str = None) -> dict:
        """
        Get current air quality index (AQI) for coordinates.
        Docs: https://dev.qweather.com/docs/api/air-quality/air-current/

        Args:
            lat: Latitude (required). Example: 39.92
            lon: Longitude (required). Example: 116.41
            lang: Language. Example: "en", "zh-Hans"

        Returns:
            dict: {"code": "200", "indexes": [{"code": "cn-mee", "name": "AQI (CN)", "aqi": 78, "level": "2", "category": "Good"}], "pollutants": [{"code": "pm2p5", "name": "PM2.5", "concentration": {"value": 46.14, "unit": "μg/m³"}}], "stations": [{"id": "P58655", "name": "Wanshou Xigong"}]}
        """
        params = {}
        if lang:
            params["lang"] = lang
        return await self._request(f"/airquality/v1/current/{lat}/{lon}", params)

    async def air_hourly(self, lat: float, lon: float, local_time: bool = None, lang: str = None) -> dict:
        """
        Get hourly air quality forecast (next 24 hours).
        Docs: https://dev.qweather.com/docs/api/air-quality/air-hourly-forecast/

        Args:
            lat: Latitude (required). Example: 39.92
            lon: Longitude (required). Example: 116.41
            local_time: Return local time (true/false, default false). Example: True, False
            lang: Language. Example: "en", "zh-Hans"

        Returns:
            dict: {"code": "200", "hours": [{"forecastTime": "2026-05-01T12:00Z", "indexes": [{"code": "cn-mee", "name": "AQI (CN)", "aqi": 63, "level": "2", "category": "Good"}], "pollutants": []}]}
        """
        params = {}
        if local_time is not None:
            params["localTime"] = "true" if local_time else "false"
        if lang:
            params["lang"] = lang
        return await self._request(f"/airquality/v1/hourly/{lat}/{lon}", params)

    async def air_daily(self, lat: float, lon: float, local_time: bool = None, lang: str = None) -> dict:
        """
        Get daily air quality forecast (next 3 days).
        Docs: https://dev.qweather.com/docs/api/air-quality/air-daily-forecast/

        Args:
            lat: Latitude (required). Example: 39.92
            lon: Longitude (required). Example: 116.41
            local_time: Return local time (true/false, default false). Example: True, False
            lang: Language. Example: "en", "zh-Hans"

        Returns:
            dict: {"code": "200", "days": [{"forecastStartTime": "2026-04-30T16:00Z", "forecastEndTime": "2026-05-01T16:00Z", "indexes": [{"code": "cn-mee", "name": "AQI (CN)", "aqi": 78, "level": "2", "category": "Good"}], "pollutants": []}]}
        """
        params = {}
        if local_time is not None:
            params["localTime"] = "true" if local_time else "false"
        if lang:
            params["lang"] = lang
        return await self._request(f"/airquality/v1/daily/{lat}/{lon}", params)

    async def air_station(self, location_id: str, lang: str = None) -> dict:
        """
        Get air quality data for a specific monitoring station.
        Docs: https://dev.qweather.com/docs/api/air-quality/air-station/

        Args:
            location_id: Station LocationID (required). Example: "P53763"
            lang: Language. Example: "en", "zh-Hans"

        Returns:
            dict: {"code": "200", "pollutants": [{"code": "pm2p5", "name": "PM2.5", "fullName": "Particulate Matter (≤2.5μm)", "concentration": {"value": 27.0, "unit": "μg/m³"}}]}
        """
        params = {}
        if lang:
            params["lang"] = lang
        return await self._request(f"/airquality/v1/station/{location_id}", params)

    async def astronomy_sun(self, location: str, date: str, lang: str = None) -> dict:
        """
        Get sunrise and sunset times.
        Docs: https://dev.qweather.com/docs/api/astronomy/sunrise-sunset/

        Args:
            location: LocationID or coordinates (required). Example: "101010100", "116.41,39.92"
            date: Date (required). Example: "20260201" (yyyyMMdd format)
            lang: Language. Example: "en", "zh-Hans"

        Returns:
            dict: {"code": "200", "sunrise": "2026-05-01T05:16+08:00", "sunset": "2026-05-01T19:08+08:00"}
        """
        params = {"location": location, "date": date}
        if lang:
            params["lang"] = lang
        return await self._request("/v7/astronomy/sun", params)

    async def astronomy_moon(self, location: str, date: str, lang: str = None) -> dict:
        """
        Get moonrise, moonset and hourly moon phase.
        Docs: https://dev.qweather.com/docs/api/astronomy/moon-and-moon-phase/

        Args:
            location: LocationID or coordinates (required). Example: "101010100", "116.41,39.92"
            date: Date (required). Example: "20260201" (yyyyMMdd format)
            lang: Language. Example: "en", "zh-Hans"

        Returns:
            dict: {"code": "200", "moonrise": "2026-05-01T19:04+08:00", "moonset": "2026-05-01T04:40+08:00", "moonPhase": [{"fxTime": "2026-05-01T00:00+08:00", "value": "0.47", "name": "Waxing Gibbous", "illumination": "99", "icon": "803"}]}
        """
        params = {"location": location, "date": date}
        if lang:
            params["lang"] = lang
        return await self._request("/v7/astronomy/moon", params)

    async def solar_elevation_angle(self, location: str, date: str, time: str, tz: str, alt: float, lang: str = None) -> dict:
        """
        Get solar elevation and azimuth angles for any time point.
        Docs: https://dev.qweather.com/docs/api/astronomy/solar-elevation-angle/

        Args:
            location: Coordinates (required). Example: "116.41,39.92"
            date: Date (required). Example: "20260201" (yyyyMMdd)
            time: Time (required). Example: "1230" (HHmm, 24-hour)
            tz: Timezone (required). Example: "0800", "-0530"
            alt: Altitude in meters (required). Example: 43
            lang: Language. Example: "en", "zh-Hans"

        Returns:
            dict: {"code": "200", "solarElevationAngle": "64.83", "solarAzimuthAngle": "190.55", "solarHour": "1218", "hourAngle": "-4.63"}
        """
        params = {"location": location, "date": date, "time": time, "tz": tz, "alt": int(alt)}
        if lang:
            params["lang"] = lang
        return await self._request("/v7/astronomy/solar-elevation-angle", params)
