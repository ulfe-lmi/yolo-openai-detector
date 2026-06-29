# ADR 0002 — Use Chat Completions as Compatibility Wrapper

## Status

Accepted at repository initialization.

## Context

Users should be able to access the detector with OpenAI-style client configuration using `api_key` and `base_url`.

The real task is not language generation. It is local object detection.

## Decision

Expose:

- `GET /v1/models`
- `POST /v1/chat/completions`

The main endpoint accepts one image as an OpenAI-style `image_url` content part with a Base64 data URL.

The assistant message content is JSON text containing detections.

## Rationale

This preserves compatibility with familiar OpenAI client patterns while avoiding custom client code.

`/v1/models` is retained as compatibility sugar because some clients and wrappers expect model discovery.

## Consequences

The project must not claim full OpenAI compatibility.

Unsupported OpenAI features must be ignored or rejected consistently and documented.
