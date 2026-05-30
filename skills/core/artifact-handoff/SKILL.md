---
name: artifact-handoff
description: Use before ending a task, transferring work to another agent, closing a sprint item, or summarizing implementation, validation, risks, decisions, and next steps as durable artifacts.
---

# Artifact Handoff

## Goal

Create a concise handoff that another agent can use to continue without reading the conversation.

## Workflow

1. Collect completed work from code/docs/artifacts, not only from memory.
2. Record validation commands and outcomes.
3. List decisions and link to ADRs if they exist.
4. Record residual risks and open questions.
5. Write next steps as concrete actions.

## Output

Use `templates/handoff.md`.

For sprint work, write to:

```text
.memory/projects/<project>/sprints/<sprint>/handoff.md
```

For repository work, write to:

```text
.memory/repo/sprints/<sprint>.md
```

## Guardrails

- Do not claim validation passed unless it actually ran or was manually verified.
- Do not include raw credentials, tokens, or private values.
- Do not bury blockers in prose; list them explicitly.
