#!/usr/bin/env python3
"""Phase 2 statistics. Usage: python3 analyze.py [--pilot] > results/ANALYSIS.md
Paired design: each arm is compared with the baseline arm on the same (question, rep) pair, run back to back in the
same window. Reports n pairs, mean paired difference in tokens with a 95% t-interval, % vs the baseline mean (CI
scaled by the same baseline mean), correctness (regraded with current keys), $ list.
Only results/<test>/*.json are read (errors live in results/_errors and are never counted)."""
import json, math, pathlib, re, statistics as st, sys
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import questions as QS
from harness import grade

HERE = pathlib.Path(__file__).resolve().parent
PILOT = "--pilot" in sys.argv
BASE = HERE / "results" / ("_pilot2" if PILOT else "")
if not PILOT and not (BASE / "session").is_dir() and (HERE / "runs" / "session").is_dir():
    BASE = HERE / "runs"  # public repo: raw logs live in runs/

T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201,
       12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 25: 2.060,
       30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980}


def tcrit(df):
    if df <= 0:
        return float("nan")
    ks = sorted(T95)
    for k in ks:
        if df <= k:
            return T95[k]
    return 1.96


def ci(xs):
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    m = st.mean(xs)
    if n < 2:
        return m, float("nan"), float("nan")
    h = tcrit(n - 1) * st.stdev(xs) / math.sqrt(n)
    return m, m - h, m + h


def load(test):
    d = BASE / test
    return {f.stem: json.loads(f.read_text()) for f in sorted(d.glob("*.json"))} if d.exists() else {}


def ok(test, name, d):
    if d.get("result") is None:
        return None
    if "_grade_before_redaction" in d:  # answer text removed from the public log, grade kept
        return d["_grade_before_redaction"]
    if test.startswith("subagent"):
        return grade(QS.SUB_KEYS[name.split("-")[1]], d["result"])
    if test.startswith("caveman"):
        m = re.search(r"(q\d+)-r\d+$", name)
        return grade(QS.KEYS[m.group(1)], d["result"]) if m else None
    if test == "naming":
        return grade(QS.SKEYS[name.split("-")[1]], d["result"])
    m = re.search(r"(?:^|-)\d?(q\d+)-", name)
    return grade(QS.KEYS[m.group(1)], d["result"]) if m else None


def tok(d):
    return d["tok"]["total"]


def fmt(x):
    return "nan" if x != x else f"{x:,.0f}"


def pct(x, b):
    return "nan" if (x != x or not b) else f"{100 * x / b:+.1f}%"


def simple(test, baseline, label=""):
    R = load(test)
    if not R:
        return
    cells = defaultdict(dict)  # (q, rep) -> arm -> run
    for n, d in R.items():
        m = re.fullmatch(r"(.+)-(q\d+|s\d+|ok|p)-r(\d+)", n)
        if not m:
            continue
        cells[(m.group(2), m.group(3))][m.group(1)] = (n, d)
    arms = sorted({a for c in cells.values() for a in c})
    print(f"\n### {test} {label}\nbaseline = `{baseline}`. Runs: {len(R)}.\n")
    print("| arm | n | mean tokens | paired diff vs baseline (95% CI) | % vs baseline (95% CI) | correct | $ list mean |")
    print("|---|---|---|---|---|---|---|")
    for bare in (False, True):
        for a in arms:
            pairs = [(c[a], c[baseline]) for k, c in cells.items() if a in c and baseline in c and ((k[0] == "ok") == bare)]
            runs = [c[a] for k, c in cells.items() if a in c and ((k[0] == "ok") == bare)]
            if not runs:
                continue
            diffs = [tok(x[1]) - tok(y[1]) for x, y in pairs]
            bm = st.mean(tok(y[1]) for _, y in pairs) if pairs else float("nan")
            m, lo, hi = ci(diffs)
            oks = [ok(test, n, d) for n, d in runs]
            oks = [o for o in oks if o is not None]
            cost = st.mean(d["tok"]["cost"] for _, d in runs)
            name = a + (" (bare 'ok')" if bare else "")
            dstr = "-" if a == baseline else f"{fmt(m)} ({fmt(lo)} to {fmt(hi)})"
            pstr = "-" if a == baseline else f"{pct(m, bm)} ({pct(lo, bm)} to {pct(hi, bm)})"
            okstr = f"{sum(oks)}/{len(oks)}" if oks else "-"
            print(f"| {name} | {len(pairs) if a != baseline else len(runs)} | {fmt(st.mean(tok(d) for _, d in runs))} | {dstr} | {pstr} | {okstr} | {cost:.4f} |")


