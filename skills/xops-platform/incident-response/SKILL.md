---
name: incident-response
description: Use during or after incidents affecting infrastructure, applications, data pipelines, ML systems, security controls, availability, latency, correctness, or access.
---

# Incident Response

## Goal

Restore service, preserve evidence, communicate clearly, and convert learnings into durable fixes.

## Workflow

1. Establish severity, scope, impact, timeline, and current mitigations.
2. Assign incident commander and domain responders.
3. Prefer reversible mitigations.
4. Record commands, observations, and decisions.
5. After stabilization, create incident report and follow-up backlog items.
6. Update runbooks, alerts, skills, or evals when gaps are found.

## Artifact

Use `templates/incident-report.md`.

## Guardrails

- Do not expose secrets in incident notes.
- Do not destroy evidence unless required for containment and explicitly recorded.
- Do not skip follow-up actions after restoration.
