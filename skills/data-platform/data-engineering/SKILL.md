---
name: data-engineering
description: Use when building or reviewing ingestion, transformation, batch jobs, streaming jobs, ELT, data contracts, schemas, and pipeline reliability.
---

# Data Engineering

## Workflow

1. Identify sources, sinks, grain, schema, freshness, and ownership.
2. Define incremental behavior, backfill, deduplication, and idempotency.
3. Add data quality checks and lineage notes.
4. Validate with sample data, tests, or dry runs.
5. Update data contract and handoff.

## Artifact

Use `templates/data-contract.yaml`.

## Guardrails

- Do not silently change metric definitions or grain.
- Do not skip backfill and replay behavior.
