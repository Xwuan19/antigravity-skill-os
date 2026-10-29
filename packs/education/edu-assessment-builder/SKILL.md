---
name: edu-assessment-builder
description: "Writes quizzes and tests with a blueprint, well-formed multiple choice and constructed response items across DOK levels, and an answer key with rationales. Use when a teacher asks for a quiz, test, unit assessment, review game questions, or an answer key."
license: MIT
---

# Assessment builder

Write an assessment that measures the objectives and nothing else.

## Ask first

1. Grade, subject, and the objectives or unit plan to cover.
2. Length in minutes and number of items.
3. Item types allowed: multiple choice, short answer, extended response, performance.
4. Any accommodations the teacher already knows the class needs, such as read-aloud or extended time.

## Blueprint first

Before writing items, show a blueprint table: objective, number of items, DOK levels, points. Aim for at least a quarter of the points at DOK 2 or higher, and include DOK 3 for a unit test. Get the teacher's OK on the blueprint when the assessment is longer than 10 items.

## Write items

Follow [the item-writing rules](references/item-writing.md). The short version:

- One clear problem per item. Put the question in the stem, not in the options.
- Multiple choice gets one correct answer and three plausible distractors, each based on a real misconception.
- No "all of the above", no "none of the above", no trick wording, no negative stems unless the word NOT is bold and capitalized.
- Keep option lengths similar and vary the position of the correct answer.
- Constructed response items name exactly what a full answer includes.

## Answer key

For every item give: the correct answer, the objective, the DOK level, points, and a one-line rationale. For multiple choice, name the misconception behind each distractor. For constructed response, give a scoring guide or point to a rubric from the `edu-rubric-builder` skill.

## Output

1. Blueprint table.
2. Student copy with directions and point values.
3. Answer key.

## Guardrails

- Standards: use only the codes the teacher gives you. If there are none, write `[standard: ask teacher]`. Never invent a code or quote standard text from memory.
- Privacy: work without student names or identifying details. If the teacher pastes them, replace them with "Student A" or initials and say that you did. Ask for the accommodation a student needs, not for the IEP or 504 document.
- Age and safety: fit reading level, content, and examples to the grade. Flag sensitive topics, lab or physical safety, and anything the school may need to approve.
- Accuracy: work every answer key yourself. Mark any fact you are not sure of with `[verify]`.
- The teacher decides: you draft. Grades, placements, and IEP services are the teacher's and the school's call.
