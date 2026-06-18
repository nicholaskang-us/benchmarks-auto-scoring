# Pilot v2 — 500-task rubric backtest

Efficacy test of the 5-criteria Task Quality rubric on **500 randomly sampled
public Kaggle Benchmark tasks** (reproducible sample; see `sample.sql`).

## What's here

- **`final_500_scores.csv`** — one row per task: name, task URL, notebook URL,
  the five criterion scores, total (0–10), the raw model-coverage stats, and a
  per-criterion notes column explaining each score.
- **`rubric.md`** — the anchors used by the LLM rater for criteria 1–3.
- **`sample.sql`** — the BigQuery query that drew the 500-task sample and
  computed the deterministic criteria 4 (model coverage) and 5 (discrimination).
- **`assemble.py`** — joins the LLM ratings (crit 1–3) with the deterministic
  scores (crit 4–5) into the final CSV.

## Method

- **Sample:** 500 public tasks (`IsPublic`, not removed, has a current version),
  drawn deterministically via `ORDER BY FARM_FINGERPRINT(CAST(Id AS STRING))`.
- **Criteria 1–3** (correctness/construct validity, problem statement,
  documentation): scored by an LLM rater against `rubric.md`, given each task's
  page prose, eval definition, and notebook source.
- **Criteria 4–5** (model coverage, discrimination): computed deterministically
  in SQL from completed leaderboard runs.
  - crit4: ≥4 distinct models → 2; 2–3 → 1; ≤1 → 0.
  - crit5: gap between best and worst model score > eps (0.05 on a 0–1 scale,
    5 on a 0–100 scale) → 2, else 0; ≤1 model → 0.

## Score distributions (n=500)

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| 1 — correctness / construct validity | 125 | 210 | 165 |
| 2 — problem statement (task page only) | 309 | 170 | 21 |
| 3 — documentation | 220 | 202 | 78 |
| 4 — model coverage | 359 | 3 | 138 |
| 5 — discrimination | 366 | — | 134 |

Mean total: **3.31 / 10**.

## Efficacy observations

1. **Criterion 2 is near-dead as written.** 309/500 tasks score 0, and only 21
   score 2 — because the rubric restricts crit2 to the *task page prose only*,
   and most authors put their problem statement in the notebook, not the task
   page. The criterion is measuring "did the author fill in the task-page
   description box," not "is there a problem statement." Recommend allowing the
   statement to count if present in *either* artifact.

2. **Criteria 4 and 5 are nearly redundant.** They agree (both >0 or both 0) on
   493/500 tasks; 359 tasks score 0 on both. They are both functions of run
   volume — a task only discriminates if multiple models ran it — so together
   they hand 4 of the 10 points to "has this task been run a lot," which
   correlates with task age/popularity more than construction quality. Consider
   collapsing them or weighting them lower.

3. **Run-volume criteria swamp construction quality at the bottom.** 105 tasks
   score 0 total and 359 score 0 on both deterministic criteria — overwhelmingly
   because they've never been run by ≥2 models, not because they're badly built.
   A freshly authored but well-constructed task is indistinguishable from a
   broken one under crit4/5.

4. **Criterion 1 surfaces real construct-validity failures.** 125 tasks have no
   verifiable ground truth or never grade a model output (e.g. asserting only
   that a SOURCES section exists while penalizing honest uncertainty — task 8146;
   formatting-only assertions with no answer key). This is the most
   discriminating of the LLM criteria and the one most worth keeping strict.

5. **The LLM criteria carry most of the signal.** 1110 of the awarded points
   come from crit 1–3 vs 547 from crit 4–5, and crit 1/3 spread tasks across the
   full 0–2 range, whereas crit 4/5 are essentially binary run/no-run gates.
