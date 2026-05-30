---
name: technical-review
description: Use to review code, infrastructure, data, ML, documentation, security, or workflow changes for bugs, regressions, missing validation, operational risk, and artifact completeness before handoff or merge.
---

# Technical Review

## Stance

Prioritize findings over summaries. Review for correctness, operability, maintainability, security, and evidence.

## Workflow

1. Inspect the diff and related context.
2. Identify behavioral risks, broken contracts, missing tests, missing artifacts, and security issues.
3. Check whether the change updated required memory and handoff artifacts.
4. Verify validation commands where practical.
5. Output findings ordered by severity.

## Finding Format

- Severity: `P0`, `P1`, `P2`, or `P3`
- Location: file and line when available
- Problem: concrete behavior or risk
- Fix: actionable recommendation

## Review Gates

Block completion when:

- validation is absent for risky changes
- xOps changes lack access map or runbook
- secrets are exposed
- acceptance criteria are untestable
- handoff is missing after multi-step work

## Guardrails

- Do not nitpick style unless it affects maintainability or local standards.
- Do not invent requirements; tie findings to task scope, repository rules, or observable behavior.
