# Workflow: Backlog Refinement

## Trigger

Use when goals, ideas, incidents, research topics, or technical debt need to become executable work.

## Agents

- `product-owner`
- `business-analyst`
- `system-analyst`
- `data-analyst` when metrics or data are involved
- relevant domain agents

## Steps

1. Clarify value, users, constraints, and risks.
2. Split items until each has one clear outcome.
3. Add acceptance criteria and required artifacts.
4. Assign owner and reviewer agents.
5. Add Linear-ready metadata when known.
6. Mark status as `ready` only when DoR is met.

## Outputs

- `.memory/projects/<project>/backlog.yaml`
- backlog items matching `templates/backlog-item.yaml`
