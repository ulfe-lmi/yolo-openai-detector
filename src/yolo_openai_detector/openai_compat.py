from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from fastapi.responses import JSONResponse

MODEL_ID = "yolo-cpu-detector"


@dataclass(frozen=True)
class OpenAIError(Exception):
    message: str
    status_code: int = 400
    error_type: str = "invalid_request_error"
    param: str | None = None
    code: str | None = None


def error_response(error: OpenAIError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": {
                "message": error.message,
                "type": error.error_type,
                "param": error.param,
                "code": error.code,
            }
        },
    )


def models_response(model_id: str = MODEL_ID) -> dict[str, Any]:
    return {
        "object": "list",
        "data": [
            {
                "id": model_id,
                "object": "model",
                "created": 0,
                "owned_by": "local",
            }
        ],
    }


def chat_completion_stub_response(
    model_id: str = MODEL_ID,
    *,
    image: dict[str, Any] | None = None,
) -> dict[str, Any]:
    content = {
        "model": model_id,
        "status": "not_implemented",
        "message": "YOLO inference is not implemented yet.",
    }
    if image is not None:
        content["image"] = image

    return {
        "id": "chatcmpl-local-000000000000",
        "object": "chat.completion",
        "created": 0,
        "model": model_id,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": json.dumps(content, separators=(",", ":")),
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
    }


def malformed_request_error() -> OpenAIError:
    return OpenAIError(
        message="Malformed request body.",
        status_code=400,
        param=None,
        code="malformed_request",
    )
