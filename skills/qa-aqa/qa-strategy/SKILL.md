---
name: qa-strategy
description: Use when defining test strategy, quality gates, regression scope, risk-based testing, release readiness, and acceptance validation across product, platform, data, ML, or security work.
---

# QA Strategy

## Workflow

1. Identify user risk, technical risk, data risk, and operational risk.
2. Define test layers: unit, integration, contract, e2e, performance, security, data quality.
3. Prioritize automation where regression value is high.
4. Define release gates and evidence.
5. Produce test plan.

## Artifact

Use `templates/test-plan.md`.

## Guardrails

- Do not chase exhaustive testing; prioritize risk.
- Do not accept untestable acceptance criteria.
