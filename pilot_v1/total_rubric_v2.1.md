# Kaggle Task Quality Framework: Total Rubric (v2.1)

This document defines the complete evaluation rubric for the Kaggle Task Quality Framework.

> **v2.1 changes (from v2):**
> 1. **Validity Gate reworked.** It now judges the eval's **design** (readable from the
>    code) rather than its run-state, judges only the **primary/headline** evaluation
>    rather than "any notebook", and explicitly **excludes our-side artifacts** (stripped
>    outputs, version pins, install/quota failures, logic imported from a dataset package).
>    On failure it applies a **soft cap of 4.0** instead of the old hard 2.0 cap.
> 2. **Category C relabeled** from "Novelty & Discriminatory Power" to "Discriminative
>    Power & Coverage" — the criteria measure measurement informativeness, not novelty.
>
> All 10 criteria, their levels, and weights are otherwise unchanged. This rubric measures
> **construction quality only** (is the task well-built, does it do what it claims, is it
> robust); it deliberately does **not** reward conceptual novelty.

All evaluations are conducted at the **individual task level**. The two primary input artifacts are:

*   **Task Page**: The public-facing task description on Kaggle (title, description, problem statement)
*   **Task Notebook**: The associated task notebook code (evaluation logic, prompts, data loading, metrics)

Each criterion below specifies which artifact(s) it evaluates: 📄 Task Page, 📓 Notebook, or both.

---

## Summary of Criteria

The framework consists of **10 criteria** organized into **3 categories** inspired by the AGI Hackathon evaluation structure.

### Scoring Mechanics
*   **Standardized Scale**: Each criterion is scored on a **0-2 level scale** (Level 0, Level 1, or Level 2)
*   **Score Calculation**: Each criterion contributes equally within its category. The score for each criterion is: Level × 0.5 (yielding 0.0, 0.5, or 1.0 points)
*   **Category weights are built into the distribution**: 5 criteria in Category A (50%), 2 in Category B (20%), 3 in Category C (30%)
*   **Total Score**: Sum of all 10 criterion scores (Maximum: **10.0 points**)

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
| **C** | 8 | Capability Targeting | 📄📓 | 0.0 | 0.5 | 1.0 | LLM Auto-rater |
| **C** | 9 | Item Diversity Within Task | 📓 | 0.0 | 0.5 | 1.0 | LLM Auto-rater |
| **C** | 10 | Model Coverage | 📓 | 0.0 | 0.5 | 1.0 | Deterministic |
| | | *Category C Subtotal* | | *0.0* | *1.5* | *3.0 (30%)* | |
| | | **Total Task Score** | | **0.0** | **5.0** | **10.0** | |

---

## Validity Gate (overriding rule — apply BEFORE scoring the 10 criteria)

*Is the task's PRIMARY evaluation DESIGNED to measure a model's responses?*

A task certifies construction quality only if its **primary/headline** evaluation is
designed to send prompts to a language model and score that model's responses. This gate
is about evaluation **design**, which you read from the code — NOT about whether the
captured run happened to execute, and NOT about whether outputs are present.

> **Judge the PRIMARY eval only.** If a task has several notebooks, identify the one that
> produces its headline result and judge that. A peripheral notebook that happens to call
> a model does NOT rescue a task whose main evaluation asserts on its own data; and a
> broken auxiliary notebook does NOT sink a task whose main evaluation is soundly designed.

**The task FAILS the gate only if the PRIMARY evaluation's LOGIC does not measure a model**
— i.e. any of the following, judged from the code:

*   The model is never called — the eval asserts on hardcoded values, on the task's own
    Python data structures, or on the authors' pre-computed/handwritten outputs rather
    than on a model's responses.
    *   *Example*: a notebook that builds an internal Python dictionary/store and then
        asserts the store returns the expected value (e.g. "942/942 correct") — this
        tests the authors' own code, not the model. Note that such a self-test still
        prints run values; the presence of a score is NOT evidence the gate passes.
*   The scoring is structurally disconnected from any model output (the metric is computed
    over fixed/synthetic data that no model produced).
*   The primary evaluation's design is fundamentally broken so that no valid model score
    could ever be produced (e.g. an answer-format mismatch baked into the harness that
    yields 0/N for all items by construction, not by a runtime fluke).

**Do NOT fail the gate for our-side or environmental artifacts.** The following are NOT
construction defects and must be EXCLUDED from the gate decision:

*   **Stripped or truncated source/outputs.** We strip notebook outputs; "no output on the
    run cell" is expected and is NOT evidence the model wasn't called.
*   **Environment/dependency failures** — version pins, failed `pip install`, missing
    packages, import errors caused by the captured environment.
