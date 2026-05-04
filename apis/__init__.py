import httpx

_shared_http_client: httpx.AsyncClient = None


def get_shared_http_client() -> httpx.AsyncClient:
    global _shared_http_client
    if _shared_http_client is None or _shared_http_client.is_closed:
        _shared_http_client = httpx.AsyncClient(
            headers={"Accept-Encoding": "gzip"},
            timeout=10.0,
        )
    return _shared_http_client


async def close_shared_http_client():
    global _shared_http_client
    if _shared_http_client and not _shared_http_client.is_closed:
        await _shared_http_client.aclose()
        _shared_http_client = None


from .geo import GeoAPI
from .weather import WeatherAPI
from .minutely import MinutelyAPI

__all__ = ["GeoAPI", "WeatherAPI", "MinutelyAPI", "get_shared_http_client", "close_shared_http_client"]