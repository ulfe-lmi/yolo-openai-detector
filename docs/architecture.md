# Architecture

## Product shape

This is a small local inference gateway:

```text
OpenAI-style client
        |
        | base_url = http://host:port/v1
        | Authorization: Bearer <fixed-key>
        v
FastAPI application
        |
        +-- auth boundary
        +-- OpenAI-compatible request parser
        +-- strict single-image data URL validator
        +-- image decoder and limiter
        +-- CPU YOLO detector
        +-- OpenAI-shaped response formatter
```

## API boundary

The public compatibility boundary is `/v1`.

Required endpoints:

- `GET /v1/models`
- `POST /v1/chat/completions`

The service should not grow extra user-facing endpoints without an explicit work order.

## Component responsibilities

| Component | Responsibility |
|---|---|
| `config` | Environment variables, limits, defaults |
| `auth` | Bearer-token extraction and constant-time comparison |
| `openai_compat` | OpenAI-shaped request, response, and error models |
| `image_input` | Strict extraction of exactly one Base64 data URL |
| `image_decode` | Safe MIME/Base64/Pillow decoding and size limits |
| `detector` | CPU-only YOLO model loading and prediction |
| `formatting` | Deterministic detection JSON and chat-completion wrapper |

## Data flow

1. Request reaches `POST /v1/chat/completions`.
2. Authorization is checked first.
3. Request model name is validated.
4. Exactly one `image_url.url` data URL is extracted.
5. Input is checked for allowed MIME type and Base64 shape.
6. Decoded bytes and image dimensions are bounded.
7. Image is passed to CPU detector.
8. Detection results are normalized to the public JSON schema.
9. JSON is returned as assistant message content inside an OpenAI-shaped response.

## Fail-closed order

The service must reject invalid requests before expensive work:

```text
auth -> model -> request shape -> image count -> data URL -> MIME -> bytes -> pixels -> inference
```

## CPU-only design

The detector must explicitly run on CPU. GPU must be neither required nor assumed.

Acceptable implementation pattern:

```python
model.predict(source=image, device="cpu", imgsz=..., conf=...)
```

The exact call depends on the selected backend, but the invariant is stable: CPU is the default and required path.

## No persistence

The first architecture has no database and no durable image storage.

The implementation should not store:

- raw images;
- prompts;
- request bodies;
- detection histories;
- API keys.

Logs may include request IDs, timing, model ID, status code, and error codes, but not secrets or full image payloads.

## Model backend

The first likely backend is Ultralytics YOLO, but this is not locked until license and dependency implications are accepted.

A later backend abstraction may be useful:

```text
DetectorBackend.detect(image: PIL.Image) -> DetectionResult
```

Do not over-engineer the abstraction in PR 1. Add it when inference is implemented.

## Performance posture

Optimize for predictable CPU behavior:

- small default model;
- bounded image size;
- configurable confidence threshold;
- configurable image size;
- no video;
- no batching;
- no background jobs.

## Future extension boundaries

Allowed future extensions only with human approval:

- additional local detector models;
- ONNX Runtime CPU backend;
- internal liveness endpoint;
- Docker packaging;
- CPU performance benchmark script.

Forbidden unless constitution changes:

- tracking;
- video;
- segmentation;
- multi-image requests;
- URL fetching;
- file storage;
- upstream OpenAI calls.
