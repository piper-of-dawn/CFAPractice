# CFA Question Generator — Building-Block Edition

### Objective
Generate CFA-style MCQs for “{TOPIC}” as a JSON array. Each question must test exactly one primitive building-block concept and be solvable from first principles with minimal cognitive load. The numericals must be as easy so that they can be solved in head. You can keep few questions confusing.

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
- When writing to an existing topic file, always append new questions to the existing JSON array. Never overwrite existing questions unless the user explicitly asks for replacement.
- In generated JSON content, never refer to the source as the “PDF.” Refer to it as the “CFA Curriculum.”

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
* Always include a space after the currency code, for example `USD 30` and `EUR 30`.
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

# Enumeration / Counting Format (Difficult)

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
* When writing to an existing topic file, always append new questions to the existing JSON array. Never overwrite existing questions unless the user explicitly asks for replacement.
* In generated JSON content, never refer to the source as the “PDF.” Refer to it as the “CFA Curriculum.”

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
* Always include a space after the currency code, for example `USD 30` and `EUR 30`.

### Validation

* IDs 1..n.
* Exactly three options.
* Counting-based options only.
* Roman numeral listing present in every stem.
* Exact explanation structure followed.
* Strict adherence to PDF is mandatory.


# Assertion–Reason (A–R) Format

### Objective
For a given {TOPIC} and attached PDF content, generate CFA-style assertion–reason (A–R) questions that test conceptual understanding through causality, mechanism, and boundary conditions.

### Source of Truth (MANDATORY)
- Source PDFs are located in the `PDF/` folder.
- The PDF is the only source.
- Do not introduce any concept, term, assumption, example, or extension not explicitly present or directly implied in the PDF.

### Quantity
- Generate {COUNT} questions.

### Format (strict)
For each question:
```
Assertion (A): …
Reason (R): …
```

### Output Rule

* Return ONLY a JSON array.
* When writing to an existing topic file, always append new questions to the existing JSON array. Never overwrite existing questions unless the user explicitly asks for replacement.
* In generated JSON content, never refer to the source as the “PDF.” Refer to it as the “CFA Curriculum.”

### Schema (exact)

```json
{
  "id": "int (1..n)",
  "topic": "PDF-based subtopic",
  "stem": "string",
  "options": {"A": "Both A and R are true and R is the correct explanation of A", "B": "Both A and R are true but R is not the correct explanation of A
", "C": "A is true but R is false", "D": "A is false but R is true"},
  "correct_answer": "A|B|C",
  "explanation": "string"
}
```

### Content Rules
- Uniformly distribute correct answers across options A, B, C, D (no clustering).
- Questions must be conceptually difficult, not memory-based.
- Assertions and reasons must each be individually plausible, even when incorrect.
- Avoid obvious giveaways such as absolute terms unless used deliberately as traps.
- Focus on causality, mechanism, or definitional boundaries rather than surface facts.
- Do not reveal answers within the question text.
- Avoid citations entirely.
- Always include a space after the currency code, for example `USD 30` and `EUR 30`.

### Validation
- Exact schema match with `Hedge Funds.json`.
- Uniform answer distribution across A, B, C, D.
- Each question follows the strict A–R format.
- Strict adherence to PDF content is mandatory.

---
# Numerical Questions

### Objective
Generate CFA-style numerical MCQs for “{TOPIC}” using a **solver-first architecture**. All answers must be computed via deterministic backend solvers to ensure numerical accuracy.

### Source of Truth (MANDATORY)
- Source PDFs are located in the `PDF/` folder.
- The PDF is the only source.
- Use only formulas, conventions, and definitions explicitly present or directly implied in the PDF.
- Do not introduce external finance assumptions.

### 1. Backend Solvers (MANDATORY FIRST)
- Implement solver functions for each numerical concept in the PDF.
- Each solver must:
  - Take structured inputs (no free text).
  - Return:
    - `final_answer`
    - `intermediate_steps`
    - `units`
    - `rounded_answer`
    - `validation_checks`
- Use exact formulas as defined in the PDF.
- No approximation unless explicitly allowed in the PDF.

### 2. Precision Rules
- Avoid floating-point drift:
  - Use `Decimal` or equivalent precise arithmetic.
- Centralize rounding rules:
  - Match PDF conventions (e.g., decimal places, compounding).
- Ensure deterministic outputs (same input → same result).

### 3. Validation Layer
- Validate:
  - Input domains (e.g., rates ≥ 0 if required).
  - Formula selection correctness.
  - Unit consistency.
- Fail loudly on invalid inputs or ambiguity.

### Testing (MANDATORY BEFORE GENERATION)

- Write tests for every solver.
- Include:
  - Golden test cases from PDF examples.
  - Edge cases (boundary values).
  - Consistency checks (e.g., inverse relationships).
- No question generation allowed unless all solver tests pass.

### Question Generator (AFTER SOLVERS)

### Rules
- Generate questions only for numerical patterns explicitly in the PDF.
- Every answer must be computed via solver functions.
- Do NOT compute answers inside the generator.

### Distractors (MANDATORY)
Must come from realistic numerical mistakes:
- Sign errors
- Wrong compounding frequency
- Incorrect discounting direction
- Unit mismatch
- Premature rounding

### Currency Style
- Always include a space after the currency code, for example `USD 30` and `EUR 30`.