def subagent(test):
    R = load(test)
    if not R:
        return
    print(f"\n### {test}\nPer rep: main session vs delegating to a subagent; 4 calls (main task + 3 follow-ups). Runs: {len(R)}.\n")
    reps = sorted({int(n.split("-r")[-1]) for n in R})
    tot = {"main": [], "sub": []}; ctx = {"main": [], "sub": []}; diffs, okc = [], defaultdict(list)
    first, follow = [], []
    for r in reps:
        row = {}
        for a in ("main", "sub"):
            calls = [R.get(f"{a}-{c}-r{r}") for c in ("main", "f1", "f2", "f3")]
            for c, d in zip(("main", "f1", "f2", "f3"), calls):
                if d is not None:
                    o = ok(test, f"{a}-{c}-r{r}", d)
                    if o is not None:
                        okc[(a, c)].append(o)
            if all(calls):
                row[a] = (sum(tok(d) for d in calls), calls[1].get("_ctx_last_call"), tok(calls[0]), sum(tok(d) for d in calls[1:]))
        if len(row) == 2:
            diffs.append(row["sub"][0] - row["main"][0]); first.append(row["sub"][2] - row["main"][2]); follow.append(row["sub"][3] - row["main"][3])
            for a in row:
                tot[a].append(row[a][0]); ctx[a].append(row[a][1] or 0)
    for lab, xs, b in (("total of 4 calls", diffs, tot["main"]), ("main task call", first, None), ("3 follow-ups", follow, None)):
        m, lo, hi = ci(xs)
        bm = st.mean(b) if b else float("nan")
        print(f"- sub minus main, {lab}: n={len(xs)} {fmt(m)} ({fmt(lo)} to {fmt(hi)})" + (f", {pct(m, bm)} ({pct(lo, bm)} to {pct(hi, bm)}) vs main mean {fmt(bm)}" if b else ""))
    for a in ("main", "sub"):
        if ctx[a]:
            print(f"- {a}: mean total {fmt(st.mean(tot[a]))}; main-agent context at the first follow-up (last API call) mean {fmt(st.mean(ctx[a]))}")
    print("- correct: " + ", ".join(f"{a}/{c} {sum(v)}/{len(v)}" for (a, c), v in sorted(okc.items())))
    sc = [R[n].get("_subagent_calls", 0) for n in R if n.startswith("sub-main")]
    print(f"- delegation actually used in sub-main runs: {sum(1 for x in sc if x)}/{len(sc)}")


