# yolo-openai-detector

CPU-only, single-image YOLO object detection behind a narrow OpenAI-compatible API.

This repository is intentionally scoped as a **local object-detection gateway**, not as a general LLM proxy.

## What this project does

The service will let users call YOLO object detection using OpenAI-style client code:

```python
from openai import OpenAI

client = OpenAI(
    api_key="local-dev-key",
    base_url="http://localhost:8000/v1",
)

response = client.chat.completions.create(
    model="yolo-cpu-detector",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Detect objects in this image."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
                    },
                },
            ],
        }
    ],
)

print(response.choices[0].message.content)
```

The assistant message content is JSON text containing object detections.

## Current repository status

The repository now includes the FastAPI API service:

- fixed bearer-token authentication;
- `GET /v1/models`;
- `POST /v1/chat/completions`;
- OpenAI-shaped success and error envelopes;
- strict validation for exactly one JPEG/PNG Base64 image data URL;
- Pillow-based image decoding, byte limits, pixel limits, and image metadata;
- a detector interface;
- real CPU YOLO object detection through Ultralytics.

The default runtime detector is Ultralytics YOLO on CPU. A deterministic stub detector remains
available for tests.

## Product boundary

This project is only for:

- CPU-only operation;
- one image per request;
- single-shot object detection;
- Base64 image data URL input;
- OpenAI-compatible `/v1/models`;
- OpenAI-compatible `/v1/chat/completions`;
- fixed bearer-token authentication.

## Explicit non-goals

This project does **not** implement:

- tracking;
- video;
- segmentation;
- masks;
- webcam input;
- background jobs;
- async job queues;
- multiple image requests;
- file upload endpoints;
- HTTP/HTTPS image fetching;
- OpenAI Files API emulation;
- upstream OpenAI API calls;
- GPU-only execution;
- persistence/database;
- billing/accounting;
- user management.

## API key

The service uses one fixed API key from:

```bash
export YOLO_GATEWAY_API_KEY="local-dev-key"
```

Requests must include:

```http
Authorization: Bearer local-dev-key
```

The implementation must compare the key using constant-time comparison and must never log it.

## Image limits

The image validation layer uses CPU-only Pillow decoding and these environment-driven limits:

```bash
export YOLO_MAX_IMAGE_BYTES=5242880
export YOLO_MAX_IMAGE_PIXELS=12000000
```

Defaults are 5,242,880 decoded bytes and 12,000,000 pixels. Size-limit failures return
OpenAI-shaped errors with HTTP `413` and code `image_too_large`.

## Detector configuration

The default detector backend is Ultralytics YOLO on CPU:

```bash
export YOLO_DETECTOR_BACKEND=ultralytics
export YOLO_MODEL_WEIGHTS=yolo11n.pt
export YOLO_CONFIDENCE_THRESHOLD=0.25
export YOLO_IOU_THRESHOLD=0.7
export YOLO_IMAGE_SIZE=640
export YOLO_DEVICE=cpu
```

`YOLO_DEVICE` must remain `cpu`. GPU/CUDA execution is outside this project's scope.

Ultralytics may download the configured weights on first use unless the weights are already
available in the runtime environment. Do not commit downloaded `.pt` weight files.

## OpenAI-compatible endpoints

| Endpoint | Purpose |
|---|---|
| `GET /v1/models` | Return available model list containing `yolo-cpu-detector` |
| `POST /v1/chat/completions` | Accept one Base64 image data URL and return detections |

No other user-facing endpoints are part of the compatibility contract.

## Image input format

Only this image input path is supported:

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/jpeg;base64,..."
  }
}
```

Supported first-release MIME types:

- `image/jpeg`
- `image/png`

The API must reject HTTP URLs, file IDs, raw Base64 without a data URL prefix, multiple images, videos, unsupported MIME types, malformed Base64, oversized payloads, and excessive pixel counts.

## Detection response

`POST /v1/chat/completions` returns an OpenAI-shaped chat completion whose assistant message
content is JSON text:

```json
{
  "model": "yolo-cpu-detector",
  "objects": [
    {
      "label": "person",
      "confidence": 0.91,
      "bbox_xyxy": [34, 52, 188, 401]
    }
  ],
  "image": {
    "mime_type": "image/jpeg",
    "width": 640,
    "height": 480,
    "bytes": 123456
  }
}
```

Images with no detections return:

```json
{
  "model": "yolo-cpu-detector",
  "objects": [],
  "image": {
    "mime_type": "image/jpeg",
    "width": 640,
    "height": 480,
    "bytes": 123456
  }
}
```

## Development setup

The implementation is expected to use Python.

Suggested setup after implementation starts:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

Run the service locally:

```bash
export YOLO_GATEWAY_API_KEY="local-dev-key"
uvicorn yolo_openai_detector.main:app --host 127.0.0.1 --port 8000
```

Run the normal test suite without downloading model weights:

```bash
python -m pytest
ruff check .
```

Normal tests use the deterministic stub backend or monkeypatched Ultralytics objects and do not
download weights.

## Documentation map

| File | Purpose |
|---|---|
| `AGENTS.md` | Operational law for coding agents |
| `CLAUDE.md` | Equivalent operational law for Claude Code |
| `PROJECT_CHARTER.md` | Human-readable product charter |
| `docs/api-contract.md` | Detailed API contract |
| `docs/architecture.md` | Architecture and component boundaries |
| `docs/compatibility-matrix.md` | What OpenAI compatibility means and does not mean |
| `docs/dependency-policy.md` | Dependency and model-backend policy |
| `docs/security.md` | API key, logging, and fail-closed rules |
| `docs/testing-strategy.md` | Test requirements and evidence standards |
| `docs/roadmap.md` | PR-sized implementation sequence |
| `docs/release-checklist.md` | Release-readiness checklist |
| `docs/work-orders/` | Coding-agent work orders |

## External reference notes

OpenAI's image-input documentation supports image input through URLs, Base64 data URLs, and file IDs. This project deliberately supports only Base64 data URLs to keep the local service self-contained and avoid network fetching or file-storage complexity.

OpenAI-compatible model discovery is represented by `/v1/models`; this project keeps that endpoint as compatibility sugar even though there is only one local detector model.

## License

No license is chosen in this initialization package. Add a `LICENSE` file only after the human owner decides the repository license and confirms compatibility with the selected YOLO backend.

Ultralytics YOLO code and trained models are AGPL-3.0 by default. Private, proprietary,
commercial, SaaS/API, or embedded deployments may require an Ultralytics Enterprise License.
This repository does not grant such a license.
