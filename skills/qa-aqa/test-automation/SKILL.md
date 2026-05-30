---
name: test-automation
description: Use when implementing or reviewing automated tests, fixtures, CI gates, test data, mocks, contracts, regression suites, and flaky test handling.
---

# Test Automation

## Workflow

1. Choose the lowest test layer that validates the behavior.
2. Keep tests deterministic and isolated.
3. Use realistic fixtures for integration and contract tests.
4. Add CI gating only when signal is reliable.
5. Track flakes separately from product bugs.

## Guardrails

- Do not overuse e2e tests for logic covered at lower layers.
- Do not hide flaky tests by disabling them without follow-up.
