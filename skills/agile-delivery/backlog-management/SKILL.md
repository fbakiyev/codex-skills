---
name: backlog-management
description: Create or refine a requested backlog or structured work breakdown with acceptance criteria, owners, risks, dependencies, and optional Linear metadata. Do not turn every task into backlog maintenance.
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

Return backlog items in the response or save them to the approved project documentation destination when persistence is requested. Keep project-level and sprint-level backlogs separate only when that distinction is part of the delivery process. Use the configured destination and check its audience before including private context.

## Quality Bar

A backlog item is ready only when another agent can start without asking what "done" means.

## Guardrails

- Do not create vague tasks such as "improve system" without measurable acceptance criteria.
- Do not hide research uncertainty inside implementation tasks; create a spike.
- Do not assign all review to one generic reviewer when security, xOps, data, or QA review is needed.
