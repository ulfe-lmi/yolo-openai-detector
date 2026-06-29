# API Contract

## Compatibility goal

This project provides a narrow OpenAI-compatible API surface for local CPU object detection.

It intentionally supports only:

- `GET /v1/models`
- `POST /v1/chat/completions`
- bearer-token authentication
- OpenAI-shaped success and error envelopes

It does not claim full OpenAI API compatibility.

## Authentication

All `/v1/*` endpoints require:

```http
Authorization: Bearer <YOLO_GATEWAY_API_KEY>
```

Authentication failures must occur before image decoding or inference.

## `GET /v1/models`

Returns an OpenAI-shaped model list containing exactly one model:

```json
{
  "object": "list",
  "data": [
    {
      "id": "yolo-cpu-detector",
      "object": "model",
      "created": 0,
      "owned_by": "local"
    }
  ]
}
```

`created` may be `0` unless the implementation has a meaningful stable timestamp.

## `POST /v1/chat/completions`

### Request

Minimal supported request:

```json
{
  "model": "yolo-cpu-detector",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Detect objects in this image."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,..."
          }
        }
      ]
    }
  ]
}
```

### Required behavior

The request must contain exactly one image content part.

The image content part must be:

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/jpeg;base64,..."
  }
}
```

Allowed MIME types:

- `image/jpeg`
- `image/png`

Text content may be accepted but must not alter the detector behavior in MVP. The system is an object detector, not a general vision-language model.

### Unsupported request fields

If standard OpenAI fields appear, the implementation may ignore them unless they create ambiguity or unsupported behavior.

Examples that should be ignored or rejected consistently:

| Field | MVP behavior |
|---|---|
| `temperature` | ignore |
| `top_p` | ignore |
| `max_tokens` / `max_completion_tokens` | ignore or cap output if implemented |
| `stream` | reject unless streaming is implemented later |
| `tools` | reject or ignore; do not execute tools |
| `response_format` | may accept JSON-related hints later; not required in MVP |
| `n` | reject values other than 1 |
| `user` | ignore; do not store |

Document the final choice in implementation.

### Successful response

Return an OpenAI-shaped chat completion object. The assistant `content` is JSON text.

Example:

```json
{
  "id": "chatcmpl-local-000000000000",
  "object": "chat.completion",
  "created": 0,
  "model": "yolo-cpu-detector",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "{\"model\":\"yolo-cpu-detector\",\"objects\":[],\"image\":{\"width\":640,\"height\":480}}"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

`usage` may be zeros because this service is not token-based. Keep the shape stable.

### Assistant content schema

The assistant content string must parse as JSON:

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
    "width": 640,
    "height": 480
  }
}
```

Rules:

- `objects` is always an array.
- Empty detections use `"objects": []`.
- `bbox_xyxy` is `[x1, y1, x2, y2]`.
- Coordinates are pixel coordinates.
- Confidence is numeric, not a percentage string.
- No masks, track IDs, frame IDs, or job IDs.

## Errors

Use this shape:

```json
{
  "error": {
    "message": "Exactly one Base64 image data URL is required.",
    "type": "invalid_request_error",
    "param": "messages",
    "code": "invalid_image_input"
  }
}
```

## Required rejection cases

| Case | Status | Code |
|---|---:|---|
| Missing auth | 401 | `missing_api_key` |
| Wrong auth | 401 | `invalid_api_key` |
| Unknown model | 400/404 | `model_not_found` |
| Missing image | 400 | `missing_image` |
| Multiple images | 400 | `multiple_images_not_supported` |
| HTTP/HTTPS image URL | 400 | `external_image_url_not_supported` |
| File ID | 400 | `file_id_not_supported` |
| Raw Base64 | 400 | `invalid_image_url` |
| Unsupported MIME | 400 | `unsupported_image_type` |
| Malformed Base64 | 400 | `invalid_base64` |
| Image too large | 413/400 | `image_too_large` |
| Pixel count too large | 413/400 | `image_too_large` |
| Inference failure | 500 | `inference_error` |

Choose either 400 or 413 for size-related failures and document the choice.

## cURL example

```bash
BASE64_IMAGE="$(base64 -w0 example.jpg)"

curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer local-dev-key" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"yolo-cpu-detector\",
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": [
          {\"type\": \"text\", \"text\": \"Detect objects.\"},
          {
            \"type\": \"image_url\",
            \"image_url\": {
              \"url\": \"data:image/jpeg;base64,$BASE64_IMAGE\"
            }
          }
        ]
      }
    ]
  }"
```

## Python SDK example

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
                {"type": "text", "text": "Detect objects."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/jpeg;base64,..."
                    },
                },
            ],
        }
    ],
)

detections_json = response.choices[0].message.content
```
