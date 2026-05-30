---
name: infrastructure-provisioning
description: Use when provisioning or changing infrastructure with Terraform, OpenTofu, Pulumi, Ansible, Kubernetes manifests, Helm, cloud APIs, or manual bootstrap steps that must be documented and validated.
---

# Infrastructure Provisioning

## Goal

Make infrastructure changes reproducible, reviewable, and safe to operate.

## Workflow

1. Discover source of truth: IaC repo, GitOps repo, inventory, state backend, and target environment.
2. Plan the change and identify blast radius.
3. Update IaC or automation first; document manual bootstrap only when unavoidable.
4. Define validation and rollback before applying.
5. Update deployment map, access map, runbook, and handoff.

## Validation

Prefer deterministic checks:

- format/lint
- plan/diff
- dry-run/template rendering
- targeted health checks
- drift checks

## Guardrails

- Do not apply production-impacting changes without explicit user approval in interactive workflows.
- Do not hide manual steps; record them in runbook or handoff.
- Do not expose state files or credentials.