*   **Quota / API / auth errors** at run time.
*   **Logic imported from a provided dataset package.** If the notebook imports its eval
    from a captured dataset (e.g. `from benchmark.tasks import run_...`), TRACE INTO that
    package before concluding a model isn't called. Off-notebook logic is still the task's
    logic.

**Consequence of failing the gate:**

*   Assign **Criterion 1 (Answer Correctness) = Level 0** and **Criterion 2 (Construct
    Validity) = Level 0**.
*   **Cap the TOTAL task score at 4.0** (a soft cap), regardless of the levels earned on
    the other criteria. A task whose primary evaluation does not measure a model cannot be
    high quality no matter how clean its code, documentation, or dataset are; the soft cap
    keeps it low without nuking a possibly-misjudged task to the floor.

**The task PASSES the gate** (score all 10 criteria normally, no cap) if its primary
evaluation is designed to prompt a model and score the model's actual responses — even if
that evaluation is imperfect. Ordinary weaknesses (a single metric, a noisy ground-truth
source, modest accuracy) do NOT trip the gate. When in doubt — and the primary eval is
clearly designed to call and score a model — PASS the gate and let the regular criteria
capture the weaknesses.

---

## Category A: Task Construction Quality (50%, 5.0 points max)

*Is the data defensible? Is the task built well?*

### Criterion 1: Answer Correctness (📓 Notebook)
*Are the task's expected answers unambiguous and verifiable from the notebook code?*

*   **Level 0 (0.0 points)**: Answers are subjective, open-ended, or unverifiable from the task notebook. No ground truth is defined in code. If using LLM-as-a-judge, no scoring rubric is specified.
    *   *Example*: "Rate the creativity of the model's story" with no evaluation criteria defined in code.
*   **Level 1 (0.5 points)**: Ground truth exists for most items, but edge cases are unhandled or verification logic is fragile (e.g., exact string match without normalization). For LLM-as-a-judge, a rubric exists in the prompt but is vague or covers fewer than 3 dimensions.
    *   *Example*: A coding task where most test cases are well-defined, but some accept multiple valid solutions without specifying acceptance criteria.
*   **Level 2 (1.0 point)**: All answers are unambiguous and fully verifiable — using exact match, regex, numerical tolerance, or deterministic assertion logic in the task code. For LLM-as-a-judge, a comprehensive multi-dimensional rubric is defined in code with anchored examples for each score level.
    *   *Example*: A math task with exact numerical answers and assertion checks, or an LLM-judged task with a 4-dimension rubric specifying 0-5 scales with concrete anchored examples per level.

### Criterion 2: Construct Validity (📄 Task Page + 📓 Notebook)
*Is the task actually measuring what it claims to measure?*

This criterion checks whether the task's implementation (prompts, evaluation logic, item design) faithfully operationalizes the capability described on the task page. A task that claims to measure "inhibitory control" but whose failures are caused by confusing prompt formatting has low construct validity. Conversely, a task that intentionally uses ambiguous prompts to measure "ambiguity tolerance" has high construct validity — because the implementation matches the claim.

*   **Level 0 (0.0 points)**: There is a clear mismatch between the task's stated purpose and what the notebook code actually measures. Model failures on this task could plausibly be attributed to confounding factors (e.g., prompt formatting confusion, output parsing errors) rather than the claimed capability.
    *   *Example*: A task that claims to measure "mathematical reasoning" but uses a prompt so poorly formatted that failures are caused by the model misinterpreting what it's being asked, not by poor math ability.
*   **Level 1 (0.5 points)**: The task broadly measures the claimed capability, but the implementation introduces moderate confounds. The prompts, item design, or evaluation logic partially conflate the target capability with unrelated skills (e.g., instruction-following ability, output formatting compliance).
    *   *Example*: A "metacognition" task where the core evaluation is a knowledge question with a confidence rating appended — it measures knowledge more than metacognitive monitoring, but there is some signal.
*   **Level 2 (1.0 point)**: The task's implementation is tightly aligned with its stated purpose. The prompts, item design, and evaluation logic are specifically designed to isolate the claimed capability. Confounding factors are minimized through deliberate design choices visible in the code (e.g., controlling for surface-level difficulty, using paired conditions).
    *   *Example*: A task claiming to measure "inhibitory control" that uses congruent/incongruent trial pairs where the only difference is the presence of a prepotent distractor — ensuring that performance differences reflect inhibition specifically.

### Criterion 3: Code Quality (📓 Notebook)
*Is the task notebook code clean, robust, and maintainable?*

*   **Level 0 (0.0 points)**: Code is broken, undocumented, or relies on hardcoded values. **Assign Level 0 if no code or notebook exists for the task.**
    *   *Example*: No task notebook is provided, or the notebook only contains hardcoded model outputs with no evaluation logic.
