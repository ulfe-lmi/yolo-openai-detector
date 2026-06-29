# Work Order 0004 — OpenAI SDK Smoke and Documentation Hardening

## Goal

Prove that the local service can be called through the OpenAI Python client using `base_url`.

## Scope

Add:

- a smoke script using `from openai import OpenAI`;
- local `base_url="http://localhost:8000/v1"` example;
- sample Base64 data URL request;
- parse of `choices[0].message.content` as JSON;
- documentation alignment.

## Non-goals

Do not add:

- new endpoints;
- streaming;
- tracking;
- video;
- segmentation;
- URL fetching;
- file uploads.

## Tests/smoke required

The smoke should verify:

- client can call `/v1/chat/completions`;
- response is OpenAI-shaped;
- assistant content parses as JSON;
- JSON contains `objects` and `image`.

If the smoke requires starting a server, document the exact command.

## Documentation required

Update:

- README;
- `docs/api-contract.md`;
- `docs/compatibility-matrix.md`;
- `docs/testing-strategy.md`.

## Final report

Include:

- branch;
- commit;
- PR URL;
- commands run;
- SDK version used;
- known limitations.
