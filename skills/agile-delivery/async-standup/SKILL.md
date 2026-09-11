---
name: async-standup
description: Prepare a requested asynchronous standup or a status update within an established sprint process, covering done, next, blockers, risks, and changed assumptions. Do not introduce sprint artifacts for an ordinary status question.
---

# Async Standup

## Goal

Maintain sprint visibility without chatty meeting simulation.

## Workflow

1. Read the available sprint brief, backlog, blockers, and relevant prior updates; do not create missing artifacts just to produce a status answer.
2. Summarize:
   - completed since last update
   - next actions
   - blockers
   - risk changes
   - artifact updates
3. Escalate blockers to PM, PO, architect, or relevant domain agent.
4. Return the standup update; persist it only when a durable update is requested or already part of the agreed process.

## Artifact

Use `templates/standup-update.md`.

Use the response or the approved project documentation destination for a requested team update. If durable context is needed, `<context-root>` is a placeholder for the configured destination. Check its audience and visibility before including private information:

```text
<context-root>/projects/<project>/sprints/<sprint>/standups/YYYY-MM-DD.md
```

## Guardrails

- Do not invent progress.
- Do not mark blockers as resolved without evidence.
- Do not use standup as a substitute for a requested review or transfer of work.
