# Release Checklist

Use this before claiming an MVP or release candidate.

## Scope

- [ ] Product remains single-image only.
- [ ] Product remains CPU-only.
- [ ] No tracking exists.
- [ ] No video exists.
- [ ] No segmentation/masks exist.
- [ ] No background jobs exist.
- [ ] No unsupported OpenAI compatibility is claimed.

## API

- [ ] `GET /v1/models` works.
- [ ] `POST /v1/chat/completions` works.
- [ ] OpenAI Python client smoke works with `base_url`.
- [ ] Response is OpenAI-shaped.
- [ ] Assistant content is parseable JSON.
- [ ] Error responses are OpenAI-shaped.

## Auth and security

- [ ] `YOLO_GATEWAY_API_KEY` is required.
- [ ] Missing key rejected.
- [ ] Wrong key rejected.
- [ ] Constant-time comparison used.
- [ ] Authorization header is not logged.
- [ ] No real `.env` committed.
- [ ] No raw image payloads logged.
- [ ] External image URLs rejected.

## Image handling

- [ ] Exactly one image required.
- [ ] Base64 data URL required.
- [ ] JPEG supported.
- [ ] PNG supported.
- [ ] Unsupported MIME rejected.
- [ ] Malformed Base64 rejected.
- [ ] Byte limit enforced.
- [ ] Pixel limit enforced.

## Inference

- [ ] Detector runs on CPU.
- [ ] No CUDA required.
- [ ] Model/weights source documented.
- [ ] Dependency license reviewed.
- [ ] Fixture image inference test passes.
- [ ] Empty detection behavior documented.

## Tests

- [ ] Unit tests pass.
- [ ] API tests pass.
- [ ] Rejection-path tests pass.
- [ ] CPU inference test passes.
- [ ] SDK smoke passes.
- [ ] Skipped tests are documented as skipped, not passed.

## Docs

- [ ] README matches actual behavior.
- [ ] API contract matches implementation.
- [ ] Compatibility matrix updated.
- [ ] Security doc updated.
- [ ] Testing strategy updated.
- [ ] Known limitations stated.

## Human approval

- [ ] Repository license chosen.
- [ ] YOLO backend license accepted.
- [ ] Release language approved.
