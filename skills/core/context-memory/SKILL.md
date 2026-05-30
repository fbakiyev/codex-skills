---
name: context-memory
description: Use when a task needs durable project memory, sprint state, decision logs, handoffs, risk tracking, or continuity across multiple Codex sessions and agents.
---

# Context Memory

## Goal

Keep agent context outside the chat by writing concise, structured artifacts.

## Memory Layout

See `references/memory-schema.md` for the canonical layout.

Use the smallest relevant scope:

- `.memory/repo/` for this skills repository.
- `.memory/projects/<project>/` for a specific project.
- `.memory/projects/<project>/sprints/<sprint>/` for sprint delivery.
- `.memory/projects/<project>/systems/<system>/` for platform/xOps systems.

## Update Rules

1. Update memory after a meaningful milestone, decision, validation result, blocker, or handoff.
2. Prefer append-only sprint artifacts and ADRs over rewriting history.
3. Keep current-state files short and link to deeper artifacts.
4. Record assumptions explicitly.
5. Never store secret values; store only secret references.

## Required Handoff Fields

- Context
- Completed
- Validation
- Decisions
- Artifacts updated
- Risks
- Next steps

## Quality Bar

Memory should let another agent resume the task without reading the whole chat.
