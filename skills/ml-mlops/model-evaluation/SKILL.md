---
name: model-evaluation
description: Use when evaluating ML, LLM, RAG, ranking, forecasting, classification, regression, or recommendation systems with metrics, datasets, slices, error analysis, and regression checks.
---

# Model Evaluation

## Workflow

1. Define evaluation objective and acceptance threshold.
2. Select datasets, slices, metrics, and baselines.
3. Run quantitative and qualitative error analysis.
4. Record failures and regression cases.
5. Produce an eval report and update model card when relevant.

## Artifact

Use `templates/eval-report.md`.

## Guardrails

- Do not rely on aggregate metrics only.
- Do not tune on the final evaluation set.
