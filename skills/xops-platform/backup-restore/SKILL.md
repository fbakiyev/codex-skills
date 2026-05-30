---
name: backup-restore
description: Use when designing, validating, documenting, or reviewing backup, restore, disaster recovery, RPO, RTO, snapshots, replication, and recovery drills for systems or data.
---

# Backup Restore

## Goal

Make recovery paths explicit and tested.

## Workflow

1. Identify stateful components and source of truth.
2. Define backup mechanism, schedule, retention, encryption, and storage location.
3. Define RPO and RTO.
4. Document restore procedure and validation.
5. Record last restore drill and gaps.

## Artifact

Use `templates/backup-restore.md`.

## Guardrails

- Do not claim backups are valid without a restore validation path.
- Do not store backup credentials in docs.
- Do not ignore data consistency between dependent systems.
