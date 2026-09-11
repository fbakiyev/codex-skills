---
name: xops-platform-design
description: Use when designing platforms, Kubernetes clusters, GitOps foundations, cloud landing zones, observability stacks, service platforms, data platforms, ML platforms, or shared infrastructure systems.
---

# xOps Platform Design

## Goal

Design platforms that are operable, secure, observable, cost-aware, and documented from day one.

## Workflow

1. Identify users, workloads, environments, compliance needs, and ownership.
2. Define control plane, data plane, network, identity, secrets, deployment, and observability boundaries.
3. Choose build-vs-buy and managed-vs-self-hosted tradeoffs.
4. Capture architecture decisions in ADRs.
5. Define required operational artifacts before implementation.

## Required Artifacts

- `system-design.md`
- `deployment-map.yaml`
- `access-map.yaml`
- `runbook.md`
- `observability.md`
- `backup-restore.md`
- `security-notes.md`
- ADRs for consequential choices

## Guardrails

- Do not treat deployment as complete without ownership, access, observability, and rollback context.
- Do not store secret values in design documents.
- Do not skip failure modes for shared platforms.
