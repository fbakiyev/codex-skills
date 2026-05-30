---
name: appsec-review
description: Use when reviewing application code, APIs, auth, sessions, authorization, input handling, dependency risk, secure defaults, logging, and data exposure.
---

# AppSec Review

## Workflow

1. Identify authn/authz, inputs, sensitive data, dependencies, and trust boundaries.
2. Review for injection, broken access control, unsafe deserialization, SSRF, XSS, CSRF, and logging leaks as relevant.
3. Prioritize exploitable risks over theoretical issues.
4. Add findings with severity, evidence, and fix.

## Guardrails

- Do not print exploit payloads that expose real secrets or harm live systems.
- Do not mark risk resolved without code or configuration evidence.
