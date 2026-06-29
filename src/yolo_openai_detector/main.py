from __future__ import annotations

from typing import Annotated, Any

from fastapi import Body, Depends, FastAPI
from fastapi.exceptions import RequestValidationError

from yolo_openai_detector.auth import require_api_key
from yolo_openai_detector.config import Settings, get_settings
from yolo_openai_detector.image_input import extract_single_image_data_url
from yolo_openai_detector.openai_compat import (
    MODEL_ID,
    OpenAIError,
    chat_completion_stub_response,
    error_response,
    malformed_request_error,
    models_response,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="yolo-openai-detector",
        version="0.0.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    @app.exception_handler(OpenAIError)
    async def handle_openai_error(_request: Any, exc: OpenAIError):
        return error_response(exc)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_request: Any, _exc: RequestValidationError):
        return error_response(malformed_request_error())

    @app.get("/healthz", include_in_schema=False)
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/v1/models", dependencies=[Depends(require_api_key)])
    def list_models(settings: Annotated[Settings, Depends(get_settings)]) -> dict[str, Any]:
        return models_response(settings.model_id)

    @app.post("/v1/chat/completions", dependencies=[Depends(require_api_key)])
    def create_chat_completion(
        payload: Annotated[dict[str, Any], Body()],
        settings: Annotated[Settings, Depends(get_settings)],
    ) -> dict[str, Any]:
        model = payload.get("model")
        if model != MODEL_ID:
            raise OpenAIError(
                message=f"Model '{model}' was not found.",
                status_code=400,
                param="model",
                code="model_not_found",
            )

        extract_single_image_data_url(payload)
        return chat_completion_stub_response(settings.model_id)

    return app


app = create_app()
