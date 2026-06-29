# Roadmap

The roadmap is PR-sized. Do not collapse multiple stages into one broad implementation.

## PR 1 — API skeleton and constitution enforcement

Work order:

```text
docs/work-orders/0001-api-skeleton.md
```

Scope:

- FastAPI skeleton;
- fixed bearer auth;
- `/v1/models`;
- stub `/v1/chat/completions`;
- strict request-shape validation;
- no YOLO inference yet.

Evidence:

- auth tests;
- model-list tests;
- chat-completion stub tests;
- rejection tests for unsupported image paths.

## PR 2 — Strict image parser and decoder

Work order:

```text
docs/work-orders/0002-image-parser.md
```

Scope:

- Base64 data URL parser;
- JPEG/PNG MIME validation;
- decoded byte limit;
- pixel-count limit;
- Pillow decode;
- image metadata result.

Evidence:

- valid JPEG/PNG fixtures;
- malformed Base64 tests;
- unsupported MIME tests;
- oversize tests;
- multiple-image rejection.

## PR 3 — CPU YOLO detection

Work order:

```text
docs/work-orders/0003-cpu-yolo-detection.md
```

Scope:

- select and approve backend;
- add CPU detector;
- return real object detections;
- no tracking/video/segmentation.

Evidence:

- model loads on CPU;
- fixture inference test;
- output JSON contract test;
- no CUDA requirement.

## PR 4 — OpenAI SDK smoke and documentation hardening

Work order:

```text
docs/work-orders/0004-openai-sdk-smoke-and-docs.md
```

Scope:

- OpenAI Python client smoke;
- README examples verified;
- compatibility matrix updated;
- unsupported field behavior documented.

Evidence:

- local service smoke script;
- parseable `choices[0].message.content`;
- documented limitations.

## PR 5 — Packaging and deployment

Work order:

```text
docs/work-orders/0005-packaging-deployment.md
```

Scope:

- run script or console entry point;
- optional Dockerfile for CPU-only local deployment;
- model-cache docs;
- operator notes.

Evidence:

- install/run smoke;
- CPU-only container/run command if Docker is added;
- no secrets baked into images.

## Not planned without explicit human approval

- tracking;
- video;
- segmentation;
- URL fetching;
- file uploads;
- background jobs;
- multiple images;
- persistence;
- public production deployment.
