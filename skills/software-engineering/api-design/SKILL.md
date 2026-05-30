---
name: api-design
description: Use when designing or reviewing REST, GraphQL, gRPC, event, webhook, batch, or internal service contracts including schemas, errors, versioning, compatibility, and examples.
---

# API Design

## Workflow

1. Identify consumers, producers, auth, rate limits, and compatibility constraints.
2. Define request, response, errors, pagination, idempotency, and versioning.
3. Provide examples and validation expectations.
4. Coordinate with system analyst, backend, QA, and security agents.
5. Update API contract artifact.

## Artifact

Use `templates/api-contract.md`.

## Guardrails

- Do not hide breaking changes.
- Do not omit error semantics or authorization behavior.
