---
name: project-discovery
description: Use when starting work in an unfamiliar repository, project, platform, service, data product, ML system, or security scope; creates a concise map of context, ownership, artifacts, risks, and next actions without dumping the whole tree.
---

# Project Discovery

## Goal

Build the smallest useful project map before planning or implementation.

## Workflow

1. Read local guidance first: `AGENTS.md`, README, architecture docs, sprint artifacts, and visible manifests.
2. Use targeted search: `rg --files`, `rg`, bounded `sed -n`, and narrow `find`.
3. Identify:
   - project purpose
   - active stack
   - ownership hints
   - test and validation commands
   - deployment/runtime model
   - documentation and memory locations
   - risks, gaps, and unknowns
4. Create or update a discovery artifact only when the task benefits from persistent memory.
5. Keep output compact: facts, assumptions, risks, and next actions.

## Artifact

Use `.memory/projects/<project>/project-brief.md` when persistent project context is needed.

Minimum sections:

- Purpose
- Current state
- Key paths
- Validation commands
- Deployment/runtime
- Owners and stakeholders
- Risks and open questions
- Recommended next steps

## Guardrails

- Do not run broad tree dumps.
- Do not read large files end to end unless the heading search shows they are relevant.
- Do not infer ownership or production state without evidence; mark it as an assumption.
