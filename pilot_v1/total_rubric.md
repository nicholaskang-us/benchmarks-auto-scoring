# Kaggle Benchmark Quality Framework: Total Rubric

This document combines all evaluation rubrics for the Kaggle Benchmark Quality Framework into a single guide. It details the criteria, weights, scoring methods, and rating guidelines for both **Task-Level Quality** and **Benchmark-Level Multi-Dimensional Coverage (Category 2)**.

---

## 1. Task-Level Quality Rubric (LLM-Evaluated)

This rubric is evaluated for **each individual task** in a benchmark. 

### Scoring Mechanics
*   **Scale**: Each criterion is assigned a discrete level: **0, 1, or 2**.
*   **Calculation**: The score for each criterion is calculated as `Level × Weight`.
*   **Subtotal**: The task subtotal is the sum of all 5 weighted scores (Maximum: **4.00 points**).
*   **Normalization**: The subtotal is multiplied by **2.5** to normalize it to a standard **10.00-point scale** (or by **25** for a 100% percentage score).

### Table of Criteria and Weights

| Criterion | Weight | Level 0 Max | Level 1 Max | Level 2 Max |
| :--- | :---: | :---: | :---: | :---: |
| **1. Answer Correctness** | 0.35 | 0.00 | 0.35 | 0.70 |
| **2. Prompt Clarity** | 0.35 | 0.00 | 0.35 | 0.70 |
| **3. Capability Targeting** | 0.30 | 0.00 | 0.30 | 0.60 |
| **4. Code Quality** | 0.50 | 0.00 | 0.50 | 1.00 |
| **5. Documentation** | 0.50 | 0.00 | 0.50 | 1.00 |
| **Total Task Score** | | **0.00** | **2.00** | **4.00** |

---

### Detailed Criteria Descriptions

#### Criterion 1.1: Answer Correctness (Weight: 0.35)
*Evaluates the construct validity and verification method of the task's expected answers.*

*   **Level 0 (Score: 0.00)**: Subjective or open-ended answers with no clear ground truth. For LLM-as-a-judge, no evaluation rubric is provided.
*   **Level 1 (Score: 0.35)**: Partially verifiable answers. Gaps in validation or ambiguities in edge cases. For LLM-as-a-judge, the grading rubric is vague or incomplete.
*   **Level 2 (Score: 0.70)**: Unambiguous, fully verifiable answers. For LLM-as-a-judge, a comprehensive multi-dimensional rubric is provided with anchored examples.

#### Criterion 1.2: Prompt Clarity (Weight: 0.35)
*Evaluates if the model instructions are precise enough to prevent failures due to format confusion.*

*   **Level 0 (Score: 0.00)**: Instructions are ambiguous, missing format constraints, or leading.
*   **Level 1 (Score: 0.35)**: Generally clear task instructions, but missing specific formatting rules, fallback strategies, or edge-case handling guidelines.
*   **Level 2 (Score: 0.70)**: Precise instructions with exact input/output specs, structured templates (e.g., JSON schemas), and explicit constraints.

#### Criterion 1.3: Capability Targeting (Weight: 0.30)
*Evaluates if the task isolates a specific cognitive/technical capability rather than testing generic knowledge.*

*   **Level 0 (Score: 0.00)**: Unfocused task (e.g., trivia, general knowledge) with no clear capability hypothesis.
*   **Level 1 (Score: 0.30)**: Targets a broad capability domain (e.g., "reasoning") without isolating it from confounding skills.
*   **Level 2 (Score: 0.60)**: Isolates a specific, narrow sub-capability (e.g., "inhibitory control" via a Stroop task) with a clear cognitive hypothesis.

#### Criterion 1.4: Code Quality (Weight: 0.50)
*Evaluates the structure and robustness of the task implementation code.*

*   **Level 0 (Score: 0.00)**: Fragile, uncommented code, or hardcoded values. **Mandatory 0 if no task code or notebook exists.**
*   **Level 1 (Score: 0.50)**: Functional code, but poorly structured, minimally commented, or lacks input/output validation.
*   **Level 2 (Score: 1.00)**: Clean, modular, well-commented code following the `kaggle-benchmarks` SDK guidelines, with robust error-handling.

#### Criterion 1.5: Documentation (Weight: 0.50)
*Evaluates the task's completeness of explanation and instructions.*

*   **Level 0 (Score: 0.00)**: Minimal to no task writeup or documentation.
*   **Level 1 (Score: 0.50)**: Basic writeup describing the task, but missing details on data provenance, evaluation protocol, or limitations.
*   **Level 2 (Score: 1.00)**: Comprehensive writeup covering motivation, dataset card/schema, evaluation methodology, and results interpretation.

---

## 2. Benchmark-Level Coverage Rubric (Category 2)

This rubric is evaluated at the **benchmark-level** across all tasks and runs. It measures the breadth, scenario diversity, and multi-dimensional nature of the evaluation.

