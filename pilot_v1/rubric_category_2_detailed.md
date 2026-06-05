# Category 2: Multi-Dimensional Coverage - Detailed Rubric

This document provides the detailed evaluation rubric, rating methods, required input artifacts, programmatic rules, and rating guidelines for **Category 2 (Multi-dimensional coverage)** of the Kaggle Benchmark Quality Framework.

---

## Criterion 2.1: Multiple Metrics Measured Simultaneously (Task Notebook, P1)

### Description
Beyond accuracy – evaluates whether auxiliary dimensions such as calibration, robustness, and efficiency are evaluated simultaneously.

### Detailed 0-3 Rubric
*   **0 (Not Addressed):** Only a single performance metric is computed and reported (e.g., only Accuracy or only F1-score).
*   **1 (Acknowledged):** Multiple metrics are computed, but they are highly correlated and measure the same underlying dimension (e.g., Accuracy, Precision, Recall, and F1-score are all reported, but they all measure correctness/accuracy).
*   **2 (Partially Addressed):** At least two distinct dimensions of performance are measured simultaneously (e.g., Accuracy and Latency, or Accuracy and Robustness to prompt perturbations).
*   **3 (Fully Addressed):** Three or more distinct dimensions of performance are measured simultaneously (e.g., Accuracy, Latency, and Calibration/Confidence; or Accuracy, Safety, and Cost).

### Rating Method
**Hybrid (Deterministic + LLM Auto-rater)**

*Rationale:* We can deterministically extract the list of metrics computed in the Task Notebook or recorded in the run results. However, determining whether these metrics represent distinct dimensions (rather than just variations of accuracy) requires semantic understanding, which is best handled by an LLM auto-rater analyzing the metric definitions and justifications.

### Required Input Artifacts
*   Task Notebook or Task Python Code (to inspect metric computation)
*   Run Results (`.run.json`) (to verify what was actually recorded)

### Programmatic Rules (for the deterministic part)
1.  Parse the `.run.json` file and extract all keys from the `metrics` or `results` field for each run.
2.  Count the number of unique metric keys.
3.  If count is **1**, automatically assign a score of **0**.
4.  If count is **greater than 1**, pass the metric names and descriptions to the LLM auto-rater to determine distinct dimensions.

### Guidelines for Rating
*   **Distinct dimensions include:**
    *   *Correctness / Accuracy* (e.g., Accuracy, F1, BLEU, MMLU score)
    *   *Uncertainty / Calibration* (e.g., Expected Calibration Error, Brier score, confidence scores)
    *   *Efficiency / Computational cost* (e.g., Latency, token count, GPU hours, memory usage)
    *   *Robustness* (e.g., Performance under perturbation, adversarial robustness)
    *   *Safety / Alignment* (e.g., Toxicity rate, jailbreak resistance)
*   Reporting multiple variants of accuracy (e.g., Top-1 Accuracy and Top-5 Accuracy) does not qualify for a score of 2 or 3.

---

## Criterion 2.2: Diverse Scenario Taxonomy Covered (Benchmark, P1)

### Description
The benchmark spans a representative range of tasks, domains, or use cases rather than a narrow slice.

### Detailed 0-3 Rubric
*   **0 (Not Addressed):** The benchmark consists of a single task type in a single narrow domain (e.g., only multiple-choice questions about history).
*   **1 (Acknowledged):** The benchmark includes some variation in tasks but lacks a systematic taxonomy, or the domains are closely related (e.g., multiple-choice questions across different school subjects, but all using the same format and testing memorization).
*   **2 (Partially Addressed):** The benchmark is organized around a clear taxonomy covering multiple distinct domains or task types (e.g., separate categories for reasoning, coding, and creative writing), but the distribution is heavily skewed or some key areas are missing.
*   **3 (Fully Addressed):** The benchmark covers a comprehensive, well-balanced taxonomy of diverse domains and task formats (e.g., text, code, multimodal; single-turn, multi-turn; reasoning, extraction, synthesis) with explicit justification for the taxonomy design in the documentation.

### Rating Method
**LLM Auto-rater**

*Rationale:* Assessing diversity and taxonomy coverage is highly semantic. An LLM is required to understand the domains, task formats, and whether they represent a truly diverse and balanced set for the stated capability.

### Required Input Artifacts
*   Benchmark README or Documentation
*   Dataset metadata or Task configurations

### Guidelines for Rating
*   Look for an explicit *Taxonomy* or *Task Categories* section in the README.
*   Verify if the tasks actually map to this taxonomy.
*   A high score of **3** requires diversity in both **domain** (e.g., science, humanities, math) and **format** (e.g., multiple-choice, free-form generation, code execution).
*   Check if the dataset distribution across categories is balanced (e.g., no single category makes up more than 50% of the evaluation unless justified).

---

## Criterion 2.3: Trade-Offs Between Dimensions Exposed (Benchmark, P2)

### Description
Results reveal where a model excels on one metric but fails on another (e.g., accurate but poorly calibrated).

