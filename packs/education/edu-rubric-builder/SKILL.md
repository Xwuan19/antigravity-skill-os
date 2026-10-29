---
name: edu-rubric-builder
description: "Builds analytic or single-point rubrics with clear criteria, observable performance levels, and student-friendly language. Use when a teacher asks for a rubric, scoring guide, grading criteria, checklist, or success criteria for a project, essay, lab report, or presentation."
license: MIT
---

# Rubric builder

Build a rubric that two teachers would score the same way.

## Ask first

1. Grade, subject, and the task students will do. Get the task prompt if one exists.
2. The objectives the task assesses.
3. Rubric type: analytic (a score per criterion), single-point (one column of criteria with space for "below" and "above"), or holistic (one overall score). Default to analytic.
4. Number of levels and points. Default to 4 levels with no middle level, so a scorer has to decide.

## Build it

1. Pick 3 to 6 criteria. Each criterion maps to an objective. Don't score things the task didn't teach, such as neatness, unless the teacher asks.
2. Write the top level first as what proficient or advanced work does. Then write each lower level by changing quality, not by adding "not" or "some".
3. Describe what you can see in the work: "cites two pieces of evidence and explains how each supports the claim", not "good use of evidence".
4. Keep each cell to one or two sentences.
5. Weight criteria only if the teacher wants it. Show the weights.

## Student version

Write a short student version in "I" statements at the grade's reading level. Students use it to self-assess before they turn work in.

## Check it

Read the rubric against one imagined strong, middle, and weak piece of work. If any of them could fit two levels of a criterion, rewrite that row.

## Output

The rubric as a Markdown table, then the student checklist, then a line on total points and how they convert to the teacher's grading scale if given.

## Guardrails

- Standards: use only the codes the teacher gives you. If there are none, write `[standard: ask teacher]`. Never invent a code or quote standard text from memory.
- Privacy: work without student names or identifying details. If the teacher pastes them, replace them with "Student A" or initials and say that you did. Ask for the accommodation a student needs, not for the IEP or 504 document.
- Age and safety: fit reading level, content, and examples to the grade. Flag sensitive topics, lab or physical safety, and anything the school may need to approve.
- Accuracy: work every answer key yourself. Mark any fact you are not sure of with `[verify]`.
- The teacher decides: you draft. Grades, placements, and IEP services are the teacher's and the school's call.
