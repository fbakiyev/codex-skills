---
name: analytics-engineering
description: Use when creating or reviewing dbt models, semantic layers, metrics, marts, dashboards, lineage, tests, exposures, and analytics documentation.
---

# Analytics Engineering

## Workflow

1. Identify business definition, grain, dimensions, and consumers.
2. Model sources, staging, intermediate, and marts consistently.
3. Add tests for uniqueness, not-null, accepted values, relationships, and freshness.
4. Document metric definitions and lineage.

## Guardrails

- Do not create metrics without definitions and owners.
- Do not mix incompatible grains without explicit logic.
