---
name: system-analysis
description: Use when translating requirements into system behavior, integration contracts, API flows, data movement, edge cases, sequence diagrams, state transitions, and implementation constraints.
---

# System Analysis

## Goal

Make system behavior explicit before design or implementation.

## Workflow

1. Identify actors, systems, boundaries, and source of truth.
2. Describe main flows and failure flows.
3. Define API, event, database, or file contracts.
4. Capture edge cases and consistency assumptions.
5. Identify observability, security, data quality, and rollback needs.
6. Produce backlog-ready implementation and test implications.

## Artifact

Use `templates/system-analysis.md`.

## Guardrails

- Do not confuse current behavior with desired behavior.
- Do not skip failure paths for infrastructure, data, security, or payment-like flows.
- Do not define contracts only in prose when schemas or examples are needed.
