# CLAUDE.md — Project Constitution for `yolo-openai-detector`

This file intentionally mirrors `AGENTS.md`. If you are Claude Code or another coding agent that reads `CLAUDE.md`, treat this file as the same operational law. If `AGENTS.md` and `CLAUDE.md` ever diverge, stop and report the inconsistency.

## Mission

Build a small, local, CPU-first API service that exposes **OpenAI-compatible** endpoints for **single-image YOLO object detection**.

The core promise is:

> One request, one Base64 image, one CPU detection pass, one JSON object-detection result.

## Required OpenAI-compatible API

The required compatibility endpoints are:

- `GET /v1/models`
- `POST /v1/chat/completions`

The user-facing API surface is under `/v1`.

Do not add unrelated public endpoints unless a later human-approved work order explicitly asks for them.

## Product boundary

This repository is for:

- CPU-only inference;
- single-shot image object detection;
- one image per request;
- Base64 data URL image input;
- fixed bearer-key authentication;
- JSON object output inside an OpenAI-shaped chat completion.

## Non-goals

Do not implement:

- tracking;
- video;
- segmentation;
- masks;
- pose;
- webcam input;
- background jobs;
- async queues;
- Redis/Celery/RQ;
- database persistence;
- file upload endpoints;
- HTTP/HTTPS image fetching;
- OpenAI Files API emulation;
- multiple images;
- upstream OpenAI/provider forwarding;
- CUDA/GPU-only behavior.

Reject requests that would require these features.

## Model identity

Expose exactly:

```text
yolo-cpu-detector
```

Unknown model names must be rejected.

## Image input contract

Accept exactly one OpenAI-style image content part:

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/jpeg;base64,..."
  }
}
```

Initially support:

- `image/jpeg`
- `image/png`

Reject URLs, file IDs, raw Base64, multiple images, video-like inputs, unsupported MIME types, malformed Base64, oversized payloads, and excessive pixel counts.

## Response contract

Return an OpenAI-shaped chat-completion object. The assistant message content is deterministic JSON text:

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

Do not return track IDs, masks, frame numbers, or job IDs.

## Authentication

Use one fixed key from:

```text
YOLO_GATEWAY_API_KEY
```

Require:

```text
Authorization: Bearer <key>
```

Use constant-time comparison.

Never log keys or full authorization headers.

Reject missing or wrong auth before image parsing.

## CPU-only invariant

The service must work on a GPU-less machine.

Do not require CUDA. Do not assume GPU availability. Do not add GPU-only wheels or GPU-only tests. Explicitly select CPU in inference code.

## Dependency policy

Use boring dependencies. Before adding a YOLO backend such as Ultralytics, verify license implications for the intended repository and deployment model. If license compatibility is unclear, stop and report instead of adding the dependency silently.

Do not download model weights in ordinary unit tests.

## Tests

Add or update tests for every behavior change. Required themes:

- fixed bearer auth;
- `/v1/models`;
- `/v1/chat/completions`;
- image data URL parsing;
- rejection paths;
- CPU-only inference;
- OpenAI SDK smoke behavior;
- response JSON contract.

Skipped tests are not passing tests. Not-run tests are not evidence.

## Documentation

Keep documentation honest. Do not claim full OpenAI compatibility, production readiness, tracking, video, segmentation, background jobs, GPU support, persistence, billing, monitoring, or upstream OpenAI calls unless implemented and tested.

## Workflow

For normal post-initialization work:

1. Start from current `main`.
2. Create a feature branch.
3. Make a narrow change.
4. Commit only related files.
5. Run focused tests and relevant full checks.
6. Push and open a pull request.
7. Do not merge your own PR.

## Required final report

Every task report must include:

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

Never fake a PR URL, commit SHA, CI result, or test result.
