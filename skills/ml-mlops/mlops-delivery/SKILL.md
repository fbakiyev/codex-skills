---
name: mlops-delivery
description: Use when taking ML systems to production including training pipelines, model registry, serving, feature stores, monitoring, drift, evaluation, rollback, and reproducibility.
---

# MLOps Delivery

## Workflow

1. Identify training, validation, registry, deployment, serving, and monitoring path.
2. Define model versioning and promotion gates.
3. Add evaluation and rollback procedures.
4. Document feature dependencies and secret references.
5. Coordinate with xOps for runtime and observability.

## Guardrails

- Do not ship a model without evaluation and rollback.
- Do not treat notebook success as production readiness.
