from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_key: str = Field("local-dev-key", validation_alias="YOLO_GATEWAY_API_KEY")
    model_id: str = Field("yolo-cpu-detector", validation_alias="YOLO_MODEL_ID")


@lru_cache
def get_settings() -> Settings:
    return Settings()
