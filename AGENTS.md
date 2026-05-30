# Repository Agent Instructions

## Language

- Keep top-level user-facing documentation in Russian.
- Keep machine-readable ids, YAML keys, skill names, agent ids, workflow ids, and file paths in English.
- Skill bodies may be English when it improves triggering and reuse by Codex.

## Context Discipline

- Keep `SKILL.md` files concise and procedural.
- Put detailed domain material in `references/` and load it only when needed.
- Prefer templates and deterministic scripts over repeating long instructions.
- Do not create extra README files inside individual skills.

## Delivery Discipline

- Work in sprint-sized increments.
- After each meaningful sprint, update `.memory/repo/sprints/`.
- Run `python3 scripts/validate_repo.py` before committing.
- Commit and push every completed iteration when repository access is available.

## Artifact Discipline

Every non-trivial agent or workflow should define its expected artifacts:

- brief
- backlog item or task record
- decision log or ADR when architecture changes
- validation result
- handoff
- risks and open questions

For xOps/platform work also require:

- deployment map
- access map
- runbook
- observability notes
- backup/restore notes
- security notes

## Secret Handling

- Never store raw passwords, tokens, private keys, API keys, kubeconfigs, cloud credentials, or base64 Kubernetes Secret values.
- Store only secret references: provider, path, key, owner, access role, rotation policy, access request procedure, and safe validation command.
- If a task requires a secret value, ask the user to provide it through the appropriate external secret manager or local secure mechanism.
