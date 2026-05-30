---
name: threat-modeling
description: Use when designing or reviewing systems for trust boundaries, assets, actors, abuse cases, attack paths, mitigations, residual risk, and security acceptance criteria.
---

# Threat Modeling

## Workflow

1. Identify assets, actors, entry points, trust boundaries, and data flows.
2. Enumerate realistic abuse cases.
3. Map mitigations and detection.
4. Record residual risks and required follow-up.
5. Feed security requirements into backlog.

## Artifact

Use `templates/threat-model.md`.

## Guardrails

- Do not reduce threat modeling to a checklist.
- Do not ignore identity, secrets, logs, and data exposure.
