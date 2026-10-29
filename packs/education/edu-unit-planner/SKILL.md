---
name: edu-unit-planner
description: "Plans a multi-week unit with backward design (Understanding by Design): desired results, assessment evidence, then a lesson-by-lesson sequence. Use when a teacher asks for a unit plan, a scope and sequence, a pacing guide, or wants to plan several lessons around one topic."
license: MIT
---

# Unit planner

Plan a unit backward: decide what students should understand, decide how you will know, then plan the lessons. This is Understanding by Design (Wiggins and McTighe).

## Ask first

1. Grade, subject, and topic.
2. Number of lessons and minutes per lesson.
3. Standards or curriculum goals, if any.
4. What students already know, and anything the class needs (many English learners, co-taught class, limited devices).

## Stage 1: desired results

1. Write 1 to 3 enduring understandings: big ideas worth remembering in five years, written as full sentences.
2. Write 2 to 4 essential questions: open questions with no single right answer that the unit returns to.
3. Write the unit objectives with the `edu-learning-objectives` skill.
4. List likely misconceptions. Plan to surface them early.

## Stage 2: assessment evidence

1. Describe one performance task that shows transfer: students apply the learning to a new, realistic situation. Use the GRASPS frame (goal, role, audience, situation, product, standards for success).
2. Plan the rubric for the task with the `edu-rubric-builder` skill.
3. List other evidence: quizzes, exit tickets, observations, and when each one happens.
4. Place a pre-assessment in lesson 1 and at least one formative check every lesson.

## Stage 3: learning plan

1. Write a table with one row per lesson: lesson number, objective, key activity, formative check, materials.
2. Order lessons so each one builds on the last. Put the performance task where students have what they need to do it.
3. Leave one flex lesson for every 8 to 10 lessons, for reteaching or catch-up.
4. Note where differentiation matters most and point to the `edu-differentiation` skill.

## Output

The three stages in order, then the lesson table. Keep it to what a teacher can read in five minutes. Offer to expand any lesson with the `edu-lesson-planner` skill.

## Guardrails

- Standards: use only the codes the teacher gives you. If there are none, write `[standard: ask teacher]`. Never invent a code or quote standard text from memory.
- Privacy: work without student names or identifying details. If the teacher pastes them, replace them with "Student A" or initials and say that you did. Ask for the accommodation a student needs, not for the IEP or 504 document.
- Age and safety: fit reading level, content, and examples to the grade. Flag sensitive topics, lab or physical safety, and anything the school may need to approve.
- Accuracy: work every answer key yourself. Mark any fact you are not sure of with `[verify]`.
- The teacher decides: you draft. Grades, placements, and IEP services are the teacher's and the school's call.
