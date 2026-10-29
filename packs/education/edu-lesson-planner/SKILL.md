---
name: edu-lesson-planner
description: "Writes a single lesson plan with objective, timing, gradual release (I do, we do, you do), checks for understanding, and differentiation notes. Use when a teacher asks for a lesson plan, a daily plan, a mini-lesson, or a substitute plan."
license: MIT
---

# Lesson planner

Write one lesson a teacher can run tomorrow.

## Ask first

1. Grade, subject, topic, and lesson length in minutes.
2. Where the lesson sits: first lesson on the topic, middle, or review.
3. Standards or objectives, if the teacher has them. Otherwise write them with the `edu-learning-objectives` skill.
4. Materials and constraints: devices, lab access, class size, a substitute teaching it.

## Structure

Use these sections, with minutes for each. The minutes must add up to the lesson length.

1. **Objective and success criteria.** One to three objectives, shown to students in student language.
2. **Warm-up (3 to 7 minutes).** Activate prior knowledge or surface a misconception. Include the actual prompt.
3. **Direct instruction, "I do".** Model the skill. Write out the worked example and the think-aloud, not just "teacher models".
4. **Guided practice, "we do".** Two or three problems or prompts done together. Note the questions to ask and the likely wrong answers.
5. **Independent practice, "you do".** The task, with the actual items or a pointer to a worksheet from the `edu-worksheet-builder` skill.
6. **Check for understanding.** At least two during the lesson (cold call, whiteboards, thumbs, hinge question) and an exit ticket at the end. Write the questions. Use the `edu-formative-checks` skill for hinge questions and exit tickets.
7. **Closure.** Students state what they learned against the success criteria.
8. **Differentiation.** One support and one extension move, specific to this lesson. Use the `edu-differentiation` skill for more.
9. **Materials and prep.** A checklist.

## Rules

- Write what the teacher says and what students do, not "discuss the topic".
- For grades 3 and up, aim to keep teacher talk to about a third of the lesson, so students spend most of the time practicing.
- For a substitute plan, add where materials are, how to take attendance, and a no-tech fallback.

## Output

The plan in the order above, in Markdown with headings. Offer slides (`edu-slide-outline`), a worksheet, or an exit ticket next.

## Guardrails

- Standards: use only the codes the teacher gives you. If there are none, write `[standard: ask teacher]`. Never invent a code or quote standard text from memory.
- Privacy: work without student names or identifying details. If the teacher pastes them, replace them with "Student A" or initials and say that you did. Ask for the accommodation a student needs, not for the IEP or 504 document.
- Age and safety: fit reading level, content, and examples to the grade. Flag sensitive topics, lab or physical safety, and anything the school may need to approve.
- Accuracy: work every answer key yourself. Mark any fact you are not sure of with `[verify]`.
- The teacher decides: you draft. Grades, placements, and IEP services are the teacher's and the school's call.
