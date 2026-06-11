# v3 analysis — rubric v3 (gate dropped; validity folded into Criterion 2)

Set: 14 benchmarks (RIAC excluded). Design: 3 rollouts × 3 blind groups = 9 runs.
Changes vs v2: (1) Validity Gate + cap REMOVED; the "does the eval measure a model?" check
is now Criterion 2 (Construct Validity) Level 0, with primary-eval / trace-into-dataset /
exclude-our-side-artifacts guidance. (2) Category C relabeled "Discriminative Power & Coverage".

## Headline: v3 is the best version so far

| metric | baseline (v1) | v2 | v3 |
|---|---|---|---|
| top-mid gap (primary) | −0.92 | −1.46 | **−0.10** |
| mid-bottom gap | +2.53 | +2.57 | +2.50 |
| Spearman rho (secondary) | 0.386 | 0.292 | **0.493** |
| judge noise (avg within-bench std) | 0.291 | 0.473 | 0.474 |

Tier means: top 7.00, mid 7.10, bottom 4.60. Bottom is cleanly separated (+2.50). Top≈mid
(−0.10) — see "expected divergences" below; this is novelty-driven and per the project
objective is CORRECT, not a failure.

## Per-benchmark (v3 mean, sorted by human rating)
| # | human% | tier | v3 mean | std | note |
|---|---|---|---|---|---|
| 1 | 97.3 | top | 9.00 | 0.00 | perfect agreement; strong build |
| 2 | 96.4 | top | 7.67 | 0.85 | **v2 FALSE-POSITIVE FIXED** (was 3.50). Agents traced into dataset pkg, ignored version-pin import error |
| 4 | 93.7 | top | 6.33 | 0.62 | sound; human-likeness confound, single model/metric, no docs |
| 5 | 91.2 | top | 5.00 | 1.08 | only 5 single-item scenarios → sample-size/coverage L0 (real robustness gap; human ranks the idea) |
| 6 | 64.7 | mid | 7.83 | 0.62 | Stroop design, 2 models |
| 7 | 64.7 | mid | 8.67 | 0.24 | strongest mid; control/test pairs, 2 models |
| 8 | 64.6 | mid | 4.83 | 0.24 | subjective forced-choice, single metric/model |
| 9 | 64.6 | mid | 8.67 | 0.24 | heavy engineering (SDT, 600 items, bootstrap CIs) |
| 10 | 64.6 | mid | 5.50 | 1.08 | format-compliance confound; single metric/model |
| 11 | 28.6 | bottom | 8.17 | 0.62 | well-built (1200 scenarios); novelty-docked by humans → high score CORRECT |
| 12 | 26.0 | bottom | 5.00 | 0.41 | **only partly penalized** — see below |
| 13 | 22.5 | bottom | 0.00 | 0.00 | empty folder (no code) → all L0 |
| 14 | 20.4 | bottom | 2.33 | 0.24 | ~3 hardcoded items, contestable gold |
| 15 | 13.3 | bottom | 7.50 | 0.41 | polished "regex/code golf"; novelty-docked by humans → high score CORRECT |

## Validation targets

**#2 Russian Doll — FIXED.** v2 capped it to 3.50 (gate false-positive). v3 mean 7.67.
Every rollout traced `from benchmark.tasks import run_adaptive_learning` into the captured
dataset package, confirmed the real agentic model loop, and did not penalize the version-pin
import error. The output-stripping / off-notebook-logic artifact no longer sinks it.

**#12 TemporalBench — only partly caught (the remaining weak spot).** Mean 5.00 (baseline
4.67) — essentially flat, NOT strongly penalized. Root cause: #12 contains BOTH self-
asserting notebooks (`temporalbenchv4`, `temporalbench-v2-pccc`, saved as leaderboard
`.task.json`, asserting on an internal `TemporalAttentionStore`, printing 942/942 & 734/734
by construction) AND an auxiliary `temporalbench-eval` notebook that does call the model.
Judges split on which is the "primary" eval:
- r2_C judged the self-asserting tasks as primary → Criterion 2 Level 0 → 4.5
- r3_C judged the model-calling eval as primary → Criterion 2 not fully L0 → 5.5
So the construct defect is real and partially recognized, but the "primary eval" call is
genuinely ambiguous for this task, leaving it mid-pack rather than low.

## Expected (correct) divergences from human tiers — per project objective
Novelty is deliberately excluded from the rubric, so these are NOT failures:
- #11 STRATAGEM (human bottom) → 8.17 and #15 CAB (human bottom) → 7.50: well-engineered
  builds humans docked for low novelty. Construction-wise they ARE high quality.
- #5 Time Traveler (human top) → 5.00: conceptually rich but only 5 single-item scenarios;
  the rubric correctly penalizes thin sample size / single model. Humans rank the idea.
These three account for most of the top≈mid compression and the imperfect Spearman.

## Judge noise
0.474 overall, but concentrated in genuinely ambiguous tasks: #5 (std 1.08, tiny creative
set), #10 (1.08, format confound), #2 (0.85, off-notebook logic). #12 is actually low-std
(0.41). The noise is not a gate/cap artifact (there is no cap in v3) — it reflects real task
ambiguity. #1 and #13 have std 0.00.

## Verdict / open question
v3 cleanly fixes the #2 regression and is the best version on Spearman and tier gaps. The
one residual is #12: its dual nature (self-asserting leaderboard tasks + a real model-calling
aux eval) makes "judge the primary eval" ambiguous, so it isn't pushed to the bottom. Options
if we want #12 lower: sharpen the "primary eval" definition to mean the leaderboard-published
`.task.json` (risks brittleness), or accept 5.0 as defensible since the task genuinely does
contain a working model eval.
