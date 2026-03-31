## CFA Question Generator — Building-Block Edition

### Objective
Generate CFA-style MCQs for “{TOPIC}” as a JSON array. Each question must test exactly one primitive building-block concept and be solvable from first principles with minimal cognitive load.

### Source of Truth (MANDATORY)
- Source PDFs are located in the `PDF/` folder.
- The PDF is the only source.
- Do not introduce any concept, term, assumption, example, or extension not explicitly present or directly implied in the PDF.
- Coverage must strictly adhere to {TOPIC} as defined in the PDF.

### Quantity
- Generate {COUNT} questions.
- All questions must be intentionally very easy.

### Output Rule
- Return **ONLY** a JSON array. No additional text.

### Schema (exact)
```json
{
  "id": "int (1..n)",
  "model": "Grok|ChatGPT|Gemini",
  "topic": "PDF-based subtopic",
  "stem": "30–220 chars ending with ? or :",
  "options": {"A": "...", "B": "...", "C": "..."},
  "correct_answer": "A|B|C",
  "explanation": "string"
}
````

### Explanation Format (exact 4 blocks)

```html
<h3>First Principles Thinking: core idea</h3>
<p><strong>X is correct.</strong> Define the primitive as in PDF → governing rule/relation → intuition → PDF condition → apply → conclude.</p>
<p>Why top distractor is wrong (PDF-based misconception).</p>
<p>Why remaining distractor is wrong.</p>
```

### Content Rules

* Difficulty: 100% very easy; one question = one building block.
* Numerics only if present in PDF; must be mental-math friendly.
* Distractors must reflect realistic beginner errors from the PDF.
* Use CFA-style phrasing: “most likely”, “least likely”, “most accurate”, etc.
* Exactly one correct answer.
* Math must use LaTeX inside `$...$` if needed.
* Currency must be written as USD/EUR (never `$`).
* No jargon beyond PDF.
* No double negatives.
* Avoid copying phrasing verbatim; use original wording.

### Validation

* Array length = {COUNT}.
* IDs must be sequential: 1..n.
* Options must be exactly A, B, C with unique values.
* `correct_answer` must be one of A/B/C.
* Each stem must end with `?` or `:`.
* Explanations must follow the exact 4-block structure.
* Strict adherence to PDF is mandatory.

---

## Enumeration / Counting Format (Difficult)

### Objective

Generate CFA-style multiple-choice questions for “{TOPIC}” using the enumeration–counting format (list of items → ask “how many satisfy a condition?”). Questions must test conceptual precision and classification, not calculation.

### Source of Truth (MANDATORY)

* Source PDFs are located in the `PDF/` folder.
* The PDF is the only source.
* Every listed item, condition, and conclusion must be explicitly stated or directly implied in the PDF.
* Do not introduce external knowledge.

### Quantity

* Generate {COUNT} questions.
* All questions must be conceptually difficult, relying on subtle definitions, classifications, or boundary cases in the PDF.

### Output Rule

* Return ONLY a JSON array.

### Schema (exact)

```json
{
  "id": "int (1..n)",
  "topic": "PDF-based subtopic",
  "stem": "string",
  "options": {"A": "...", "B": "...", "C": "..."},
  "correct_answer": "A|B|C",
  "explanation": "string"
}
```

### Stem Rules

* Begin with “Consider the following:”
* List items using Roman numerals (I, II, III, IV if needed).
* Ask a counting question such as “How many of the above…?”, “Which of the above…?”, or “How many satisfy…?”.
* Use CFA-style neutral phrasing.

### Options (exactly three)

* A. Only one
* B. Only two
* C. All the three

### Explanation Format (exact 4 blocks)

```html
<h3>First Principles Thinking: classification rule</h3>
<p><strong>X is correct.</strong> State the defining criterion from the PDF → evaluate each item against the criterion → count qualifying items → conclude.</p>
<p>Why option B is incorrect.</p>
<p>Why option C is incorrect.</p>
```

### Rules

* No numerics unless explicitly required by the PDF.
* No “none” option.
* Language must mirror CFA exam tone.
* If math is needed, use LaTeX inside `$…$`.
* Currency must be written as USD/EUR, never using the dollar symbol.

### Validation

* IDs 1..n.
* Exactly three options.
* Counting-based options only.
* Roman numeral listing present in every stem.
* Exact explanation structure followed.
* Strict adherence to PDF is mandatory.


## Assertion–Reason (A–R) Format

### Objective
For a given {TOPIC} and attached PDF content, generate CFA-style assertion–reason (A–R) questions that test conceptual understanding through causality, mechanism, and boundary conditions.

### Source of Truth (MANDATORY)
- Source PDFs are located in the `PDF/` folder.
- The PDF is the only source.
- Do not introduce any concept, term, assumption, example, or extension not explicitly present or directly implied in the PDF.

### Quantity
- Generate {COUNT} questions.

### Output Rule
- Return ONLY a JSON array.
- The JSON schema must exactly match the structure in `Hedge Funds.json`.

### Format (strict)
For each question:
```

Assertion (A): …
Reason (R): …
Options:
(A) Both A and R are true and R is the correct explanation of A
(B) Both A and R are true but R is not the correct explanation of A
(C) A is true but R is false
(D) A is false but R is true

```

### Content Rules
- Uniformly distribute correct answers across options A, B, C, D (no clustering).
- Questions must be conceptually difficult, not memory-based.
- Assertions and reasons must each be individually plausible, even when incorrect.
- Avoid obvious giveaways such as absolute terms unless used deliberately as traps.
- Focus on causality, mechanism, or definitional boundaries rather than surface facts.
- Do not reveal answers within the question text.
- Avoid citations entirely.

### Validation
- Exact schema match with `Hedge Funds.json`.
- Uniform answer distribution across A, B, C, D.
- Each question follows the strict A–R format.
- Strict adherence to PDF content is mandatory.

