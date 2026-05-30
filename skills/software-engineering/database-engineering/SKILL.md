---
name: database-engineering
description: Use when changing schemas, queries, migrations, indexes, transactions, database performance, consistency, backups, restores, and data access behavior.
---

# Database Engineering

## Workflow

1. Identify database engine, migration tool, schema ownership, and rollback constraints.
2. Check compatibility with running application versions.
3. Review indexes, locks, transactions, data volume, and migration duration.
4. Add validation and backup/restore considerations.
5. Coordinate with DBOps for production changes.

## Guardrails

- Do not assume schema rollback is possible; document it.
- Do not run destructive migrations without explicit approval and backup path.
