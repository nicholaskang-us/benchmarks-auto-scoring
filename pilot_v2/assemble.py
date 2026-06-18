import csv, json, glob, os

meta = {}
with open("sample_meta.csv", newline="") as f:
    for row in csv.DictReader(f):
        meta[row["task_id"]] = row

ratings = {}
for p in glob.glob("tasks_out/*.json"):
    with open(p) as f:
        d = json.load(f)
    ratings[str(d["task_id"])] = d

cols = ["task_id","task_name","task_url","notebook_url",
        "crit1_correctness","crit2_problem_statement","crit3_documentation",
        "crit4_model_coverage","crit5_discrimination","total_0_10",
        "distinct_models","min_score","max_score",
        "notes_crit1","notes_crit2","notes_crit3","notes_crit4","notes_crit5"]

def num(x):
    try: return float(x)
    except: return None

rows = []
for tid, m in meta.items():
    r = ratings.get(tid, {})
    c1 = r.get("crit1", 0); c2 = r.get("crit2", 0); c3 = r.get("crit3", 0)
    c4 = int(m["crit4"]); c5 = int(m["crit5"])
    dm = int(m["distinct_models"])
    mn = m["min_score"]; mx = m["max_score"]
    total = c1 + c2 + c3 + c4 + c5
    n4 = f"{dm} distinct models run"
    if dm <= 1:
        n5 = "<=1 model -> 0"
    else:
        mnf, mxf = num(mn), num(mx)
        eps = 0.05 if (mxf is not None and mxf <= 1.0) else 5.0
        gap = (mxf - mnf) if (mnf is not None and mxf is not None) else None
        verdict = "pass" if (c5 == 2) else "fail"
        n5 = f"score gap {mn}->{mx} vs eps={eps} ({verdict})"
    rows.append({
        "task_id": tid, "task_name": m["task_name"], "task_url": m["task_url"],
        "notebook_url": m["notebook_url"],
        "crit1_correctness": c1, "crit2_problem_statement": c2, "crit3_documentation": c3,
        "crit4_model_coverage": c4, "crit5_discrimination": c5, "total_0_10": total,
        "distinct_models": dm, "min_score": mn, "max_score": mx,
        "notes_crit1": r.get("notes1",""), "notes_crit2": r.get("notes2",""),
        "notes_crit3": r.get("notes3",""), "notes_crit4": n4, "notes_crit5": n5,
    })

rows.sort(key=lambda x: int(x["task_id"]))
with open("final_500_scores.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

print(f"wrote {len(rows)} rows; missing ratings: {sum(1 for r in rows if r['task_id'] not in ratings)}")
