# Baseline analysis — current `total_rubric.md` (v1)

Set: 14 benchmarks (RIAC excluded). Design: 3 rollouts × 3 blind groups = 9 subagent runs;
each benchmark scored 3×. Ground truth (human-calibrated tiers) hidden from all agents.

## Headline numbers
- **Spearman rho (vs human %): 0.386** (secondary metric)
- **Tier separation (PRIMARY): FAILED**
  - top mean **6.04**, mid mean **6.97**, bottom mean **4.43**
  - **top–mid gap = −0.92** (top tier scores *lower* than mid — inverted)
  - mid–bottom gap = +2.53
  - clean boundaries: top>mid **False**, mid>bottom **False**
- **Judge noise: 0.29** avg within-benchmark std → the failure is **rubric-design error, not judge noise.** Three independent rollouts agree closely; the rubric is reliably measuring the wrong thing.

## Per-benchmark (sorted by human rating)
| # | human% | tier | v1 mean | verdict |
|---|---|---|---|---|
| 1 | 97.3 | top | 8.33 | ok (high) |
| 2 | 96.4 | top | 8.17 | ok (high) |
| 4 | 93.7 | top | 4.17 | **underscored** — no docs, single metric/model |
| 5 | 91.2 | top | 3.50 | **badly underscored** — 5 single-item creative scenarios crushed by sample-size/metric criteria |
| 6 | 64.7 | mid | 7.83 | overscored |
| 7 | 64.7 | mid | 8.33 | overscored |
| 8 | 64.6 | mid | 4.50 | ok-ish |
| 9 | 64.6 | mid | 8.67 | **overscored** — heavy engineering (SDT, calibration, 600 items) reads as "excellent" |
| 10 | 64.6 | mid | 5.50 | ok-ish |
| 11 | 28.6 | bottom | 7.17 | **badly overscored** |
| 12 | 26.0 | bottom | 4.67 | overscored (agents caught it never calls the LLM, but still 4.67) |
| 13 | 22.5 | bottom | 0.00 | correct direction; binary code gate → extreme outlier |
| 14 | 20.4 | bottom | 2.67 | ok (low) |
| 15 | 13.3 | bottom | 7.67 | **badly overscored** — "code/regex golf", trivial concept, polished engineering |

## Documented failure modes (each drives a v2 change)

**FM1 — No conceptual-significance axis. Engineering polish masquerades as quality.**
CAB (#15, human 13.3%) → 7.67; STRATAGEM (#11, 28.6%) → 7.17; ACP (#9, mid) → 8.67. All have
clean code, deterministic scoring, large/structured item sets — and the rubric rewards exactly
those. The rubric has **no criterion** asking "is the underlying task idea novel/significant, or
a standard replication / golf exercise?" This is the single largest driver of the inverted gap.

**FM2 — Mechanical criteria punish conceptually deep but small/lean top-tier tasks.**
Time Traveler (#5, 91.2%) → 3.50 and Supply-Chain (#4, 93.7%) → 4.17. Killed by Sample Size
(few items), Metric Design (single metric), Model Coverage (1 model), Documentation (no markdown).
These are real engineering gaps but humans rank the *ideas* top-tier. Current weighting lets
mechanical hygiene override scientific value.

**FM3 — Model Coverage (crit 10) is a dead, anti-correlated criterion.**
Mean level **0.17** (almost every benchmark single-model), variance 0.107. It is an artifact of
how these were *run*, not a property of task quality, and it uniformly drags scores down without
discriminating between tiers. Near-zero signal.

**FM4 — Binary code gate creates a cliff.**
Exec Functions (#13) → 0.0 on all criteria. Directionally correct here (it is bottom-tier), but
the all-or-nothing gate makes "missing code" score far below "bad code," which is brittle. Lower
priority since it doesn't hurt ranking on this set — note but don't over-engineer.

**FM5 — Documentation & Metric Design reward engineering ceremony, not science.**
Documentation mean 0.93 but it rewards markdown presence; Metric Design rewards metric *count*.
Neither tracks human-judged quality (top-tier #4/#5 score low on both; bottom-tier #15 scores high).

## Implication for v2
The rubric must (a) add a heavily-weighted **Novelty & Significance** axis, (b) stop letting
mechanical criteria veto conceptually strong tasks, and (c) drop or repair the dead Model Coverage
criterion. Target: restore a positive, ideally clean, top>mid>bottom ordering.
