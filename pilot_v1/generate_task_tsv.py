import json
import csv
import os
import re

def clean_name(name):
    name = re.sub(r'\s+', ' ', name).strip().lower()
    name = name.replace('’', "'").replace('—', '-').replace('-', '-')
    return name

def main():
    links_file = "/usr/local/google/home/nicholaskang/benchmarks-auto-scoring/pilot_v1/agi_hackathon_benchmark_links.md"
    eval_a_path = "/usr/local/google/home/nicholaskang/.gemini/jetski/brain/32c7545d-8652-4893-a8ec-6b46770566b4/scratch/evaluations.json"
    eval_b_path = "/tmp/benchmark_scores.json"
    eval_c_path = "/tmp/subagent_c_scores.json"
    rankings_csv_path = "/tmp/competitions-prep/misc/agi_hackathon_judge/score_calibration/calibration_output_0604/calibrated_rankings.csv"
    out_tsv_path = "/usr/local/google/home/nicholaskang/benchmarks-auto-scoring/pilot_v1/task_level_results.tsv"

    # --- 1. Parse agi_hackathon_benchmark_links.md for URLs ---
    benchmark_urls = {} # clean_name -> benchmark_url
    task_urls = {}      # (clean_benchmark_name, clean_task_name/slug) -> task_url

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
            # e.g., "## 1. Behavioral Metacognitive Control on Expert Questions in LLMs"
            m = re.match(r'^##\s+\d+\.\s*(.*)', line)
            if m:
                current_bench_name = m.group(1).strip()
                current_bench_url = None
            continue
            
        # Parse benchmark URL
        if current_bench_name and "**Benchmark URL:**" in line:
            # e.g., "*   **Benchmark URL:** [msv-metacognition-benchmark](https://www.kaggle.com/benchmarks/professorsethi/msv-metacognition-benchmark)"
            m = re.search(r'\(https://www.kaggle.com/benchmarks/[^\)]+\)', line)
            if m:
                current_bench_url = m.group(0)[1:-1]
                benchmark_urls[clean_name(current_bench_name)] = current_bench_url
            continue
            
        # Parse task lines
        if current_bench_name and line.startswith("*") and "**Task" in line:
            # e.g., "*   **Task 1:** [t01-msv-delegate-game](https://www.kaggle.com/benchmarks/tasks/professorsethi/t01-msv-delegate-game/4) | [Notebook](...)"
            # Extract task name/slug and task URL
            slug_match = re.search(r'\[(.*?)\]\((https://www.kaggle.com/benchmarks/tasks/[^\)]+)\)', line)
            if slug_match:
                task_slug = slug_match.group(1)
                task_url = slug_match.group(2)
                task_urls[(clean_name(current_bench_name), clean_name(task_slug))] = task_url

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
        # Find matched benchmark standard name
        standard_b_name = None
        for k, v in name_replacements.items():
            if clean_name(k) == clean_b or clean_b in clean_name(k) or clean_name(k) in clean_b:
                standard_b_name = v
                break
        if not standard_b_name:
            standard_b_name = b_name

        b_url = benchmark_urls.get(clean_name(standard_b_name), "")
        
        # Match task URL
        clean_t = clean_name(t_name)
        t_url = ""
        # Search task urls keys for matching (clean_b, clean_t)
        for (cb, ct), url in task_urls.items():
            if cb == clean_name(standard_b_name):
                # Check if task slug matches
                if ct == clean_t or clean_t in ct or ct in clean_t:
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

    # --- 4. Write to TSV ---
    headers = [
        "benchmark (url)", "task (url)",
        "answer_correctness_score", "answer_correctness_justification",
        "prompt_clarity_score", "prompt_clarity_justification",
        "capability_targeting_score", "capability_targeting_justification",
        "code_quality_score", "code_quality_justification",
        "documentation_score", "documentation_justification",
        "sum_of_scores", "human_calibrated_judge_rating"
    ]

    with open(out_tsv_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(headers)
        for r in tasks_rows:
            # Build benchmark (url) and task (url) Markdown links or plain strings
            b_link = f"[{r['benchmark_name']}]({r['benchmark_url']})" if r['benchmark_url'] else r['benchmark_name']
            t_link = f"[{r['task_name']}]({r['task_url']})" if r['task_url'] else r['task_name']
            
            row_vals = [
                b_link,
                t_link,
                r["answer_correctness_score"], r["answer_correctness_justification"],
                r["prompt_clarity_score"], r["prompt_clarity_justification"],
                r["capability_targeting_score"], r["capability_targeting_justification"],
                r["code_quality_score"], r["code_quality_justification"],
                r["documentation_score"], r["documentation_justification"],
                r["sum_of_scores"],
                r["human_calibrated_judge_rating"]
            ]
            writer.writerow(row_vals)

    print(f"Successfully wrote {len(tasks_rows)} rows to {out_tsv_path}")

if __name__ == "__main__":
    main()
