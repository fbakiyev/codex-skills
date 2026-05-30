---
name: async-standup
description: Use to facilitate asynchronous standups between agents by aggregating done, next, blockers, risks, artifact updates, and changed assumptions from sprint memory rather than simulating meetings.
---

# Async Standup

## Goal

Maintain sprint visibility without chatty meeting simulation.

## Workflow

1. Read sprint brief, sprint backlog, blockers, and latest handoffs.
2. Summarize:
   - completed since last update
   - next actions
   - blockers
   - risk changes
   - artifact updates
3. Escalate blockers to PM, PO, architect, or relevant domain agent.
4. Update standup artifact.

## Artifact

Use `templates/standup-update.md`.

Write updates to:

```text
.memory/projects/<project>/sprints/<sprint>/standups/YYYY-MM-DD.md
```

## Guardrails

- Do not invent progress.
- Do not mark blockers as resolved without evidence.
- Do not use standup as a substitute for review or handoff.
