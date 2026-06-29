from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_key: str = Field("local-dev-key", validation_alias="YOLO_GATEWAY_API_KEY")
    model_id: str = Field("yolo-cpu-detector", validation_alias="YOLO_MODEL_ID")
    max_image_bytes: int = Field(5_242_880, validation_alias="YOLO_MAX_IMAGE_BYTES")
    max_image_pixels: int = Field(12_000_000, validation_alias="YOLO_MAX_IMAGE_PIXELS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
