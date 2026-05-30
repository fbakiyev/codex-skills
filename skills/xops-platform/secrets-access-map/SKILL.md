---
name: secrets-access-map
description: Use when documenting where tokens, passwords, credentials, kubeconfigs, cloud secrets, certificates, and service credentials are stored, requested, rotated, validated, and consumed without exposing secret values.
---

# Secrets Access Map

## Goal

Document how to find and request secrets without ever storing secret values.

## Allowed

- provider
- path
- key
- owner
- access role or group
- rotation policy
- access request procedure
- safe validation command
- breakglass location and approval path

## Forbidden

- raw password
- raw token
- API key value
- private key
- kubeconfig content
- base64 Kubernetes Secret data
- copied `.env` with real values

## Workflow

1. Identify source of truth for each secret.
2. Document runtime consumer separately from source of truth.
3. Capture required access role and request path.
4. Define safe validation that proves access without printing the secret.
5. Update `access-map.yaml`.

## Artifact

Use `templates/access-map.yaml`.
