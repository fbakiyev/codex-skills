---
name: api-testing
description: Use when testing API behavior, schemas, contracts, auth, errors, pagination, idempotency, compatibility, and service integrations.
---

# API Testing

## Workflow

1. Read API contract and system analysis.
2. Cover happy paths, errors, auth, validation, idempotency, and compatibility.
3. Add contract tests where multiple services depend on the API.
4. Validate examples and schema changes.

## Guardrails

- Do not test only status codes.
- Do not ignore backward compatibility for public or shared APIs.
