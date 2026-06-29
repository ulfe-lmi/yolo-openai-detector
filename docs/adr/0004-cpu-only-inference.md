# ADR 0004 — CPU-Only Inference

## Status

Accepted at repository initialization.

## Context

The service must run on GPU-less machines.

## Decision

The default and required inference path is CPU-only.

## Rationale

The product is intended for machines without GPUs. Depending on CUDA would violate the main deployment requirement.

## Consequences

- Use a small detector model by default.
- Enforce image size limits.
- Do not support video or background jobs.
- Tests must pass without GPU.
- GPU acceleration may not be introduced as a required path.
