---
name: runbook-authoring
description: Use when creating or updating operational runbooks for services, platforms, pipelines, clusters, databases, ML systems, security tooling, or incident-prone workflows.
---

# Runbook Authoring

## Goal

Make operations repeatable under pressure.

## Workflow

1. Identify normal operations, failure modes, health checks, dashboards, and rollback path.
2. Link to access map rather than duplicating secret details.
3. Write concrete commands only when they are safe and environment-scoped.
4. Include escalation path and owners.
5. Keep runbook current after implementation or incident review.

## Artifact

Use `templates/runbook.md`.

## Guardrails

- Do not include credentials.
- Do not include destructive commands without preconditions and rollback notes.
- Do not assume dashboards or alerts exist; document gaps.
