# Backtest Execution Plan

**Authors:** Antigravity | **Date:** June 5, 2026

---

## Objective

Run the LLM-as-a-judge rubric against 15 AGI Hackathon benchmarks (top 5, middle 5, bottom 5) to validate whether our automated scoring correlates with the human-calibrated rankings.

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
*   The full LLM-as-a-judge system prompt and rubric from [llm_judge_backtest_instructions.md](llm_judge_backtest_instructions.md)
*   The writeup, benchmark, task, and notebook URLs from [agi_hackathon_benchmark_links.md](agi_hackathon_benchmark_links.md)
*   Instructions to navigate to each writeup and inspect the task notebook implementations to score each task individually
*   Instructions to average the task scores to compute the overall benchmark score

Each subagent returns **5 JSON scoring objects** (one per benchmark).

---

## Step 2: Collect Results into a CSV

Once all 3 subagents return, collect their 15 JSON results and generate a CSV with the following columns:
*   `rank`
*   `benchmark_name`
*   `tier` (top / middle / bottom)
*   `human_calibrated_pct` (from the AGI Hackathon)
*   `answer_correctness_level`
*   `answer_correctness_score`
*   `prompt_clarity_level`
*   `prompt_clarity_score`
*   `capability_targeting_level`
*   `capability_targeting_score`
*   `code_quality_level`
*   `code_quality_score`
*   `documentation_level`
*   `documentation_score`
*   `llm_subtotal` (max 4.00)
*   `llm_subtotal_normalized_to_10` (llm_subtotal / 4.0 * 10, for easier comparison against the human 0-100 scale)

**Save to:** `/usr/local/google/home/nicholaskang/.gemini/jetski/brain/0eb36fbc-7223-46d0-9dc5-a7f6fc62371d/scratch/backtest_results.csv`

---

## Step 3: Merge with the Human-Calibrated Rankings

Append the LLM scores alongside the human scores from:
`/tmp/competitions-prep/misc/agi_hackathon_judge/score_calibration/calibration_output_0604/calibrated_rankings.csv`

Create a merged comparison table with both the human-calibrated percentage and the LLM-judge normalized score side by side.

---

## Step 4: Review and Analyze

Produce a summary artifact answering:
*   **Rank-order correlation:** whether the LLM rubric ranks the 15 benchmarks in roughly the same order as the human judges (Spearman's rho)
*   **Tier separation:** whether the LLM clearly separates the top, middle, and bottom tiers (mean scores per tier)
*   **Criterion variance:** which criteria show the most variance and which are most/least aligned with human scores
*   **Failure modes:** any benchmarks where the LLM score dramatically disagrees with the human score and the reasons why
*   **Rubric adjustments:** whether any criterion weights or level descriptions should be revised based on the backtest

---

## Expected Timeline

*   **Step 1:** ~3-5 minutes (parallel subagent execution)
*   **Step 2:** ~1 minute (CSV generation)
*   **Step 3:** ~1 minute (merge)
*   **Step 4:** ~2 minutes (analysis artifact)
*   **Total:** ~10 minutes end to end
