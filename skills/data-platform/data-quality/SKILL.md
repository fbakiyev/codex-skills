---
name: data-quality
description: Use when defining, implementing, or reviewing data quality checks, anomaly detection, freshness, completeness, uniqueness, validity, reconciliation, and incident response.
---

# Data Quality

## Workflow

1. Define dimensions: freshness, completeness, validity, uniqueness, consistency, and accuracy.
2. Tie checks to business impact.
3. Choose blocking, warning, or monitoring behavior.
4. Document ownership and incident workflow.
5. Add quality expectations to data contract.

## Guardrails

- Do not block pipelines on noisy checks without owner agreement.
- Do not treat passing schema checks as full data quality.
