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

The project currently uses Ultralytics as the default YOLO backend.

Current selection:

- selected package: `ultralytics`;
- selected model/weights: `yolo11n.pt`;
- license: AGPL-3.0 by default for Ultralytics YOLO software/models;
- CPU-only inference: required through `YOLO_DEVICE=cpu`;
- ordinary tests: use the stub backend or monkeypatched Ultralytics objects and must not download weights.

## Ultralytics note

Ultralytics documentation and licensing pages state that Ultralytics YOLO software/models are AGPL-3.0 by default, with enterprise licensing available for uses that cannot comply with AGPL obligations.

This may be acceptable for an open-source academic repository, but it is a human decision. The agent must not silently choose a dependency that imposes license obligations the project owner did not approve.

Ultralytics YOLO code and trained models are AGPL-3.0 by default. Private, proprietary,
commercial, SaaS/API, or embedded deployments may require an Ultralytics Enterprise License.
This repository does not grant such a license.

Ultralytics may download configured model weights on first use unless they are already available
in the runtime environment. Do not commit downloaded weights.

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
