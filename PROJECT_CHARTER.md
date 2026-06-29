# Project Charter — yolo-openai-detector

## One-sentence description

`yolo-openai-detector` is a CPU-only local object-detection gateway that exposes a narrow OpenAI-compatible API for single-image YOLO detection.

## Core promise

> One request, one Base64 image, one CPU detection pass, one JSON object-detection result.

## Intended user

A user who already knows OpenAI-style client usage and wants to send an image to a local service using:

- `OPENAI_API_KEY` or explicit `api_key`;
- `OPENAI_BASE_URL` or explicit `base_url`;
- `client.chat.completions.create(...)`.

## Why OpenAI-compatible?

The project should let users reuse familiar client code and tooling while running local CPU object detection instead of calling an upstream LLM provider.

Compatibility is intentionally narrow:

- model discovery through `/v1/models`;
- request submission through `/v1/chat/completions`;
- bearer-token auth;
- OpenAI-shaped response and error objects.

The service does not claim full OpenAI API compatibility.

## Scope

### In scope

- FastAPI backend;
- fixed bearer API key;
- OpenAI-style request/response shapes;
- one Base64 data URL image per request;
- JPEG/PNG image decoding;
- CPU YOLO detection;
- JSON object output;
- tests proving rejection paths;
- local run documentation.

### Out of scope

- tracking;
- video;
- segmentation;
- masks;
- pose;
- multiple images;
- HTTP URL fetching;
- file uploads;
- OpenAI upstream calls;
- background jobs;
- queueing;
- persistence;
- billing/accounting;
- user management;
- production cluster deployment.

## Initial release target

A local CPU service that can:

1. start without GPU;
2. authenticate requests;
3. expose `/v1/models`;
4. accept exactly one Base64 image data URL in `/v1/chat/completions`;
5. run YOLO detection on CPU;
6. return bounding boxes, labels, confidence scores, and image dimensions;
7. reject all unsupported request forms before inference.

## Human decision points

The human owner must decide before first non-demo release:

- repository license;
- whether Ultralytics AGPL licensing is acceptable;
- whether an enterprise/commercial YOLO license is required;
- maximum accepted image byte size;
- maximum accepted pixel count;
- default YOLO model/weights;
- whether this is local-only, LAN-facing, or public-facing.

## Definition of done for MVP

- OpenAI Python client smoke example works with local `base_url`.
- All documented rejection cases have tests.
- Inference works on CPU-only machine.
- No CUDA dependency is required.
- README and API contract match actual behavior.
- No docs claim tracking/video/segmentation/background jobs.
- No real secrets are committed or logged.
