# Kaggle Task Quality Framework: Total Rubric (v4)

This document defines the complete evaluation rubric for the Kaggle Task Quality Framework.

> **v4 changes (from the v3 line):** This release is about **artifact discipline** — being
> explicit, for every criterion, about *which artifact the judge must inspect*: the **Task
> Page**, the **Notebook**, or **both**. v3 already tagged artifacts, but judges in practice
> collapsed everything into "the notebook." v4 makes the separation mandatory and operational.
> 1. **Criterion 2 (Construct Validity)** now *requires an explicit two-artifact comparison*:
>    read the capability the **Task Page** claims, read what the **Notebook** code actually
>    does, and judge the alignment between the two. A claim with no matching implementation —
>    or an implementation that measures something other than the claim — is the failure mode.
> 2. **Criterion 6 (Problem Statement)** is **Task-Page-only**. Judge the public-facing
>    description text *exclusively*. Do not let notebook quality, code, or results raise or
>    lower this score.
> 3. **Criterion 10 (Model Coverage)** now reads the **Task Page model runs** (the leaderboard
>    of models the task has actually been run against), **not** the notebook. It is scored
>    deterministically from the Kaggle Benchmarks API (`model_runs.json`), since the count of
>    distinct models is a property of the task page, not of the notebook code.
>
> The 10 criteria, their levels, and weights are otherwise unchanged from v3. As in v3, there
> is no validity gate and no score cap; the "does the eval measure a model?" check lives inside
> Criterion 2. This rubric measures **construction quality only** (is the task well-built, does
> it do what it claims, is it robust); it deliberately does **not** reward conceptual novelty.

## Input artifacts — read the right one for each criterion

All evaluations are conducted at the **individual task level**. There are two distinct input
artifacts, and **each criterion below states which one(s) it evaluates**. Treat them as
separate sources of evidence — do **not** merge them into one undifferentiated blob:

*   **📄 Task Page**: the public-facing task on Kaggle — its **title, description, and problem
    statement** (the prose a reader sees before opening any code), plus the **model runs /
    leaderboard** (which models have been run against the task).
    *   *Where to find it in the captured material*: the task-page title/description/problem
        statement are embedded as **markdown cells and docstrings inside the notebook source** —
        read those prose cells as "the Task Page," distinct from the code cells. The **model
        runs** are not in the notebook at all; they come from the Kaggle Benchmarks API and are
        provided to you as `experiment/model_runs.json` (see Criterion 10).
*   **📓 Notebook**: the task notebook **code** — evaluation logic, prompts, data loading,
    metric computation. This is the implementation, not the description.

**Artifact discipline (mandatory):**
*   For a **📄-only** criterion (6), score *only* from the task-page prose. Ignore code quality.
*   For a **📓-only** criterion (1, 3, 4, 5, 9), score *only* from the notebook code/data.
*   For a **📄📓** criterion (2, 7, 8), you must consult **both** and, where the criterion calls
    for it, **compare them against each other**.
*   For Criterion 10, use the **provided model-run data** (`model_runs.json`), not the notebook.

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
| **C** | 10 | Model Coverage | 📄 | 0.0 | 0.5 | 1.0 | Deterministic |
| | | *Category C Subtotal* | | *0.0* | *1.5* | *3.0 (30%)* | |
| | | **Total Task Score** | | **0.0** | **5.0** | **10.0** | |

---

## Category A: Task Construction Quality (50%, 5.0 points max)

*Is the data defensible? Is the task built well?*

### Criterion 1: Answer Correctness (📓 Notebook)
*Are the task's expected answers unambiguous and verifiable from the notebook code?*

**Artifact:** Notebook code only. Judge the ground-truth definition and verification logic.

*   **Level 0 (0.0 points)**: Answers are subjective, open-ended, or unverifiable from the task notebook. No ground truth is defined in code. If using LLM-as-a-judge, no scoring rubric is specified.
    *   *Example*: "Rate the creativity of the model's story" with no evaluation criteria defined in code.
*   **Level 1 (0.5 points)**: Ground truth exists for most items, but edge cases are unhandled or verification logic is fragile (e.g., exact string match without normalization). For LLM-as-a-judge, a rubric exists in the prompt but is vague or covers fewer than 3 dimensions.
    *   *Example*: A coding task where most test cases are well-defined, but some accept multiple valid solutions without specifying acceptance criteria.
*   **Level 2 (1.0 point)**: All answers are unambiguous and fully verifiable — using exact match, regex, numerical tolerance, or deterministic assertion logic in the task code. For LLM-as-a-judge, a comprehensive multi-dimensional rubric is defined in code with anchored examples for each score level.
    *   *Example*: A math task with exact numerical answers and assertion checks, or an LLM-judged task with a 4-dimension rubric specifying 0-5 scales with concrete anchored examples per level.

