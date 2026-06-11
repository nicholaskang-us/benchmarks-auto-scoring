#!/usr/bin/env python3
"""Build viewer/manifest.json from the experiment result dirs.

Scans experiment/<version>/ for r{1,2,3}_{A,B,C}.json rollouts, computes the same
metrics as analyze.py (tier separation, Spearman, per-criterion discrimination,
judge noise), and embeds every per-criterion justification so the static viewer
needs only this one file plus the rubric/prompt markdown.

Run this after every new scoring run, then commit + push:
    python3 build_manifest.py
"""
import json, glob, os
from datetime import datetime
from statistics import mean, pstdev

PILOT = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(PILOT, "experiment")
VIEWER = os.path.join(PILOT, "viewer")

CRITS = ["1_answer_correctness", "2_construct_validity", "3_code_quality", "4_sample_size",
         "5_metric_design", "6_problem_statement", "7_technical_documentation",
         "8_capability_targeting", "9_item_diversity", "10_model_coverage"]

# criterion -> category (mirrors backtest_execution_plan.md)
CRIT_META = [
    ("1_answer_correctness",      "Answer Correctness",       "A"),
    ("2_construct_validity",      "Construct Validity",       "A"),
    ("3_code_quality",            "Code Quality",             "A"),
    ("4_sample_size",             "Sample Size",              "A"),
    ("5_metric_design",           "Metric Design",            "A"),
    ("6_problem_statement",       "Problem Statement",        "B"),
    ("7_technical_documentation", "Technical Documentation",  "B"),
    ("8_capability_targeting",    "Capability Targeting",     "C"),
    ("9_item_diversity",          "Item Diversity",           "C"),
    ("10_model_coverage",         "Model Coverage",           "C"),
]
CAT_LABEL = {"A": "Task Construction", "B": "Task Description", "C": "Discriminative Power"}

# How a results dir maps to its rubric + scorer prompt. Convention with overrides.
def rubric_for(version):
    cands = ["total_rubric.md"] if version == "baseline" else [f"total_rubric_{version}.md"]
    for c in cands:
        if os.path.exists(os.path.join(PILOT, c)):
            return c
    return None

def prompt_for(version):
    cands = ["scorer_prompt.md"] if version == "baseline" else [f"scorer_prompt_{version}.md"]
    for c in cands:
        if os.path.exists(os.path.join(EXP, "prompts", c)):
            return os.path.join("experiment", "prompts", c)
    return None


def spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = mean(rx), mean(ry)
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    den = (sum((rx[i] - mx) ** 2 for i in range(n)) * sum((ry[i] - my) ** 2 for i in range(n))) ** 0.5
    return num / den if den else None


def build_version(version, gt):
    vdir = os.path.join(EXP, version)
    files = sorted(glob.glob(os.path.join(vdir, "r*_*.json")))
    if not files:
        return None

    # bench_num -> list of rollout dicts
    runs = {}
    for f in files:
        fname = os.path.basename(f)
        for e in json.load(open(f)):
            n = e["benchmark_number"]
            crit = {c: {"level": e["criteria"][c]["level"],
                        "justification": e["criteria"][c].get("justification", "")}
                    for c in CRITS}
            runs.setdefault(n, []).append({"file": fname, "total": e["total_score"], "criteria": crit})

    nums = sorted(runs)
    mean_total = {n: mean(r["total"] for r in runs[n]) for n in nums}
    std_total = {n: pstdev([r["total"] for r in runs[n]]) if len(runs[n]) > 1 else 0.0 for n in nums}

    benchmarks = []
    for n in nums:
        g = gt.get(n, {})
        benchmarks.append({
            "n": n,
            "title": g.get("title", f"benchmark {n}"),
            "human": g.get("human"),
            "tier": g.get("tier"),
            "mean_total": round(mean_total[n], 3),
            "std_total": round(std_total[n], 3),
            "rollouts": runs[n],
        })

    # tier separation
    tier_scores = {"top": [], "mid": [], "bottom": []}
    for n in nums:
        t = gt.get(n, {}).get("tier")
        if t in tier_scores:
            tier_scores[t].append(mean_total[n])
    tiers = {}
    for t, s in tier_scores.items():
        tiers[t] = {"mean": round(mean(s), 3), "min": round(min(s), 3),
                    "max": round(max(s), 3), "n": len(s)} if s else None
    sep = {"tiers": tiers}
    if all(tier_scores.values()):
        sep["gap_top_mid"] = round(mean(tier_scores["top"]) - mean(tier_scores["mid"]), 3)
        sep["gap_mid_bottom"] = round(mean(tier_scores["mid"]) - mean(tier_scores["bottom"]), 3)
        sep["clean_top_mid"] = min(tier_scores["top"]) > max(tier_scores["mid"])
        sep["clean_mid_bottom"] = min(tier_scores["mid"]) > max(tier_scores["bottom"])

    # spearman vs human
    paired = [(mean_total[n], gt[n]["human"]) for n in nums if gt.get(n, {}).get("human") is not None]
    rho = spearman([p[0] for p in paired], [p[1] for p in paired]) if len(paired) > 1 else None

    # per-criterion discrimination
    per_crit = []
    for c in CRITS:
        per_bench = [mean(r["criteria"][c]["level"] for r in runs[n]) for n in nums]
        per_crit.append({"key": c, "mean": round(mean(per_bench), 3),
                         "var": round(pstdev(per_bench) ** 2, 4)})

    noise = round(mean(std_total[n] for n in nums), 3)

    return {
        "id": version,
        "label": version,
        "rubric_path": rubric_for(version),
        "prompt_path": prompt_for(version),
        "run_files": [os.path.basename(f) for f in files],
        "n_rollouts": max(len(runs[n]) for n in nums),
        "n_benchmarks": len(nums),
        "aggregate": {
            "tier_separation": sep,
            "spearman": round(rho, 4) if rho is not None else None,
            "judge_noise": noise,
            "per_criterion": per_crit,
        },
        "benchmarks": benchmarks,
    }


def main():
    gt = {int(k): v for k, v in json.load(open(os.path.join(EXP, "ground_truth.json"))).items()}

    # every immediate subdir of experiment/ that holds r*_*.json
    versions = []
    for name in sorted(os.listdir(EXP)):
        d = os.path.join(EXP, name)
        if os.path.isdir(d) and glob.glob(os.path.join(d, "r*_*.json")):
            v = build_version(name, gt)
            if v:
                versions.append(v)

    # newest-looking version first (baseline last); keep simple lexical-ish ordering
    order = {"baseline": 0}
    versions.sort(key=lambda v: (order.get(v["id"], 1), v["id"]), reverse=True)

    manifest = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "criteria": [{"key": k, "label": lbl, "category": cat,
                      "category_label": CAT_LABEL[cat]} for k, lbl, cat in CRIT_META],
        "ground_truth": {str(k): v for k, v in gt.items()},
        "versions": versions,
    }

    os.makedirs(VIEWER, exist_ok=True)
    out = os.path.join(VIEWER, "manifest.json")
    with open(out, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"wrote {os.path.relpath(out, PILOT)}")
    for v in versions:
        agg = v["aggregate"]
        print(f"  {v['id']:>8}: {v['n_benchmarks']} benchmarks x {v['n_rollouts']} rollouts | "
              f"spearman={agg['spearman']} noise={agg['judge_noise']} | rubric={v['rubric_path']}")


if __name__ == "__main__":
    main()
