# Check that every row of data/runs.csv matches the raw run log in runs/<test>/<run>.json.
# Usage: python3 verify_runs.py   (no network, no Claude calls)
import csv, json, os, sys

bad = 0
rows = list(csv.DictReader(open("data/runs.csv")))
for r in rows:
    d = json.load(open(os.path.join("runs", r["test"], r["run"] + ".json")))
    checks = {"tokens_total": d["tok"]["total"], "output": d["tok"]["output"],
              "cache_read": d["tok"]["cache_read"], "correct": d.get("_correct")}
    for k, v in checks.items():
        want = r[k]
        if k == "correct" and want == "":
            continue  # naming and subagent answers are graded in analyze.py with the per-question keys
        got = "" if v is None else str(int(v)) if isinstance(v, (bool, int, float)) else str(v)
        if want != got:
            bad += 1
            print(f"MISMATCH {r['test']}/{r['run']} {k}: csv={want} log={got}")
print(f"{len(rows)} rows checked, {bad} mismatches", file=sys.stderr)
sys.exit(1 if bad else 0)
