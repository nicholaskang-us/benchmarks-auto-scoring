# v2 analysis — rubric v2 (validity gate added)

Set: 14 benchmarks (RIAC excluded). Design: 3 rollouts × 3 blind groups = 9 runs, same as
baseline. Only rubric change vs v1: the hard **Validity Gate**.

## Headline: v2 is WORSE than baseline. The gate backfired.

| metric | baseline (v1) | v2 | change |
|---|---|---|---|
| top-mid gap (primary) | −0.92 | **−1.46** | worse |
| mid-bottom gap | +2.53 | +2.57 | ~flat |
| Spearman rho (secondary) | 0.386 | **0.292** | worse |
| judge noise (avg within-bench std) | 0.291 | **0.473** | worse |

## Per-benchmark baseline → v2
| # | tier | base | v2 | note |
|---|---|---|---|---|
| 1 | top | 8.33 | 9.00 | drift up (noise) |
| 2 | top | 8.17 | **3.50** | **GATE FALSE-POSITIVE** — failed 2/3 rollouts (→2.0), passed 1/3 (→6.5). std 2.12 |
| 4 | top | 4.17 | 5.67 | drift up |
| 5 | top | 3.50 | 4.00 | ~flat |
| 6 | mid | 7.83 | 7.83 | flat |
| 7 | mid | 8.33 | 7.83 | drift |
| 8 | mid | 4.50 | 4.67 | flat |
| 9 | mid | 8.67 | 8.67 | flat |
| 10 | mid | 5.50 | 6.00 | drift |
| 11 | bottom | 7.17 | 7.67 | drift (well-built, novelty-docked by humans — fine) |
| 12 | bottom | 4.67 | **4.83** | **GATE MISSED ITS TARGET** — passed all 3 rollouts |
| 13 | bottom | 0.00 | 0.00 | gate fired but already 0 (no effect) |
| 14 | bottom | 2.67 | 2.67 | flat |
| 15 | bottom | 7.67 | 7.00 | drift |

## Why the gate failed — two opposite errors

**Error 1 — FALSE POSITIVE on #2 Russian Doll (top tier, 96.4%).**
#2's public notebook is a *thin wrapper*: it pip-installs deps, imports the real benchmark
package from a captured dataset (`_dataset_russian-doll-source-code/benchmark/tasks.py`), and
calls `run_adaptive_learning(kbench.llm)` — which genuinely exercises a model. But:
- The eval logic lives OFF-notebook (in the dataset package). Agents inconsistently traced the
  `from benchmark.tasks import ...` import into the dataset to verify model invocation.
- We strip notebook outputs, so agents saw "no output" on the run cell and some inferred "no
  model score was ever produced" / "import crash from the version pin."
Result: gate failed in 2 of 3 rollouts, capping a genuinely well-built top-tier task at 2.0.
This is a SOURCE-COMPLETENESS / output-stripping artifact, not a real construction defect.

**Error 2 — MISS on #12 TemporalBench (the intended target).**
The gate was designed to catch #12 (headline eval asserts on the authors' own Python store,
scores 0/734). But the gate rule says "PASS if ANY notebook genuinely evaluates a model."
#12 has peripheral notebooks (e.g. a staleness notebook) that DO call a model on a few mock
items, so every rollout passed it on that technicality — leaving it at ~4.8, basically
unchanged from baseline. The broken HEADLINE eval was not penalized.

## Diagnosis
The gate concept is sound (a task that doesn't exercise a model is low quality), but the
operationalization is wrong on two axes:
1. **Run-state vs design.** It must judge whether the eval LOGIC is designed to exercise a
   model — readable from code (incl. imported dataset packages) — NOT whether outputs are
   present or whether the captured environment happens to install/run. Output stripping and
   version pins are our-side artifacts and must not trip the gate.
2. **"Any notebook" is too lenient.** It must assess the task's PRIMARY/headline evaluation.
   A peripheral model-calling notebook must not rescue a task whose main eval asserts on its
   own data; a broken auxiliary notebook must not sink a task whose main eval is sound.

## Proposed v2.1 gate wording
- Gate is about eval DESIGN: fails only if the primary evaluation's LOGIC never sends prompts
  to a model and scores model responses (e.g. asserts on hardcoded/self-computed values).
- Explicitly EXCLUDE: environment/dependency/version/install failures, quota/API errors,
  truncated or output-stripped source, and logic imported from a provided dataset package
  (trace into it before concluding a model isn't called).
- Judge the PRIMARY eval, not "any notebook."

Expected effect: #2 passes (sound design), #12 fails (broken headline eval), #13 stays failed
(no code at all). That would pull only the genuinely-broken bottom-tier task down.
