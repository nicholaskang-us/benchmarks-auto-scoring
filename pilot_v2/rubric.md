# Kaggle Task Quality Rubric — LLM auto-rater (Criteria 1-3 only)

You are scoring ONE Kaggle Benchmark task on three criteria. You are given an input file with: TASK TITLE, TASK PAGE PROSE (title+description), EVAL DEFINITION (config/code), and NOTEBOOK SOURCE (kernel code+markdown; may be truncated or absent).

Score strictly against the anchors. Be calibrated and skeptical — do not give benefit of the doubt for things not actually present. Output integer levels only.

## Criterion 1 — Answer correctness & construct validity (0/1/2)
Does the task have a verifiable ground truth, and does it actually measure a MODEL on the capability it claims? Compare the CLAIM (task page prose + title) against the IMPLEMENTATION (eval definition + notebook). Trace into the eval logic.
- 0: No verifiable ground truth; OR the evaluation does not measure a model at all (asserts on hardcoded values / the task's own data structures, never calls/grades a model output); OR clear mismatch between what the task claims and what the code measures.
- 1: Ground truth exists and a model is genuinely evaluated, but with moderate confounds — fragile verification (e.g. exact match without normalization) or implementation partially conflates the target capability with unrelated skills (formatting, instruction-following).
- 2: Answers unambiguous and verifiable (exact/regex/tolerance/deterministic assertions, or a multi-dimensional LLM-judge rubric) AND implementation tightly aligned with the claimed capability, confounds minimized by deliberate design.

## Criterion 2 — Problem statement (0/1/2) — TASK PAGE PROSE ONLY
Judge ONLY the TASK PAGE PROSE (title + description). Do NOT use the notebook or definition for this criterion. Code quality does not count.
- 0: No problem statement, or so unclear a reader cannot tell what the task measures or why it exists. (An empty/near-empty description = 0.)
- 1: Names the target capability and gives basic motivation, but does not connect it to a broader question or explain the gap it fills.
- 2: Specific, compelling statement that names the exact capability, explains why it matters, and identifies the gap it fills relative to existing evaluations.

## Criterion 3 — Documentation (0/1/2) — TASK PAGE + NOTEBOOK
Are dataset, methodology, and scoring documented well enough to understand and reproduce? Consult task page AND notebook markdown/comments.
- 0: No documentation of dataset provenance, evaluation protocol, or scoring. A reader must reverse-engineer the code.
- 1: Partial — some key areas covered (e.g. dataset source OR method) but missing details like schema, scoring edge cases, or metric interpretation.
- 2: Comprehensive across one or both artifacts: dataset provenance/schema, evaluation methodology and scoring rules, metric definitions, and a step-by-step walkthrough in notebook markdown.

## Output
Write ONLY a JSON object to the specified output path:
{"task_id":"<id>","crit1":<0-2>,"crit2":<0-2>,"crit3":<0-2>,"notes1":"<=200 chars why","notes2":"<=200 chars why","notes3":"<=200 chars why"}
Notes must cite concrete evidence (what you saw or didn't see). Keep each note under 200 characters.
