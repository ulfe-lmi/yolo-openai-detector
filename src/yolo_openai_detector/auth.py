from __future__ import annotations

import hmac
from typing import Annotated

from fastapi import Depends, Header

from yolo_openai_detector.config import Settings, get_settings
from yolo_openai_detector.openai_compat import OpenAIError


def require_api_key(
    settings: Annotated[Settings, Depends(get_settings)],
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    if not authorization:
        raise OpenAIError(
            message="Missing API key.",
            status_code=401,
            error_type="authentication_error",
            param=None,
            code="missing_api_key",
        )

    scheme, separator, supplied_key = authorization.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not supplied_key:
        raise OpenAIError(
            message="Invalid API key.",
            status_code=401,
            error_type="authentication_error",
            param=None,
            code="invalid_api_key",
        )

    if not hmac.compare_digest(supplied_key, settings.api_key):
        raise OpenAIError(
            message="Invalid API key.",
            status_code=401,
            error_type="authentication_error",
            param=None,
            code="invalid_api_key",
        )
