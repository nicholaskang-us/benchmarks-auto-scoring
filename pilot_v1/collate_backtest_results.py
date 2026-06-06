import json
import csv
import os
import re

def clean_name(name):
    name = re.sub(r'\s+', ' ', name).strip().lower()
    name = name.replace('’', "'").replace('—', '-').replace('-', '-')
    return name

def main():
    eval_a_path = "/usr/local/google/home/nicholaskang/.gemini/jetski/brain/32c7545d-8652-4893-a8ec-6b46770566b4/scratch/evaluations.json"
    eval_b_path = "/tmp/benchmark_scores.json"
    eval_c_path = "/tmp/subagent_c_scores.json"
    rankings_csv_path = "/tmp/competitions-prep/misc/agi_hackathon_judge/score_calibration/calibration_output_0604/calibrated_rankings.csv"
    
    # Target benchmark mappings
    target_mappings = {
        "behavioral metacognitive control on expert questions in llms": {
            "tier": "top",
            "csv_name": "Behavioral Metacognitive Control on Expert Questions in LLMs"
        },
        "russian doll bench: infrastructure building capabilities": {
            "tier": "top",
            "csv_name": "Russian Doll Bench: Infrastructure Building Capabilities"
        },
        "riac - repetition-induced attention collapse": {
            "tier": "top",
            "csv_name": "RIAC - Repetition-Induced Attention Collapse"
        },
        "riac": {
            "tier": "top",
            "csv_name": "RIAC - Repetition-Induced Attention Collapse"
        },
        "can llms inhibit optimization in supply-chain decision-making?": {
            "tier": "top",
            "csv_name": "Can LLMs Inhibit Optimization in Supply-Chain Decision-Making?"
        },
        "the time traveler's dilemma: empathy, oversight, & the stop sign effect": {
            "tier": "top",
            "csv_name": "The Time Traveler's Dilemma: Empathy, Oversight, & the Stop Sign Effect"
        },
        "ittia - i think therefore i am": {
            "tier": "middle",
            "csv_name": "ITTIA - I think therefore I am"
        },
        "embodied inhibitory control in animalai": {
            "tier": "middle",
            "csv_name": "Embodied Inhibitory Control in AnimalAI"
        },
        "social cognition - understanding the mind of agents and semantics": {
            "tier": "middle",
            "csv_name": "Social Cognition - Understanding The Mind of Agents and Semantics"
        },
        "social cognition": {
            "tier": "middle",
            "csv_name": "Social Cognition - Understanding The Mind of Agents and Semantics"
        },
        "adversarial cognitive profiling (acp): metacognitive calibration benchmark": {
            "tier": "middle",
            "csv_name": "Adversarial Cognitive Profiling (ACP): Metacognitive Calibration Benchmark"
        },
        "observe-reason-learn-verify-adapt-loop": {
            "tier": "middle",
            "csv_name": "Observe-Reason-Learn-Verify-Adapt-Loop"
        },
        "stratagem-sc: strategic theory-of-mind benchmark for social cognition": {
            "tier": "bottom",
            "csv_name": "STRATAGEM-SC: Strategic Theory-of-Mind Benchmark for Social Cognition"
        },
        "temporalbench: validity windows beat decay functions in temporal reasoning": {
            "tier": "bottom",
            "csv_name": "TemporalBench: Validity Windows Beat Decay Functions in Temporal Reasoning"
        },
        "temporalbench": {
            "tier": "bottom",
            "csv_name": "TemporalBench: Validity Windows Beat Decay Functions in Temporal Reasoning"
        },
        "executive functions: the cognitive control suite": {
            "tier": "bottom",
            "csv_name": "Executive Functions: The Cognitive Control Suite"
        },
        "the efficiency paradox: measuring heuristic capture in vehicle-centric planning": {
            "tier": "bottom",
            "csv_name": "The Efficiency Paradox: Measuring Heuristic Capture in Vehicle-Centric Planning"
        },
        "the efficiency paradox: measuring heuristic capture": {
            "tier": "bottom",
            "csv_name": "The Efficiency Paradox: Measuring Heuristic Capture in Vehicle-Centric Planning"
        },
        "constraint adaptation benchmark (cab)": {
            "tier": "bottom",
            "csv_name": "Constraint Adaptation Benchmark (CAB)"
        }
    }

    # Group tasks by matched benchmark
    benchmarks_tasks = {}
    
    # Rubric weights
    weights = {
        "answer_correctness": 0.35,
        "prompt_clarity": 0.35,
        "capability_targeting": 0.30,
        "code_quality": 0.50,
        "documentation": 0.50
    }

    # Load Subagent A (flat list of tasks)
    with open(eval_a_path, "r") as f:
        tasks_a = json.load(f)
        for t in tasks_a:
            b_name = t.get("benchmark_name")
            if not b_name:
                continue
            
            # Match b_name to target
            clean_b = clean_name(b_name)
            matched_key = None
            for key in target_mappings:
                if clean_name(key) == clean_b or clean_b == clean_name(key):
                    matched_key = key
                    break
            if not matched_key:
                # Try substring check
                for key in target_mappings:
                    if clean_name(key) in clean_b or clean_b in clean_name(key):
                        matched_key = key
                        break
            if not matched_key:
                print(f"Warning: A - Could not match '{b_name}'")
                continue
                
            csv_name = target_mappings[matched_key]["csv_name"]
            if csv_name not in benchmarks_tasks:
                benchmarks_tasks[csv_name] = []
                
            # Extract criteria levels
            evaluation = t.get("evaluation", {})
            task_scores = {}
            for crit in weights:
                crit_data = evaluation.get(crit, {})
                task_scores[crit] = int(crit_data.get("level", 0))
            benchmarks_tasks[csv_name].append(task_scores)
            
    # Load Subagent B
    with open(eval_b_path, "r") as f:
        benchmarks_b = json.load(f)
        for b in benchmarks_b:
            b_name = b.get("benchmark_name")
            if not b_name:
                continue
                
            clean_b = clean_name(b_name)
            matched_key = None
            for key in target_mappings:
                if clean_name(key) == clean_b or clean_b == clean_name(key):
                    matched_key = key
                    break
            if not matched_key:
                for key in target_mappings:
                    if clean_name(key) in clean_b or clean_b in clean_name(key):
                        matched_key = key
                        break
            if not matched_key:
                print(f"Warning: B - Could not match '{b_name}'")
                continue
                
            csv_name = target_mappings[matched_key]["csv_name"]
            if csv_name not in benchmarks_tasks:
                benchmarks_tasks[csv_name] = []
                
            for t in b.get("tasks", []):
                llm_scores = t.get("llm_scores", {})
                task_scores = {}
                for crit in weights:
                    crit_data = llm_scores.get(crit, {})
                    task_scores[crit] = int(crit_data.get("level", 0))
                benchmarks_tasks[csv_name].append(task_scores)

    # Load Subagent C
    with open(eval_c_path, "r") as f:
        benchmarks_c = json.load(f)
        for b in benchmarks_c:
            b_name = b.get("benchmark_name")
            if not b_name:
                continue
                
            clean_b = clean_name(b_name)
            matched_key = None
            for key in target_mappings:
                if clean_name(key) == clean_b or clean_b == clean_name(key):
                    matched_key = key
                    break
            if not matched_key:
                for key in target_mappings:
                    if clean_name(key) in clean_b or clean_b in clean_name(key):
                        matched_key = key
                        break
            if not matched_key:
                print(f"Warning: C - Could not match '{b_name}'")
                continue
                
            csv_name = target_mappings[matched_key]["csv_name"]
            if csv_name not in benchmarks_tasks:
                benchmarks_tasks[csv_name] = []
                
            for t in b.get("tasks", []):
                llm_scores = t.get("llm_scores", {})
                task_scores = {}
                for crit in weights:
                    crit_data = llm_scores.get(crit, {})
                    task_scores[crit] = int(crit_data.get("level", 0))
                benchmarks_tasks[csv_name].append(task_scores)

    # Load rankings CSV
    rankings = []
    with open(rankings_csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rankings.append(row)

    output_rows = []
    for csv_name, task_list in benchmarks_tasks.items():
        if not task_list:
            continue
            
        num_tasks = len(task_list)
        
        # Get tier
        tier = None
        for key, val in target_mappings.items():
            if val["csv_name"] == csv_name:
                tier = val["tier"]
                break
                
        # Look up human calibrated score and rank in Rankings CSV
        human_row = None
        for row in rankings:
            if clean_name(row["Project Name"]) == clean_name(csv_name):
                human_row = row
                break
        if not human_row:
            # Substring match
            for row in rankings:
                if clean_name(row["Project Name"]) in clean_name(csv_name) or clean_name(csv_name) in clean_name(row["Project Name"]):
                    human_row = row
                    break
                    
        if not human_row:
            print(f"Warning: Could not find human calibrated rank for '{csv_name}'.")
            human_rank = ""
            human_score = ""
        else:
            human_rank = int(human_row["Rank"])
            human_score = float(human_row["Calibrated Total (%)"])

        # Compute averages
        avg_scores = {}
        for crit in weights:
            avg_scores[f"{crit}_level"] = sum(t[crit] for t in task_list) / num_tasks
            avg_scores[f"{crit}_score"] = (sum(t[crit] * weights[crit] for t in task_list)) / num_tasks

        # Calculate benchmark subtotal
        llm_subtotal = sum(avg_scores[f"{crit}_score"] for crit in weights)
        llm_subtotal_normalized = (llm_subtotal / 4.0) * 10
        
        row_data = {
            "rank": human_rank,
            "benchmark_name": csv_name,
            "tier": tier,
            "human_calibrated_pct": human_score,
            "answer_correctness_level": round(avg_scores["answer_correctness_level"], 2),
            "answer_correctness_score": round(avg_scores["answer_correctness_score"], 2),
            "prompt_clarity_level": round(avg_scores["prompt_clarity_level"], 2),
            "prompt_clarity_score": round(avg_scores["prompt_clarity_score"], 2),
            "capability_targeting_level": round(avg_scores["capability_targeting_level"], 2),
            "capability_targeting_score": round(avg_scores["capability_targeting_score"], 2),
            "code_quality_level": round(avg_scores["code_quality_level"], 2),
            "code_quality_score": round(avg_scores["code_quality_score"], 2),
            "documentation_level": round(avg_scores["documentation_level"], 2),
            "documentation_score": round(avg_scores["documentation_score"], 2),
            "llm_subtotal": round(llm_subtotal, 2),
            "llm_subtotal_normalized_to_10": round(llm_subtotal_normalized, 2)
        }
        output_rows.append(row_data)

    # Sort output rows by human rank
    output_rows.sort(key=lambda x: x["rank"] if isinstance(x["rank"], int) else 9999)
    
    # Save output CSV
    out_dir = "/usr/local/google/home/nicholaskang/.gemini/jetski/brain/0eb36fbc-7223-46d0-9dc5-a7f6fc62371d/scratch"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "backtest_results.csv")
    
    headers = [
        "rank", "benchmark_name", "tier", "human_calibrated_pct",
        "answer_correctness_level", "answer_correctness_score",
        "prompt_clarity_level", "prompt_clarity_score",
        "capability_targeting_level", "capability_targeting_score",
        "code_quality_level", "code_quality_score",
        "documentation_level", "documentation_score",
        "llm_subtotal", "llm_subtotal_normalized_to_10"
    ]
    
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(output_rows)
        
    print(f"\nSuccessfully wrote {len(output_rows)} rows to {out_path}")

if __name__ == "__main__":
    main()
