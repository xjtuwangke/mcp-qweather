import httpx
import time
import base64
import json
import logging
from pathlib import Path

from config import settings

logger = logging.getLogger(__name__)


class QWeatherAPI:
    """
    Base class for QWeather API clients.
    Provides JWT generation and HTTP request handling.
    """

    def __init__(self, api_host: str = None):
        self.api_host = api_host or settings.qweather_api_host

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
        logger.info(f"GET {url} params={params}")
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            logger.info(f"GET {response.request.url} status={response.status_code}")
            response.raise_for_status()
            return response.json()
