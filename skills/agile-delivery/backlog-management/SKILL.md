---
name: backlog-management
description: Use when turning goals, requirements, incidents, research, platform work, data work, ML work, QA work, or security work into structured backlog items with acceptance criteria, owners, risks, dependencies, and Linear-ready metadata.
---

# Backlog Management

## Goal

Convert intent into executable work items with clear value and acceptance criteria.

## Workflow

1. Clarify the outcome, not only the activity.
2. Split work into independently reviewable items.
3. Add acceptance criteria that can be verified.
4. Assign owner and review agents by capability.
5. Capture dependencies, risks, artifact requirements, and validation expectations.
6. Keep Linear fields present but optional until integration is active.

## Artifact

Use `templates/backlog-item.yaml`.

For sprint work, aggregate items in:

```text
.memory/projects/<project>/sprints/<sprint>/sprint-backlog.yaml
```

For project-level work:

```text
.memory/projects/<project>/backlog.yaml
```

## Quality Bar

A backlog item is ready only when another agent can start without asking what "done" means.

## Guardrails

- Do not create vague tasks such as "improve system" without measurable acceptance criteria.
- Do not hide research uncertainty inside implementation tasks; create a spike.
- Do not assign all review to one generic reviewer when security, xOps, data, or QA review is needed.
