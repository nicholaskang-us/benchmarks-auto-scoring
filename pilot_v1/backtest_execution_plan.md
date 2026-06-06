# Backtest Execution Plan

**Authors:** Antigravity | **Date:** June 5, 2026

---

## Objective

Run the LLM-as-a-judge rubric against 15 AGI Hackathon benchmarks (top 5, middle 5, bottom 5) to validate whether our automated scoring correlates with the human-calibrated rankings.

The rubric used is the **Kaggle Task Quality Framework** defined in [total_rubric.md](total_rubric.md), which scores 10 criteria across 3 categories (A: Task Construction 50%, B: Task Description 20%, C: Novelty & Discriminatory Power 30%).

---

## Step 1: Spin Up 3 Research Subagents

Each subagent reviews 5 randomly assigned benchmarks. This parallelizes the work and ensures blind evaluation (subagents do not see the human rankings or categories).

### Subagent A
*   RIAC — Repetition-Induced Attention Collapse
*   Can LLMs Inhibit Optimization in Supply-Chain Decision-Making?
*   Embodied Inhibitory Control in AnimalAI
*   Observe-Reason-Learn-Verify-Adapt-Loop
*   Executive Functions: The Cognitive Control Suite

### Subagent B
*   Behavioral Metacognitive Control on Expert Questions in LLMs
*   ITTIA - I think therefore I am
*   Social Cognition - Understanding The Mind of Agents and Semantics
*   STRATAGEM-SC: Strategic Theory-of-Mind Benchmark for Social Cognition
*   The Efficiency Paradox: Measuring Heuristic Capture

### Subagent C
*   Russian Doll Bench: Infrastructure Building Capabilities
*   The Time Traveler's Dilemma: Empathy, Oversight, & the Stop Sign Effect
*   Adversarial Cognitive Profiling (ACP): Metacognitive Calibration Benchmark
*   TemporalBench: Validity Windows Beat Decay Functions
*   Constraint Adaptation Benchmark (CAB)

### Each subagent receives:
*   The full rubric from [total_rubric.md](total_rubric.md) — all 10 criteria with level definitions and examples
*   The writeup, benchmark, task, and notebook URLs from [agi_hackathon_benchmark_links.md](agi_hackathon_benchmark_links.md)
*   Instructions to navigate to each writeup and inspect the task page and notebook to score each task individually across all 10 criteria
*   Instructions to average the task scores to compute the overall benchmark score

Each subagent returns **5 JSON scoring objects** (one per benchmark), with all 10 criterion scores per task.

---

## Step 2: Collect Results into a CSV

Once all 3 subagents return, collect their 15 JSON results and generate a CSV with the following columns:

### Identifiers
*   `rank`
*   `benchmark_name`
*   `tier` (top / middle / bottom)
*   `human_calibrated_pct` (from the AGI Hackathon)

### Category A: Task Construction Quality (5.0 points max)
*   `answer_correctness_level` / `answer_correctness_score`
*   `construct_validity_level` / `construct_validity_score`
*   `code_quality_level` / `code_quality_score`
*   `sample_size_level` / `sample_size_score`
*   `metric_design_level` / `metric_design_score`
*   `category_a_subtotal` (max 5.0)

### Category B: Task Description Quality (2.0 points max)
*   `problem_statement_level` / `problem_statement_score`
*   `technical_documentation_level` / `technical_documentation_score`
*   `category_b_subtotal` (max 2.0)

### Category C: Novelty & Discriminatory Power (3.0 points max)
*   `capability_targeting_level` / `capability_targeting_score`
*   `item_diversity_level` / `item_diversity_score`
*   `model_coverage_level` / `model_coverage_score`
*   `category_c_subtotal` (max 3.0)

### Totals
*   `total_score` (max 10.0)
*   `total_score_pct` (total_score / 10.0 * 100, for comparison against the human 0-100 scale)

---

## Step 3: Merge with the Human-Calibrated Rankings

Append the LLM scores alongside the human scores from:
`/tmp/competitions-prep/misc/agi_hackathon_judge/score_calibration/calibration_output_0604/calibrated_rankings.csv`

Create a merged comparison table with both the human-calibrated percentage and the automated rubric score side by side.

---

## Step 4: Review and Analyze

Produce a summary artifact answering:
*   **Rank-order correlation:** whether the automated rubric ranks the 15 benchmarks in roughly the same order as the human judges (Spearman's rho)
*   **Tier separation:** whether the rubric clearly separates the top, middle, and bottom tiers (mean scores per tier)
*   **Category-level analysis:** which of the 3 categories (A, B, C) is most/least aligned with human scores
*   **Criterion variance:** which criteria show the most variance and which are most/least aligned with human scores
*   **Failure modes:** any benchmarks where the automated score dramatically disagrees with the human score and the reasons why
*   **Rubric adjustments:** whether any criterion definitions or category distributions should be revised based on the backtest

---

## Step 5: Staging and Pushing Results

When pushing backtest evaluation results to the repository, follow this folder structure:
*   Create a subfolder under `/pilot_v1` named `results_<YYYY-MM-DD HH:MM>` using the UTC time of the push (e.g. `results_2026-06-06 00:30`)
*   Place the following files inside the timestamped subfolder:
    *   `task_level_results.md` - the complete Markdown table containing evaluations of all individual tasks with hyperlinked benchmark and task pages
    *   `backtest_analysis_results.md` - the markdown report detailing correlation statistics, criterion-level analysis, and key discrepancies
*   Clean up any scratch or script files (such as python code used for collation or generation) from the root `/pilot_v1` directory before committing, ensuring only the core documentation remains in the parent folder

---

## Expected Timeline

*   **Step 1:** ~3-5 minutes (parallel subagent execution)
*   **Step 2:** ~1 minute (CSV generation)
*   **Step 3:** ~1 minute (merge)
*   **Step 4:** ~2 minutes (analysis artifact)
*   **Step 5:** ~1 minute (results staging and pushing)
*   **Total:** ~11 minutes end to end

