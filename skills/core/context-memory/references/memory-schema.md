# Memory Schema

## Repository Memory

```text
.memory/repo/
  sprints/
    sprint-000-foundation.md
  decisions/
  risks.md
  roadmap.md
```

## Project Memory

```text
.memory/projects/<project>/
  project-brief.md
  current-state.md
  backlog.yaml
  risks.md
  glossary.md
  decisions/
    ADR-0001-title.md
  sprints/
    sprint-YYYY-MM-DD/
      sprint-brief.md
      sprint-backlog.yaml
      standups/
      blockers.md
      review.md
      retro.md
      handoff.md
  systems/
    <system>/
      system-design.md
      deployment-map.yaml
      access-map.yaml
      runbook.md
      observability.md
      backup-restore.md
      security-notes.md
```

## Current State Files

Keep current state short:

- what exists now
- where source of truth lives
- latest validation result
- known blockers
- next recommended action

Do not duplicate full runbooks, ADRs, or backlog items.
