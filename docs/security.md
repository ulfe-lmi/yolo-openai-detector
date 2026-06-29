# Security Model

## Scope

This is a local API service protected by a fixed bearer token. It is not a multi-user authorization system.

## Main security goals

- Reject unauthenticated requests.
- Avoid leaking the API key.
- Avoid logging large or sensitive payloads.
- Avoid fetching external URLs.
- Avoid storing images or prompts.
- Avoid accidental GPU/proprietary/cloud assumptions.
- Fail closed on unsupported request shapes.

## API key handling

The key is configured through:

```text
YOLO_GATEWAY_API_KEY
```

Implementation requirements:

- Compare using constant-time comparison.
- Do not log the full `Authorization` header.
- Do not log the configured key.
- Reject before parsing Base64 image data.
- Use fake placeholder keys in tests and docs.

## Logging rules

Allowed log fields:

- request ID;
- endpoint;
- status code;
- model ID;
- timing;
- error code;
- decoded image dimensions if useful;
- object count if useful.

Forbidden log fields:

- full Authorization header;
- API key;
- raw request body;
- Base64 image data;
- decoded image bytes;
- full assistant content if it may contain large payloads;
- stack traces in client-facing error responses.

## External network

The service must not fetch image URLs.

Reasons:

- avoids SSRF;
- avoids unpredictable latency;
- avoids dependency on external network;
- preserves local-only product boundary.

Reject `http://` and `https://` image URLs even though OpenAI supports them.

## Image payload risk

Base64 images can be large. Enforce:

- maximum decoded byte size;
- maximum pixel count;
- allowed MIME types;
- Pillow verification/loading protections;
- inference timeout if practical.

Reject animated or multi-frame formats unless explicitly supported later.

## No persistence

Do not store:

- raw images;
- prompts;
- request bodies;
- detection histories;
- API keys;
- user identifiers.

Temporary in-memory data is acceptable only for request processing.

## Error safety

Client-facing errors must not leak:

- paths;
- keys;
- environment variables;
- model-cache locations;
- stack traces;
- raw payloads.

Use OpenAI-shaped error objects with stable codes.

## Dependency risk

Model/backend dependencies may have license or supply-chain implications.

Before adding a YOLO backend:

- verify license implications;
- document model weight source;
- document download/cache behavior;
- avoid implicit downloads in unit tests;
- pin or constrain versions when stability matters.

## Deployment warning

A fixed-key service may be acceptable for local or trusted LAN use. It is not sufficient for a public internet service without additional controls such as TLS, rate limits, per-key auth, request size limits at the proxy, monitoring, and abuse handling.

Do not claim public production readiness without a separate security review.
