#!/usr/bin/env python3
"""Fetch distinct model-run counts per benchmark from the Kaggle Benchmarks API.

Parses task URLs from ../agi_hackathon_benchmark_links.md, queries
list_benchmark_task_runs for each task (with owner_slug so public tasks owned by
other users resolve), counts distinct models with a COMPLETED run, and writes
experiment/model_runs.json. This is the deterministic data source for rubric
Criterion 10 (Model Coverage) — model runs live on the task page, not the notebook.

Usage: python3 fetch_model_runs.py
"""
import json, os, re

EXP = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.dirname(EXP)
LINKS = os.path.join(PILOT, "agi_hackathon_benchmark_links.md")

from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk.benchmarks.types.benchmark_tasks_api_service import (
    ApiListBenchmarkTaskRunsRequest, ApiBenchmarkTaskSlug)

# benchmark_number in ground_truth -> the heading number in the links file.
# The links file is numbered 1..15 (3 = RIAC, excluded from ground truth).
TASK_URL_RE = re.compile(r"/benchmarks/tasks/([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)(?:/(\d+))?")
HEADING_RE = re.compile(r"^##\s+(\d+)\.\s+(.*)$")


def parse_links():
    """heading number -> list of (owner, task_slug)."""
    out = {}
    cur = None
    for line in open(LINKS):
        h = HEADING_RE.match(line.strip())
        if h:
            cur = int(h.group(1)); out[cur] = []
            continue
        if cur is None:
            continue
        for owner, slug, _ver in TASK_URL_RE.findall(line):
            # task URLs only (skip /benchmarks/<owner>/<slug> benchmark URLs which
            # lack the /tasks/ segment — findall already filtered to /tasks/)
            out[cur].append((owner, slug))
    return out


def completed_models_for_task(client, owner, slug):
    s = ApiBenchmarkTaskSlug(); s.owner_slug = owner; s.task_slug = slug
    req = ApiListBenchmarkTaskRunsRequest(); req.task_slug = s
    models_completed, models_any = set(), set()
    try:
        resp = client.list_benchmark_task_runs(req)
    except Exception as e:
        return None, None, f"{type(e).__name__}: {str(e)[:120]}"
    for r in (resp.runs or []):
        m = getattr(r, "model_version_slug", None)
        if not m:
            continue
        models_any.add(m)
        st = str(getattr(r, "state", ""))
        if "COMPLETED" in st:
            models_completed.add(m)
    return models_completed, models_any, None


def level_for(n):
    if n is None: return None
    if n >= 4: return 2
    if n >= 2: return 1
    return 0


def main():
    links = parse_links()
    api = KaggleApi(); api.authenticate()
    result = {}
    with api.build_kaggle_client() as kaggle:
        client = kaggle.benchmarks.benchmark_tasks_api_client
        for bnum, tasks in sorted(links.items()):
            if not tasks:
                continue
            union_completed, union_any = set(), set()
            per_task = []
            for owner, slug in tasks:
                comp, any_, err = completed_models_for_task(client, owner, slug)
                if err:
                    per_task.append({"task": f"{owner}/{slug}", "error": err})
                    continue
                union_completed |= comp; union_any |= any_
                per_task.append({"task": f"{owner}/{slug}",
                                 "completed": len(comp), "total": len(any_)})
            result[str(bnum)] = {
                "distinct_models_completed": len(union_completed),
                "distinct_models_any": len(union_any),
                "level": level_for(len(union_completed)),
                "models": sorted(union_completed),
                "per_task": per_task,
            }
            print(f"  benchmark {bnum:>2}: {len(union_completed):>2} completed models "
                  f"(level {level_for(len(union_completed))})  [{len(tasks)} task(s)]")

    out = os.path.join(EXP, "model_runs.json")
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"wrote {os.path.relpath(out, PILOT)}")


if __name__ == "__main__":
    main()
