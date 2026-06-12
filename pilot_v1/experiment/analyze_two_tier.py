#!/usr/bin/env python3
import json
import glob
import os
import sys
from statistics import mean, pstdev

EXP = os.path.dirname(os.path.abspath(__file__))
v4_dir = os.path.join(EXP, "v4")
v5_dir = os.path.join(EXP, "v5")
gt = {int(k): v for k, v in json.load(open(os.path.join(EXP, "ground_truth.json"))).items()}

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

# Collect scores across v4 runs
v4_runs = {} # bench_num -> list of total scores
v4_files = sorted(glob.glob(os.path.join(v4_dir, "r*_*.json")))
for f in v4_files:
    for e in json.load(open(f)):
        n = e["benchmark_number"]
        v4_runs.setdefault(n, []).append(e["total_score"])

# Collect scores across v5 runs
v5_runs = {} # bench_num -> list of dicts {pre_run, post_run}
v5_files = sorted(glob.glob(os.path.join(v5_dir, "r*_*.json")))
for f in v5_files:
    for e in json.load(open(f)):
        n = e["benchmark_number"]
        v5_runs.setdefault(n, []).append({
            "pre_run": e["pre_run_score"],
            "post_run": e["post_run_score"]
        })

nums = sorted(v5_runs)
bench_titles = {n: gt[n]['title'][:40] for n in nums}

print(f"=== Merged Quality Framework Analysis (V4 vs. Proposed V5) ===\n")

# Per-benchmark Details Table
print(f"{'#':>3} {'tier':>6} {'human%':>7} | {'v4_mean':>8} {'v4_std':>6} | {'v5_pre_mean':>12} {'pre_std':>7} | {'v5_post_mean':>13} {'post_std':>8} | title")
print("-" * 125)
for n in sorted(nums, key=lambda x: -gt[x]['human']):
    v4_scores = v4_runs[n]
    pre_scores = [r["pre_run"] for r in v5_runs[n]]
    post_scores = [r["post_run"] for r in v5_runs[n]]
    print(f"{n:>3} {gt[n]['tier']:>6} {gt[n]['human']:>6.1f}% | {mean(v4_scores):>8.2f} {pstdev(v4_scores):>6.2f} | {mean(pre_scores):>12.2f} {pstdev(pre_scores):>7.2f} | {mean(post_scores):>13.2f} {pstdev(post_scores):>8.2f} | {bench_titles[n]}")

# ----------------- TIER SEPARATION COMPARISON -----------------
tier_scores_v4 = {"top":[], "mid":[], "bottom":[]}
tier_scores_pre = {"top":[], "mid":[], "bottom":[]}
tier_scores_post = {"top":[], "mid":[], "bottom":[]}

for n in nums:
    mean_v4 = mean(v4_runs[n])
    mean_pre = mean(r["pre_run"] for r in v5_runs[n])
    mean_post = mean(r["post_run"] for r in v5_runs[n])
    tier_scores_v4[gt[n]['tier']].append(mean_v4)
    tier_scores_pre[gt[n]['tier']].append(mean_pre)
    tier_scores_post[gt[n]['tier']].append(mean_post)

print("\n" + "=" * 85)
print(" COMPARISON OF SCORE TIERS (Official V4 vs. Proposed V5)")
print("=" * 85)
print(f"{'Metric':<25} | {'Official V4':<18} | {'V5 Pre-Run (Static)':<20} | {'V5 Post-Run (Empirical)':<22}")
print("-" * 97)

# Tier Means
for t in ["top", "mid", "bottom"]:
    v4_m = mean(tier_scores_v4[t])
    pre_m = mean(tier_scores_pre[t])
    post_m = mean(tier_scores_post[t])
    print(f"{t.capitalize() + ' Tier Mean':<25} | {v4_m:>18.2f} | {pre_m:>20.2f} | {post_m:>22.2f}")

# Gaps
gap_tm_v4 = mean(tier_scores_v4['top']) - mean(tier_scores_v4['mid'])
gap_tm_pre = mean(tier_scores_pre['top']) - mean(tier_scores_pre['mid'])
gap_tm_post = mean(tier_scores_post['top']) - mean(tier_scores_post['mid'])
print(f"{'Gap Top-Mid':<25} | {gap_tm_v4:>+18.2f} | {gap_tm_pre:>+20.2f} | {gap_tm_post:>+22.2f}")

gap_mb_v4 = mean(tier_scores_v4['mid']) - mean(tier_scores_v4['bottom'])
gap_mb_pre = mean(tier_scores_pre['mid']) - mean(tier_scores_pre['bottom'])
gap_mb_post = mean(tier_scores_post['mid']) - mean(tier_scores_post['bottom'])
print(f"{'Gap Mid-Bottom':<25} | {gap_mb_v4:>+18.2f} | {gap_mb_pre:>+20.2f} | {gap_mb_post:>+22.2f}")

# Spearman Rho
rho_v4 = spearman([mean(v4_runs[n]) for n in nums], [gt[n]['human'] for n in nums])
rho_pre = spearman([mean(r["pre_run"] for r in runs[n]) if 'runs' in globals() else mean(r["pre_run"] for r in v5_runs[n]) for n in nums], [gt[n]['human'] for n in nums])
rho_post = spearman([mean(r["post_run"] for r in v5_runs[n]) for n in nums], [gt[n]['human'] for n in nums])
print(f"{'Spearman Correlation (Rho)':<25} | {rho_v4:>18.4f} | {rho_pre:>20.4f} | {rho_post:>22.4f}")

# Judge Noise (avg std)
noise_v4 = mean(pstdev(v4_runs[n]) for n in nums)
noise_pre = mean(pstdev([r["pre_run"] for r in v5_runs[n]]) for n in nums)
noise_post = mean(pstdev([r["post_run"] for r in v5_runs[n]]) for n in nums)
print(f"{'Average Judge Noise (Std)':<25} | {noise_v4:>18.4f} | {noise_pre:>20.4f} | {noise_post:>22.4f}")
print("-" * 97)
print()
