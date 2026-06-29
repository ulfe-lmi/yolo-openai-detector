# OpenAI Compatibility Matrix

This project is OpenAI-compatible only in a narrow, deliberate sense.

## Compatibility summary

| Feature | Status | Notes |
|---|---:|---|
| Bearer API key | Supported | Fixed local key from `YOLO_GATEWAY_API_KEY` |
| `GET /v1/models` | Supported | Returns local `yolo-cpu-detector` |
| `POST /v1/chat/completions` | Supported | Main detection endpoint |
| OpenAI Python client with `base_url` | Required | Must be smoke-tested |
| Image content part `type: image_url` | Supported | Data URL only |
| Base64 data URL image input | Supported | Required input path |
| HTTP/HTTPS image URLs | Not supported | Must be rejected |
| File IDs / Files API | Not supported | Must be rejected |
| Multiple images | Not supported | Must be rejected |
| Streaming | Not supported | Reject `stream=true` unless later implemented |
| Tools/function calling | Not supported | Must not execute tools |
| Chat history semantics | Not supported | Request is treated as one image detection task |
| Token accounting | Not applicable | Usage may be zeroed |
| Embeddings | Not supported | No endpoint |
| Responses API | Not supported | No endpoint |
| Audio | Not supported | No endpoint |
| Image generation | Not supported | No endpoint |
| Moderation | Not supported | No endpoint |

## Compatibility intent

The goal is user convenience, not protocol completeness.

A user should be able to write:

```python
client = OpenAI(
    api_key="local-dev-key",
    base_url="http://localhost:8000/v1",
)
```

and call:

```python
client.chat.completions.create(...)
```

with one Base64 image data URL.

## Non-compatibility statement

This project does not emulate OpenAI models, reasoning, natural-language vision analysis, token billing, file uploads, streaming, tools, assistants, responses, or storage.

It performs local object detection and returns structured JSON.

## `/v1/models`

Keep `/v1/models` even though there is only one model because it improves compatibility with OpenAI-style clients and wrappers that discover available model IDs.

The response should be stable and simple.

## `/v1/chat/completions`

This endpoint is a compatibility wrapper around object detection.

The request may include text, but the detector does not interpret open-ended language in the MVP. The text prompt should not change detection behavior except perhaps future output-format options that are explicitly implemented and tested.

## Unsupported-field policy

The implementation should make an explicit choice per field:

- ignore harmless generation controls;
- reject fields implying unsupported behavior;
- document the choice.

Fields implying unsupported behavior include:

- `stream: true`;
- `tools`;
- `tool_choice`;
- `n` greater than 1;
- multiple images;
- image URLs;
- file IDs.

## OpenAI SDK smoke test requirement

Before claiming SDK compatibility, add a test or script that uses the real `openai` Python package against the local service with:

```python
OpenAI(api_key="local-dev-key", base_url="http://localhost:8000/v1")
```

The smoke must verify:

- `/v1/models` can be listed or called directly if supported by the SDK path;
- `chat.completions.create(...)` returns a parseable response;
- `choices[0].message.content` parses as JSON.