### Detailed 0-3 Rubric
*   **0 (Not Addressed):** Results are presented as a single flat leaderboard score, with no analysis of trade-offs.
*   **1 (Acknowledged):** The documentation mentions that trade-offs exist (e.g., "larger models are slower but more accurate") but provides no data or analysis to support this.
*   **2 (Partially Addressed):** Multiple metrics are plotted or tabulated together (e.g., a table showing both accuracy and latency for all models), allowing the reader to infer trade-offs, but there is no explicit analysis or visualization of the trade-off frontier.
*   **3 (Fully Addressed):** The benchmark explicitly analyzes and visualizes trade-offs (e.g., Pareto frontier plots of accuracy vs. latency, or radar charts showing multi-dimensional profiles), with discussion on how different model families or training methodologies navigate these trade-offs.

### Rating Method
**LLM Auto-rater**

*Rationale:* Detecting the analysis and visualization of trade-offs in documentation and notebooks is a qualitative task suited for an LLM.

### Required Input Artifacts
*   Benchmark README or Documentation
*   Analysis Notebooks or Visualization artifacts (if available)

### Guidelines for Rating
*   Look for visualizations like scatter plots (X-axis: Latency/Cost, Y-axis: Accuracy) or radar/spider charts.
*   Check for text discussing Pareto frontier, efficiency trade-offs, or calibration vs. accuracy.
*   A score of **3** requires active discussion of these trade-offs, helping users choose models based on their specific constraints (e.g., "Model X is best for low-latency needs, while Model Y is best for maximum accuracy").

---

## Criterion 2.4: Model Coverage Breadth (Benchmark, P0)

### Description
The benchmark supports evaluation across a sufficient range of models (API-based and local).

### Detailed 0-3 Rubric
*   **0 (Not Addressed):** The benchmark results only report performance for a single model, or the evaluation pipeline is locked to a single provider.
*   **1 (Acknowledged):** Evaluated on multiple models, but they are all from the same model family or provider (e.g., only tested on Gemini models).
*   **2 (Partially Addressed):** Evaluated on a diverse set of models (at least 3 distinct families/providers), but lacks balance (e.g., only proprietary API models, or only small local models).
*   **3 (Fully Addressed):** Evaluated across a comprehensive and balanced set of models (4+ distinct families), including a mix of proprietary API models (e.g., Gemini, GPT, Claude), open-weights models (e.g., Llama, Gemma, Mistral), and models of varying sizes (small/edge, medium, large/frontier).

### Rating Method
**Deterministic Python Code**

*Rationale:* Model metadata (model names, creators, types) is structured and can be verified deterministically from the run results or leaderboard configuration.

### Required Input Artifacts
*   Run Results (`.run.json` or leaderboard data showing evaluated models)
*   Task configuration (to check supported model integrations)

### Programmatic Rules (for the deterministic part)
1.  Parse the run results to extract all unique model identifiers.
2.  Map each model to its creator/family using a predefined mapping (e.g., `gemini` -> Google, `gpt` -> OpenAI, `claude` -> Anthropic, `llama` -> Meta, `gemma` -> Google, etc.).
3.  Map each model to its type (Proprietary vs. Open-weights) based on the family.
4.  **Rules:**
    *   If unique models count is **1**, assign a score of **0**.
    *   If unique families count is **1**, assign a score of **1**.
    *   If unique families count is **3 or more** but all are Proprietary OR all are Open-weights, assign a score of **2**.
    *   If unique families count is **4 or more** AND includes both Proprietary and Open-weights AND includes different sizes, assign a score of **3**.

### Guidelines for Rating
*   If the programmatic check cannot resolve model families, fall back to manual/LLM check of the model list.
*   *Representative families:* Google (Gemini/Gemma), OpenAI (GPT), Anthropic (Claude), Meta (Llama), Mistral (Mistral/Mixtral).

---

## Criterion 2.5: Informed Choice of Performance Metrics (Benchmark, P0)

### Description
Selected metrics are justified, interpretable, meaningful, and aligned with standard conventions.

### Detailed 0-3 Rubric
*   **0 (Not Addressed):** Metrics are used without any explanation, or the chosen metrics are clearly inappropriate for the task (e.g., using Exact Match for a creative writing task).
*   **1 (Acknowledged):** Standard metrics are used with minimal explanation, ignoring known limitations for the specific task (e.g., using BLEU for translation without addressing its correlation with human judgment).
*   **2 (Partially Addressed):** Metrics are appropriate and their choice is justified in the documentation. Limitations are acknowledged, and simple mitigations are implemented (e.g., using multiple metrics like Rouge AND LLM-eval to balance automated and semantic evaluation).
*   **3 (Fully Addressed):** The metric choice is highly rigorous and thoroughly justified. If using standard metrics, their alignment with the specific task constraints is demonstrated. If using custom metrics (or LLM-as-a-judge), the scoring rubrics are fully documented, validated (e.g., correlation with human judges is reported), and robust to edge cases (e.g., formatting issues, length bias).

### Rating Method
**LLM Auto-rater**

*Rationale:* Evaluating the appropriateness and justification of a metric requires deep semantic understanding of the task domain and evaluation theory.

### Required Input Artifacts
*   Benchmark README or Documentation (specifically Metrics or Evaluation section)
*   Task Notebook or Code (to verify metric implementation details)

### Guidelines for Rating
*   Check if the README has a *Metrics* or *Evaluation Methodology* section.
*   Look for justifications of why these metrics were chosen over alternatives.
*   For LLM-as-a-judge, a score of **3** requires:
    *   Explicit prompt template used for judging.
    *   Description of the judging model used.
    *   Analysis of judge reliability (e.g., self-consistency, correlation with humans).
    *   Mitigations for common biases (position bias, verbosity bias).
