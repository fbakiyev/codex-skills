# Workflow: Async Standup

## Trigger

Use when an asynchronous standup is requested or a status update is part of an established sprint process. Answer ordinary status questions directly without introducing sprint artifacts.

## Agents

- `scrum-master`
- `project-manager`
- `context-steward`

## Steps

1. Read the available sprint backlog, relevant prior updates, blockers, and validation evidence.
2. Summarize done, next, blockers, and risk changes.
3. Escalate unresolved blockers to the right owner agent.
4. Return the update; save a standup artifact only when persistence is requested or agreed for this process.

## Outputs

- standup update in the response or the approved project documentation destination
- optional durable context at `<context-root>/projects/<project>/sprints/<sprint>/standups/YYYY-MM-DD.md`, where `<context-root>` is the configured destination; check its audience and visibility before including private information
- updated blockers when needed