def session():
    R = load("session")
    if not R:
        return
    print(f"\n### session\nRuns: {len(R)}. Per chain rep and history size N: tokens of the 3 target questions after the fork, "
          "cumulative; compact includes the /compact call itself.\n")
    by = defaultdict(dict)  # (N, rep) -> arm -> [tok per pos], plus compactcmd
    ctxb, oks = {}, defaultdict(list)
    for n, d in R.items():
        m = re.fullmatch(r"N(\d+)-(continue|clear|compact)-(\d)(q\d+)-r(\d+)", n)
        if m:
            N, arm, pos, q, rep = int(m.group(1)), m.group(2), int(m.group(3)), m.group(4), int(m.group(5))
            by[(N, rep)].setdefault(arm, {})[pos] = tok(d); ctxb[(N, rep)] = d.get("_ctx_before")
            o = ok("session", n, d); oks[(N, arm)].append(bool(o)) if o is not None else None
            by[(N, rep)].setdefault(("pq", arm), {})[q] = tok(d)
        m = re.fullmatch(r"N(\d+)-compactcmd-r(\d+)", n)
        if m:
            by[(int(m.group(1)), int(m.group(2)))]["cmd"] = tok(d)
    Ns = sorted({k[0] for k in by})
    print("| N | ctx before fork (mean) | arm | after 1 q | after 2 q | after 3 q | diff vs continue after 3 q (95% CI) | % | correct |")
    print("|---|---|---|---|---|---|---|---|---|")
    for N in Ns:
        reps = [r for (n, r) in by if n == N]
        cum = defaultdict(lambda: defaultdict(list))
        full = defaultdict(dict)
        for r in reps:
            c = by[(N, r)]
            for arm in ("continue", "clear", "compact"):
                if arm not in c or len(c[arm]) < 3:
                    continue
                s = c.get("cmd", 0) if arm == "compact" else 0
                if arm == "compact" and "cmd" not in c:
                    continue
                for k in (1, 2, 3):
                    s += c[arm][k]; cum[arm][k].append(s)
                full[r][arm] = s
        cb = st.mean([ctxb[(N, r)] for r in reps if ctxb.get((N, r))] or [float("nan")])
        for arm in ("continue", "clear", "compact"):
            if not cum[arm][3]:
                continue
            diffs = [full[r][arm] - full[r]["continue"] for r in full if arm in full[r] and "continue" in full[r]]
            bm = st.mean(full[r]["continue"] for r in full if "continue" in full[r])
            m, lo, hi = ci(diffs)
            o = oks[(N, arm)]
            print(f"| {N} | {fmt(cb)} | {arm} | {fmt(st.mean(cum[arm][1]))} | {fmt(st.mean(cum[arm][2]))} | {fmt(st.mean(cum[arm][3]))} | "
                  + ("-" if arm == "continue" else f"{fmt(m)} ({fmt(lo)} to {fmt(hi)}), n={len(diffs)}") + f" | {'-' if arm == 'continue' else pct(m, bm)} | {sum(o)}/{len(o)} |")
    print("\nPer target question (mean tokens of that question, any position):\n")
    print("| N | arm | " + " | ".join(QS.SESSION_TARGETS) + " |")
    print("|---|---|" + "---|" * len(QS.SESSION_TARGETS))
    for N in Ns:
        for arm in ("continue", "clear", "compact"):
            vals = []
            for q in QS.SESSION_TARGETS:
                xs = [by[(n, r)][("pq", arm)][q] for (n, r) in by if n == N and ("pq", arm) in by[(n, r)] and q in by[(n, r)][("pq", arm)]]
                vals.append(fmt(st.mean(xs)) if xs else "-")
            print(f"| {N} | {arm} | " + " | ".join(vals) + " |")
    cmds = defaultdict(list)
    for (N, r), c in by.items():
        if "cmd" in c:
            cmds[N].append(c["cmd"])
    print("\n/compact call cost by N: " + ", ".join(f"N={N}: {fmt(st.mean(v))} (n={len(v)})" for N, v in sorted(cmds.items())))
    comp = [(n, d["_compact"][0]) for n, d in R.items() if "compactcmd" in n and d.get("_compact")]
    print("compact pre->post tokens: " + "; ".join(f"{n}: {c.get('pre_tokens')}->{c.get('post_tokens')}" for n, c in sorted(comp)))
    auto = [n for n, d in R.items() if n.startswith("build") and d.get("_compact")]
    print(f"auto-compact inside build chains: {auto or 'none'}")


def _skill_injected(d):
    """Proof the caveman skill body reached the model: search the session transcript for its first line."""
    import glob, os
    fs = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{d.get('session_id')}.jsonl"))
    return bool(fs) and any("Respond terse like smart caveman" in open(f).read() for f in fs)


