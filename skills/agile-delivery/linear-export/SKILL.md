---
name: linear-export
description: Use when preparing backlog or sprint items for future Linear import or synchronization by normalizing team, project, cycle, labels, owner agents, priorities, statuses, and acceptance criteria.
---

# Linear Export

## Goal

Keep backlog data ready for future Linear integration without requiring Linear during local planning.

## Workflow

1. Ensure each backlog item has stable `id`, `title`, `type`, `status`, `priority`, and `acceptance_criteria`.
2. Populate `linear.team`, `linear.project`, `linear.cycle`, and `linear.issue_id` when known.
3. Normalize labels to lowercase kebab-case.
4. Keep agent ownership separate from future human ownership.
5. Use `templates/linear-export.yaml` for batch export planning.

## Guardrails

- Do not overwrite local ids with external ids unless mapping is explicit.
- Do not mark items ready for Linear export when acceptance criteria are empty.
