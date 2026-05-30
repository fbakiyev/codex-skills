# Workflow: Backup Restore

## Trigger

Use for stateful services, databases, object storage, registries, secrets backends, data platforms, ML registries, and disaster recovery planning.

## Agents

- `sre-engineer`
- `dbops-engineer`
- `dataops-engineer`
- `platform-architect`

## Steps

1. Identify stateful components and dependencies.
2. Define backup mechanism, schedule, retention, encryption, and owner.
3. Define RPO and RTO.
4. Document restore procedure and validation.
5. Track last restore test and gaps.

## Outputs

- `backup-restore.md`
- updated runbook
- follow-up backlog for missing restore validation
