---
name: backend-engineering
description: Use when designing, implementing, reviewing, or refactoring backend services, APIs, jobs, integrations, domain logic, reliability behavior, and server-side validation.
---

# Backend Engineering

## Workflow

1. Read local architecture, tests, API contracts, and data contracts.
2. Identify behavior, edge cases, error handling, idempotency, and observability needs.
3. Prefer existing project patterns over new abstractions.
4. Implement narrowly and update tests.
5. Verify with unit, integration, contract, or smoke checks as appropriate.
6. Leave handoff with validation and risks.

## Artifacts

- API contract when interfaces change.
- ADR when architecture changes.
- Handoff for multi-step work.

## Guardrails

- Do not change public contracts without documenting compatibility.
- Do not skip failure paths for async, payment-like, data-changing, or external integration flows.
