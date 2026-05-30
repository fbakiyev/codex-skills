---
name: performance-engineering
description: Use when investigating or improving latency, throughput, resource usage, scalability, frontend performance, backend hotspots, database queries, and load test results.
---

# Performance Engineering

## Workflow

1. Define target metric and baseline.
2. Identify bottleneck with evidence before optimizing.
3. Make one meaningful change at a time when possible.
4. Validate with repeatable measurements.
5. Record tradeoffs and residual bottlenecks.

## Artifact

Use `templates/performance-report.md`.

## Guardrails

- Do not optimize without a baseline.
- Do not trade correctness or security for speed without explicit decision.
