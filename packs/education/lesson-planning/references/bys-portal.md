# Optional guidance for BYS portal users

Use this guidance when the BYS MCP tools are available in the conversation, even if the teacher does not mention the portal. A lesson proposal is not evidence that a lesson was saved, approved, published, or taught. Do not claim any of those states without explicit evidence supplied by the teacher. This reference does not provide portal access or authority.

## Portal BYS (MCP)

Before proposing a lesson, run `get_lesson_design_context` for the class and `get_class_context` for its roster, current levels, active study plans, recent sessions, and tasks, then `get_course_design_student_context` for each learner you adapt for; cite each learner's level evidence or state what context was missing. `get_student_academic_context` deepens an individual learner. `get_student_proficiency` adds read-only proficiency history within the connection's scope. Treat attendance and prior study as unconfirmed unless the returned context states otherwise.

With `mcp:read`, `list_my_lesson_plan_drafts` discovers lesson-plan drafts created by the authenticated teacher, including migration drafts, so they can be resumed through any of that teacher's MCP connections. With `mcp:write`, `create_lesson_plan_draft`, `update_lesson_plan_draft`, and `create_migration_lesson_plan_draft` save or edit drafts. Updates require the current revision; migration drafts require certified historical selection and provenance. These tools do not approve or publish lesson plans. The standalone skill works without a portal connection.
