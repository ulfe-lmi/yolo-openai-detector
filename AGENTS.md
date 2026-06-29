# AGENTS.md — Project Constitution for `yolo-openai-detector`

This repository implements a **CPU-only, single-image YOLO object-detection gateway** with a narrow **OpenAI-compatible HTTP interface**.

This file is operational law for coding agents. Read it before editing. If another instruction conflicts with this file, report the conflict and ask the strategic/human lead before continuing, unless the conflict is clearly resolved by a more specific nested instruction in the repository.

## 1. Mission

Build a small, local, CPU-first API service that lets users call object detection through OpenAI-style client code:

- users configure `base_url` to point to this service;
- users provide a fixed API key as a bearer token;
- users call `chat.completions.create(...)`;
- users attach exactly one image as a Base64 data URL in an OpenAI-style `image_url` content part;
- the service returns detected objects as deterministic JSON text inside an OpenAI-shaped chat-completion response.

The core promise is:

> One request, one Base64 image, one CPU detection pass, one JSON object-detection result.

## 2. Product boundary

This project is only for:

- CPU-only inference;
- single-shot image object detection;
- one image per request;
- Base64 data URL image input;
- fixed bearer-key authentication;
- OpenAI-compatible `/v1/models` and `/v1/chat/completions` behavior sufficient for ordinary client usage.

This project is not a general LLM gateway, not an OpenAI proxy, not a video service, and not a background-processing system.

## 3. OpenAI-compatible API surface

The required OpenAI-compatible endpoints are:

| Endpoint | Required | Purpose |
|---|---:|---|
| `GET /v1/models` | yes | Compatibility sugar: expose `yolo-cpu-detector` as the available model |
| `POST /v1/chat/completions` | yes | Main detection endpoint |

The public compatibility API must live under `/v1`.

Do **not** add non-`/v1` user-facing endpoints unless a work order explicitly asks for them. An internal operator liveness endpoint may be proposed later, but it is not part of the current API contract and must not be presented as OpenAI compatibility.

## 4. Explicit non-goals

Do not implement any of the following unless a later human-approved work order changes the constitution:

- tracking;
- video;
- streaming video;
- webcam input;
- segmentation;
- masks;
- pose estimation;
- oriented bounding boxes;
- classification-only mode;
- background jobs;
- async job queues;
- Redis/Celery/RQ;
- database persistence;
- file upload endpoints;
- OpenAI Files API emulation;
- HTTP/HTTPS image fetching;
- multiple images per request;
- upstream OpenAI/provider forwarding;
- prompt storage;
- raw image storage;
- user accounts;
- multi-key management;
- quota/billing/accounting;
- CUDA-only or GPU-required behavior.

If a user request appears to ask for tracking, video, segmentation, masks, multiple images, URL fetching, files, or background jobs, reject it at the API boundary with an OpenAI-shaped error.

## 5. Model identity

Expose exactly one model at first:

```text
yolo-cpu-detector
```

Unknown models must be rejected.

Model implementation details, weights, and backend libraries may evolve, but the API model identifier above is the first public compatibility contract.

## 6. Image input contract

Accept exactly one image content part in an OpenAI-style chat message content array:

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/jpeg;base64,..."
  }
}
```

Supported MIME types for first release:

- `image/jpeg`
- `image/png`

`image/webp` may be added only if tests prove Pillow support in the target CPU environment.

Reject:

- no image;
- more than one image;
- `http://` or `https://` URLs;
- file IDs;
- raw Base64 without the `data:image/...;base64,` prefix;
- unsupported MIME types;
- malformed Base64;
- decoded payload above configured byte limit;
- decoded image above configured pixel limit;
- animated/multi-frame image formats unless explicitly supported and tested later;
- image content outside the OpenAI-style `image_url.url` field.

## 7. Response contract

Return an OpenAI-shaped chat-completion object. The assistant message `content` must be a JSON string.

The JSON string must be deterministic and must contain:

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

- `bbox_xyxy` coordinates are pixel coordinates in the decoded input image coordinate system.
- `confidence` is a number between 0 and 1.
- `objects` may be empty.
- Do not return track IDs.
- Do not return masks.
- Do not return frame numbers.
- Do not return job IDs.
- Do not return natural-language-only results unless explicitly requested in a future approved feature.

## 8. Authentication and secrets

Authentication uses one fixed bearer token read from:

```text
YOLO_GATEWAY_API_KEY
```

Rules:

- Require `Authorization: Bearer <key>`.
- Use constant-time comparison.
- Reject missing or incorrect auth before image decoding or model inference.
- Never log the API key.
- Never log the full `Authorization` header.
- Never commit real `.env` files.
- Keep `.env.example` fake and safe.
- Use only placeholder keys in docs/tests.
- If a secret appears in output, stop and report it.

## 9. CPU-only invariant

The project must work on a GPU-less machine.

Rules:

