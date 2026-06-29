from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from io import BytesIO
from typing import Any

from PIL import Image, UnidentifiedImageError

from yolo_openai_detector.openai_compat import OpenAIError

SUPPORTED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png"}


@dataclass(frozen=True)
class ImageDataUrl:
    mime_type: str
    data_url: str


@dataclass(frozen=True)
class ValidatedImage:
    mime_type: str
    width: int
    height: int
    bytes: int
    image_bytes: bytes


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
    if not lowered.startswith("data:image/") or "," not in url:
        raise OpenAIError(
            message="Image input must be a Base64 image data URL.",
            param="messages",
            code="invalid_image_input",
        )

    metadata, encoded = url.split(",", 1)
    metadata_parts = metadata.split(";")
    mime_type = metadata_parts[0].removeprefix("data:").lower()
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
            code="invalid_image_input",
        )

    if not encoded:
        raise OpenAIError(
            message="Image data URL contains malformed Base64.",
            param="messages",
            code="invalid_base64_image",
        )

    return ImageDataUrl(mime_type=mime_type, data_url=url)


def validate_and_decode_image(
    image_data_url: ImageDataUrl,
    *,
    max_image_bytes: int,
    max_image_pixels: int,
) -> ValidatedImage:
    encoded = image_data_url.data_url.split(",", 1)[1]
    try:
        image_bytes = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise OpenAIError(
            message="Image data URL contains malformed Base64.",
            param="messages",
            code="invalid_base64_image",
        ) from exc

    byte_count = len(image_bytes)
    if byte_count > max_image_bytes:
        raise OpenAIError(
            message="Decoded image exceeds the configured byte limit.",
            status_code=413,
            param="messages",
            code="image_too_large",
        )

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            actual_mime_type = Image.MIME.get(image.format)
            width, height = image.size
            pixel_count = width * height

            if actual_mime_type != image_data_url.mime_type:
                raise OpenAIError(
                    message="Declared image MIME type does not match the decoded image.",
                    param="messages",
                    code="invalid_image_file",
                )
            if pixel_count > max_image_pixels:
                raise OpenAIError(
                    message="Decoded image exceeds the configured pixel limit.",
                    status_code=413,
                    param="messages",
                    code="image_too_large",
                )

            image.verify()

        with Image.open(BytesIO(image_bytes)) as image:
            image.load()
    except OpenAIError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
        raise OpenAIError(
            message="Decoded image bytes are not a valid JPEG or PNG image.",
            param="messages",
            code="invalid_image_file",
        ) from exc

    return ValidatedImage(
        mime_type=image_data_url.mime_type,
        width=width,
        height=height,
        bytes=byte_count,
        image_bytes=image_bytes,
    )


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
