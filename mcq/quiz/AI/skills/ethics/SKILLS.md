# Ethics Skill

## Purpose
Use this skill for CFA Ethics question generation and CFA Ethics question repair work.

## Scope
- Applies to ethics question writing, rewriting, review, and cleanup.
- Applies when the topic comes from the Ethics source text in `PDF/Ethics/`.
- Use it for any ethics standard the prompt specifies.

## Source Of Truth
- The source of truth must be explicitly provided in the prompt.
- Use only the source text in `PDF/Ethics/` specified in the prompt.
- Do not introduce concepts, duties, exceptions, examples, or terminology not stated or directly implied by the source text.
- When referring to the source in generated JSON, call it the `CFA Curriculum`, not the PDF.

## Standard Selection
- The topic must be explicitly provided in the prompt.
- The user prompt determines the governing ethics standard or topic.
- The user prompt also determines the source-of-truth file.
- Do not assume `Standard IV` unless the prompt says so.
- Do not assume `PDF/Ethics/standard_04_duties_to_employers.txt` unless the prompt says so.
- If the prompt names a standard and a source file, treat those as authoritative for the task.
- If the prompt does not explicitly provide both the topic and the source-of-truth file, do not proceed.

## JSON Handling
- Never overwrite an existing topic JSON file unless the user explicitly asks for replacement.
- If the destination file exists, read and validate the current JSON array first.
- Continue IDs from the current last `id`.
- Write the final file as one valid JSON array containing old and new objects.
- Validate JSON after writing.

Recommended checks:
```bash
ls -lah "Target File.json"
jq empty "Target File.json"
jq 'length, .[-1].id' "Target File.json"
```

## Ethics Option Design Rules
- Do not make the correct answer mechanically guessable from surface wording.
- Do not use a pattern where the correct option is the only one labeled `Violation` or `Not a violation`.
- Avoid blunt giveaway phrasing such as `always`, `never`, `categorically`, `strictly liable`, `per se`, or similar absolutes unless the source text itself truly requires that exact rigidity.
- Make wrong answers fail for a narrow, plausible CFA-style reason, not because they are obviously extreme.
- For compliant outcomes, make the correct option look suspicious first and then hinge the conclusion on the narrow exception, timing rule, boundary, or disclosure condition recognized by the source text.
- For violation outcomes, make distractors look plausible by using nearby but incorrect boundaries, missing steps, wrong timing, overbroad consent requirements, or mistaken confidentiality logic.

## Ethics Drafting Heuristics
- Prefer scenarios where the compliant answer looks risky on first read.
- Build distractors from realistic candidate mistakes:
  - confusing preparation with competition
  - confusing notification with consent
  - overreading confidentiality
  - inventing cooling-off periods
  - treating supervision as strict liability
  - assuming interim restrictions are improper before proof
  - demanding extra approvals the standard does not require
- Adjust the mistake patterns to the actual standard named in the prompt rather than reusing Standard IV-specific logic where it does not fit.
- Keep all options close in tone and length where practical.
- Avoid making one option stand out through noticeably different wording structure.

## Output Expectations
- Return only a JSON array when generating question content.
- Preserve the user-requested schema exactly.
- Keep explanations aligned with the curriculum rule that actually resolves the question.

## Maintenance Use
When repairing existing ethics JSON files:
- Check stems, options, and explanations against the source text.
- Rewrite options if the answer can be guessed from formatting or asymmetry rather than ethics reasoning.
- Preserve IDs unless the user explicitly asks for renumbering or regeneration.
