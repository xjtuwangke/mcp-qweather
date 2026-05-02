import logging

from apis.base import QWeatherAPI

logger = logging.getLogger(__name__)


class GeoAPI(QWeatherAPI):
    """
    QWeather GeoAPI - City search and POI search services.
    Docs: https://dev.qweather.com/docs/api/geoapi/
    """

    async def city_lookup(self, location: str, adm: str = None, range: str = None, number: int = 10, lang: str = None) -> dict:
        """
        City search by name or coordinates.
        Docs: https://dev.qweather.com/docs/api/geoapi/city-lookup/

        Args:
            location: City name or coordinates (required). Example: "Beijing", "116.41,39.92"
            adm: Upper administrative district. Example: "Beijing", "Shaanxi"
            range: Country code (ISO 3166). Example: "cn", "us", "jp"
            number: Number of results (1-20, default 10). Example: 5, 10
            lang: Language. Example: "en", "zh"

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
            lang: Language. Example: "en", "zh"

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
            lang: Language. Example: "en", "zh"

        Returns:
            dict: {"code": "200", "poi": [{"name": "Zhongshan Park", "id": "10101010016A", "lat": "39.91", "lon": "116.39", "type": "scenic", "adm2": "Beijing", "adm1": "Beijing", "country": "China"}]}
        """
        params = {"location": location, "type": type, "radius": radius}
        if number:
            params["number"] = number
        if lang:
            params["lang"] = lang
        return await self._request("/geo/v2/poi/range", params)
