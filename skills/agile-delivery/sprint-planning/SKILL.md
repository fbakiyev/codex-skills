---
name: sprint-planning
description: Plan a requested sprint or an increment within an established sprint process, including goal, scope, roles, risks, dependencies, readiness, completion criteria, and deliverables. Do not impose sprints on unrelated tasks.
---

# Sprint Planning

## Goal

Create a sprint plan that agents can execute asynchronously.

## Workflow

1. Review project goal, current state, risks, and backlog.
2. Preserve the requested delivery mode. If the mode is unspecified, choose an appropriate sprint, Kanban, research spike, or incident workflow based on scope; do not force a sprint on a small fix.
3. Define sprint goal and non-goals.
4. Select backlog items that fit the goal.
5. Assign owner and reviewer agents.
6. Define DoR and DoD.
7. List required artifacts and validation commands.

## Artifact

Use `templates/sprint-brief.md`.

Return the sprint plan in the response or save it to the approved project documentation destination when a durable plan is requested. Use the configured destination and check its audience before including private context.

## Quality Bar

A sprint plan should make scope tradeoffs explicit before execution starts.
