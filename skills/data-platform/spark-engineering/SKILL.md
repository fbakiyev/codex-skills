---
name: spark-engineering
description: Use when designing, debugging, or optimizing Apache Spark, PySpark, Scala Spark, Databricks, EMR, large joins, partitioning, skew, shuffle, and distributed data jobs.
---

# Spark Engineering

## Workflow

1. Identify data size, partitioning, file format, cluster/runtime, and bottleneck.
2. Check joins, skew, shuffles, caching, broadcast strategy, and write layout.
3. Validate with representative samples and execution plans where available.
4. Record performance and correctness tradeoffs.

## Guardrails

- Do not optimize Spark jobs only from code shape; inspect data shape assumptions.
- Do not use collect-like patterns on large data.
