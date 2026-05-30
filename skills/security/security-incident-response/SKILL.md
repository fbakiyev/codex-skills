---
name: security-incident-response
description: Use during or after suspected security incidents involving credentials, intrusion, malware, data exposure, suspicious activity, policy violations, or compromised systems.
---

# Security Incident Response

## Workflow

1. Preserve evidence and establish scope.
2. Contain with least destructive reversible steps where possible.
3. Rotate affected credentials through the secret manager.
4. Record timeline, impact, indicators, and actions.
5. Create follow-up hardening and detection backlog.

## Guardrails

- Do not publish indicators that contain sensitive customer or credential data.
- Do not destroy evidence unless containment requires it and the decision is recorded.
