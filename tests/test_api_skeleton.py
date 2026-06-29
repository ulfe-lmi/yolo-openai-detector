from __future__ import annotations

import base64
import json
import sys
from io import BytesIO
from types import ModuleType, SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from yolo_openai_detector.config import Settings, get_settings
from yolo_openai_detector.detector import (
    Detection,
    DetectionResult,
    DetectorConfigurationError,
    StubDetector,
    clear_detector_cache,
    detection_response_content,
    get_detector,
)
from yolo_openai_detector.image_input import (
    ValidatedImage,
    validate_and_decode_image,
    validate_image_data_url,
)
from yolo_openai_detector.main import app
from yolo_openai_detector.yolo_detector import UltralyticsYoloDetector

client = TestClient(app)
AUTH_HEADERS = {"Authorization": "Bearer local-dev-key"}


@pytest.fixture(autouse=True)
def isolate_runtime_settings(monkeypatch):
    monkeypatch.setenv("YOLO_DETECTOR_BACKEND", "stub")
    get_settings.cache_clear()
    clear_detector_cache()
    yield
    get_settings.cache_clear()
    clear_detector_cache()


def make_image_data_url(*, image_format: str = "JPEG", mime_type: str = "image/jpeg", size=(3, 2)):
    image = Image.new("RGB", size, color=(32, 96, 160))
    buffer = BytesIO()
    image.save(buffer, format=image_format)
    image_bytes = buffer.getvalue()
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}", image_bytes


VALID_IMAGE_URL, VALID_IMAGE_BYTES = make_image_data_url()


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


def assistant_content(response):
    return json.loads(response.json()["choices"][0]["message"]["content"])


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
        json=valid_payload(messages="not parsed first"),
    )

    assert_openai_error(response, status_code=401, code="invalid_api_key")


def test_chat_accepts_valid_single_image_data_url_request():
    response = client.post("/v1/chat/completions", headers=AUTH_HEADERS, json=valid_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "chat.completion"
    assert body["model"] == "yolo-cpu-detector"
    assert body["choices"][0]["message"]["role"] == "assistant"
    content = assistant_content(response)
    assert content == {
        "model": "yolo-cpu-detector",
        "objects": [],
        "image": {
            "mime_type": "image/jpeg",
            "width": 3,
            "height": 2,
            "bytes": len(VALID_IMAGE_BYTES),
        },
    }
    assert "status" not in content
    assert "image_bytes" not in content
    assert base64.b64encode(VALID_IMAGE_BYTES).decode("ascii") not in response.text
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


def test_chat_rejects_unknown_model_before_image_decoding():
    response = client.post(
        "/v1/chat/completions",
        headers=AUTH_HEADERS,
        json=valid_payload(model="unknown-model", messages="not parsed first"),
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

    assert_openai_error(response, status_code=400, code="invalid_image_input")


def test_chat_rejects_malformed_data_url():
    response = client.post(
        "/v1/chat/completions",
        headers=AUTH_HEADERS,
        json=valid_payload(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": "data:image/jpeg;name=test"}}
                    ],
                }
            ]
        ),
    )

    assert_openai_error(response, status_code=400, code="invalid_image_input")


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

    assert_openai_error(response, status_code=400, code="invalid_base64_image")


def test_chat_rejects_base64_that_is_not_an_image():
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
                            "image_url": {"url": "data:image/png;base64,aGVsbG8="},
                        }
                    ],
                }
            ]
        ),
    )

    assert_openai_error(response, status_code=400, code="invalid_image_file")


def test_chat_accepts_valid_png_data_url_with_image_metadata():
    png_url, png_bytes = make_image_data_url(image_format="PNG", mime_type="image/png", size=(4, 5))
    response = client.post(
        "/v1/chat/completions",
        headers=AUTH_HEADERS,
        json=valid_payload(
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "image_url", "image_url": {"url": png_url}}],
                }
            ]
        ),
    )

    assert response.status_code == 200
    content = assistant_content(response)
    assert content["objects"] == []
    assert content["image"] == {
        "mime_type": "image/png",
        "width": 4,
        "height": 5,
        "bytes": len(png_bytes),
    }


def test_chat_enforces_decoded_byte_limit(monkeypatch):
    monkeypatch.setenv("YOLO_MAX_IMAGE_BYTES", "8")
    get_settings.cache_clear()

    response = client.post("/v1/chat/completions", headers=AUTH_HEADERS, json=valid_payload())

    assert_openai_error(response, status_code=413, code="image_too_large")


