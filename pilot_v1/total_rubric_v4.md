# Kaggle Task Quality Framework: Total Rubric (v4)

This document defines the complete evaluation rubric for the Kaggle Task Quality Framework.

> **v4 changes (from the v2 line):**
> 1. **Empirical Discrimination (Criterion 10)**: Replaced the static "Model Coverage" count check with an empirical calculation based on actual model score spread (max - min performance delta) across reference models.
> 2. **Contamination Resistance (Criterion 11)**: Added a new criterion to Category C evaluating whether evaluation prompts/items are novel or leaked in public training corpora.
> 3. **Category C Scoring**: To keep the total score out of 10.0 points maximum, the 4 criteria in Category C contribute Level × 0.375 (yielding 0.0, 0.375, or 0.75 points each). Category C max subtotal remains 3.0 points (30%).

All evaluations are conducted at the **individual task level**. The two primary input artifacts are:

*   **Task Page**: The public-facing task description on Kaggle (title, description, problem statement)
*   **Task Notebook**: The associated task notebook code (evaluation logic, prompts, data loading, metrics)

Each criterion below specifies which artifact(s) it evaluates: 📄 Task Page, 📓 Notebook, or both.

---

## Summary of Criteria

The framework consists of **11 criteria** organized into **3 categories** inspired by the AGI Hackathon evaluation structure.

### Scoring Mechanics
*   **Standardized Scale**: Each criterion is scored on a **0-2 level scale** (Level 0, Level 1, or Level 2).
*   **Score Calculation**: 
    *   **Category A** (5 criteria): Level × 0.5 (yielding 0.0, 0.5, or 1.0 points). Max: **5.0 points (50%)**
    *   **Category B** (2 criteria): Level × 0.5 (yielding 0.0, 0.5, or 1.0 points). Max: **2.0 points (20%)**
    *   **Category C** (4 criteria): Level × 0.375 (yielding 0.0, 0.375, or 0.75 points). Max: **3.0 points (30%)**
*   **Total Score**: Sum of all 11 criterion scores (Maximum: **10.0 points**)

| Cat | # | Criterion | Evaluates | Level 0 | Level 1 | Level 2 | Rating Method |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **A** | 1 | Answer Correctness | 📓 | 0.0 | 0.5 | 1.0 | LLM Auto-rater |
| **A** | 2 | Construct Validity | 📄📓 | 0.0 | 0.5 | 1.0 | LLM Auto-rater |
| **A** | 3 | Code Quality | 📓 | 0.0 | 0.5 | 1.0 | LLM Auto-rater |
| **A** | 4 | Sample Size Adequacy | 📓 | 0.0 | 0.5 | 1.0 | Deterministic |
| **A** | 5 | Metric Design | 📓 | 0.0 | 0.5 | 1.0 | Hybrid |
| | | *Category A Subtotal* | | *0.0* | *2.5* | *5.0 (50%)* | |
| **B** | 6 | Problem Statement & Motivation | 📄 | 0.0 | 0.5 | 1.0 | LLM Auto-rater |
| **B** | 7 | Technical Documentation | 📄📓 | 0.0 | 0.5 | 1.0 | LLM Auto-rater |
| | | *Category B Subtotal* | | *0.0* | *1.0* | *2.0 (20%)* | |
| **C** | 8 | Capability Targeting | 📄📓 | 0.0 | 0.375 | 0.75 | LLM Auto-rater |
| **C** | 9 | Item Diversity Within Task | 📓 | 0.0 | 0.375 | 0.75 | LLM Auto-rater |
| **C** | 10 | Empirical Discrimination | 📓 | 0.0 | 0.375 | 0.75 | Deterministic |
| **C** | 11 | Contamination Resistance | 📄📓 | 0.0 | 0.375 | 0.75 | Hybrid |
| | | *Category C Subtotal* | | *0.0* | *1.5* | *3.0 (30%)* | |
| | | **Total Task Score** | | **0.0** | **5.0** | **10.0** | |

---

## Category A: Task Construction Quality (50%, 5.0 points max)

