---
name: observability-setup
description: Use when designing or updating metrics, logs, traces, alerts, SLOs, dashboards, probes, synthetic checks, or incident visibility for services and platforms.
---

# Observability Setup

## Goal

Make service health, user impact, and operational risk visible.

## Workflow

1. Identify critical user journeys or platform functions.
2. Define signals: metrics, logs, traces, events, and probes.
3. Define SLOs or health thresholds where appropriate.
4. Add dashboards and alerts with owners.
5. Document known blind spots.

## Artifact

Use `templates/observability.md`.

## Guardrails

- Do not create alerts without owner or action.
- Do not rely only on infrastructure health when user-facing behavior matters.
- Do not treat logging as safe for secrets; redact sensitive values.
