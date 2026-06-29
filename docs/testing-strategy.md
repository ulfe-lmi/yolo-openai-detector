# Testing Strategy

## Testing principle

Tests are evidence. A skipped test is not a passing test. A test that was not run is not evidence.

## Test levels

| Level | Purpose |
|---|---|
| Unit tests | Pure parsing, auth, formatting, error-shape behavior |
| API tests | FastAPI endpoint behavior through test client |
| Integration tests | Real image decoding and later real CPU inference |
| SDK smoke tests | OpenAI Python client against local running service |
| Packaging smoke | Start installed service from clean environment |

## Initial test matrix

### Authentication

- missing `Authorization` rejected;
- malformed `Authorization` rejected;
- wrong bearer token rejected;
- correct token accepted;
- auth rejection occurs before image parsing.

### `/v1/models`

- returns object `"list"`;
- returns one model with ID `yolo-cpu-detector`;
- requires auth if policy says all `/v1/*` endpoints require auth.

### `/v1/chat/completions`

- accepts minimal valid OpenAI-shaped request;
- rejects unknown model;
- rejects missing messages;
- rejects malformed message content;
- rejects missing image;
- rejects multiple images;
- rejects HTTP image URL;
- rejects file ID;
- rejects raw Base64;
- rejects unsupported MIME;
- rejects malformed Base64;
- rejects oversize decoded payload;
- rejects excessive pixel count.

### Image decoding

- JPEG data URL decodes;
- PNG data URL decodes;
- MIME mismatch policy is tested if implemented;
- dimensions are reported correctly;
- large payload is rejected before inference.

### CPU inference

When inference is added:

- model loads on CPU;
- prediction runs with `device="cpu"` or equivalent;
- fixture image returns a parseable object list;
- empty/no-object image behavior is tested;
- no CUDA requirement exists.

### Response contract

- response is OpenAI-shaped;
- `choices[0].message.role == "assistant"`;
- `choices[0].message.content` is valid JSON;
- JSON has `model`, `objects`, and `image`;
- every object has `label`, `confidence`, and `bbox_xyxy`.

### Forbidden feature regression tests

Add tests proving rejection of:

- `stream=true`;
- multiple images;
- video MIME types;
- tracking requests if represented by model or prompt flags;
- segmentation/mask requests if represented by model or prompt flags;
- external image URLs.

## Commands

Suggested after implementation begins:

```bash
python -m pytest
python -m pytest tests -q
ruff check .
```

When SDK smoke is added:

```bash
python scripts/smoke_openai_client.py
```

## Fixtures

Use tiny safe fixture images.

Do not commit:

- large images;
- private images;
- copyrighted datasets without permission;
- model weights;
- cache directories.

## Reporting standard

Coding agents must report exact commands:

```markdown
Tests run:
- `python -m pytest tests/test_auth.py`: 8 passed
- `ruff check .`: passed
- `python scripts/smoke_openai_client.py`: not run; script not implemented yet
```

Avoid:

```text
All tests passed.
```

unless the entire relevant suite actually ran.
