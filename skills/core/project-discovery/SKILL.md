---
name: project-discovery
description: "Map an unfamiliar repository or technical project before implementation: locate entry points, validation commands, runtime boundaries, and relevant constraints. Use for missing project context, not as a prerequisite for a self-contained office task."
---

# Project Discovery

1. Read applicable local instructions, the entry README, and manifests relevant to the task.
2. Use targeted `rg --files` and `rg` searches; expand reads only when the dependency or heading warrants it.
3. Identify the requested outcome, affected components, validation commands, runtime/deployment boundaries, ownership evidence, and material unknowns.
4. State observed facts separately from assumptions. An example configuration is not evidence of production state.
5. Continue the requested work once there is enough context. Do not turn discovery into an automatic backlog, sprint, or architecture exercise.

Return the smallest useful map: purpose, relevant paths, checks, boundaries, and open questions. If durable context is requested or needed for a real transfer, use the configured project destination with appropriate visibility; otherwise keep the map in the response. Preserve existing user documents and their source-of-truth location.