def caveman():
    R = load("caveman")
    if R:
        print(f"\n### caveman (a): 10 explanation questions, default vs caveman skill\nRuns: {len(R)}.\n")
        cells = defaultdict(dict)
        for n, d in R.items():
            m = re.fullmatch(r"(default|caveman)-(q\d+)-r(\d+)", n)
            if m:
                cells[(m.group(2), m.group(3))][m.group(1)] = (n, d)
        pairs = [(c["caveman"][1], c["default"][1]) for c in cells.values() if len(c) == 2]
        for lab, key in (("total tokens", "total"), ("output tokens", "output")):
            xs = [a["tok"][key] - b["tok"][key] for a, b in pairs]; bm = st.mean(b["tok"][key] for _, b in pairs) if pairs else float("nan")
            m, lo, hi = ci(xs)
            print(f"- caveman minus default, {lab}: n={len(xs)} {fmt(m)} ({fmt(lo)} to {fmt(hi)}), {pct(m, bm)} ({pct(lo, bm)} to {pct(hi, bm)}) vs default mean {fmt(bm)}")
        for a in ("default", "caveman"):
            runs = [c[a] for c in cells.values() if a in c]
            o = [ok("caveman", n, d) for n, d in runs]
            print(f"- {a}: n={len(runs)} mean total {fmt(st.mean(d['tok']['total'] for _, d in runs))}, mean output {fmt(st.mean(d['tok']['output'] for _, d in runs))}, "
                  f"mean answer chars {fmt(st.mean(len(d.get('result') or '') for _, d in runs))}, $ {st.mean(d['tok']['cost'] for _, d in runs):.4f}, correct {sum(o)}/{len(o)}")
        cv = [d for (n, d) in R.items() if n.startswith("caveman")]
        print(f"- skill listed in init: {sum(1 for d in cv if 'caveman' in ((d.get('_init') or {}).get('skills_local') or []))}/{len(cv)}; "
              f"skill body in transcript: {sum(1 for d in cv if _skill_injected(d))}/{len(cv)}")
    R = load("caveman-session")
    if not R:
        return
    print(f"\n### caveman-session (b): 10-turn sessions, default vs caveman (activated on turn 1)\nRuns: {len(R)}.\n")
    by = defaultdict(lambda: defaultdict(dict))
    for n, d in R.items():
        m = re.fullmatch(r"(default|caveman)-t(\d+)(q\d+)-r(\d+)", n)
        if m:
            by[int(m.group(4))][m.group(1)][int(m.group(2))] = (n, d)
    tot, outp, okc = defaultdict(list), defaultdict(list), defaultdict(list)
    diffs_t, diffs_o, late = [], [], []
    for r, arms in sorted(by.items()):
        full = {a: v for a, v in arms.items() if len(v) == max(len(x) for x in arms.values())}
        for a, v in arms.items():
            for i, (n, d) in v.items():
                o = ok("caveman-session", n, d); okc[a].append(o) if o is not None else None
        if len(full) == 2 and len(full["default"]) == len(full["caveman"]):
            T = {a: sum(d["tok"]["total"] for _, d in v.values()) for a, v in full.items()}
            O = {a: sum(d["tok"]["output"] for _, d in v.values()) for a, v in full.items()}
            for a in T:
                tot[a].append(T[a]); outp[a].append(O[a])
            diffs_t.append(T["caveman"] - T["default"]); diffs_o.append(O["caveman"] - O["default"])
            ctx = {a: full[a][max(full[a])][1].get("_ctx_last_call") for a in full}
            late.append((r, ctx))
    for lab, xs, b in (("session total tokens", diffs_t, tot["default"]), ("session output tokens", diffs_o, outp["default"])):
        m, lo, hi = ci(xs); bm = st.mean(b) if b else float("nan")
        print(f"- caveman minus default, {lab}: n={len(xs)} reps, {fmt(m)} ({fmt(lo)} to {fmt(hi)}), {pct(m, bm)} ({pct(lo, bm)} to {pct(hi, bm)}) vs default mean {fmt(bm)}")
    print(f"- context at the last turn (last API call): " + "; ".join(f"r{r}: default {fmt(c.get('default') or float('nan'))}, caveman {fmt(c.get('caveman') or float('nan'))}" for r, c in late))
    print("- correct: " + ", ".join(f"{a} {sum(v)}/{len(v)}" for a, v in sorted(okc.items())))
    print("- per turn mean tokens (total / output):")
    turns = sorted({i for arms in by.values() for v in arms.values() for i in v})
    for i in turns:
        cells = []
        for a in ("default", "caveman"):
            xs = [by[r][a][i][1]["tok"] for r in by if i in by[r].get(a, {})]
            cells.append(f"{a} {fmt(st.mean(x['total'] for x in xs))} / {fmt(st.mean(x['output'] for x in xs))}" if xs else f"{a} -")
        print(f"  - t{i:02d}: " + "; ".join(cells))
    cv = [d for n, d in R.items() if n.startswith("caveman-t01")]
    print(f"- skill body in transcript (turn 1 of caveman chains): {sum(1 for d in cv if _skill_injected(d))}/{len(cv)}")


def totals():
    runs, toks, cost, rl = 0, 0, 0.0, []
    for d in BASE.iterdir():
        if not d.is_dir() or d.name.startswith("_"):
            continue
        for f in d.glob("*.json"):
            x = json.loads(f.read_text())
            if "tok" not in x:
                continue
            runs += 1; toks += x["tok"].get("total", 0); cost += x["tok"].get("cost", 0)
            r = x.get("_rate_limit")
            if r:
                w = r.get("unifiedWindows", {})
                rl.append((x.get("_t_end"), w.get("five_hour", {}).get("utilization"), w.get("seven_day", {}).get("utilization")))
    rl.sort()
    print(f"\n## Totals\nruns (saved calls) {runs}, tokens {toks:,}, $ list {cost:.2f}")
    if rl:
        print(f"seven_day first {rl[0][2]} ({rl[0][0]}) -> last {rl[-1][2]} ({rl[-1][0]})")


if __name__ == "__main__":
    print(f"# Phase 2 analysis ({'pilot' if PILOT else 'full'})")
    simple("claudemd", "none"); simple("effort", "medium"); simple("models", "sonnet"); simple("mcp", "default")
    simple("deny", "noise"); simple("flatmap", "plain"); simple("naming", "vague"); simple("opus", "none-medium")
    simple("memory", "sonnet", "(no tools: answer from memory)")
    simple("denyprobe", "noise", "(ungraded probe)"); simple("verify", "plain", "(bare 'ok' per template)")
    subagent("subagent"); subagent("subagent-deep"); session(); caveman(); totals()
