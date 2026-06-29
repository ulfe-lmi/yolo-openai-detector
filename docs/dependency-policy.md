# Dependency and Model Backend Policy

## General rule

Dependencies must be boring, justified, and testable on CPU-only machines.

## Initial runtime dependencies

Recommended initial runtime dependencies:

- FastAPI;
- Uvicorn;
- Pydantic v2;
- Pydantic Settings;
- Pillow.

Recommended development dependencies:

- pytest;
- httpx;
- ruff;
- mypy, if useful.

## YOLO backend policy

The project may later use a YOLO backend such as Ultralytics, ONNX Runtime with exported YOLO weights, or another compatible CPU detector.

Do not add a YOLO backend until the API skeleton and image parser are stable.

Before adding a YOLO backend, the coding agent must report:

- selected package;
- selected model/weights;
- license;
- whether the license is compatible with the intended repository license and deployment;
- whether weights are downloaded automatically;
- where weights are cached;
- whether CPU-only inference is supported;
- how tests avoid large downloads.

## Ultralytics note

Ultralytics documentation and licensing pages state that Ultralytics YOLO software/models are AGPL-3.0 by default, with enterprise licensing available for uses that cannot comply with AGPL obligations.

This may be acceptable for an open-source academic repository, but it is a human decision. The agent must not silently choose a dependency that imposes license obligations the project owner did not approve.

## Weight files

Do not commit model weight files such as:

- `.pt`;
- `.onnx`;
- `.engine`;
- `.torchscript`;
- `.tflite`.

Keep weights in an ignored cache or documented external download path.

## Unit tests

Ordinary unit tests must not download model weights.

Model-backed tests should be marked or isolated so that CI and local developers can distinguish:

- fast unit tests;
- integration tests requiring weights;
- performance smoke tests.

## Version pinning

Avoid unbounded dependencies in release branches.

For the initial repository, broad lower bounds are acceptable. Before a release, pin or constrain versions enough to make installation reproducible.