*   **Level 1 (0.5 points)**: Code is functional and produces results, but is poorly organized. Comments are sparse, error handling is minimal, and the implementation has rough edges (e.g., no input validation, no graceful handling of malformed model outputs).
    *   *Example*: A notebook that runs 250 prompts in a loop without resetting conversation history, risking context overflow, or one that uses bare `except` blocks.
*   **Level 2 (1.0 point)**: Clean, modular, well-commented code. Uses the `kaggle-benchmarks` SDK idiomatically (e.g., `@task` decorators, `evaluate()` over datasets, fresh context per item). Includes robust output parsing with fallback strategies and handles edge cases gracefully.
    *   *Example*: A notebook using `evaluate()` to iterate over a DataFrame, normalizing LLM outputs before comparison, including fallback JSON parsing, and logging warnings for unparseable responses.

### Criterion 4: Sample Size Adequacy (📓 Notebook)
*Does the task have enough evaluation items for reliable conclusions?*

*   **Level 0 (0.0 points)**: The task contains 1-9 evaluation items. Too few to draw any meaningful conclusions about model performance.
    *   *Example*: A task with 3 hand-crafted scenarios — a single lucky or unlucky response can swing the score dramatically.
*   **Level 1 (0.5 points)**: The task contains 10-20 evaluation items. Enough to detect large performance differences between models, but limited granularity.
    *   *Example*: A task with 15 reasoning questions — sufficient to see that Model A scores ~80% and Model B scores ~40%, but not enough for fine-grained analysis.
*   **Level 2 (1.0 point)**: The task contains more than 20 evaluation items, providing sufficient coverage for meaningful model comparisons.
    *   *Example*: A task evaluating 50 items across multiple sub-conditions, enabling per-condition analysis and more reliable aggregate scores.

### Criterion 5: Metric Design (📓 Notebook)
*Are the metrics computed in the notebook diverse, appropriate for the task, and robust?*

*   **Level 0 (0.0 points)**: Only a single metric is computed (e.g., only Accuracy), with no justification. Or the chosen metric is clearly inappropriate for the task type.
    *   *Example*: Using Exact Match for a creative writing evaluation, or computing only Accuracy with no explanation.
*   **Level 1 (0.5 points)**: Multiple metrics are computed, but they all measure the same underlying dimension (e.g., Accuracy, Precision, Recall, and F1 all measure correctness). Standard metrics are used with minimal justification.
    *   *Example*: A notebook computing Accuracy and F1 on a classification task with a comment "we use standard metrics" but no discussion of limitations.
*   **Level 2 (1.0 point)**: The notebook computes at least two distinct performance dimensions (e.g., Accuracy and Calibration, or Accuracy and Latency). The metric choice is justified in markdown, and for LLM-judges, the notebook documents and mitigates known biases (e.g., position bias, length bias).
    *   *Example*: A notebook computing both accuracy and confidence calibration (Brier score), with markdown explaining why calibration matters, and code that randomizes option order to mitigate position bias.

---

## Category B: Task Description Quality (20%, 2.0 points max)

*Can the community use and learn from this task?*

### Criterion 6: Problem Statement & Motivation (📄 Task Page)
*Does the task page clearly articulate which capability is being targeted and why it matters?*

*   **Level 0 (0.0 points)**: No problem statement, or a completely unclear description. A reader cannot understand what the task measures or why it exists.
    *   *Example*: A task titled "Benchmark Task 7" with a one-line description like "Tests LLM capabilities."
*   **Level 1 (0.5 points)**: The task page names the target capability and provides basic motivation, but does not connect it to a broader research question or explain the gap it fills.
    *   *Example*: "This task tests Theory of Mind by asking models to predict what characters believe" — clear, but no motivation for why this matters or what existing benchmarks miss.
*   **Level 2 (1.0 point)**: The task page presents a compelling, specific problem statement that names the exact capability, explains why it matters for understanding model behavior, and identifies what gap this task fills relative to existing evaluations.
    *   *Example*: "This task isolates L2 false-belief tracking — the ability to reason about what Agent A believes about Agent B's beliefs. Existing ToM benchmarks (e.g., BigToM) test only L1 beliefs. We target L2 because it's the level where frontier models begin to fail, making it a useful discriminator."

### Criterion 7: Technical Documentation (📄 Task Page + 📓 Notebook)
*Are the dataset, evaluation methodology, and results documented clearly enough for reproduction?*

*   **Level 0 (0.0 points)**: No documentation of the dataset provenance, evaluation protocol, or scoring methodology. A reader cannot reproduce or understand the evaluation without reverse-engineering the code.
    *   *Example*: A notebook with only code cells, no markdown, and a task page with no technical details.
