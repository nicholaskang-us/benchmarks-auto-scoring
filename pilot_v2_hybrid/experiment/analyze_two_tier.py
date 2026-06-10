#!/usr/bin/env python3
import json
import glob
import os
import sys
from statistics import mean, pstdev

EXP = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(EXP, "v4_two_tier")
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

# Collect scores across runs
runs = {} # bench_num -> list of dicts {pre_run, post_run}
files = sorted(glob.glob(os.path.join(results_dir, "r*_*.json")))

for f in files:
    for e in json.load(open(f)):
        n = e["benchmark_number"]
        runs.setdefault(n, []).append({
            "pre_run": e["pre_run_score"],
            "post_run": e["post_run_score"]
        })

nums = sorted(runs)
bench_titles = {n: gt[n]['title'][:40] for n in nums}

print(f"=== Two-Tier Scoring Analysis (rollouts directory: {os.path.basename(results_dir)}) ===\n")

# Per-benchmark Details Table
print(f"{'#':>3} {'tier':>6} {'human%':>7} | {'pre_run_mean':>12} {'pre_std':>7} | {'post_run_mean':>13} {'post_std':>8} | title")
print("-" * 105)
for n in sorted(nums, key=lambda x: -gt[x]['human']):
    pre_means = [r["pre_run"] for r in runs[n]]
    post_means = [r["post_run"] for r in runs[n]]
    print(f"{n:>3} {gt[n]['tier']:>6} {gt[n]['human']:>6.1f}% | {mean(pre_means):>12.2f} {pstdev(pre_means):>7.2f} | {mean(post_means):>13.2f} {pstdev(post_means):>8.2f} | {bench_titles[n]}")

# ----------------- TIER SEPARATION COMPARISON -----------------
tier_scores_pre = {"top":[], "mid":[], "bottom":[]}
tier_scores_post = {"top":[], "mid":[], "bottom":[]}

for n in nums:
    mean_pre = mean(r["pre_run"] for r in runs[n])
    mean_post = mean(r["post_run"] for r in runs[n])
    tier_scores_pre[gt[n]['tier']].append(mean_pre)
    tier_scores_post[gt[n]['tier']].append(mean_post)

print("\n" + "=" * 55)
print(" COMPARISON OF SCORE TIERS (Pre-Run vs. Post-Run)")
print("=" * 55)
print(f"{'Metric':<25} | {'Pre-Run (Static)':<18} | {'Post-Run (Empirical)':<20}")
print("-" * 71)

# Tier Means
for t in ["top", "mid", "bottom"]:
    pre_m = mean(tier_scores_pre[t])
    post_m = mean(tier_scores_post[t])
    print(f"{t.capitalize() + ' Tier Mean':<25} | {pre_m:>18.2f} | {post_m:>20.2f}")

# Gaps
gap_tm_pre = mean(tier_scores_pre['top']) - mean(tier_scores_pre['mid'])
gap_tm_post = mean(tier_scores_post['top']) - mean(tier_scores_post['mid'])
print(f"{'Gap Top-Mid':<25} | {gap_tm_pre:>+18.2f} | {gap_tm_post:>+20.2f}")

gap_mb_pre = mean(tier_scores_pre['mid']) - mean(tier_scores_pre['bottom'])
gap_mb_post = mean(tier_scores_post['mid']) - mean(tier_scores_post['bottom'])
print(f"{'Gap Mid-Bottom':<25} | {gap_mb_pre:>+18.2f} | {gap_mb_post:>+20.2f}")

# Spearman Rho
rho_pre = spearman([mean(r["pre_run"] for r in runs[n]) for n in nums], [gt[n]['human'] for n in nums])
rho_post = spearman([mean(r["post_run"] for r in runs[n]) for n in nums], [gt[n]['human'] for n in nums])
print(f"{'Spearman Correlation (Rho)':<25} | {rho_pre:>18.4f} | {rho_post:>20.4f}")

# Judge Noise (avg std)
noise_pre = mean(pstdev([r["pre_run"] for r in runs[n]]) for n in nums)
noise_post = mean(pstdev([r["post_run"] for r in runs[n]]) for n in nums)
print(f"{'Average Judge Noise (Std)':<25} | {noise_pre:>18.4f} | {noise_post:>20.4f}")
print("-" * 71)
