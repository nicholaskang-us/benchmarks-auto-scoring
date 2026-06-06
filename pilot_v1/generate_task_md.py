import json
import csv
import os
import re

def clean_name(name):
    name = re.sub(r'\s+', ' ', name).strip().lower()
    name = name.replace('’', "'").replace('—', '-').replace('-', '-')
    return name

def normalize_string(name):
    # Remove all non-alphanumeric characters
    return re.sub(r'[^a-z0-9]', '', name.lower())

def main():
    links_file = "/usr/local/google/home/nicholaskang/benchmarks-auto-scoring/pilot_v1/agi_hackathon_benchmark_links.md"
    eval_a_path = "/usr/local/google/home/nicholaskang/.gemini/jetski/brain/32c7545d-8652-4893-a8ec-6b46770566b4/scratch/evaluations.json"
    eval_b_path = "/tmp/benchmark_scores.json"
    eval_c_path = "/tmp/subagent_c_scores.json"
    rankings_csv_path = "/tmp/competitions-prep/misc/agi_hackathon_judge/score_calibration/calibration_output_0604/calibrated_rankings.csv"
    out_md_path = "/usr/local/google/home/nicholaskang/benchmarks-auto-scoring/pilot_v1/task_level_results.md"

    # --- 1. Parse agi_hackathon_benchmark_links.md for URLs ---
    benchmark_urls = {} # clean_name -> benchmark_url
    task_urls = {}      # (clean_benchmark_name, clean_task_slug_no_spaces) -> task_url

    with open(links_file, "r") as f:
        lines = f.readlines()

    current_bench_name = None
    current_bench_url = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Parse benchmark header
        if line.startswith("## "):
            m = re.match(r'^##\s+\d+\.\s*(.*)', line)
            if m:
                current_bench_name = m.group(1).strip()
                current_bench_url = None
            continue
            
        # Parse benchmark URL
        if current_bench_name and "**Benchmark URL:**" in line:
            m = re.search(r'\(https://www.kaggle.com/benchmarks/[^\)]+\)', line)
            if m:
                current_bench_url = m.group(0)[1:-1]
                benchmark_urls[clean_name(current_bench_name)] = current_bench_url
            continue
            
        # Parse task lines
        if current_bench_name and line.startswith("*") and "**Task" in line:
            slug_match = re.search(r'\[(.*?)\]\((https://www.kaggle.com/benchmarks/tasks/[^\)]+)\)', line)
            if slug_match:
                task_slug = slug_match.group(1)
                task_url = slug_match.group(2)
                task_urls[(clean_name(current_bench_name), normalize_string(task_slug))] = task_url

    # Add fallback mappings for writeup names to clean names
    name_replacements = {
        "riac": "RIAC - Repetition-Induced Attention Collapse",
        "can llms inhibit optimization in supply-chain decision-making?": "Can LLMs Inhibit Optimization in Supply-Chain Decision-Making?",
        "embodied inhibitory control in animalai": "Embodied Inhibitory Control in AnimalAI",
        "observe-reason-learn-verify-adapt-loop": "Observe-Reason-Learn-Verify-Adapt-Loop",
        "executive functions: the cognitive control suite": "Executive Functions: The Cognitive Control Suite",
        "behavioral metacognitive control on expert questions in llms": "Behavioral Metacognitive Control on Expert Questions in LLMs",
        "ittia - i think therefore i am": "ITTIA - I think therefore I am",
        "social cognition - understanding the mind of agents and semantics": "Social Cognition - Understanding The Mind of Agents and Semantics",
        "stratagem-sc: strategic theory-of-mind benchmark for social cognition": "STRATAGEM-SC: Strategic Theory-of-Mind Benchmark for Social Cognition",
        "the efficiency paradox: measuring heuristic capture in vehicle-centric planning": "The Efficiency Paradox: Measuring Heuristic Capture in Vehicle-Centric Planning",
        "russian doll bench: infrastructure building capabilities": "Russian Doll Bench: Infrastructure Building Capabilities",
        "the time traveler's dilemma: empathy, oversight, & the stop sign effect": "The Time Traveler's Dilemma: Empathy, Oversight, & the Stop Sign Effect",
        "adversarial cognitive profiling (acp): metacognitive calibration benchmark": "Adversarial Cognitive Profiling (ACP): Metacognitive Calibration Benchmark",
        "temporalbench: validity windows beat decay functions in temporal reasoning": "TemporalBench: Validity Windows Beat Decay Functions in Temporal Reasoning",
        "constraint adaptation benchmark (cab)": "Constraint Adaptation Benchmark (CAB)"
    }

    # Task Synonyms Map to resolve non-matching slugs Fuzzily
    task_synonyms = {
        "repetition-induced attention collapse (numbers)": "riac-bench-number-repetition",
        "repetition-induced attention collapse (words)": "riac-bench-word-repetition",
        "repetition-induced attention collapse (symbols)": "riac-bench-symbol-repetition",
        "repetition-induced attention collapse (noise)": "riac-bench-noise",
        "animalai control task": "animalai-task",
        "temporalbench-v1-causalquery": "causalreasoning",
        "code golf benchmark": "code-golf-task",
        "embedding geometry awareness test | tier 1: shared semantic space com convergence": "egat-tier1-shared-semantic-space"
    }

    # --- 2. Load rankings for human calibrated judge rating ---
    human_ratings = {} # clean_name -> rating
    with open(rankings_csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            human_ratings[clean_name(row["Project Name"])] = float(row["Calibrated Total (%)"])

    # --- 3. Process all task-level scores from the three subagents ---
    tasks_rows = []
    weights = {
        "answer_correctness": 0.35,
        "prompt_clarity": 0.35,
        "capability_targeting": 0.30,
        "code_quality": 0.50,
        "documentation": 0.50
    }

    # Helper function to find matching URL from our maps
    def get_urls(b_name, t_name):
        clean_b = clean_name(b_name)
        standard_b_name = None
        for k, v in name_replacements.items():
            if clean_name(k) == clean_b or clean_b in clean_name(k) or clean_name(k) in clean_b:
                standard_b_name = v
                break
        if not standard_b_name:
            standard_b_name = b_name

        # Match benchmark URL fuzzily
        b_url = ""
        clean_standard_b = clean_name(standard_b_name)
        for k, v in benchmark_urls.items():
            if k == clean_standard_b or k in clean_standard_b or clean_standard_b in k:
                b_url = v
                break
        
        # Match task URL using synonyms or similarity matching with fuzzy benchmark matching too
        lookup_t_name = t_name
        clean_t_lower = t_name.strip().lower()
        if clean_t_lower in task_synonyms:
            lookup_t_name = task_synonyms[clean_t_lower]

        norm_t = normalize_string(lookup_t_name)
        t_url = ""
        for (cb, ct), url in task_urls.items():
            if cb == clean_standard_b or cb in clean_standard_b or clean_standard_b in cb:
                # Check if normalized strings match or one is substring of the other
                if ct == norm_t or norm_t in ct or ct in norm_t:
                    t_url = url
                    break
        return standard_b_name, b_url, t_url

    # Subagent A
    with open(eval_a_path, "r") as f:
        data_a = json.load(f)
        for item in data_a:
            b_name = item.get("benchmark_name")
            t_name = item.get("task_name")
            if not b_name or not t_name:
                continue
            
            standard_b, b_url, t_url = get_urls(b_name, t_name)
            evaluation = item.get("evaluation", {})
            
            row = {
                "benchmark_name": standard_b,
                "benchmark_url": b_url,
                "task_name": t_name,
                "task_url": t_url
            }
            subtotal = 0.0
            for crit in weights:
                crit_data = evaluation.get(crit, {})
                lvl = int(crit_data.get("level", 0))
                score = lvl * weights[crit]
                subtotal += score
                row[f"{crit}_score"] = round(score, 2)
                row[f"{crit}_justification"] = crit_data.get("justification", "")
                
            row["sum_of_scores"] = round(subtotal, 2)
            row["human_calibrated_judge_rating"] = human_ratings.get(clean_name(standard_b), "")
            tasks_rows.append(row)

    # Subagent B
    with open(eval_b_path, "r") as f:
        data_b = json.load(f)
        for b in data_b:
            b_name = b.get("benchmark_name")
            for t in b.get("tasks", []):
                t_name = t.get("task_name")
                standard_b, b_url, t_url = get_urls(b_name, t_name)
                llm_scores = t.get("llm_scores", {})
                
                row = {
                    "benchmark_name": standard_b,
                    "benchmark_url": b_url,
                    "task_name": t_name,
                    "task_url": t_url
                }
                subtotal = 0.0
                for crit in weights:
                    crit_data = llm_scores.get(crit, {})
                    lvl = int(crit_data.get("level", 0))
                    score = lvl * weights[crit]
                    subtotal += score
                    row[f"{crit}_score"] = round(score, 2)
                    row[f"{crit}_justification"] = crit_data.get("justification", "")
                    
                row["sum_of_scores"] = round(subtotal, 2)
                row["human_calibrated_judge_rating"] = human_ratings.get(clean_name(standard_b), "")
                tasks_rows.append(row)

    # Subagent C
    with open(eval_c_path, "r") as f:
        data_c = json.load(f)
        for b in data_c:
            b_name = b.get("benchmark_name")
            for t in b.get("tasks", []):
                t_name = t.get("task_name")
                standard_b, b_url, t_url = get_urls(b_name, t_name)
                llm_scores = t.get("llm_scores", {})
                
                row = {
                    "benchmark_name": standard_b,
                    "benchmark_url": b_url,
                    "task_name": t_name,
                    "task_url": t_url
                }
                subtotal = 0.0
                for crit in weights:
                    crit_data = llm_scores.get(crit, {})
                    lvl = int(crit_data.get("level", 0))
                    score = lvl * weights[crit]
                    subtotal += score
                    row[f"{crit}_score"] = round(score, 2)
                    row[f"{crit}_justification"] = crit_data.get("justification", "")
                    
                row["sum_of_scores"] = round(subtotal, 2)
                row["human_calibrated_judge_rating"] = human_ratings.get(clean_name(standard_b), "")
                tasks_rows.append(row)

    # --- 4. Write to Markdown Table ---
    with open(out_md_path, "w") as f:
        f.write("# Task-Level Results\n\n")
        
        headers = [
            "Benchmark (URL)", "Task (URL)",
            "Answer Correctness Score", "Answer Correctness Justification",
            "Prompt Clarity Score", "Prompt Clarity Justification",
            "Capability Targeting Score", "Capability Targeting Justification",
            "Code Quality Score", "Code Quality Justification",
            "Documentation Score", "Documentation Justification",
            "Sum of Scores", "Human Calibrated Judge Rating"
        ]
        
        f.write(" | ".join(headers) + "\n")
        f.write(" | ".join(["---"] * len(headers)) + "\n")
        
        for r in tasks_rows:
            b_link = f"[{r['benchmark_name']}]({r['benchmark_url']})" if r['benchmark_url'] else r['benchmark_name']
            t_link = f"[{r['task_name']}]({r['task_url']})" if r['task_url'] else r['task_name']
            
            # Clean justifications of any line breaks to keep markdown table row valid
            for k in r:
                if isinstance(r[k], str):
                    r[k] = r[k].replace("\n", " ").replace("\r", "")
            
            row_vals = [
                b_link,
                t_link,
                str(r["answer_correctness_score"]), r["answer_correctness_justification"],
                str(r["prompt_clarity_score"]), r["prompt_clarity_justification"],
                str(r["capability_targeting_score"]), r["capability_targeting_justification"],
                str(r["code_quality_score"]), r["code_quality_justification"],
                str(r["documentation_score"]), r["documentation_justification"],
                str(r["sum_of_scores"]),
                f"{r['human_calibrated_judge_rating']}%" if r['human_calibrated_judge_rating'] != "" else ""
            ]
            f.write(" | ".join(row_vals) + "\n")

    print(f"Successfully wrote {len(tasks_rows)} rows to {out_md_path}")

if __name__ == "__main__":
    main()
