# Optional guidance for BYS portal users

Use this guidance when the BYS MCP tools are available in the conversation, even if the teacher does not mention the portal. A task proposal is not a task that has been assigned, saved, or published. Do not claim any of those states without explicit evidence supplied by the teacher. This reference does not provide portal access or authority.

## Portal BYS (MCP)

Use authenticated BYS MCP tools only within their documented scope. Before proposing a task, run `list_my_classes` to identify the authorized class and `get_class_context` for its roster, current levels, active study plans, recent sessions, and recent tasks; `get_student_academic_context` deepens an individual learner and `get_student_proficiency` adds proficiency history. Cite each learner's level evidence in the proposal or state what context was missing.

### Drafts and publication

When the teacher explicitly asks to save a task, use `create_task_draft` or `update_task_draft`. Use `list_my_task_drafts` and `get_task_draft` to resume a draft; load its current revision before editing. A saved draft is not assigned or published. For an explicit publication request, call `request_task_publish` for the current revision, present the preview, obtain confirmation for that exact content and destination, then call `confirm_task_publish` with that revision. Report saved or published status only when the corresponding tool result confirms it. A person without the required tools should explain that someone with access and authority must apply the proposal.

### Archiving

For an explicit request to withdraw a published task, call `request_task_archive`, present its affected classes, students, and preserved submission count, obtain confirmation for that action, then call `confirm_task_archive`. Archiving preserves submissions and history; do not describe it as deletion.

For a publication batch, use `preview_pedagogical_batch` with at most 25 task, review, or study-plan items. Present every item result and the complete batch preview, then obtain confirmation before calling `confirm_pedagogical_batch` once with the same items and returned `previewHash`. Report each outcome, including partial failures. Retrying an item must reuse its idempotency key; never automatically replay only failed items without a new preview and confirmation. The standalone skill works without a portal connection.
