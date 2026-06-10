#!/usr/bin/env python3
import json
import glob
import os

EXP = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(EXP, "v3")
output_dir = os.path.join(EXP, "v3_empirical")
results_path = os.path.join(EXP, "model_run_results.json")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load model scores
with open(results_path, "r") as f:
    model_results = json.load(f)

print(f"Loaded model results for {len(model_results)} benchmarks.")

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
        scores_dict = model_results.get(bench_num, {})
        
        # Determine empirical discrimination level
        if not scores_dict:
            level = 0
            justification = "Empirical Discrimination: Level 0. No reference model scores found (no execution telemetry or empty task)."
        else:
            scores = list(scores_dict.values())
            spread = max(scores) - min(scores)
            count = len(scores)
            
            if spread >= 0.30:
                level = 2
                justification = f"Empirical Discrimination: Level 2. Strong capability separation with a spread of {spread:.2f} (Max: {max(scores):.2f}, Min: {min(scores):.2f}) across {count} reference models."
            elif spread >= 0.10:
                level = 1
                justification = f"Empirical Discrimination: Level 1. Moderate capability separation with a spread of {spread:.2f} (Max: {max(scores):.2f}, Min: {min(scores):.2f}) across {count} reference models."
            else:
                level = 0
                justification = f"Empirical Discrimination: Level 0. Weak or no capability separation with a spread of {spread:.2f} (Max: {max(scores):.2f}, Min: {min(scores):.2f}) across {count} reference models."
        
        # Update Criterion 10
        entry["criteria"]["10_model_coverage"] = {
            "level": level,
            "justification": justification
        }
        
        # Recalculate total score
        total = 0.0
        for crit, info in entry["criteria"].items():
            total += info["level"] * 0.5
        
        entry["total_score"] = round(total, 2)
        updated_data.append(entry)
    
    # Save the updated rollout file
    out_file = os.path.join(output_dir, filename)
    with open(out_file, "w") as f:
        json.dump(updated_data, f, indent=2)
    print(f"Updated and saved: {out_file}")

print("Completed successfully!")
