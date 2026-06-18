#!/usr/bin/env python3
import json
import glob
import os

EXP = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(EXP, "v3")
output_dir = os.path.join(EXP, "v4")
model_results_path = os.path.join(EXP, "model_run_results.json")
contamination_results_path = os.path.join(EXP, "contamination_results.json")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load model scores
with open(model_results_path, "r") as f:
    model_results = json.load(f)

# Load contamination scores
with open(contamination_results_path, "r") as f:
    contamination_results = json.load(f)

print(f"Loaded model results for {len(model_results)} and contamination results for {len(contamination_results)} benchmarks.")

# Read all rollout files from v3
rollout_files = glob.glob(os.path.join(input_dir, "r*_*.json"))
print(f"Found {len(rollout_files)} rollout files in {input_dir}.")

for r_file in rollout_files:
    filename = os.path.basename(r_file)
    with open(r_file, "r") as f:
        data = json.load(f)
    
    updated_data = []
    for entry in data:
        bench_num = str(entry["benchmark_number"])
        
        # --- 1. Empirical Discrimination (Criterion 10) ---
        scores_dict = model_results.get(bench_num, {})
        if not scores_dict:
            disc_level = 0
            disc_justification = "Empirical Discrimination: Level 0. No reference model scores found (no execution telemetry or empty task)."
        else:
            scores = list(scores_dict.values())
            spread = max(scores) - min(scores)
            count = len(scores)
            
            if spread >= 0.30:
                disc_level = 2
                disc_justification = f"Empirical Discrimination: Level 2. Strong capability separation with a spread of {spread:.2f} (Max: {max(scores):.2f}, Min: {min(scores):.2f}) across {count} reference models."
            elif spread >= 0.10:
                disc_level = 1
                disc_justification = f"Empirical Discrimination: Level 1. Moderate capability separation with a spread of {spread:.2f} (Max: {max(scores):.2f}, Min: {min(scores):.2f}) across {count} reference models."
            else:
                disc_level = 0
                disc_justification = f"Empirical Discrimination: Level 0. Weak or no capability separation with a spread of {spread:.2f} (Max: {max(scores):.2f}, Min: {min(scores):.2f}) across {count} reference models."
        
        # --- 2. Contamination Resistance (Criterion 11) ---
        contam_dict = contamination_results.get(bench_num, {})
        if not contam_dict:
            contam_level = 0
            contam_justification = "Contamination Resistance: Level 0. No check telemetry available."
        else:
            leakage = contam_dict["prompt_leakage_detected"]
            hits = contam_dict["web_search_hits"]
            overlap = contam_dict["corpus_overlap_ngram_pct"]
            
            if leakage or hits >= 5 or overlap >= 0.20:
                contam_level = 0
                contam_justification = f"Contamination Resistance: Level 0. Prompt leakage detected or public index overlap is high. Leakage flag: {leakage}, Search hits: {hits}, Corpus overlap: {overlap*100:.1f}%."
            elif hits > 0 or overlap >= 0.05:
                contam_level = 1
                contam_justification = f"Contamination Resistance: Level 1. Minor leakage or template matching suspected. Search hits: {hits}, Corpus overlap: {overlap*100:.1f}%."
            else:
                contam_level = 2
                contam_justification = f"Contamination Resistance: Level 2. Clean evaluation items. No leakage detected, 0 search hits, and negligible corpus overlap ({overlap*100:.1f}%)."

        # Update criteria (Remove model_coverage, add v4 criteria)
        entry["criteria"].pop("10_model_coverage", None)
        entry["criteria"]["10_empirical_discrimination"] = {
            "level": disc_level,
            "justification": disc_justification
        }
        entry["criteria"]["11_contamination_resistance"] = {
            "level": contam_level,
            "justification": contam_justification
        }
        
        # --- 3. Recalculate total score with v4 weights ---
        # Category A (1_answer_correctness to 5_metric_design) -> Level * 0.5
        # Category B (6_problem_statement to 7_technical_documentation) -> Level * 0.5
        # Category C (8_capability_targeting to 11_contamination_resistance) -> Level * 0.375
        
        total = 0.0
        for crit, info in entry["criteria"].items():
            if crit in ["1_answer_correctness", "2_construct_validity", "3_code_quality", "4_sample_size", "5_metric_design",
                        "6_problem_statement", "7_technical_documentation"]:
                total += info["level"] * 0.5
            elif crit in ["8_capability_targeting", "9_item_diversity", "10_empirical_discrimination", "11_contamination_resistance"]:
                total += info["level"] * 0.375
        
        entry["total_score"] = round(total, 2)
        updated_data.append(entry)
    
    # Save the updated rollout file
    out_file = os.path.join(output_dir, filename)
    with open(out_file, "w") as f:
        json.dump(updated_data, f, indent=2)
    print(f"Updated and saved: {out_file}")

print("Completed successfully!")
