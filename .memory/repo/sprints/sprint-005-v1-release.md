# Sprint 005: v1.0 Release Hardening

## Goal

Harden the repository for version 1.0.0 with stronger validation, inventory reporting, release artifact, and updated Russian README.

## Scope

- Set repository version to 1.0.0.
- Mark release target as achieved.
- Document v1.0 packs in README.
- Require all packs to have skills, agents, workflows, and eval samples.
- Require all core and domain templates.
- Add inventory script.
- Add release and roadmap memory artifacts.

## Definition Of Done

- `python3 scripts/validate_repo.py` passes.
- `python3 scripts/inventory.py` shows all packs populated.
- Final commit is pushed to GitHub.
- `v1.0.0` tag is pushed.

## Handoff

Version 1.0.0 is ready as a baseline. Future work should evolve from real task failures, recurring workflows, and project-specific needs.
