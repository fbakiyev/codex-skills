---
name: skill-evolution-loop
description: Use after an agent mistake, repeated manual workflow, missing artifact, failed validation, or recurring user correction to update skills, templates, scripts, workflows, or eval cases so future agents improve.
---

# Skill Evolution Loop

## Goal

Turn failures and repeated work into durable improvements.

## Workflow

1. Identify the trigger:
   - mistake
   - missing instruction
   - repeated manual steps
   - weak validation
   - unclear artifact contract
2. Choose the smallest durable fix:
   - update `SKILL.md`
   - add a reference file
   - add or update a template
   - add a deterministic script
   - add an eval sample
   - update an agent role
3. Add a regression case when behavior can recur.
4. Run repository validation.
5. Record the change in a skill evolution artifact.

## Artifact

Use `templates/skill-evolution-record.md`.

## Quality Bar

The fix should reduce future context load, reduce ambiguity, or make validation more deterministic.

## Guardrails

- Do not add long explanations to `SKILL.md` when a focused reference file is better.
- Do not add a new agent when an existing role or workflow can own the behavior.
- Do not encode one-off user preferences as universal rules unless they are clearly reusable.
