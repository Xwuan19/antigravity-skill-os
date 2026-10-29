# BYS portal syllabus rule

In the BYS portal, profiles and syllabuses are always individual. When a teacher asks for one syllabus for a class, propose one syllabus per learner and ask for the individual information needed to tailor them. Use only information the teacher supplied; mark missing learner context and do not invent needs, levels, or progress. Treat each syllabus as a proposal. Do not say one was saved, approved, or published without explicit evidence from the teacher. This reference provides no portal access or authority.

## Portal BYS (MCP)

When the BYS MCP tools are available in the conversation, run `get_course_design_student_context` for each learner before planning, and `get_lesson_design_context` first when the request concerns a class; `get_student_academic_context` only complements that context. `search_students`, `get_student_proficiency`, `list_pending_course_imports`, and `get_course_import_text` can supply further learner or source context within the connection's scope. `list_my_classes` and `list_class_students` can help identify a class roster. The read tools `observe_course_design_bundle_authority`, `observe_course_design_verification_state`, and `observe_lesson_verification_state` expose only their authorized, sanitized verification projections.

With a connection that has the `mcp:write` scope, `save_pedagogical_profile_draft`, `create_syllabus_draft`, `update_syllabus_draft`, and `apply_course_design_draft_bundle` can save individual drafts. The bundle creates a profile and syllabus draft atomically and uses the supplied idempotency keys for safe retries. These tools never approve or publish. Use only the returned context needed for the proposal. The standalone skill works without a portal connection.
