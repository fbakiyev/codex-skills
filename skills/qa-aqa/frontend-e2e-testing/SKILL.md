---
name: frontend-e2e-testing
description: Use when designing, implementing, or reviewing browser E2E tests, Playwright flows, visual checks, accessibility checks, and user workflow regression coverage.
---

# Frontend E2E Testing

## Workflow

1. Select critical user workflows.
2. Prefer stable selectors and deterministic setup.
3. Verify responsive behavior when UI changed.
4. Capture screenshots only when they add review value.
5. Keep tests focused on user-visible behavior.

## Guardrails

- Do not rely on arbitrary sleeps.
- Do not automate flows that are already better covered at lower layers.
