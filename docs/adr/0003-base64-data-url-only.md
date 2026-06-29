# ADR 0003 — Base64 Data URL Only

## Status

Accepted at repository initialization.

## Context

OpenAI-style image input can be represented through image URLs, Base64 data URLs, or file IDs. This local detector should remain small and self-contained.

## Decision

Support only:

```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/jpeg;base64,..."
  }
}
```

Reject:

- `http://` and `https://` URLs;
- file IDs;
- raw Base64 without data URL prefix;
- multiple images.

## Rationale

This avoids:

- SSRF risk;
- network latency;
- file storage;
- implementing an OpenAI Files API subset;
- ambiguity about where images come from.

## Consequences

Users must encode images into Base64 data URLs before calling the service.
