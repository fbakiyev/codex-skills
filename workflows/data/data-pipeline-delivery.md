# Workflow: Data Pipeline Delivery

## Trigger

Use for ingestion, transformation, orchestration, analytics, quality, or governance changes.

## Agents

- `data-engineer`
- `data-quality-engineer`
- `dataops-engineer`
- `data-governance-engineer` when access or classification changes

## Steps

1. Define source, sink, schema, grain, freshness, and owner.
2. Implement pipeline or model changes.
3. Add quality checks, lineage, and observability.
4. Define backfill and rollback behavior.
5. Validate with tests or sample runs.
6. Update the relevant data contract; write a handoff when work is transferred or a durable handoff is requested.

## Outputs

- data contract
- quality checks
- observability notes
- handoff when work is transferred or a durable handoff is requested