*   **Level 1 (0.5 points)**: Partial documentation covering some but not all key areas. The dataset source or evaluation method is described, but details like column schemas, scoring edge cases, or metric interpretation are missing.
    *   *Example*: The task page says "We use the GoEmotions dataset" and the notebook has a brief markdown header, but there is no description of which columns are used, how ground truth was derived, or how edge cases are handled.
*   **Level 2 (1.0 point)**: Comprehensive documentation across both the task page and notebook covering: dataset provenance and schema, evaluation methodology and scoring rules, metric definitions and interpretation, and step-by-step code walkthrough in notebook markdown cells.
    *   *Example*: The task page describes the dataset construction process and column definitions. The notebook includes markdown sections for "Dataset Loading," "Evaluation Logic," and "Metric Calculation," each with 2-3 sentences explaining the approach and design choices.

---

## Category C: Discriminative Power & Coverage (30%, 3.0 points max)

*Does the task produce an informative signal that separates strong from weak models?*

### Criterion 8: Capability Targeting (📄 Task Page + 📓 Notebook)
*Does the task probe a specific, well-defined capability with a clear hypothesis about what it reveals?*

*   **Level 0 (0.0 points)**: The task is unfocused — it tests general knowledge, trivia, or a grab-bag of skills. It is unclear what succeeding or failing reveals about a model.
    *   *Example*: A task that mixes math, coding, and language questions with no unifying capability being measured.
*   **Level 1 (0.5 points)**: The task targets a named capability domain (e.g., "reasoning," "metacognition") but does not isolate a specific sub-capability. The task design does not include experimental controls, so it's unclear whether performance reflects the stated capability or confounding factors.
    *   *Example*: A "social cognition" task that asks free-form empathy questions — it targets the right domain, but doesn't isolate a specific mechanism like false-belief tracking vs. emotion recognition.
*   **Level 2 (1.0 point)**: The task probes a specific, well-defined sub-capability with a clear cognitive or technical hypothesis. The notebook includes experimental controls (e.g., control vs. perturbation conditions, difficulty gradients) that allow attributing performance differences to the target capability.
    *   *Example*: A Stroop-like task measuring "inhibitory control" where congruent trials serve as a baseline and incongruent trials measure interference, with the performance delta as the primary metric. The hypothesis is explicit: "Models that can suppress prepotent responses will show a smaller congruency effect."

### Criterion 9: Item Diversity Within Task (📓 Notebook)
*Do the task's evaluation items span a structured range of sub-conditions or difficulty levels that can reveal a gradient of model performance?*

A task where every model scores 0% is as uninformative as one where every model scores 100%. This criterion rewards tasks whose item design enables a meaningful performance gradient.

*   **Level 0 (0.0 points)**: All evaluation items are homogeneous — same format, same difficulty, no internal categorization. The task cannot distinguish between models of different capability levels.
    *   *Example*: 100 multiple-choice questions all at the same difficulty level with no sub-category labels.
*   **Level 1 (0.5 points)**: Some natural variation exists in the items (e.g., different topics or surface-level differences), but there is no structured taxonomy, difficulty stratification, or sub-condition labeling in the code or data.
    *   *Example*: A reasoning task with questions about different domains (science, history), but no explicit difficulty tiers or controlled manipulation of item properties.
*   **Level 2 (1.0 point)**: The task explicitly organizes items into a structured taxonomy with labeled sub-conditions or difficulty tiers, and the evaluation code reports results broken down by these categories — enabling analysis of *where* models fail, not just *how often*.
    *   *Example*: A Theory of Mind task with items labeled by belief-depth (L0, L1, L2, L3) where the notebook computes and reports accuracy at each depth level separately. This reveals that GPT-4o handles L1 but fails at L3, while Gemini 2.5 Pro handles L2 — a meaningful performance gradient.

### Criterion 10: Model Coverage (📓 Notebook)
*How many distinct models has the task been run against?*

*   **Level 0 (0.0 points)**: The task has been run on only 1 model.
    *   *Example*: A task with results only from `gemini-2.5-pro` — no cross-model comparison is possible.
*   **Level 1 (0.5 points)**: The task has been run on 2-3 distinct models.
    *   *Example*: A task with results from `gemini-2.5-pro` and `gpt-4o` — some comparative signal, but limited coverage.
*   **Level 2 (1.0 point)**: The task has been run on 4 or more distinct models, enabling broad cross-model comparison.
    *   *Example*: A task with results from `gemini-2.5-pro`, `gpt-4o`, `claude-sonnet-4`, and `llama-4-maverick` — providing a comprehensive performance landscape across providers and model sizes.
