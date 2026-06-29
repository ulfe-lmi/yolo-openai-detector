# Work Order 0003 — CPU YOLO Detection

## Governing instructions

Read `AGENTS.md`, `CLAUDE.md`, and `docs/dependency-policy.md` first.

This work order assumes Work Orders 0001 and 0002 are merged.

## Goal

Add real CPU-only YOLO object detection for one decoded image.

## Mandatory preflight

Before adding the backend dependency, report:

- chosen backend;
- chosen model/weights;
- license;
- whether the license is acceptable for this repository/deployment;
- whether weights are downloaded automatically;
- where weights are cached;
- how unit tests avoid uncontrolled downloads.

If license compatibility is unclear, stop and report alternatives.

## Scope

Implement:

- CPU-only detector backend;
- model loading;
- prediction on one Pillow image or equivalent;
- normalized detections with label, confidence, and `bbox_xyxy`;
- OpenAI-shaped chat completion response with JSON assistant content.

## Non-goals

Do not implement:

- tracking;
- video;
- segmentation;
- masks;
- multiple images;
- URL fetching;
- background jobs;
- GPU-only behavior.

## CPU requirement

The implementation must explicitly select CPU.

Tests must be runnable on a GPU-less machine.

## Tests required

Add tests for:

- detector interface returns normalized detections;
- response content parses as JSON;
- each object has `label`, `confidence`, and `bbox_xyxy`;
- image width/height preserved;
- no CUDA requirement;
- fixture inference path works or is clearly marked as integration if weights are required.

Do not make ordinary unit tests download large weights.

## Documentation required

Update:

- README;
- `docs/api-contract.md`;
- `docs/dependency-policy.md`;
- `docs/testing-strategy.md`;
- `docs/compatibility-matrix.md`.

Document model source and cache behavior.

## Verification commands

Run:

```bash
python -m pytest
ruff check .
```

If an integration/model-smoke test is not run, report it as not run and explain why.

## Final report

Include:

- branch;
- commit;
- PR URL;
- backend selected;
- license note;
- model/weights note;
- tests run;
- CPU-only confirmation;
- known limitations.
