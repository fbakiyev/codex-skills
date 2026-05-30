# Workflow: Review And Handoff

## Trigger

Use before closing a meaningful task, sprint item, platform change, or repository iteration.

## Agents

- `technical-reviewer`
- `context-steward`
- domain reviewers required by the task

## Steps

1. Inspect changed files and artifacts.
2. Run available validation.
3. Check definition of done for the task type.
4. Create or update handoff.
5. If a failure or repeated gap is found, run `skill-evolution-loop`.

## Outputs

- review notes
- validation result
- handoff
- optional skill evolution record
