from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    qweather_api_host: str = Field(default="", alias="QWEATHER_API_HOST")
    private_key_path: str = "keys/ed25519-private.pem"

    key_id: str = Field(default="", alias="QWEATHER_KEY_ID")
    project_id: str = Field(default="", alias="QWEATHER_PROJECT_ID")


settings = Settings()
