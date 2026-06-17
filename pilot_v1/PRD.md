# PRD: Task Quality Score for Kaggle Benchmarks

**Status:** Draft
**Author:** Nicholas Kang
**Audience:** Kaggle Benchmarks product & engineering
**Last updated:** 2026-06-17

---

## Background

Kaggle Benchmarks hosts **~11,000 tasks**, of which **~56% are public**. Today we have
**no signal for task quality**. That creates three concrete problems:

1. **No way to filter for good tasks.** A user (or we, internally) browsing the catalog
   cannot tell a carefully-built evaluation apart from a throwaway one. Quality is only
   discoverable by opening each task and reading its code and description.
2. **Meta-analysis and downstream sharing are manual.** When we want to do meta-analysis
   across tasks, or hand a curated slice to the **Gemini research team**, today the only
   option is to review tasks one by one. At 11k tasks this does not scale.
3. **Slop accumulates with no defense.** Tasks are created continuously. Without a quality
   signal to sort against, low-quality tasks dilute the catalog over time and the good
   tasks get buried. There is no mechanism to push quality up and slop down.

We need an automated, per-task quality signal that is cheap to compute, easy to explain,
and good enough to **separate clearly low-quality tasks from higher-quality ones at scale.**

## Goals

* **Filter out slop.** Produce a quality score that reliably separates very low-quality
  tasks from higher-quality ones. The bar is *differentiation*, not *ranking the best*.
* **A 0-10 score**, modeled on Kaggle's existing **Dataset Usability Score**. The
  framing is identical: a 10 means the task **meets basic hygiene requirements** for a
  good task — not that it is elite.
* **Make tasks sortable and filterable** by quality, both for end users on Kaggle and for
  internal/downstream curation (e.g. assembling a candidate set to share with Gemini).
* **Cheap and automatic** enough to run across the full catalog and to recompute as tasks
  change.

### Non-goals

* **Not a measure of "best."** A 10 does **not** mean a task is good enough for a Gemini
  eval set. That decision requires human judgment, domain expertise, and checks this score
  does not perform.
* **No contamination / data-leakage detection.** Out of scope.
* **No novelty or research-value judgment.** We measure construction quality, not whether
  the idea is original or important.
* **Not a substitute for human review** on the high end. The score is a floor (hygiene),
  not a ceiling (excellence).

> **Mental model:** like the Dataset Usability Score — a 10/10 says "this clears the
> basic hygiene bar," and tasks scoring low are safe to deprioritize or hide. The middle
> and top of the range still need a human to make the final call.

## Product surface

* **Quality Score (0-10) displayed on the task page.** A single, prominent number,
  consistent with the look and behavior of the Dataset Usability Score users already know.
* The score should be **expandable into its component breakdown** (the 5 criteria below)
  so a task author can see *why* they scored what they did and what to improve.

## How we will use it

1. **On the task page** — surface the score so authors and viewers immediately see a
   task's hygiene level, and authors get actionable feedback to improve.
2. **Sort & filter** — let users sort/filter the catalog by quality, and let us produce
   curated, quality-thresholded slices to share with downstream teams (e.g. the Gemini
   research team) without manual per-task review.

## Proposed rubric

Feedback on the prior **v4 rubric** (10 criteria, weighted categories) was that it is
**too complex**. This PRD collapses it to **5 criteria**, each scored **0-2 points**,
summing to a **0-10** total. Equal weighting keeps the score trivial to explain and to
display as a component breakdown.

| # | Criterion | Source artifact | Points | Rating method |
| :-: | :-- | :-- | :-: | :-- |
| 1 | Answer correctness & construct validity | Notebook + Task page | 0-2 | LLM auto-rater |
| 2 | Problem statement | Task page | 0-2 | LLM auto-rater |
| 3 | Documentation | Task page + Notebook | 0-2 | LLM auto-rater |
| 4 | Model coverage | Task page (model runs API) | 0-2 | Deterministic |
| 5 | Discrimination | Model runs / results | 0/2 | Deterministic (binary) |
| | **Total** | | **0-10** | |

---

### Criterion 1: Answer correctness & construct validity (0-2)

*Does the task have a verifiable ground truth, and does it actually measure a model on the
capability it claims?* This is the heart of the score — a task that scores a model on its
own hardcoded data, or whose evaluation is disconnected from its stated purpose, is not a
real evaluation regardless of how polished the rest is.

