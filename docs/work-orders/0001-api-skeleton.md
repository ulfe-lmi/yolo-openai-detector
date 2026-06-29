# Work Order 0001 — API Skeleton and Constitution Enforcement

You are working in the repository for `yolo-openai-detector`.

## Governing instructions

Read `AGENTS.md` and `CLAUDE.md` first.

If live repository state differs from this work order, report the difference before making changes.

## Goal

Create the initial FastAPI service skeleton for a CPU-only, single-image object-detection gateway with a narrow OpenAI-compatible API.

This PR establishes:

- fixed bearer-key authentication;
- `GET /v1/models`;
- stub `POST /v1/chat/completions`;
- OpenAI-shaped errors;
- strict product-boundary rejection behavior;
- tests for the API skeleton.

Actual YOLO inference is out of scope.

## Required endpoints

### `GET /v1/models`

Return an OpenAI-shaped model list exposing exactly:

```text
yolo-cpu-detector
```

### `POST /v1/chat/completions`

Accept an OpenAI-shaped request with exactly one Base64 image data URL.

For this PR, return a stub assistant message indicating that detection inference is not implemented yet.

Even though inference is stubbed, the endpoint must enforce:

- authentication;
- known model name;
- exactly one image content part;
- data URL shape;
- rejection of unsupported image input forms.

## Non-goals

Do not implement:

- YOLO inference;
- tracking;
- video;
- segmentation;
- background jobs;
- file upload endpoints;
- HTTP/HTTPS image fetching;
- OpenAI upstream proxying;
- database persistence;
- CUDA/GPU behavior.

## Required implementation areas

Expected package layout:

```text
src/yolo_openai_detector/
  __init__.py
  main.py
  config.py
  auth.py
  openai_compat.py
  image_input.py
```

Tests under:

```text
tests/
```

## Authentication requirements

Use `YOLO_GATEWAY_API_KEY`.

Require:

```text
Authorization: Bearer <key>
```

Use constant-time comparison.

Reject missing or wrong keys before parsing image input.

Never log the key or full authorization header.

## Image request-shape requirements

Accept exactly one content part:

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/jpeg;base64,..."
  }
}
```

For this PR, it is enough to validate:

- `data:image/` prefix;
- `;base64,` marker;
- supported MIME prefix for JPEG/PNG;
- exactly one image part.

Full Base64 decoding and Pillow image validation belong to Work Order 0002.

Reject:

- no image;
- more than one image;
- HTTP/HTTPS URLs;
- file IDs;
- raw Base64 without data URL prefix.

## Tests required

Add tests for:

- missing auth rejected;
- wrong auth rejected;
- correct auth accepted;
- `GET /v1/models` returns `yolo-cpu-detector`;
- unknown model rejected;
- valid single-image OpenAI-shaped request accepted by stub endpoint;
- missing image rejected;
- multiple images rejected;
- HTTP image URL rejected;
- raw Base64 rejected;
- error response shape is OpenAI-shaped.

## Documentation required

Update README only if necessary. Do not remove the existing constitution or product boundary docs.

## Verification commands

Run at least:

```bash
python -m pytest
ruff check .
```

If `ruff` is not configured yet, configure it minimally in `pyproject.toml`.

## Workflow

Create a branch from current `main`.

Commit only related files.

Open a PR.

Do not merge.

## Final report

Return:

- branch;
- commit;
- PR URL;
- summary;
- files changed;
- tests run with exact results;
- confirmation that no YOLO weights were downloaded;
- confirmation that no CUDA/GPU dependency was introduced;
- known limitations.
