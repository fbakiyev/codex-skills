# Context Storage

`<context-root>` is a placeholder for the destination configured by the user or project. It may be a local directory, a knowledge base, or a repository location. Use the established destination and naming conventions; do not treat the placeholder as a literal path.

For a filesystem destination, one note per project can be enough:

```text
<context-root>/<project>/current-state.md
```

Keep the objective, authoritative sources, verified state, consequential decisions, blockers, and next action. Add a separate decision or transfer note only when needed. Time-sensitive observations need a date, timezone, and coverage limits.

Check the audience and visibility before saving. Public locations must not receive private context. Keep credentials in the approved secret store, and omit unnecessary personal data and raw conversation dumps.

User-facing ADRs, backlogs, runbooks, meeting minutes, and project handovers keep their existing source-of-truth locations. Reference them rather than duplicating entire artifacts. Change historical records only within the requested maintenance scope.
