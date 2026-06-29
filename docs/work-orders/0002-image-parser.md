# Work Order 0002 — Strict Base64 Image Parser and Decoder

## Governing instructions

Read `AGENTS.md` and `CLAUDE.md` first.

This work order assumes Work Order 0001 is merged.

## Goal

Implement strict decoding and validation for exactly one Base64 image data URL.

No YOLO inference yet.

## Scope

Add:

- robust data URL parser;
- allowed MIME validation;
- Base64 decoding;
- decoded byte limit;
- Pillow image open/verify/load;
- pixel-count limit;
- normalized image metadata output for the stub response or internal structure.

## Non-goals

Do not implement:

- YOLO inference;
- tracking;
- video;
- segmentation;
- URL fetching;
- file uploads;
- multiple images;
- background jobs.

## Required config

Add configurable limits, with safe defaults:

- `YOLO_MAX_IMAGE_BYTES`
- `YOLO_MAX_IMAGE_PIXELS`

Document defaults in `.env.example` and README if changed.

## Required rejection tests

Add tests for:

- valid JPEG data URL;
- valid PNG data URL;
- malformed Base64;
- unsupported MIME;
- MIME missing;
- payload too large;
- pixel count too large;
- HTTP URL still rejected;
- multiple images still rejected.

## Response behavior

If inference is still stubbed, include decoded image width/height in the stub JSON content so the parser behavior is visible and testable.

## Verification commands

Run:

```bash
python -m pytest
ruff check .
```

## Final report

Include:

- branch;
- commit;
- PR URL;
- summary;
- tests run;
- image limits implemented;
- known limitations.