*Is the data defensible? Is the task built well?*

### Criterion 1: Answer Correctness (📓 Notebook)
*Are the task's expected answers unambiguous and verifiable from the notebook code?*

*   **Level 0 (0.0 points)**: Answers are subjective or open-ended with no verification logic, OR the assertion code contains critical flaws:
    *   *Trivial matching*: The grader code uses weak conditions that pass on empty strings (e.g., `assert output != ""`) or generic outputs.
    *   *Variable mismatches*: Prompt templates reference parameters/variables (e.g., `{{input}}`) that are not dynamically verified in the notebook assertion code.
*   **Level 1 (0.5 points)**: Ground truth exists, but the parser or assertion is fragile/gameable:
    *   *Exact matching on free text*: Using exact string equality checks on natural language responses without normalizing whitespace, casing, or punctuation.
    *   *Generic regex*: Using regex checks that accept trivially short or irrelevant answers.
    *   *Weak LLM rubric*: For LLM-as-a-judge, a rubric exists in the prompt but is vague, covers fewer than 3 dimensions, or lacks anchored scoring definitions.
*   **Level 2 (1.0 point)**: Grader logic is robust, un-gameable, and fully verifiable:
    *   *Normalized assertions*: Normalizes all output strings (stripping whitespace, normalizing case/special characters) or uses numerical tolerance for floating-points before asserting correctness.
    *   *Variable alignment*: Prompt variables and assertion comparisons are fully aligned and tested.
    *   *Anchored LLM rubric*: For LLM-as-a-judge, a comprehensive grading prompt is defined with at least 3 dimensions, explicit 0-5 score definitions, and anchored good/bad example pairs.


### Criterion 2: Construct Validity (📄 Task Page + 📓 Notebook)
*Is the task actually measuring what it claims to measure?*

This criterion checks whether the task's implementation (prompts, evaluation logic, item design) faithfully operationalizes the capability described on the task page. 

**The most severe construct-validity failure is an evaluation that does not measure a model at all.** Confirm the task's **primary/headline** evaluation is *designed* (readable from the code) to send prompts to a model and score that model's actual responses.

*   **Level 0 (0.0 points)**: Either (a) the primary evaluation does not measure a model at all — it asserts on hardcoded values, on the task's own Python data structures, or on the authors' pre-computed outputs rather than on a model's responses; or (b) there is a clear mismatch between what is claimed on the task page and what is implemented in the notebook.
*   **Level 1 (0.5 points)**: The task genuinely prompts and scores a model, but the evaluation design contains minor construct confounding factors (e.g., a reasoning task where failures are highly sensitive to superficial prompt formatting constraints, making it a format-following task rather than a reasoning task).
*   **Level 2 (1.0 point)**: The evaluation setup is clean and tightly aligned. No major construct confounders are present.

### Criterion 3: Code Quality (📓 Notebook)
*Is the notebook code modular, clean, and robust?*

*   **Level 0 (0.0 points)**: Code is fragile, copy-pasted, hard to read, or fails to run. No exception handling or formatting normalization.
*   **Level 1 (0.5 points)**: Code is functional and runs end-to-end, but has anti-patterns (shadowed names, massive single-cell execution) or lacks error-handling for API timeouts or malformed LLM responses.
*   **Level 2 (1.0 point)**: Code is modular, utilizes standard platform SDK decorators properly, implements custom classes/dataclasses, and robustly handles API failure rates or parse errors.

### Criterion 4: Sample Size Adequacy (📓 Notebook)
*Does the task evaluate models on a sufficient number of test items?*

*   **Level 0 (0.0 points)**: Fewer than 10 test items.
*   **Level 1 (0.5 points)**: Between 10 and 20 test items.
*   **Level 2 (1.0 point)**: More than 20 test items.

### Criterion 5: Metric Design (📓 Notebook)
*Are the metrics mathematically sound and well-suited?*

