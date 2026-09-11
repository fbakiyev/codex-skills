---
name: artifact-handoff
description: Prepare a resumable handoff when work is being transferred or a durable completion record is requested. Capture verified state, decisions, blockers, and next actions; ordinary task completion alone does not require a handoff document.
---

# Artifact Handoff

1. Establish what the receiving person needs to continue and where the record belongs. Reuse an already approved destination.
2. Read the relevant deliverables and verification results. Separate completed work from attempted, pending, or unavailable work.
3. Include exact relevant commands or queries and outcomes. For time-dependent diagnosis, include source, observation window, timezone, and coverage limits.
4. State consequential decisions, blockers, material risks, and concrete next actions. Link authoritative artifacts instead of duplicating them.
5. Deliver the handoff in the requested format. If no persistent destination is agreed, provide it in the response while continuing any independent authorized work.

The record needs only context, completed work, validation, decisions, blockers, artifact links, and next actions that actually matter. Omit empty sections. `templates/handoff.md` is optional when this repository is available.

Store continuity notes and project handover documents in the destination chosen by the user or project. Check its audience and visibility before including private context. Never include secret values or invent a successful check.
