# Workflow: Secret Onboarding

## Trigger

Use when a new system needs credentials, certificates, tokens, service accounts, repository credentials, cloud access, or runtime secrets.

## Agents

- `devsecops-engineer`
- `gitops-engineer`
- `cloudops-engineer`
- `context-steward`

## Steps

1. Identify source of truth for each secret.
2. Record provider, path, key, owner, access role, and rotation policy.
3. Record runtime consumer and delivery mechanism.
4. Add safe validation commands.
5. Update access map and security notes.

## Outputs

- `access-map.yaml`
- `security-notes.md`
- updated runbook if operators need access