### Output Format

- Return ONLY a JSON array.
- When writing to an existing topic file, always append new questions to the existing JSON array. Never overwrite existing questions unless the user explicitly asks for replacement.
- In generated JSON content, never refer to the source as the “PDF.” Refer to it as the “CFA Curriculum.”

### Schema (exact)
```json
{
  "id": "int (1..n)",
  "topic": "PDF-based subtopic",
  "stem": "string ending with ?",
  "options": {"A": "...", "B": "...", "C": "..."},
  "correct_answer": "A|B|C",
  "explanation": "string"
}

# CFA Ethics Confusion-Driven and Hard Edition

### Objective
Generate **highly confusing CFA-style MCQs** for “{STANDARD}” using the PDFs in `PDF/`:
- `standards-practice-handbook-12th-edition.pdf`
- (Second PDF assumed present)

Questions must simulate **real ethical ambiguity**, not textbook recall. Focus on edge cases where multiple answers appear defensible.

---

### Source of Truth (MANDATORY)
- Use only content from PDFs in `PDF/`.
- All scenarios, logic, and traps must be grounded in examples or guidance from the Handbook :contentReference[oaicite:0]{index=0}
- Do not introduce external ethics frameworks.

---

## Core Design Principle

**Confusion = competing obligations + subtle hierarchy**

Every question must:
- Create tension between **two valid principles**
- Force candidate to identify **which one dominates**
- Exploit **“almost correct” reasoning**

---

## Question Construction Rules

### 1. Scenario Design
- Use realistic professional situations:
  - Client vs employer conflict
  - Law vs Code
  - Disclosure vs avoidance
  - Independence vs business pressure
- Add **irrelevant but tempting details**
- Avoid clean textbook setups

---

### 2. Trap Mechanisms (MANDATORY)

Each question must include at least one:

- **Hierarchy Trap**
  - Law vs Code (more strict rule)
- **Intent Trap**
  - “Knowingly” vs “should have known”
- **Disclosure Trap**
  - Disclosure sufficient vs must avoid
- **Materiality Trap**
  - What actually affects decision-making
- **Independence Trap**
  - Perception vs actual impairment
- **Omission Trap**
  - Missing fact changes conclusion

---

### 3. Options Design

- All 3 options must look correct at first glance
- Only one survives strict interpretation
- Use CFA phrasing:
  - “most appropriate”
  - “least likely”
  - “most accurate”

---

### 4. Explanation Format (MANDATORY)

```html
<h3>First Principles Thinking: governing standard</h3>
<p><strong>X is correct.</strong> Identify the governing standard → identify competing principle → resolve hierarchy → apply to facts → conclude.</p>
<p>Why top distractor is tempting but wrong (missed nuance).</p>
<p>Why remaining distractor fails (boundary violation).</p>
````

---

## Difficulty Definition

A question is valid only if:

* A strong candidate hesitates between 2 options
* Wrong answers are not obviously wrong
* The distinction depends on **one subtle clause** in the standard

---

## Content Constraints

* No direct copying of examples (must mutate scenarios)
* Must reflect ambiguity seen in Handbook examples 
* Avoid extreme/obvious violations
* Avoid purely definitional questions

---

## Output Format

Return ONLY a JSON array.

### Schema

```json
{
  "id": "int (1..n)",
  "topic": "{STANDARD}",
  "stem": "scenario-based question",
  "options": {"A": "...", "B": "...", "C": "..."},
  "correct_answer": "A|B|C",
  "explanation": "string"
}
```

---

### Validation

* Each question must contain:

  * At least one ethical conflict
  * At least one trap mechanism
* Options must be mutually exclusive but plausible
* Explanation must resolve ambiguity explicitly
* Strict adherence to PDF required


# CFA Ethics Questions Fundamental Katas Edition

### Objective
Generate **very easy, primitive, building-block ethics questions (“Katas”)** for “{STANDARD}”.  
Each question must isolate **one irreducible concept** and test it directly from first principles.

---

### Source of Truth (MANDATORY)
- Source PDFs are located in the `PDF/` folder.
- Use only concepts, definitions, and examples from the Handbook :contentReference[oaicite:0]{index=0}
- No external interpretation or extensions.

---

## Core Design Principle

**One question = one concept**

No ambiguity, no layering, no multi-step reasoning.

---

## Question Construction Rules

### 1. Concept Isolation
Each question must test exactly ONE of:
- definition (e.g., what counts as misrepresentation)
- boundary (allowed vs not allowed)
- hierarchy (law vs Code)
- obligation (must / must not / when required)

---

### 2. Scenario Design
- Use **minimal scenarios** (1–3 lines)
- Remove irrelevant details
- Make the violation (or compliance) hinge on a single fact

---

### 3. Difficulty Rules
- Must be immediately solvable if concept is known
- No traps, no ambiguity
- No competing principles

---

### 4. Options Design
- 3 options only
- One clearly correct, two clearly incorrect (but plausible beginner errors)
- Use CFA phrasing:
  - “most appropriate”
  - “least likely”

---

### 5. Explanation Format (MANDATORY)

```html
<h3>First Principles Thinking: core concept</h3>
<p><strong>X is correct.</strong> Define the concept → state rule → apply to fact → conclude.</p>
<p>Why first distractor is incorrect.</p>
<p>Why second distractor is incorrect.</p>
