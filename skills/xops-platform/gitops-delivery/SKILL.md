---
name: gitops-delivery
description: Use when delivering applications or platform components through GitOps with Argo CD, Flux, Helm, Kustomize, Kubernetes manifests, environment overlays, sync waves, drift detection, and promotion workflows.
---

# GitOps Delivery

## Goal

Keep runtime state traceable to Git and make promotion, rollback, and drift visible.

## Workflow

1. Identify Git source of truth, cluster, namespace, application, chart, values, and overlays.
2. Render manifests when possible before changing runtime.
3. Check ownership labels, sync order, health checks, and secrets wiring.
4. Document promotion and rollback path.
5. Update deployment map and runbook.

## Required Artifacts

- `deployment-map.yaml`
- `runbook.md`
- `observability.md`
- `security-notes.md` when RBAC, network, or secrets change

## Guardrails

- Do not patch live Kubernetes resources as the final state when GitOps is the source of truth.
- Do not store base64 Kubernetes Secret values in Git.
- Do not call drift resolved unless Git and cluster state are reconciled or the exception is documented.