### Criterion 2: Construct Validity (📄 Task Page + 📓 Notebook — compare the two)
*Does the notebook actually measure the capability the task page claims it measures?*

**Artifact discipline — this is an explicit two-step comparison:**
1.  **Read the 📄 Task Page claim.** From the task-page prose (title/description/problem
    statement, found in the notebook's markdown cells), state in your own words *what capability
    the task says it measures*.
2.  **Read the 📓 Notebook implementation.** From the code (prompts, item design, evaluation
    logic), determine *what the task actually measures*.
3.  **Judge the alignment between (1) and (2).** Low construct validity = a gap between the
    stated claim and the implemented measurement. A task that claims "inhibitory control" but
    whose failures are driven by confusing prompt formatting is misaligned. A task that
    intentionally uses ambiguous prompts to measure "ambiguity tolerance" is aligned — the
    implementation matches the claim. If the task page makes a claim the notebook never
    operationalizes (or vice versa), that mismatch is the defect this criterion catches.

**The most severe construct-validity failure is an evaluation that does not measure a model at all.** Before assessing alignment, confirm the task's **primary/headline** evaluation is *designed* (readable from the code) to send prompts to a model and score that model's actual responses. Judge the primary eval — a peripheral notebook that calls a model does not redeem a headline eval that asserts on its own data, and a broken auxiliary notebook does not condemn a soundly-designed headline eval. When making this judgment, **do NOT penalize our-side or environmental artifacts**: stripped/truncated outputs ("no output" is expected — we strip outputs), version pins, failed installs, missing packages, and quota/API/auth errors are not construction defects. If the eval logic is imported from a captured dataset package (e.g. `from benchmark.tasks import run_...`), **trace into that package** before concluding a model isn't called — off-notebook logic is still the task's logic. Note that a self-asserting eval still prints run values, so the presence of a score is not evidence a model was measured.

*   **Level 0 (0.0 points)**: Either (a) the primary evaluation does not measure a model at all — it asserts on hardcoded values, on the task's own Python data structures, or on the authors' pre-computed outputs rather than on a model's responses; the scoring is structurally disconnected from any model output; or the design is fundamentally broken so no valid model score could ever be produced (e.g. an answer-format mismatch baked into the harness that yields 0/N by construction). OR (b) there is a clear mismatch between the task page's stated purpose and what the notebook code actually measures — model failures could plausibly be attributed to confounding factors (e.g., prompt formatting confusion, output parsing errors) rather than the claimed capability.
    *   *Example (a)*: A notebook that builds an internal Python dictionary/store and then asserts the store returns the expected value (e.g. "942/942 correct") — this tests the authors' own code, not the model.
    *   *Example (b)*: A task page that claims to measure "mathematical reasoning" but whose notebook uses a prompt so poorly formatted that failures are caused by the model misinterpreting what it's being asked, not by poor math ability.
*   **Level 1 (0.5 points)**: The notebook broadly measures the capability the task page claims, but the implementation introduces moderate confounds. The prompts, item design, or evaluation logic partially conflate the target capability with unrelated skills (e.g., instruction-following ability, output formatting compliance).
    *   *Example*: A "metacognition" task whose page promises metacognitive monitoring, but whose core evaluation is a knowledge question with a confidence rating appended — it measures knowledge more than metacognition, though there is some signal.
*   **Level 2 (1.0 point)**: The notebook implementation is tightly aligned with the task page's stated purpose. The prompts, item design, and evaluation logic are specifically designed to isolate the claimed capability. Confounding factors are minimized through deliberate design choices visible in the code (e.g., controlling for surface-level difficulty, using paired conditions).
    *   *Example*: A task whose page claims "inhibitory control" and whose notebook uses congruent/incongruent trial pairs where the only difference is the presence of a prepotent distractor — ensuring performance differences reflect inhibition specifically.

### Criterion 3: Code Quality (📓 Notebook)
*Is the task notebook code clean, robust, and maintainable?*

**Artifact:** Notebook code only.

*   **Level 0 (0.0 points)**: Code is broken, undocumented, or relies on hardcoded values. **Assign Level 0 if no code or notebook exists for the task.**
    *   *Example*: No task notebook is provided, or the notebook only contains hardcoded model outputs with no evaluation logic.
*   **Level 1 (0.5 points)**: Code is functional and produces results, but is poorly organized. Comments are sparse, error handling is minimal, and the implementation has rough edges (e.g., no input validation, no graceful handling of malformed model outputs).
    *   *Example*: A notebook that runs 250 prompts in a loop without resetting conversation history, risking context overflow, or one that uses bare `except` blocks.
*   **Level 2 (1.0 point)**: Clean, modular, well-commented code. Uses the `kaggle-benchmarks` SDK idiomatically (e.g., `@task` decorators, `evaluate()` over datasets, fresh context per item). Includes robust output parsing with fallback strategies and handles edge cases gracefully.
    *   *Example*: A notebook using `evaluate()` to iterate over a DataFrame, normalizing LLM outputs before comparison, including fallback JSON parsing, and logging warnings for unparseable responses.

### Criterion 4: Sample Size Adequacy (📓 Notebook)
*Does the task have enough evaluation items for reliable conclusions?*

**Artifact:** Notebook/data only — count the evaluation items.

*   **Level 0 (0.0 points)**: The task contains 1-9 evaluation items. Too few to draw any meaningful conclusions about model performance.
    *   *Example*: A task with 3 hand-crafted scenarios — a single lucky or unlucky response can swing the score dramatically.
*   **Level 1 (0.5 points)**: The task contains 10-20 evaluation items. Enough to detect large performance differences between models, but limited granularity.
    *   *Example*: A task with 15 reasoning questions — sufficient to see that Model A scores ~80% and Model B scores ~40%, but not enough for fine-grained analysis.
*   **Level 2 (1.0 point)**: The task contains more than 20 evaluation items, providing sufficient coverage for meaningful model comparisons.
    *   *Example*: A task evaluating 50 items across multiple sub-conditions, enabling per-condition analysis and more reliable aggregate scores.

### Criterion 5: Metric Design (📓 Notebook)
*Are the metrics computed in the notebook diverse, appropriate for the task, and robust?*

**Artifact:** Notebook code only.

*   **Level 0 (0.0 points)**: Only a single metric is computed (e.g., only Accuracy), with no justification. Or the chosen metric is clearly inappropriate for the task type.
    *   *Example*: Using Exact Match for a creative writing evaluation, or computing only Accuracy with no explanation.
*   **Level 1 (0.5 points)**: Multiple metrics are computed, but they all measure the same underlying dimension (e.g., Accuracy, Precision, Recall, and F1 all measure correctness). Standard metrics are used with minimal justification.
    *   *Example*: A notebook computing Accuracy and F1 on a classification task with a comment "we use standard metrics" but no discussion of limitations.
*   **Level 2 (1.0 point)**: The notebook computes at least two distinct performance dimensions (e.g., Accuracy and Calibration, or Accuracy and Latency). The metric choice is justified in markdown, and for LLM-judges, the notebook documents and mitigates known biases (e.g., position bias, length bias).
    *   *Example*: A notebook computing both accuracy and confidence calibration (Brier score), with markdown explaining why calibration matters, and code that randomizes option order to mitigate position bias.

---

## Category B: Task Description Quality (20%, 2.0 points max)

*Can the community use and learn from this task?*

### Criterion 6: Problem Statement & Motivation (📄 Task Page ONLY)
*Does the task page clearly articulate which capability is being targeted and why it matters?*

**Artifact discipline — Task Page ONLY.** Judge **exclusively** the public-facing description
prose (the task-page title/description/problem statement, found in the notebook's markdown
cells). **Do not inspect the code, and do not let notebook quality, metric design, or results
influence this score.** A task with beautiful code but a one-line description scores low here;
a task with messy code but a compelling, specific problem statement scores high. You are rating
the *writing on the page*, nothing else.

*   **Level 0 (0.0 points)**: No problem statement, or a completely unclear description. A reader cannot understand what the task measures or why it exists.
    *   *Example*: A task titled "Benchmark Task 7" with a one-line description like "Tests LLM capabilities."
*   **Level 1 (0.5 points)**: The task page names the target capability and provides basic motivation, but does not connect it to a broader research question or explain the gap it fills.
    *   *Example*: "This task tests Theory of Mind by asking models to predict what characters believe" — clear, but no motivation for why this matters or what existing benchmarks miss.
*   **Level 2 (1.0 point)**: The task page presents a compelling, specific problem statement that names the exact capability, explains why it matters for understanding model behavior, and identifies what gap this task fills relative to existing evaluations.
    *   *Example*: "This task isolates L2 false-belief tracking — the ability to reason about what Agent A believes about Agent B's beliefs. Existing ToM benchmarks (e.g., BigToM) test only L1 beliefs. We target L2 because it's the level where frontier models begin to fail, making it a useful discriminator."

### Criterion 7: Technical Documentation (📄 Task Page + 📓 Notebook)
*Are the dataset, evaluation methodology, and results documented clearly enough for reproduction?*

**Artifact discipline:** consult **both** — the task-page prose for high-level methodology/dataset
description, and the notebook markdown for code-level walkthrough. Level 2 requires documentation
quality across *both* artifacts.

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

**Artifact discipline:** consult **both** — the task page for the stated hypothesis/capability,
and the notebook for whether the item design (controls, conditions) actually isolates it.

*   **Level 0 (0.0 points)**: The task is unfocused — it tests general knowledge, trivia, or a grab-bag of skills. It is unclear what succeeding or failing reveals about a model.
    *   *Example*: A task that mixes math, coding, and language questions with no unifying capability being measured.
*   **Level 1 (0.5 points)**: The task targets a named capability domain (e.g., "reasoning," "metacognition") but does not isolate a specific sub-capability. The task design does not include experimental controls, so it's unclear whether performance reflects the stated capability or confounding factors.
    *   *Example*: A "social cognition" task that asks free-form empathy questions — it targets the right domain, but doesn't isolate a specific mechanism like false-belief tracking vs. emotion recognition.
*   **Level 2 (1.0 point)**: The task probes a specific, well-defined sub-capability with a clear cognitive or technical hypothesis. The notebook includes experimental controls (e.g., control vs. perturbation conditions, difficulty gradients) that allow attributing performance differences to the target capability.
    *   *Example*: A Stroop-like task measuring "inhibitory control" where congruent trials serve as a baseline and incongruent trials measure interference, with the performance delta as the primary metric. The hypothesis is explicit: "Models that can suppress prepotent responses will show a smaller congruency effect."

### Criterion 9: Item Diversity Within Task (📓 Notebook)
*Do the task's evaluation items span a structured range of sub-conditions or difficulty levels that can reveal a gradient of model performance?*

**Artifact:** Notebook/data only — inspect item structure, labels, and per-condition reporting.

A task where every model scores 0% is as uninformative as one where every model scores 100%. This criterion rewards tasks whose item design enables a meaningful performance gradient.

*   **Level 0 (0.0 points)**: All evaluation items are homogeneous — same format, same difficulty, no internal categorization. The task cannot distinguish between models of different capability levels.
    *   *Example*: 100 multiple-choice questions all at the same difficulty level with no sub-category labels.
*   **Level 1 (0.5 points)**: Some natural variation exists in the items (e.g., different topics or surface-level differences), but there is no structured taxonomy, difficulty stratification, or sub-condition labeling in the code or data.
    *   *Example*: A reasoning task with questions about different domains (science, history), but no explicit difficulty tiers or controlled manipulation of item properties.
*   **Level 2 (1.0 point)**: The task explicitly organizes items into a structured taxonomy with labeled sub-conditions or difficulty tiers, and the evaluation code reports results broken down by these categories — enabling analysis of *where* models fail, not just *how often*.
    *   *Example*: A Theory of Mind task with items labeled by belief-depth (L0, L1, L2, L3) where the notebook computes and reports accuracy at each depth level separately. This reveals that GPT-4o handles L1 but fails at L3, while Gemini 2.5 Pro handles L2 — a meaningful performance gradient.

### Criterion 10: Model Coverage (📄 Task Page — model runs)
*How many distinct models has the task actually been run against?*

**Artifact discipline — Task Page model runs, NOT the notebook.** Model coverage is a property
of the **task page** (its leaderboard of completed model runs), not of the notebook code. Counting
model names mentioned in the notebook is **wrong** — a notebook can name many models it never ran,
or run many it never names. Score this criterion **deterministically** from the provided
`experiment/model_runs.json`, which is fetched from the Kaggle Benchmarks API and gives, per
benchmark, the count of **distinct models with a COMPLETED run** on the task page. Use the
`distinct_models_completed` value for the benchmark; do not infer this from the notebook.

*   **Level 0 (0.0 points)**: The task has been run on only 1 model (`distinct_models_completed` ≤ 1).
    *   *Example*: A task with completed results only from `gemini-2.5-pro` — no cross-model comparison is possible.
*   **Level 1 (0.5 points)**: The task has been run on 2-3 distinct models (`distinct_models_completed` is 2 or 3).
    *   *Example*: A task with completed results from `gemini-2.5-pro` and `gpt-4o` — some comparative signal, but limited coverage.
*   **Level 2 (1.0 point)**: The task has been run on 4 or more distinct models (`distinct_models_completed` ≥ 4), enabling broad cross-model comparison.
    *   *Example*: A task with completed results from `gemini-2.5-pro`, `gpt-4o`, `claude-sonnet-4`, and `llama-4-maverick` — providing a comprehensive performance landscape across providers and model sizes.
