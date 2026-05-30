---
name: feature-engineering
description: Use when designing, reviewing, or operating ML features, feature stores, offline/online consistency, point-in-time correctness, leakage prevention, and feature monitoring.
---

# Feature Engineering

## Workflow

1. Define feature owner, source, grain, freshness, and serving path.
2. Check point-in-time correctness and leakage risk.
3. Document offline and online transformations.
4. Add quality and drift checks.
5. Update data contract and model card.

## Guardrails

- Do not reuse future data in training features.
- Do not assume offline and online feature logic match without validation.