*   **Level 0 (0.0 points)**: No defined metric, or using arbitrary ad hoc penalization rules with no mathematical justification.
*   **Level 1 (0.5 points)**: Uses a standard metric (e.g., simple accuracy) but evaluates only a single dimension, without explaining justification or checking for bias.
*   **Level 2 (1.0 point)**: Uses non-trivial, multi-dimensional metrics (e.g., relative performance deltas, F1-scores, or human baselines) with clear documentation explaining the metric design.

---

## Category B: Task Description (20%, 2.0 points max)

*Is the task documentation clear and helpful?*

### Criterion 6: Problem Statement & Motivation (📄 Task Page)
*Is the problem statement clear and well-motivated?*

*   **Level 0 (0.0 points)**: No task page or description content is provided.
*   **Level 1 (0.5 points)**: Description provides basic clarity on what is measured, but offers no motivation explaining why it matters or what gap it fills.
*   **Level 2 (1.0 point)**: Clear problem statement with theoretical or practical motivation, clarifying why this benchmark is relevant to Measuring AGI.

### Criterion 7: Technical Documentation (📄 Task Page + 📓 Notebook)
*Are the dataset, evaluation methodology, and results documented clearly?*

*   **Level 0 (0.0 points)**: No documentation of dataset provenance, schemas, or protocols.
*   **Level 1 (0.5 points)**: Partial documentation (e.g., covers the dataset name but lacks schema/column definitions, scoring rules, or metric descriptions).
*   **Level 2 (1.0 point)**: Comprehensive documentation across both the task page and notebook covering schema, scoring rules, metric definitions, and step-by-step notebook markdown cells.

---

## Category C: Discriminative Power & Coverage (30%, 3.0 points max)

*Does the task produce an informative signal that separates strong from weak models?*

### Criterion 8: Capability Targeting (📄 Task Page + 📓 Notebook)
*Does the task probe a specific, well-defined capability with a clear hypothesis?*

*   **Level 0 (0.0 points)**: The task is unfocused, testing general knowledge, trivia, or a random grab-bag of skills.
*   **Level 1 (0.5 points)**: Targets a named capability (e.g., "reasoning") but lacks experimental controls (e.g., no paired congruent/incongruent tests).
*   **Level 2 (1.0 point)**: Targets a specific sub-capability with explicit control vs. perturbation conditions, allowing performance differences to be directly attributed to the target capability.

### Criterion 9: Item Diversity Within Task (📓 Notebook)
*Do the items span a structured range of sub-conditions or difficulty levels?*

*   **Level 0 (0.0 points)**: Items are homogeneous with no taxonomy, difficulty stratification, or category labels.
*   **Level 1 (0.5 points)**: Natural variation exists in items, but there is no structured taxonomy or difficulty tiers reported separately in code.
*   **Level 2 (1.0 point)**: Items are organized into a structured taxonomy with labeled sub-conditions or difficulty tiers, and evaluation code reports results broken down by these categories.

### Criterion 10: Empirical Discrimination (📓 Notebook)
*Does the task produce a performance spread across reference models that separates strong from weak models?*

*   **Level 0 (0.0 points)**: Weak or no capability separation (score spread between maximum and minimum performing reference models is < 10%), or the evaluation is completely broken (all models scoring 0%).
*   **Level 1 (0.5 points)**: Moderate capability separation (max-min score spread is between 10% and 30%).
*   **Level 2 (1.0 point)**: Strong capability separation (max-min score spread is >= 30%) across standard reference models.

### Criterion 11: Contamination Resistance (📄 Task Page + 📓 Notebook)
*Are the evaluation items novel and resistant to model memorization/contamination?*

*   **Level 0 (0.0 points)**: Prompts/items contain copy-pasted public corpus text, or exact matches are found in public web search results / known benchmark datasets, meaning models can solve the task by memorization.
*   **Level 1 (0.5 points)**: Prompts use public templates but with slight modifications/paraphrases, or moderate n-gram overlap is present.
*   **Level 2 (1.0 point)**: Highly novel scenarios, custom synthetic logic, or custom datasets with negligible public n-gram overlap, ensuring models must perform online reasoning.
