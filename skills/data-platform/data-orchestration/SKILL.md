---
name: data-orchestration
description: Use when designing or reviewing Airflow, Dagster, Prefect, cron, event-driven pipelines, dependencies, retries, backfills, SLAs, and operational ownership.
---

# Data Orchestration

## Workflow

1. Define DAG ownership, schedule, dependencies, retries, and failure semantics.
2. Plan backfill and catchup behavior.
3. Add observability and alert routing.
4. Validate DAG parsing and task-level behavior.
5. Document runbook and handoff.

## Guardrails

- Do not create pipelines without failure ownership.
- Do not let retries hide non-idempotent behavior.
