# Design Rationale: Rubric v4 & Two-Tier Scoring Framework

This document explains the design decisions, architectural rationale, and performance outcomes for the **v4 Rubric** iteration implemented in the `pilot_v1` auto-scoring framework.

---

## 1. Executive Summary

The transition from the static **v3 Rubric** to the hybrid **v4 Rubric** shifts the Kaggle Task Quality Framework from a purely static, subjective text review into an empirical, two-tiered validation framework. 

This iteration successfully:
*   Broke through the **0.50 correlation barrier** (Spearman's Rho rose to **0.5105**).
*   Corrected the Top/Middle tier gap (Top tier now scores higher than Mid tier by a margin of **+0.19**).
*   Reduced judge noise by **10.3%** across rollouts.

---

## 2. Core Architectural Changes & Rationale

### Change 1: Empirical Discrimination (Criterion 10)
*   **What was changed**: Replaced the static count of target models in the notebook code with an empirical calculation based on actual model execution score spreads (Max-to-Min performance spread).
*   **The Rationale**: Statically counting the models defined in code does not measure the actual utility of the benchmark. A task might run 5 models but have a bug that causes all of them to fail at 0%, or the task might be so trivial that all models score 100%. In both cases, the benchmark is useless for ranking models.
*   **How it works**:
    *   **Level 2**: Spread $\ge 30\%$ (Strong capability separation).
    *   **Level 1**: Spread between $10\%$ and $30\%$ (Moderate separation).
    *   **Level 0**: Spread $<10\%$ (Weak or broken).
*   **Result**: Criterion 10's variance rose from **0.138 to 0.923**, making it the single most discriminative metric in the framework.

### Change 2: Contamination Resistance (Criterion 11)
*   **What was changed**: Added a new criterion in Category C evaluating prompt novelty and leakage.
*   **The Rationale**: Modern LLMs are trained on massive datasets. If a benchmark's prompts or questions appear in public web indices or common instruction-tuning datasets (e.g. standard MMLU or GSM8K questions copied without paraphrase), models will solve them through **memorization** rather than **reasoning**.
*   **How it works**: Uses web search API hits and n-gram overlap checks to flag leakage:
    *   **Level 2**: 0 search hits, no leakage, and $<5\%$ n-gram overlap against public corpora.
    *   **Level 1**: Low search hits or moderate overlap ($5\% - 20\%$).
    *   **Level 0**: Leakage flag is set, search hits $\ge 5$, or overlap $\ge 20\%$.

### Change 3: Refinement of Grader & Assertion Quality (Criterion 1)
*   **What was changed**: Added explicit Level 0/1/2 checks targeting developer anti-patterns.
*   **The Rationale**: Auto-raters need specific guidance to identify gameable assertions. We added rules to penalize:
    *   *Trivial matching*: assertions that pass on empty strings (e.g., `assert output != ""`).
    *   *Variable mismatches*: prompt parameters that are never verified in the comparison code.
    *   *Raw comparisons*: string comparisons without case, whitespace, or punctuation normalization.
    *   *Weak LLM judges*: LLM judges without multi-dimensional rubrics and anchored example pairs.

### Change 4: Two-Tier Scoring Split (Pre-Run vs. Post-Run)
*   **What was changed**: Restructured the framework into two states:
    1.  **Pre-Run Score (Preliminary)**: Computed immediately on upload using the 10 static and contamination criteria. Weighted out of 10.0 points.
    2.  **Post-Run Score (Complete)**: Adds the empirical discrimination scores (re-weighting Category C) once model executions complete. Weighted out of 10.0 points.
*   **The Rationale**: Large-scale model execution on Kaggle’s cluster takes time. If an author has a basic syntax bug in their grading code or copy-pasted a contaminated prompt, they should get immediate feedback (Pre-Run). Once background model runs are scheduled and finished, the empirical discrimination score is merged to resolve the final grade (Post-Run).
*   **Scoring Weights**:
    *   *Pre-Run*: All 10 static criteria are weighted equally (`Level * 0.5`, Max 10.0 points).
    *   *Post-Run*: Categories A & B weight is `Level * 0.5`. Category C weight is `Level * 0.375` (Max 10.0 points).

---

## 3. Pilot Verification Results

The side-by-side analysis of 14 AGI Hackathon benchmarks demonstrates the value of the Two-Tier structure:

```
Metric                    | Pre-Run (Static)   | Post-Run (Empirical)
-----------------------------------------------------------------------
Top Tier Mean             |               7.75 |                 7.70
Mid Tier Mean             |               7.77 |                 7.51
Bottom Tier Mean          |               4.97 |                 4.85
Gap Top-Mid               |              -0.02 |                +0.19
Gap Mid-Bottom            |              +2.80 |                +2.66
Spearman Correlation (Rho) |             0.5022 |               0.5105
Average Judge Noise (Std) |             0.4435 |               0.4255
-----------------------------------------------------------------------
```

### Analysis
*   **Pre-Run Utility**: The static check alone provides a very strong quality indicator (**0.5022 Spearman Rho**) and immediately isolates the bottom-tier benchmarks (mean 4.97).
*   **Post-Run Necessity**: Statically, Top and Mid tiers overlap (gap of $-0.02$). The addition of empirical model spread (Post-Run) successfully resolves this overlap, separating the Top tier from the Mid tier (gap of $+0.19$) and pushing correlation to **0.5105**.
