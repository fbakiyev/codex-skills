---
name: performance-testing
description: Use when designing or reviewing load tests, stress tests, soak tests, frontend performance checks, capacity tests, and performance regression gates.
---

# Performance Testing

## Workflow

1. Define workload model, baseline, target, and environment.
2. Choose load, stress, soak, or regression test.
3. Capture metrics and bottlenecks.
4. Compare results to acceptance criteria.
5. Produce performance report.

## Guardrails

- Do not compare runs from incompatible environments.
- Do not report averages without tail latency or error rate when relevant.
