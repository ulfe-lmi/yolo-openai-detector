from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from typing import Any

from yolo_openai_detector.openai_compat import OpenAIError

SUPPORTED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png"}


@dataclass(frozen=True)
class ImageDataUrl:
    mime_type: str
    data_url: str


def extract_single_image_data_url(payload: dict[str, Any]) -> ImageDataUrl:
    messages = payload.get("messages")
    if not isinstance(messages, list):
        raise OpenAIError(
            message="Messages must be an array.",
            param="messages",
            code="malformed_request",
        )

    image_urls: list[str] = []
    for message in messages:
        if not isinstance(message, dict):
            raise OpenAIError(
                message="Each message must be an object.",
                param="messages",
                code="malformed_request",
            )

        content = message.get("content")
        if isinstance(content, list):
            for part in content:
                if _is_image_url_part(part):
                    image_urls.append(part["image_url"]["url"])
                elif _is_file_id_part(part):
                    raise OpenAIError(
                        message="File ID image inputs are not supported.",
                        param="messages",
                        code="file_id_not_supported",
                    )
        elif _is_file_id_part(content):
            raise OpenAIError(
                message="File ID image inputs are not supported.",
                param="messages",
                code="file_id_not_supported",
            )
        elif isinstance(content, dict) and _is_image_url_part(content):
            image_urls.append(content["image_url"]["url"])
        elif content is not None and not isinstance(content, str | list | dict):
            raise OpenAIError(
                message="Message content must be a string or content-part array.",
                param="messages",
                code="malformed_request",
            )

    if not image_urls:
        raise OpenAIError(
            message="Exactly one Base64 image data URL is required.",
            param="messages",
            code="missing_image",
        )
    if len(image_urls) > 1:
        raise OpenAIError(
            message="Only one image is supported per request.",
            param="messages",
            code="multiple_images_not_supported",
        )

    return validate_image_data_url(image_urls[0])


def validate_image_data_url(url: Any) -> ImageDataUrl:
    if not isinstance(url, str):
        raise OpenAIError(
            message="Image URL must be a string.",
            param="messages",
            code="invalid_image_url",
        )

    lowered = url.lower()
    if lowered.startswith(("http://", "https://")):
        raise OpenAIError(
            message="External image URLs are not supported.",
            param="messages",
            code="external_image_url_not_supported",
        )
    if lowered.startswith("data:video/"):
        raise OpenAIError(
            message="Video inputs are not supported.",
            param="messages",
            code="unsupported_image_type",
        )
    if not lowered.startswith("data:image/") or ";base64," not in lowered:
        raise OpenAIError(
            message="Image input must be a Base64 image data URL.",
            param="messages",
            code="invalid_image_url",
        )

    metadata, encoded = url.split(",", 1)
    metadata_parts = metadata.split(";")
    mime_type = metadata_parts[0].removeprefix("data:")
    if mime_type not in SUPPORTED_IMAGE_MIME_TYPES:
        raise OpenAIError(
            message="Only JPEG and PNG image data URLs are supported.",
            param="messages",
            code="unsupported_image_type",
        )
    if "base64" not in {part.lower() for part in metadata_parts[1:]}:
        raise OpenAIError(
            message="Image input must be Base64 encoded.",
            param="messages",
            code="invalid_image_url",
        )

    try:
        base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise OpenAIError(
            message="Image data URL contains malformed Base64.",
            param="messages",
            code="invalid_base64",
        ) from exc

    return ImageDataUrl(mime_type=mime_type, data_url=url)


def _is_image_url_part(part: Any) -> bool:
    return (
        isinstance(part, dict)
        and part.get("type") == "image_url"
        and isinstance(part.get("image_url"), dict)
        and "url" in part["image_url"]
    )


def _is_file_id_part(part: Any) -> bool:
    if not isinstance(part, dict):
        return False
    if "file_id" in part:
        return True
    image_url = part.get("image_url")
    return isinstance(image_url, dict) and "file_id" in image_url