def test_chat_enforces_pixel_limit(monkeypatch):
    monkeypatch.setenv("YOLO_MAX_IMAGE_PIXELS", "5")
    get_settings.cache_clear()

    response = client.post("/v1/chat/completions", headers=AUTH_HEADERS, json=valid_payload())

    assert_openai_error(response, status_code=413, code="image_too_large")


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


def test_stub_detector_returns_empty_object_list():
    image = ValidatedImage(mime_type="image/jpeg", width=3, height=2, bytes=631, image_bytes=b"")

    result = StubDetector().detect(image)

    assert result.objects == []


def test_validated_image_preserves_bytes_internally():
    image_data_url = validate_image_data_url(VALID_IMAGE_URL)

    image = validate_and_decode_image(
        image_data_url,
        max_image_bytes=10_000,
        max_image_pixels=10_000,
    )

    assert image.bytes == len(VALID_IMAGE_BYTES)
    assert image.image_bytes == VALID_IMAGE_BYTES


def test_detection_response_content_serializes_objects_without_raw_bytes():
    image = ValidatedImage(
        mime_type="image/jpeg",
        width=3,
        height=2,
        bytes=631,
        image_bytes=b"raw-image-bytes",
    )
    detection_result = DetectionResult(
        objects=[
            Detection(
                label="person",
                confidence=0.91,
                bbox_xyxy=(34, 52, 188, 401),
            )
        ]
    )

    content = detection_response_content(
        model_id="yolo-cpu-detector",
        detection_result=detection_result,
        image=image,
    )

    assert content == {
        "model": "yolo-cpu-detector",
        "objects": [
            {
                "label": "person",
                "confidence": 0.91,
                "bbox_xyxy": [34, 52, 188, 401],
            }
        ],
        "image": {
            "mime_type": "image/jpeg",
            "width": 3,
            "height": 2,
            "bytes": 631,
        },
    }
    assert "image_bytes" not in json.dumps(content)
    assert "raw-image-bytes" not in json.dumps(content)


def test_detector_factory_selects_real_detector_by_default(monkeypatch):
    monkeypatch.delenv("YOLO_DETECTOR_BACKEND", raising=False)
    settings = Settings(_env_file=None)

    detector = get_detector(settings)

    assert isinstance(detector, UltralyticsYoloDetector)
    assert detector.device == "cpu"
    assert settings.device == "cpu"


def test_detector_factory_can_select_stub_backend():
    settings = Settings(_env_file=None, detector_backend="stub")

    detector = get_detector(settings)

    assert isinstance(detector, StubDetector)


def test_detector_factory_rejects_unsupported_backend():
    settings = Settings(_env_file=None, detector_backend="not-real")

    with pytest.raises(DetectorConfigurationError, match="Unsupported detector backend"):
        get_detector(settings)


def test_ultralytics_detector_can_be_unit_tested_without_downloading_weights(monkeypatch):
    captured = {}

    class FakeYOLO:
        names = {0: "person", 1: "cat"}

        def __init__(self, weights):
            captured["weights"] = weights

        def predict(self, source, conf, iou, imgsz, device, verbose):
            captured["source_mode"] = source.mode
            captured["conf"] = conf
            captured["iou"] = iou
            captured["imgsz"] = imgsz
            captured["device"] = device
            captured["verbose"] = verbose
            return [
                SimpleNamespace(
                    boxes=SimpleNamespace(
                        xyxy=[
                            [20.0, 10.0, 30.0, 40.0],
                            [1.2, 2.6, 10.4, 20.6],
                        ],
                        conf=[0.50, 0.95],
                        cls=[1, 0],
                    )
                )
            ]

    fake_ultralytics = ModuleType("ultralytics")
    fake_ultralytics.YOLO = FakeYOLO
    monkeypatch.setitem(sys.modules, "ultralytics", fake_ultralytics)

    detector = UltralyticsYoloDetector(
        model_weights="fake.pt",
        confidence_threshold=0.6,
        iou_threshold=0.7,
        image_size=640,
        device="cpu",
    )
    image = ValidatedImage(
        mime_type="image/jpeg",
        width=3,
        height=2,
        bytes=len(VALID_IMAGE_BYTES),
        image_bytes=VALID_IMAGE_BYTES,
    )

    result = detector.detect(image)

    assert captured == {
        "weights": "fake.pt",
        "source_mode": "RGB",
        "conf": 0.6,
        "iou": 0.7,
        "imgsz": 640,
        "device": "cpu",
        "verbose": False,
    }
    assert result.objects == [
        Detection(label="person", confidence=0.95, bbox_xyxy=(1, 3, 10, 21))
    ]
