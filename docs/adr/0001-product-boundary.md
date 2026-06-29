# ADR 0001 — Product Boundary

## Status

Accepted at repository initialization.

## Context

The project originally considered object tracking, video, and broader API behavior. The approved scope is narrower.

## Decision

The product is a CPU-only, single-image, single-shot object detection gateway using an OpenAI-compatible API shape.

The product does not implement:

- tracking;
- video;
- segmentation;
- masks;
- background jobs;
- external URL fetching;
- multiple images.

## Rationale

A narrow scope makes the MVP testable, CPU-suitable, and easy to use through OpenAI-style clients.

The project should first prove:

- authentication;
- request parsing;
- image safety;
- CPU inference;
- deterministic JSON output.

## Consequences

All unsupported features must be rejected at the API boundary.

Any future expansion requires a new ADR and human approval.
