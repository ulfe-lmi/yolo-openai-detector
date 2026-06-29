from __future__ import annotations

import json

from fastapi.testclient import TestClient

from yolo_openai_detector.main import app

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer local-dev-key"}
VALID_IMAGE_URL = "data:image/jpeg;base64,aGVsbG8="


def valid_payload(**overrides):
    payload = {
        "model": "yolo-cpu-detector",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Detect objects in this image."},
                    {"type": "image_url", "image_url": {"url": VALID_IMAGE_URL}},
                ],
            }
        ],
    }
    payload.update(overrides)
    return payload


def assert_openai_error(response, *, status_code: int, code: str):
    assert response.status_code == status_code
    body = response.json()
    assert set(body) == {"error"}
    assert body["error"]["message"]
    assert body["error"]["type"] in {"invalid_request_error", "authentication_error"}
    assert body["error"]["code"] == code
    assert "param" in body["error"]


def test_app_imports_successfully():
    assert app is not None


def test_models_requires_auth():
    response = client.get("/v1/models")

    assert_openai_error(response, status_code=401, code="missing_api_key")


def test_models_returns_yolo_cpu_detector():
    response = client.get("/v1/models", headers=AUTH_HEADERS)

    assert response.status_code == 200
    assert response.json() == {
        "object": "list",
        "data": [
            {
                "id": "yolo-cpu-detector",
                "object": "model",
                "created": 0,
                "owned_by": "local",
            }
        ],
    }


def test_chat_rejects_missing_auth_before_body_validation():
    response = client.post("/v1/chat/completions", json={"messages": "not parsed first"})

    assert_openai_error(response, status_code=401, code="missing_api_key")


def test_chat_rejects_wrong_auth():
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer wrong-key"},
        json=valid_payload(),
    )

    assert_openai_error(response, status_code=401, code="invalid_api_key")


def test_chat_accepts_valid_single_image_data_url_request():
    response = client.post("/v1/chat/completions", headers=AUTH_HEADERS, json=valid_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "chat.completion"
    assert body["model"] == "yolo-cpu-detector"
    assert body["choices"][0]["message"]["role"] == "assistant"
    content = json.loads(body["choices"][0]["message"]["content"])
    assert content == {
        "model": "yolo-cpu-detector",
        "status": "not_implemented",
        "message": "YOLO inference is not implemented in this skeleton PR.",
    }
    assert body["usage"] == {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }


def test_chat_rejects_unknown_model():
    response = client.post(
        "/v1/chat/completions",
        headers=AUTH_HEADERS,
        json=valid_payload(model="unknown-model"),
    )

    assert_openai_error(response, status_code=400, code="model_not_found")


def test_chat_rejects_missing_image():
    response = client.post(
        "/v1/chat/completions",
        headers=AUTH_HEADERS,
        json=valid_payload(
            messages=[{"role": "user", "content": [{"type": "text", "text": "Hi"}]}]
        ),
    )

    assert_openai_error(response, status_code=400, code="missing_image")


def test_chat_rejects_multiple_images():
    response = client.post(
        "/v1/chat/completions",
        headers=AUTH_HEADERS,
        json=valid_payload(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": VALID_IMAGE_URL}},
                        {"type": "image_url", "image_url": {"url": VALID_IMAGE_URL}},
                    ],
                }
            ]
        ),
    )

    assert_openai_error(response, status_code=400, code="multiple_images_not_supported")


def test_chat_rejects_http_image_url():
    response = client.post(
        "/v1/chat/completions",
        headers=AUTH_HEADERS,
        json=valid_payload(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": "https://example.com/cat.jpg"}}
                    ],
                }
            ]
        ),
    )

    assert_openai_error(response, status_code=400, code="external_image_url_not_supported")


def test_chat_rejects_raw_base64():
    response = client.post(
        "/v1/chat/completions",
        headers=AUTH_HEADERS,
        json=valid_payload(
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "image_url", "image_url": {"url": "aGVsbG8="}}],
                }
            ]
        ),
    )

    assert_openai_error(response, status_code=400, code="invalid_image_url")


def test_chat_rejects_unsupported_mime_prefix():
    response = client.post(
        "/v1/chat/completions",
        headers=AUTH_HEADERS,
        json=valid_payload(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": "data:image/gif;base64,aGVsbG8="},
                        }
                    ],
                }
            ]
        ),
    )

    assert_openai_error(response, status_code=400, code="unsupported_image_type")


def test_chat_rejects_video_like_input():
    response = client.post(
        "/v1/chat/completions",
        headers=AUTH_HEADERS,
        json=valid_payload(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": "data:video/mp4;base64,aGVsbG8="},
                        }
                    ],
                }
            ]
        ),
    )

    assert_openai_error(response, status_code=400, code="unsupported_image_type")


def test_chat_rejects_malformed_base64():
    response = client.post(
        "/v1/chat/completions",
        headers=AUTH_HEADERS,
        json=valid_payload(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": "data:image/png;base64,not-valid!!!!"},
                        }
                    ],
                }
            ]
        ),
    )

    assert_openai_error(response, status_code=400, code="invalid_base64")


def test_chat_rejects_file_id():
    response = client.post(
        "/v1/chat/completions",
        headers=AUTH_HEADERS,
        json=valid_payload(
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "image_url", "image_url": {"file_id": "file-123"}}],
                }
            ]
        ),
    )

    assert_openai_error(response, status_code=400, code="file_id_not_supported")


def test_chat_rejects_malformed_body_with_openai_error_shape():
    response = client.post(
        "/v1/chat/completions",
        headers={**AUTH_HEADERS, "Content-Type": "application/json"},
        content="{",
    )

    assert_openai_error(response, status_code=400, code="malformed_request")