### Scoring Mechanics
*   **Scale**: Each criterion is graded on a scale of **0 to 3**.
*   **Weights**: Unweighted raw sum (Maximum: **15.00 points**).
*   **Methods**: Rated using deterministic rules, LLM auto-raters, or hybrid checks.

### Table of Criteria and Scoring

| Criterion | Max Score | Rating Method | Unit of Input |
| :--- | :---: | :---: | :--- |
| **2.1: Multiple Metrics Measured** | 3.00 | Hybrid | Run results & task code |
| **2.2: Scenario Taxonomy Diversity** | 3.00 | LLM Auto-rater | README & config metadata |
| **2.3: Dimension Trade-offs Exposed** | 3.00 | LLM Auto-rater | README & analysis notebooks |
| **2.4: Model Coverage Breadth** | 3.00 | Deterministic | Run results (`.run.json`) |
| **2.5: Metric Choice Justification** | 3.00 | LLM Auto-rater | README & task notebooks |
| **Total Category 2 Score** | **15.00** | | |

---

### Detailed Criteria Descriptions

#### Criterion 2.1: Multiple Metrics Measured (Max: 3.00)
*Evaluates if auxiliary performance dimensions (e.g., latency, robustness, cost) are evaluated alongside accuracy.*

*   **Rating Method**: Hybrid (Deterministic metric count + LLM semantic check).
*   **0 Points (Not Addressed)**: Only a single metric is computed (e.g., only Accuracy).
*   **1 Point (Acknowledged)**: Multiple metrics are computed, but they all measure the same dimension (e.g., Accuracy, F1, Precision, and Recall).
*   **2 Points (Partially Addressed)**: At least two distinct dimensions are measured simultaneously (e.g., Accuracy and Latency).
*   **3 Points (Fully Addressed)**: Three or more distinct dimensions are measured (e.g., Accuracy, Latency, and Calibration/Uncertainty).

#### Criterion 2.2: Scenario Taxonomy Diversity (Max: 3.00)
*Evaluates if the benchmark spans a representative range of tasks, domains, or formats.*

*   **Rating Method**: LLM Auto-rater.
*   **0 Points (Not Addressed)**: Single task type in a narrow domain.
*   **1 Point (Acknowledged)**: Multiple tasks but lack a systematic taxonomy, or domains are highly correlated.
*   **2 Points (Partially Addressed)**: Clear taxonomy covering multiple domains or task types, but the distribution is skewed or lacks key domains.
*   **3 Points (Fully Addressed)**: Well-balanced, comprehensive taxonomy spanning diverse domains and formats (e.g., text vs. code vs. multimodal).

#### Criterion 2.3: Dimension Trade-offs Exposed (Max: 3.00)
*Evaluates if the results analyze trade-offs between different performance dimensions.*

*   **Rating Method**: LLM Auto-rater.
*   **0 Points (Not Addressed)**: Results presented only as a flat leaderboard score.
*   **1 Point (Acknowledged)**: trade-offs mentioned conceptually, but unsupported by data or plots.
*   **2 Points (Partially Addressed)**: Multiple metrics tabulated or plotted, allowing trade-offs to be inferred, but lack Pareto-frontier or trade-off analysis.
*   **3 Points (Fully Addressed)**: Explicitly visualizes (e.g., Pareto scatter plots, radar charts) and discusses trade-offs across model families.

#### Criterion 2.4: Model Coverage Breadth (Max: 3.00)
*Evaluates if the benchmark supports and has been evaluated on a diverse, balanced set of models.*

*   **Rating Method**: Deterministic Python Code.
*   **0 Points (Not Addressed)**: Evaluated only on a single model.
*   **1 Point (Acknowledged)**: Evaluated on multiple models, but all from a single family or creator (e.g., only Gemini).
*   **2 Points (Partially Addressed)**: Evaluated on at least 3 distinct families/providers, but lacks balance (e.g., only proprietary APIs).
*   **3 Points (Fully Addressed)**: Evaluated on 4+ distinct families/providers, representing a balanced mix of proprietary APIs (GPT, Gemini, Claude) and open-weights (Llama, Gemma, Mistral) of varying sizes.

#### Criterion 2.5: Metric Choice Justification (Max: 3.00)
*Evaluates if selected metrics are justified, standard, and robust to bias.*

*   **Rating Method**: LLM Auto-rater.
*   **0 Points (Not Addressed)**: Metrics used without explanation, or clearly inappropriate for the tasks.
*   **1 Point (Acknowledged)**: Standard metrics used with minimal explanation, ignoring known limitations.
*   **2 Points (Partially Addressed)**: Metric choice is justified, and mitigations are implemented (e.g., combining BLEU with human evaluation).
*   **3 Points (Fully Addressed)**: Highly rigorous justification. For custom/LLM-as-a-judge metrics: the rubric is documented, validated (correlation with human scores is reported), and robust to biases (position, verbosity).
