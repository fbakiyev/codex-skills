---
name: technical-review
description: Review a proposed technical or documentation change for concrete defects, regressions, validation gaps, and operational risk. Use for a review request or a consequential change needing independent scrutiny, not for ceremonial approval of every small edit.
---

# Technical Review

1. Establish the changed behavior and the acceptance criteria from the request and applicable project rules.
2. Inspect the diff and related contracts. Prioritize failures that users or operators can encounter over stylistic preferences.
3. Check evidence proportionate to the change. Verify relevant commands when available; do not rerun successful checks without a new change or unresolved concern.
4. Check operational documents only when affected: for example, a changed recovery procedure needs corresponding runbook and rollback information.
5. Report actionable findings in severity order, with location, concrete trigger, impact, and suggested correction. Use `P0`–`P3` when the project uses these levels.

Tie every finding to evidence or an explicit requirement. Do not invent a gate for missing sprint records, private notes, or handoff when the task does not require them. If there are no findings, say so and identify material verification limits. A review request authorizes inspection and reporting; implement fixes only if they are also in scope.
