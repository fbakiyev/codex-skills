# Workflow: Project Intake

## Trigger

Use when starting work on a new repository, initiative, platform system, data product, ML project, or security scope.

## Agents

- `delivery-lead`
- `context-steward`
- `chief-architect`
- domain-specific agents as needed

## Steps

1. Run `project-discovery`.
2. Create or update `project-brief.md`.
3. Identify missing stakeholders, systems, environments, and validation commands.
4. Decide whether the work should run as Kanban, sprint, spike, or incident.
5. Create initial backlog items and risks.

## Outputs

- `.memory/projects/<project>/project-brief.md`
- `.memory/projects/<project>/backlog.yaml`
- `.memory/projects/<project>/risks.md`
