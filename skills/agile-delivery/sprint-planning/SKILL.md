---
name: sprint-planning
description: Use to plan an agentic sprint by selecting backlog items, defining sprint goal, scope, roles, risks, dependencies, definition of ready, definition of done, and required artifacts.
---

# Sprint Planning

## Goal

Create a sprint plan that agents can execute asynchronously.

## Workflow

1. Review project goal, current state, risks, and backlog.
2. Choose sprint mode:
   - sprint for planned delivery
   - kanban for small fixes
   - spike for research
   - incident for urgent restoration
3. Define sprint goal and non-goals.
4. Select backlog items that fit the goal.
5. Assign owner and reviewer agents.
6. Define DoR and DoD.
7. List required artifacts and validation commands.

## Artifact

Use `templates/sprint-brief.md`.

Write sprint plans to:

```text
.memory/projects/<project>/sprints/<sprint>/sprint-brief.md
```

## Quality Bar

A sprint plan should make scope tradeoffs explicit before execution starts.
