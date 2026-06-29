# Work Order 0005 — Packaging and CPU Deployment

## Goal

Make the service easy to run on a GPU-less machine.

## Scope

Add one or more of:

- console entry point;
- documented `uvicorn` command;
- Dockerfile for CPU-only local deployment;
- model-cache documentation;
- operator run notes.

## Non-goals

Do not add:

- Kubernetes;
- public production deployment claims;
- TLS termination;
- multi-user auth;
- rate limiting;
- monitoring stack;
- background jobs;
- video/tracking/segmentation.

## Requirements

- No secrets baked into images.
- `.env.example` remains fake.
- CPU-only behavior is documented.
- Model weight/cache behavior is documented.
- Request limits are documented.

## Tests/smoke

Add or document:

- local run command;
- curl smoke;
- OpenAI Python client smoke;
- CPU-only environment note.

## Final report

Include:

- branch;
- commit;
- PR URL;
- packaging files changed;
- smoke commands run;
- limitations.