- Do not require CUDA.
- Do not assume `torch.cuda.is_available()`.
- Do not make CUDA a startup requirement.
- Do not require GPU-specific wheels in default installation.
- Explicitly select CPU in inference code.
- Tests must be able to run without GPU.
- Documentation must state CPU-only scope honestly.

If adding a model backend would require GPU to pass tests or run the service, reject that approach.

## 10. Dependency and license policy

Dependencies must be boring and justified.

Default stack direction:

- FastAPI;
- Pydantic v2;
- Uvicorn;
- Pillow for image decoding;
- pytest/httpx for tests;
- Ruff for linting.

YOLO backend policy:

- A later work order may add Ultralytics or another YOLO-compatible backend.
- Before adding Ultralytics as a runtime dependency, verify license implications for the intended repository and deployment model.
- If the repository/deployment cannot comply with the selected YOLO backend license, stop and report alternatives instead of silently adding the dependency.
- Do not download model weights in tests unless a test is explicitly marked as an integration/model-smoke test and the download/cache behavior is documented.
- Prefer small CPU-suitable detection weights for default examples.

## 11. Error behavior

Use OpenAI-shaped errors:

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

Fail closed before expensive work:

| Case | Expected behavior |
|---|---|
| Missing API key | 401 |
| Wrong API key | 401 |
| Unknown model | 400 or 404, consistently documented |
| Missing image | 400 |
| Multiple images | 400 |
| HTTP/HTTPS image URL | 400 |
| Raw Base64 without data URL prefix | 400 |
| Malformed Base64 | 400 |
| Unsupported MIME type | 400 |
| Oversized decoded payload | 413 or documented 400 |
| Excessive pixel count | 413 or documented 400 |
| Internal inference failure | 500 without secret leakage |

## 12. Repository structure

Use this general structure unless a work order approves a change:

```text
AGENTS.md
CLAUDE.md
README.md
PROJECT_CHARTER.md
pyproject.toml
.env.example
docs/
  architecture.md
  api-contract.md
  compatibility-matrix.md
  dependency-policy.md
  roadmap.md
  security.md
  testing-strategy.md
  release-checklist.md
  adr/
  handoffs/
  reviews/
  work-orders/
src/
  yolo_openai_detector/
tests/
```

## 13. Testing rules

Tests are required for behavior changes.

Required categories over the first implementation PRs:

- auth tests;
- `/v1/models` compatibility tests;
- `/v1/chat/completions` request-shape tests;
- image data URL parser tests;
- rejection tests for forbidden inputs;
- CPU-only inference tests;
- OpenAI Python SDK smoke tests;
- output JSON contract tests.

A skipped test is not a passing test. A test not run is not evidence.

When reporting tests, distinguish:

- passed;
- failed;
- skipped;
- not run;
- blocked.

Do not write shallow tests that merely assert implementation details. Every important rejection path should have a test.

## 14. Documentation rules

Documentation must remain honest.

Whenever behavior changes, update the relevant docs:

- `README.md`;
- `docs/api-contract.md`;
- `docs/compatibility-matrix.md`;
- `docs/security.md`;
- `docs/testing-strategy.md`;
- work orders if the plan changes.

Do not claim:

- production readiness;
- full OpenAI API compatibility;
- video support;
- tracking support;
- segmentation support;
- GPU acceleration;
- multi-user security;
- persistence;
- monitoring;
- billing/accounting;
- upstream OpenAI integration.

Unless those features are explicitly implemented and tested.

## 15. Workflow rules for coding agents

For normal implementation after repository initialization:

1. Start from current `main`.
2. Read `AGENTS.md` and `CLAUDE.md`.
3. Verify current repository state.
4. Create a feature branch.
5. Make a narrow, scoped change.
6. Commit only related files.
7. Run required tests.
8. Push and open a pull request.
9. Do not merge your own PR.

Repository initialization may be done manually by the human from the initial ZIP package. After that, implementation work should normally be PR-sized.

## 16. Final report format

Every coding-agent task must end with:

```markdown
## Agent Report

Branch:
Commit:
Pull request:

## Summary
- ...

## Files changed
- ...

## Tests run
- `command`: result

## Documentation changed
- ...

## Safety confirmations
- No real secrets committed.
- No API keys logged.
- No CUDA/GPU requirement introduced.
- No tracking/video/segmentation/background job behavior introduced.
- No unsupported OpenAI endpoint claimed.
- No YOLO weights downloaded unless explicitly required and reported.

## Known limitations
- ...

## Follow-up recommended
- ...
```

Never fake a PR URL, CI result, test result, or commit SHA.

## 17. Stop conditions

Stop and report before proceeding if:

- a request conflicts with the product boundary;
- a dependency license appears incompatible;
- implementation would require GPU;
- implementing the task would require tracking/video/segmentation/background jobs;
- the repository state differs materially from the work order;
- a secret is discovered;
- tests cannot be run for environmental reasons;
- a required behavior cannot be proven with tests.
