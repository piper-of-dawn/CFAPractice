# PDF and JSON Workflow for CFA Question Tasks

## Purpose

Use this workflow when generating CFA-style MCQs from curriculum PDFs in this repository.

The goal is to:

1. read only the relevant curriculum text from `PDF/`,
2. generate questions strictly from that source,
3. append them to the correct JSON file without overwriting existing questions,
4. validate the final JSON array against `AGENTS.md`.

## Source of Truth

- The only content source is the curriculum PDF in [`PDF`](/home/karma/CFAPractice/mcq/quiz/AI/PDF).
- Do not introduce concepts, examples, assumptions, or terminology not explicitly stated or directly implied by the curriculum.
- In generated JSON, refer to the source as the `CFA Curriculum`, never as the PDF.

## File Discovery

Start by locating:

- the relevant PDF in [`PDF`](/home/karma/CFAPractice/mcq/quiz/AI/PDF),
- any existing extracted text files such as [`module6_source.txt`](/home/karma/CFAPractice/mcq/quiz/AI/module6_source.txt),
- the destination JSON file for the topic.

Preferred commands:

```bash
rg --files
ls -lah PDF
ls -lah "Target File.json"
```

## PDF Parsing

### Preferred approach

If a reliable local text extraction already exists, use it first. This is faster and keeps the workflow deterministic.

Examples:

- [`module6_source.txt`](/home/karma/CFAPractice/mcq/quiz/AI/module6_source.txt)
- [`module9_raw.txt`](/home/karma/CFAPractice/mcq/quiz/AI/module9_raw.txt)

Use targeted search and partial reads instead of loading the whole document:

```bash
rg -n "Module 6|Yield-to-Maturity|Flat Price|Accrued Interest" module6_source.txt
sed -n '8350,9800p' module6_source.txt
```

### If no extracted text exists

Create a plain-text extraction from the PDF, then search within that extracted text. Keep the extraction local and reusable for later runs.

The extraction should preserve:

- module headings,
- learning outcomes,
- examples,
- knowledge checks,
- practice problem solutions when they clarify definitions or boundary conditions.

### Reading strategy

Do not read the full PDF blindly. Narrow to:

1. the named topic or module,
2. the exact subsection used for the requested question type,
3. the nearby examples or solutions needed to confirm interpretation.

For example, for bond valuation:

- `Bond Pricing with a Market Discount Rate`
- `Yield-to-Maturity`
- `Flat Price, Accrued Interest, and the Full Price`
- `Relationships between Bond Prices and Bond Features`

## JSON Reading

Destination files must contain only a JSON array.

Before writing:

1. check whether the file exists,
2. if it exists, parse it,
3. determine the last used `id`,
4. append new objects to the existing array,
5. never overwrite unless explicitly asked.

Useful checks:

```bash
ls -lah "Target File.json"
jq empty "Target File.json"
jq 'length, .[-1].id' "Target File.json"
```

If the file does not exist, create a new JSON array with sequential IDs starting at `1`.

## Append Rules

When appending:

- preserve the existing array structure,
- continue IDs sequentially,
- keep the schema exactly as required by [`AGENTS.md`](/home/karma/CFAPractice/mcq/quiz/AI/AGENTS.md),
- do not alter unrelated existing questions.

If adding 5 questions to an existing file whose last ID is `12`, the new IDs must be `13` to `17`.

## Question Construction Constraints

Always read the relevant section in [`AGENTS.md`](/home/karma/CFAPractice/mcq/quiz/AI/AGENTS.md) before generation because the required schema and explanation format differ by question type.

Common required checks:

- exact question count,
- sequential IDs,
- exact option keys,
- exact explanation structure,
- topic tied to the curriculum section,
- no external knowledge,
- no extra text outside the JSON array.

For Assertion–Reason tasks specifically:

- use the strict `Assertion (A): ...` and `Reason (R): ...` format inside `stem`,
- use the four standard answer options,
- keep assertions and reasons plausible on their own,
- distribute correct answers across `A`, `B`, `C`, `D`,
- focus on mechanism, causality, or definitional boundaries from the curriculum.

## Validation

After writing:

```bash
jq empty "Target File.json"
jq 'length' "Target File.json"
```

Then spot-check:

- first and last IDs,
- `correct_answer` distribution if required,
- whether explanations follow the exact HTML block structure,
- whether the file contains only the array and no commentary.

## Safe Working Pattern

Use this sequence:

1. locate PDF and any local extraction,
2. locate the destination JSON file,
3. read only the relevant curriculum subsection,
4. draft questions from that subsection only,
5. append to the JSON array,
6. validate with `jq`,
7. stop if schema, IDs, or source fidelity is uncertain.

## Practical Notes

- Prefer `rg` over slower search tools.
- Prefer targeted `sed -n` ranges over full-file reads.
- Use `jq` for JSON validation whenever available.
- Keep terminology aligned with the curriculum.
- If a fact cannot be traced to the curriculum text, do not use it.
