#!/usr/bin/env python3
"""Analyze a rubric rollout: tier separation (primary) + Spearman (secondary).
Usage: python3 analyze.py <results_dir>   e.g. python3 analyze.py baseline
Reads r{1,2,3}_{A,B,C}.json from the dir, ground_truth.json from experiment/.
"""
import json, sys, glob, os
from statistics import mean, pstdev

EXP = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(EXP, sys.argv[1] if len(sys.argv) > 1 else "baseline")
gt = {int(k): v for k, v in json.load(open(os.path.join(EXP, "ground_truth.json"))).items()}

CRITS = ["1_answer_correctness","2_construct_validity","3_code_quality","4_sample_size",
         "5_metric_design","6_problem_statement","7_technical_documentation",
         "8_capability_targeting","9_item_diversity","10_empirical_discrimination",
         "11_contamination_resistance"]

# Collect: per benchmark -> list of (total, criteria-levels-dict) across rollouts
runs = {}  # bench_num -> list of dicts {total, levels}
files = sorted(glob.glob(os.path.join(results_dir, "r*_*.json")))
for f in files:
    for e in json.load(open(f)):
        n = e["benchmark_number"]
        levels = {c: e["criteria"][c]["level"] for c in CRITS}
        runs.setdefault(n, []).append({"total": e["total_score"], "levels": levels})

def spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0]*len(v)
        i = 0
        while i < len(v):
            j = i
            while j+1 < len(v) and v[order[j+1]] == v[order[i]]: j += 1
            avg = (i+j)/2 + 1
            for k in range(i, j+1): r[order[k]] = avg
            i = j+1
        return r
    rx, ry = rank(xs), rank(ys)
    n = len(xs); mx, my = mean(rx), mean(ry)
    num = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    den = (sum((rx[i]-mx)**2 for i in range(n))*sum((ry[i]-my)**2 for i in range(n)))**0.5
    return num/den if den else float('nan')

nums = sorted(runs)
mean_total = {n: mean(r["total"] for r in runs[n]) for n in nums}
std_total  = {n: pstdev([r["total"] for r in runs[n]]) if len(runs[n])>1 else 0.0 for n in nums}

print(f"=== Rollout analysis: {os.path.basename(results_dir)} ===")
print(f"benchmarks: {len(nums)}  rollouts/benchmark: {len(runs[nums[0]])}\n")

# Per-benchmark table sorted by human rating
print(f"{'#':>3} {'human%':>7} {'tier':>6} {'mean':>5} {'std':>5}  title")
for n in sorted(nums, key=lambda x: -gt[x]['human']):
    print(f"{n:>3} {gt[n]['human']:>6.1f}% {gt[n]['tier']:>6} {mean_total[n]:>5.2f} {std_total[n]:>5.2f}  {gt[n]['title'][:46]}")

# Tier separation (PRIMARY)
print("\n--- TIER SEPARATION (primary metric) ---")
tier_scores = {"top":[], "mid":[], "bottom":[]}
for n in nums: tier_scores[gt[n]['tier']].append(mean_total[n])
for t in ["top","mid","bottom"]:
    s = tier_scores[t]
    print(f"  {t:>6}: mean={mean(s):.2f}  range=[{min(s):.2f},{max(s):.2f}]  n={len(s)}")
gap_tm = mean(tier_scores['top']) - mean(tier_scores['mid'])
gap_mb = mean(tier_scores['mid']) - mean(tier_scores['bottom'])
print(f"  gap top-mid:    {gap_tm:+.2f}")
print(f"  gap mid-bottom: {gap_mb:+.2f}")
# clean separation check: does every top > every mid > every bottom?
clean_tm = min(tier_scores['top']) > max(tier_scores['mid'])
clean_mb = min(tier_scores['mid']) > max(tier_scores['bottom'])
print(f"  clean top>mid boundary: {clean_tm}   clean mid>bottom boundary: {clean_mb}")

# Spearman (SECONDARY)
xs = [mean_total[n] for n in nums]
ys = [gt[n]['human'] for n in nums]
print(f"\n--- Spearman rho (secondary): {spearman(xs, ys):.4f} ---")

# Per-criterion discriminative power (variance across benchmarks of mean level)
print("\n--- PER-CRITERION discrimination (mean level across benchmarks + variance) ---")
print(f"{'criterion':>28} {'mean':>5} {'var':>5}")
for c in CRITS:
    per_bench = [mean(r["levels"][c] for r in runs[n]) for n in nums]
    m = mean(per_bench); v = pstdev(per_bench)**2
    print(f"{c:>28} {m:>5.2f} {v:>5.3f}")

# Judge noise: avg within-benchmark std of totals
noise = mean(std_total[n] for n in nums)
print(f"\n--- Judge noise (avg within-benchmark std of total, across rollouts): {noise:.3f} ---")