* **Level 0 (0 pts):** No verifiable ground truth, **or** the evaluation does not measure
  a model at all (it asserts on hardcoded values / the task's own data structures), **or**
  there is a clear mismatch between what the task page claims and what the code measures.
* **Level 1 (1 pt):** Ground truth exists and a model is genuinely evaluated, but with
  moderate confounds — fragile verification (e.g. exact match without normalization) or an
  implementation that partially conflates the target capability with unrelated skills
  (formatting, instruction-following).
* **Level 2 (2 pts):** Answers are unambiguous and verifiable (exact/regex/tolerance/
  deterministic assertions, or a multi-dimensional LLM-judge rubric), **and** the
  implementation is tightly aligned with the claimed capability, with confounds minimized
  by deliberate design.

### Criterion 2: Problem statement (0-2)

*Does the task page clearly articulate which capability is targeted and why it matters?*
Judged **on the task-page prose only** — code quality does not count here.

* **Level 0 (0 pts):** No problem statement, or so unclear a reader cannot tell what the
  task measures or why it exists.
* **Level 1 (1 pt):** Names the target capability and gives basic motivation, but does not
  connect it to a broader question or explain the gap it fills.
* **Level 2 (2 pts):** A specific, compelling problem statement that names the exact
  capability, explains why it matters, and identifies the gap it fills relative to existing
  evaluations.

### Criterion 3: Documentation (0-2)

*Are the dataset, methodology, and scoring documented well enough to understand and
reproduce the task?* Consult **both** the task page and the notebook markdown.

* **Level 0 (0 pts):** No documentation of dataset provenance, evaluation protocol, or
  scoring. A reader must reverse-engineer the code.
* **Level 1 (1 pt):** Partial — some key areas covered (e.g. dataset source or method) but
  missing details like schema, scoring edge cases, or metric interpretation.
* **Level 2 (2 pts):** Comprehensive across both artifacts: dataset provenance/schema,
  evaluation methodology and scoring rules, metric definitions, and a step-by-step
  walkthrough in notebook markdown.

### Criterion 4: Model coverage (0-2)

*How many distinct models has the task actually been run against?* Scored
**deterministically** from the model-runs leaderboard on the task page (Kaggle Benchmarks
API), **not** from model names mentioned in the notebook.

* **Level 0 (0 pts):** Run on ≤ 1 model — no cross-model comparison possible.
* **Level 1 (1 pt):** Run on 2-3 distinct models — limited comparative signal.
* **Level 2 (2 pts):** Run on ≥ 4 distinct models — broad cross-model comparison.

### Criterion 5: Discrimination (0/2)

*Do the task's results actually separate models — i.e. not every model passes (or fails)?*
A task on which every model scores ~100% (or ~0%) carries no signal. This is a **binary
check** with no middle level.

* **Fail (0 pts):** Scores are effectively undifferentiated across models — all near the
  ceiling or all near the floor (within a small epsilon), so the task does not separate
  strong from weak models.
* **Pass (2 pts):** There is meaningful separation in model scores — at least one model
  clearly outperforms another beyond the epsilon threshold.

> **Note (open question):** because discrimination requires multiple model runs to be
> meaningful, it interacts with Criterion 4. A task run on ≤1 model cannot be assessed for
> discrimination — we need to decide whether that case scores 0 or is treated as N/A.
> The exact epsilon / separation threshold also needs to be set empirically.

## How the score is computed (brief)

The score combines two kinds of checks, run per task:

* **Deterministic checks** (Criteria 4 and 5) read structured data from the **Kaggle
  Benchmarks API** — the per-task model-runs leaderboard (`model_runs.json`) for distinct
  completed-model count, and the model result scores for the discrimination separation
  check. No LLM involved.
* **LLM auto-rater checks** (Criteria 1-3) read the task's two artifacts — the **task-page
  prose** (title/description/problem statement) and the **notebook code + markdown** — and
  assign a level per criterion against the anchors above. Criterion 1 requires comparing
  the two artifacts (claim vs. implementation); Criteria 2 and 3 are scoped to the
  artifact(s) named above.

**Inputs per task:** task-page prose, notebook source (code + markdown), and the model-runs
/ results data from the API.

**Recompute cadence:** the score should be recomputed when a task's notebook or description
changes, and when new model runs complete (which can change Criteria 4 and 5). Exact
trigger/cadence is a design-doc detail.

> A separate technical design doc will cover the rater prompts, the deterministic
> thresholds, output-stripping handling, and the recompute pipeline.

## Open questions

1. **Discrimination vs. coverage interaction** — how to score discrimination when a task
   has too few model runs to assess separation (0 vs. N/A); and what epsilon defines
   "meaningful separation."
2. **Weighting** — Criterion 1 (correctness & construct validity) is the substantive core
   of quality but carries the same 2 points as the others under equal weighting. Do we
   accept that for simplicity, or give it more weight / make it a gate?
3. **Surface details** — how the score and its breakdown render on the task page, and
   whether low scores are hidden vs. shown with improvement guidance.
4. **Backfill** — order and cost of scoring the existing ~11k tasks.
