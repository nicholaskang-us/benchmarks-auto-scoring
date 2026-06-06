Backtest analysis report

Authors: Antigravity | Date: June 6, 2026

Executive summary
This report presents the results and analysis of backtesting our automated LLM-as-a-judge quality rubric against 15 AGI Hackathon benchmarks spanning top, middle, and bottom tiers as calibrated by human judges.

Analysis of correlation and tier separation
- Rank-order correlation is low: Spearman's rho is 0.2821, and Pearson correlation is 0.2804, indicating a weak positive linear relationship between the LLM auto-rater score and the human-calibrated rankings
- Tiers are not separated cleanly: The mean LLM score for the top tier is 9.28, for the middle tier is 9.34, and for the bottom tier is 8.08. When excluding one bottom-tier outlier that lacked code, the bottom tier mean rises to 9.47, showing that the rubric fails to distinguish between different human-evaluated quality tiers

Criterion-level statistics
- Documentation: Mean level is 2.00 / 2.00 (Variance: 0.0000) — Every single benchmark received a perfect score, indicating this criterion has zero discriminative power
- Prompt clarity: Mean level is 1.85 / 2.00 (Variance: 0.2661) — Most benchmarks got Level 2, showing low discrimination
- Capability targeting: Mean level is 1.73 / 2.00 (Variance: 0.3524)
- Answer correctness: Mean level is 1.71 / 2.00 (Variance: 0.3471)
- Code quality: Mean level is 1.58 / 2.00 (Variance: 0.4256) — This criterion showed the highest variance and was the most effective at identifying low-quality implementations

Key failure modes and discrepancies
- Bottom-tier benchmarks scoring perfect 10.00: Benchmarks like Constraint Adaptation Benchmark (CAB) (human calibrated 13.3%), TemporalBench (human calibrated 26.0%), and STRATAGEM-SC (human calibrated 28.6%) received perfect 10.00 LLM scores. These benchmarks had highly polished code, deterministic assertions, and complete documentation, but were ranked very low by human judges due to lack of conceptual novelty (e.g. CAB uses standard code golf and regex golf) or limited dataset scale
- Top-tier benchmarks penalized on minor code issues: Behavioral Metacognitive Control on Expert Questions in LLMs (human calibrated 97.3%) was penalized down to 8.75 due to high code replication (cloned config files) despite having excellent scientific validity and dataset quality
- Code presence as a binary gate: Executive Functions: The Cognitive Control Suite (human calibrated 22.5%) scored 2.50 because it did not submit any code files, triggering the Level 0 auto-fail code quality rule. While this accurately flags unrunnable benchmarks, it creates a massive score gulf between bad implementations and missing implementations

Rubric adjustment recommendations
- Introduce a novelty and significance criterion: To align with human evaluations, add a criterion assessing whether the task design is novel or a standard replication (e.g. code/regex golf)
- Tighten Level 2 requirements for documentation: Instead of general completeness, require documentation of concrete dataset schemas, baseline runs, and error analysis to introduce variance
- Separate code engineering from scientific validity: A benchmark with clean code but trivial task design should be capped, and a benchmark with great tasks but messy code should not be overly penalized
- Increase sample size weights: A task with 50+ items should receive a score boost over a task with only 1-5 items to reflect statistical reliability
