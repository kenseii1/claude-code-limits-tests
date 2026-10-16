#!/usr/bin/env python3
"""Usage-limits v2 harness (for the 21.10.2026 article). Follows our test-design checklist.

Every run = its own headless `claude -p --output-format stream-json --verbose` process with explicit --model and --effort,
in a FRESH APFS clone (cp -c) of a template work copy outside your project (scratchpad/ul-v2). Arms of a test are interleaved:
per rep and per question the arm order is shuffled (seeded). Results: results/<test>/<arm>-<q>-r<n>.json (resumable).
Pilot: --pilot writes to results/_pilot/ with 1 run per arm on 1-2 questions (sessions: N=5 only).

Token accounting (see NOTES.md):
- tok.total = sum over ALL models in modelUsage of input+output+cacheRead+cacheCreation (subagents included).
- modelUsage/total_cost_usd of a --resume call are CUMULATIVE for the session chain, so for chained calls
  the per-call value is the delta vs the previous call of the same chain (tok.method = "delta").
Usage:  python3 harness.py [--pilot] [--jobs N] [--reps N] test [test ...]
Tests:  env verify claudemd effort models mcp deny flatmap naming session subagent opus   (or: all)
"""
import argparse, concurrent.futures as cf, datetime as dt, json, os, pathlib, random, re, shutil, subprocess, sys, threading, time

import questions as QS
import make_private_repo as MPR

HERE = pathlib.Path(__file__).resolve().parent
SRC_FLASK = pathlib.Path(os.environ.get("FLASK_SRC", "./flask")).resolve()  # phase 1 only, kept for reference
FIX = HERE / "fixtures"
SCRATCH = pathlib.Path(os.environ.get("UL_SCRATCH", "./scratch")).resolve()  # work copies live here, outside your project
SRC = SCRATCH / "src-private" / "tessel"  # PHASE 2 (design decision 14.10): renamed private codebase, built by make_private_repo.py
TPL = SCRATCH / "templates-p2"  # phase-1 Flask templates stay in SCRATCH/templates
VENDOR = SCRATCH / "noise-vendor-p2"  # big vendor/ tree for the deny test
RUNS = SCRATCH / "runs"
RES = HERE / "results"
PILOT = False
PILOT_NAME = "_pilot2"  # phase-1 pilot stays in results/_pilot
LOCK = threading.Lock()
SEVEN_DAY_STOP, FIVE_HOUR_PAUSE = 0.95, 0.90  # ignore the weekly limit, stop only at 0.95
RL_STATE = {"five": None, "five_reset": None, "seven": None, "seven_reset": None, "t": None}
STOP = threading.Event()


class Stopped(Exception):
    pass

READ_TOOLS = ["Read", "Grep", "Glob", "Bash(ls:*)", "Bash(grep:*)", "Bash(find:*)", "Bash(cat:*)", "Bash(head:*)",
              "Bash(wc:*)", "Bash(rg:*)"]  # same as 11.10
PYTEST_TOOLS = ["Bash(PYTHONPATH=src python3 -m pytest:*)", "Bash(python3 -m pip show:*)", "Bash(pip show:*)",
                "Bash(pip list:*)", "Bash(python3 -m pip list:*)", "Bash(python3 -c:*)"]
DEFAULT_MODEL, DEFAULT_EFFORT = "sonnet", "medium"


# ---------------- work copies ----------------
def unrelated(nbytes):
    """An unrelated project's CLAUDE.md (20.9 KB, private, not published: put any long unrelated markdown at fixtures/unrelated-source-CLAUDE.md) cut at a line boundary <= nbytes."""
    out, n = [], 0
    for line in (FIX / "unrelated-source-CLAUDE.md").read_text().splitlines(keepends=True):
        b = len(line.encode())
        if n + b > nbytes:
            break
        out.append(line); n += b
    return "".join(out)


def _setup(name, d):
    if name == "plain":
        return
    if name == "cm-short":
        (d / "CLAUDE.md").write_text(QS.SHORT_CLAUDE_MD)
    elif name in ("cm-8k", "cm-16k"):
        (d / "CLAUDE.md").write_text(unrelated(8192 if name == "cm-8k" else 16384))
    elif name == "skill":
        sk = d / ".claude" / "skills" / "project-rules"
        sk.mkdir(parents=True)
        (sk / "SKILL.md").write_text("---\nname: project-rules\ndescription: Rules for a separate project. "
                                     "Use only when working on that project.\n---\n\n" + unrelated(16384))
        (d / "CLAUDE.md").write_text("Rules for the separate project live in the project-rules skill. Load them only for that project.\n")
    elif name == "caveman":  # real public skill, verbatim (fixtures/caveman/SOURCE.txt)
        sk = d / ".claude" / "skills" / "caveman"
        sk.mkdir(parents=True)
        shutil.copy(FIX / "caveman" / "SKILL.md", sk / "SKILL.md")
    elif name in ("noise", "noise-deny"):  # phase 2: big vendor tree (10 vendored copies + generated build files)
        subprocess.run(["cp", "-cR", str(build_vendor()), str(d / "vendor")], check=True)
        if name == "noise-deny":
            (d / ".claude").mkdir()
            (d / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"deny": ["Read(./vendor/**)"]}}, indent=1))
    elif name == "brain":  # 11.10 brain notes + flat index CLAUDE.md with the trust rule (fixtures/), renamed like the repo
        (d / "brain").mkdir()
        for f in sorted((FIX / "brain").glob("*.md")):
            (d / "brain" / f.name).write_text(MPR.rn(f.read_text()))
        (d / "CLAUDE.md").write_text(MPR.rn((FIX / "brain-CLAUDE.md").read_text()))
    else:
        raise ValueError(name)


VENDOR_VERSIONS = ["3.0.0", "3.0.1", "3.0.2", "3.0.3", "3.1.0", "3.1.1", "3.1.2", "3.1.3", "3.1.4", "3.2.0rc1"]


def build_vendor():
    """Deterministic noise tree (design decision 14.10): vendor/python/tessel-<v>/ = 10 full copies of the renamed repo
    (as if older versions were vendored) + vendor/assets/<pkg>/dist/*.js generated build output. Built once."""
    if VENDOR.exists():
        return VENDOR
    tmp = VENDOR.with_name(VENDOR.name + ".building")
    for v in VENDOR_VERSIONS:
        shutil.copytree(MPR.build(), tmp / "python" / f"tessel-{v}")
    r = random.Random("vendor-noise-p2")
    words = ("session request response handler error view route config cookie template render cache store query user "
             "token auth init update create remove load save parse format value item list map node event state props "
             "context module export default require function return const let var this null undefined").split()
    for i in range(40):
        pkg = tmp / "assets" / f"pkg-{i:02d}-{r.choice(words)}" / "dist"
        pkg.mkdir(parents=True)
        for j in range(60):
            parts, size = [], 0
            target = r.randint(4000, 9000)
            while size < target:
                a, b, c = r.choice(words), r.choice(words), r.choice(words)
                t = f"function {a}_{b}{j}(e,t){{var n={c}(e);return n&&n.{b}?t({a}):null}};"
                parts.append(t); size += len(t)
            (pkg / f"chunk-{j:03d}.min.js").write_text("".join(parts))
    tmp.rename(VENDOR)
    return VENDOR


def template(name):
    d = TPL / name
    with LOCK:
        if not d.exists():
            MPR.build()
            tmp = TPL / f".{name}.building"
            shutil.copytree(SRC, tmp, ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__"))
            _setup(name, tmp)
            tmp.rename(d)
    return d


def fresh_copy(tpl_name, test, run_name):
    """APFS clone of the template; a new folder per run (never reused, never deleted by us)."""
    src = template(tpl_name)
    dst = RUNS / (PILOT_NAME if PILOT else "main") / test / run_name
    k = 1
    while dst.exists():  # a retry gets its own folder
        k += 1; dst = dst.with_name(f"{run_name}~{k}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-cR", str(src), str(dst)], check=True)
    return dst


# ---------------- plan limits (design decision 14.10): pause at five_hour >= 0.90, stop at seven_day >= 0.75 ----------------
def note_rl(info):
    w = (info or {}).get("unifiedWindows") or {}
    with LOCK:
        if "five_hour" in w:
            RL_STATE["five"], RL_STATE["five_reset"] = w["five_hour"].get("utilization"), w["five_hour"].get("resetsAt")
        if "seven_day" in w:
            RL_STATE["seven"], RL_STATE["seven_reset"] = w["seven_day"].get("utilization"), w["seven_day"].get("resetsAt")
        RL_STATE["t"] = time.time()
        (SCRATCH / "rl_state.json").write_text(json.dumps(RL_STATE))


def gate():
    while True:
        if STOP.is_set():
            raise Stopped("stop flag")
        five, fr, seven = RL_STATE["five"], RL_STATE["five_reset"], RL_STATE["seven"]
        if seven is not None and seven >= SEVEN_DAY_STOP:
            STOP.set(); log(f"STOP: seven_day={seven} >= {SEVEN_DAY_STOP}"); raise Stopped("seven_day")
        if five is not None and five >= FIVE_HOUR_PAUSE:
            if fr and time.time() < fr + 60:
                log(f"PAUSE: five_hour={five}, sleeping until reset {dt.datetime.fromtimestamp(fr)} (+60 s)")
                time.sleep(min(fr + 60 - time.time(), 1800)); continue
            with LOCK:
                RL_STATE["five"] = None  # window reset; next call reports the new value
        return


def wait_after_limit_error():
    """429 / usage or session limit: sleep until the five-hour reset if known, else 15 min."""
    fr = RL_STATE["five_reset"]
    w = (fr + 60 - time.time()) if fr and fr + 60 > time.time() else 900
    log(f"limit error: sleeping {int(w)} s"); time.sleep(min(w, 18000))


# ---------------- one claude call ----------------
def mu_tot(mu):
    t = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0, "cost": 0.0}
    for m in (mu or {}).values():
        t["input"] += m.get("inputTokens", 0); t["output"] += m.get("outputTokens", 0)
        t["cache_read"] += m.get("cacheReadInputTokens", 0); t["cache_creation"] += m.get("cacheCreationInputTokens", 0)
        t["cost"] += m.get("costUSD", 0.0)
    t["total"] = t["input"] + t["output"] + t["cache_read"] + t["cache_creation"]
    return t


def tok_delta(cur, prev):
    if not prev:
        return dict(cur, method="single")
    d = {k: cur[k] - prev.get(k, 0) for k in ("input", "output", "cache_read", "cache_creation", "total", "cost")}
    d["cost"] = round(d["cost"], 6)
    return dict(d, method="delta")


def parse_stream(text, RL=None, CB=None):
    RL = [] if RL is None else RL; CB = [] if CB is None else CB
    init, result, trace, models_seen = None, None, [], set()
    pending = {}
    for line in text.splitlines():
        try:
            m = json.loads(line)
        except Exception:
            continue
        ty = m.get("type")
        if ty == "system" and m.get("subtype") == "init" and init is None:
            init = {"model": m.get("model"), "version": m.get("claude_code_version"), "n_tools": len(m.get("tools", [])),
                    "mcp_tools": sum(1 for t in m.get("tools", []) if t.startswith("mcp__")),
                    "mcp_servers": [(s.get("name"), s.get("status")) for s in m.get("mcp_servers", [])],
                    "n_skills": len(m.get("skills", [])), "skills_local": [s for s in m.get("skills", []) if s in ("x", "caveman")],
                    "agents": m.get("agents"), "memory_paths": m.get("memory_paths"), "permissionMode": m.get("permissionMode")}
        elif ty == "assistant":
            msg = m.get("message", {})
            if msg.get("model"):
                models_seen.add(msg["model"])
            for c in msg.get("content", []) or []:
                if c.get("type") == "tool_use":
                    e = {"tool": c.get("name"), "input": json.dumps(c.get("input"))[:400],
                         "sub": bool(m.get("parent_tool_use_id"))}
                    trace.append(e); pending[c.get("id")] = e
        elif ty == "user":
            for c in (m.get("message", {}).get("content") or []):
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    body = c.get("content")
                    s = body if isinstance(body, str) else json.dumps(body)
                    e = pending.get(c.get("tool_use_id"))
                    if e is not None:
                        e["result_chars"] = len(s); e["vendor_hits"] = s.count("vendor/")
                        e["is_error"] = bool(c.get("is_error")); e["result_head"] = s[:160]
        elif ty == "result":
            result = m
        elif ty == "rate_limit_event":
            RL.append(m.get("rate_limit_info"))
        elif ty == "system" and m.get("subtype") == "compact_boundary":
            CB.append(m.get("compact_metadata"))
    return init, result, trace, sorted(models_seen)


def _j(line):
    try:
        return json.loads(line)
    except Exception:
        return None


ERR_PAT = re.compile(r"usage limit|rate limit|429|overloaded|session limit|limit reached|spend limit|credit balance", re.I)


def claude(cwd, prompt, model=DEFAULT_MODEL, effort=DEFAULT_EFFORT, tools=READ_TOOLS, args=(), resume=None, fork=False,
           prev_mu=None, env=None, timeout=1500, mcp="strict"):
    """mcp="strict": --strict-mcp-config (no MCP; default for every test except the MCP test, because the claude.ai
    connectors load asynchronously in -p and were connected at start in only ~half of the pilot runs, adding ~2.2k tokens
    per API call at random). mcp="default": user MCP as configured; the run is rejected (retried) if not all connected."""
    gate()
    cmd = ["claude", "-p", prompt, "--model", model, "--effort", effort, "--output-format", "stream-json", "--verbose",
           "--permission-mode", "dontAsk"] + (["--allowedTools", *tools] if tools else [])
    if resume:
        cmd += ["--resume", resume]
        if fork:
            cmd += ["--fork-session"]
    cmd += list(args)
    if mcp == "strict" and "--strict-mcp-config" not in cmd:
        cmd += ["--strict-mcp-config"]
    t0 = time.time(); start = dt.datetime.now(dt.timezone.utc).isoformat()
    if mcp == "default":  # wait for connectors at start (pilot 14.10: without this they were "pending" in ~50% of -p runs)
        env = {"MCP_CONNECTION_NONBLOCKING": "false", **(env or {})}
    if mcp == "default":  # stop at init when the claude.ai connectors are not connected yet (saves a wasted full run)
        p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                             stdin=subprocess.DEVNULL, env={**os.environ, **(env or {})})
        first = []
        for line in p.stdout:
            first.append(line)
            m = _j(line)
            if m and m.get("type") == "system" and m.get("subtype") == "init":
                st = [x.get("status") for x in m.get("mcp_servers", [])]
                if not st or any(x not in ("connected", "needs-auth") for x in st):
                    p.kill(); p.wait()
                    return {"_error": {"reason": "mcp_not_ready", "mcp_servers": m.get("mcp_servers")}, "_cmd": {"mcp": mcp},
                            "_killed_at_init": True, "tok": {"total": 0}}
                break
        try:
            rest, err = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill(); rest, err = p.communicate()
        out, rc = "".join(first) + rest, p.returncode
    else:
        try:
            p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL,
                               env={**os.environ, **(env or {})})
            out, err, rc = p.stdout, p.stderr, p.returncode
        except subprocess.TimeoutExpired as e:
            out, err, rc = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT", -9
    RL, CB = [], []
    init, result, trace, models_seen = parse_stream(out, RL, CB)
    for x in RL:
        note_rl(x)
    raw = SCRATCH / "streams" / (PILOT_NAME if PILOT else "main") / f"{int(t0*1000)}-{os.getpid()}-{threading.get_ident()}.jsonl"
    raw.parent.mkdir(parents=True, exist_ok=True); raw.write_text(out)
    d = dict(result or {})
    d["_stream_file"] = str(raw)
    d["_events"] = sorted({f"{m.get('type')}:{m.get('subtype')}" for m in map(_j, out.splitlines()) if m and m.get("type") not in ("assistant", "user")})
    d["_init"], d["_trace"], d["_models_seen"] = init, trace, models_seen
    d["_rate_limit"] = RL[-1] if RL else None  # plan utilization (five_hour / seven_day, 0.01 steps) after this call
    d["_compact"] = CB  # compact_boundary metadata (pre_tokens/post_tokens) if the call compacted
    d["_wall_s"] = round(time.time() - t0, 1); d["_t_start"] = start; d["_t_end"] = dt.datetime.now(dt.timezone.utc).isoformat()
    d["_cmd"] = {"model": model, "effort": effort, "args": list(args), "mcp": mcp, "resume": resume, "fork": fork, "cwd": str(cwd),
                 "env": env, "tools": tools, "prompt": prompt}
    d["_mu_cum"] = mu_tot(d.get("modelUsage"))
    d["tok"] = tok_delta(d["_mu_cum"], prev_mu)
    u = d.get("usage") or {}
    d["_tok_usage_field"] = sum(u.get(k, 0) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    it = (u.get("iterations") or [])
    d["_ctx_last_call"] = (sum(it[-1].get(k, 0) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
                           if it else None)  # context size of the last API call of this run
    d["_subagent_calls"] = sum(1 for e in trace if e["tool"] in ("Agent", "Task") and not e["sub"])
    bad = (result is None) or d.get("is_error") or not d.get("modelUsage") or (rc not in (0,) and not d.get("result"))
    if mcp == "default" and not bad:
        st = [s for _, s in (init or {}).get("mcp_servers", [])]
        if not st or any(x not in ("connected", "needs-auth") for x in st):
            d["_error"] = {"reason": "mcp_not_ready", "mcp_servers": (init or {}).get("mcp_servers")}
            return d
    if bad or (d.get("subtype") not in (None, "success")) or ERR_PAT.search((d.get("result") or "")[:300] if bad else ""):
        d["_error"] = {"rc": rc, "stderr": err[-1500:], "stdout_tail": out[-1500:]}
    return d


# ---------------- grading, saving ----------------
def _hit(k, t):
    return bool(re.search(k[3:], t, re.I)) if k.startswith("re:") else k.lower() in t


def grade(keys, text):
    t = (text or "").lower()
    return all(any(_hit(k, t) for k in group) for group in keys)


def res_dir(test):
    return (RES / PILOT_NAME if PILOT else RES) / test


def have(test, name):
    return (res_dir(test) / f"{name}.json").exists()


def save(test, name, d):
    f = res_dir(test) / f"{name}.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    if d.get("_error"):
        e = (RES / "_errors"); e.mkdir(parents=True, exist_ok=True)
        (e / f"{'pilot-' if PILOT else ''}{test}-{name}-{int(time.time())}.json").write_text(json.dumps(d, indent=1))
        log("ERROR", test, name, d["_error"].get("reason") or "", (d["_error"].get("stderr") or "")[-200:], (d.get("result") or "")[:200])
        return False
    f.write_text(json.dumps(d, indent=1))
    return True


def log(*a):
    line = time.strftime("%H:%M:%S") + " " + " ".join(str(x) for x in a)
    with LOCK:
        print(line, flush=True)
        with open(HERE / ("pilot2.log" if PILOT else "run.log"), "a") as f:
            f.write(line + "\n")


def short(d):
    t = d.get("tok", {})
    return (f"tok={t.get('total')} cr={t.get('cache_read')} ${t.get('cost', 0):.4f} turns={d.get('num_turns')} "
            f"wall={d.get('_wall_s')}s sub={d.get('_subagent_calls')}")


def is_limit_error(d):
    e = d.get("_error") or {}
    txt = " ".join(str(x) for x in (e.get("stderr"), e.get("stdout_tail"), d.get("result")))
    return bool(ERR_PAT.search(txt))


def run_one(test, name, tpl, prompt, keys=None, retries=4, cwd=None, extra=None, **kw):
    """One saved call. Default: fresh session in a fresh work copy (cwd=None). Chains (sessions, subagent follow-ups)
    pass their own cwd + resume. Resumable: a saved result is loaded, not rerun. Errors go to results/_errors (never
    counted); limit errors wait for the five-hour reset and do not use up attempts."""
    if have(test, name):
        return json.loads((res_dir(test) / f"{name}.json").read_text())
    attempt, not_ready, limit_waits = 0, 0, 0
    while attempt < retries and not_ready < 15 and limit_waits < 12:
        wd = cwd if cwd is not None else fresh_copy(tpl, test, name)
        d = claude(wd, prompt, **kw)
        if keys is not None:
            d["_correct"] = grade(keys, d.get("result"))
        d["_tpl"] = tpl
        d.update(extra or {})
        if save(test, name, d):
            log(test, name, short(d), "" if keys is None else ("correct" if d["_correct"] else "WRONG"),
                f"ctx={d.get('_ctx_last_call')}", f"5h={RL_STATE['five']} 7d={RL_STATE['seven']}")
            return d
        if d["_error"].get("reason") == "mcp_not_ready":  # connectors still loading: not a usage error, retry soon
            not_ready += 1; time.sleep(5); continue
        if is_limit_error(d):
            limit_waits += 1; wait_after_limit_error(); continue
        time.sleep(300 if attempt == 0 else 900); attempt += 1
    return None


def rng(*parts):
    return random.Random("|".join(map(str, parts)))


def jobs_run(units, jobs):
    """units = list of callables; each unit runs its arms sequentially in shuffled order."""
    if jobs <= 1:
        for u in units:
            u()
        return
    with cf.ThreadPoolExecutor(jobs) as ex:
        for f in cf.as_completed([ex.submit(u) for u in units]):
            f.result()


# ---------------- simple A/B/C tests: same question, arms differ by template/model/effort/args ----------------
def simple_test(test, arms, qs, reps, jobs, bare_reps=0):
    """arms: {arm: dict(tpl=..., model=..., effort=..., args=...)}; qs: {q: (prompt, keys)}"""
    units = []
    for rep in range(1, reps + 1):
        for q, (prompt, keys) in qs.items():
            def unit(rep=rep, q=q, prompt=prompt, keys=keys):
                order = list(arms); rng(test, q, rep).shuffle(order)
                for a in order:
                    c = dict(arms[a]); tpl = c.pop("tpl", "plain")
                    run_one(test, f"{a}-{q}-r{rep}", tpl, prompt, keys, **c)
            units.append(unit)
    for rep in range(1, bare_reps + 1):
        def unit(rep=rep):
            order = list(arms); rng(test, "ok", rep).shuffle(order)
            for a in order:
                c = dict(arms[a]); tpl = c.pop("tpl", "plain")
                run_one(test, f"{a}-ok-r{rep}", tpl, QS.BARE, None, **c)
        units.append(unit)
    rng(test, "units").shuffle(units)
    jobs_run(units, jobs)


def graded(qnames):
    return {q: (QS.Q[q], QS.KEYS[q]) for q in qnames}


ALLQ = list(QS.Q)


def t_claudemd(reps, jobs):
    arms = {"none": dict(tpl="plain"), "short": dict(tpl="cm-short"), "u8k": dict(tpl="cm-8k"),
            "u16k": dict(tpl="cm-16k"), "skill": dict(tpl="skill")}
    simple_test("claudemd", arms, graded(["q1", "q6"] if PILOT else ALLQ), 1 if PILOT else reps, jobs, bare_reps=1 if PILOT else 5)


def t_effort(reps, jobs):
    arms = {e: dict(effort=e) for e in ("low", "medium", "high")}
    simple_test("effort", arms, graded(["q1", "q6"] if PILOT else ALLQ), 1 if PILOT else reps, jobs)


def t_models(reps, jobs):
    arms = {m: dict(model=m) for m in ("haiku", "sonnet", "opus")}
    simple_test("models", arms, graded(["q1", "q6"] if PILOT else ALLQ), 1 if PILOT else reps, jobs)


def t_mcp(reps, jobs):
    arms = {"default": dict(mcp="default"), "strict": dict(mcp="strict")}
    simple_test("mcp", arms, graded(["q1"] if PILOT else ALLQ), 1 if PILOT else reps, jobs, bare_reps=1 if PILOT else 10)


def t_deny(reps, jobs):
    arms = {"noise": dict(tpl="noise"), "deny": dict(tpl="noise-deny")}
    simple_test("deny", arms, graded(["q1"] if PILOT else ALLQ), 1 if PILOT else reps, jobs)


def t_flatmap(reps, jobs):
    arms = {"plain": dict(tpl="plain"), "brain": dict(tpl="brain")}
    simple_test("flatmap", arms, graded(["q4", "q7", "q9"] if PILOT else ALLQ), 1 if PILOT else reps, jobs)


def t_naming(reps, jobs):
    """Vague symptom task vs the same task with file + function named."""
    units = []
    tasks = ["s3"] if PILOT else list(QS.VAGUE)
    for rep in range(1, (1 if PILOT else reps) + 1):
        for s in tasks:
            def unit(rep=rep, s=s):
                order = ["vague", "named"]; rng("naming", s, rep).shuffle(order)
                for a in order:
                    run_one("naming", f"{a}-{s}-r{rep}", "plain", (QS.VAGUE if a == "vague" else QS.NAMED)[s], QS.SKEYS[s])
            units.append(unit)
    jobs_run(units, jobs)


def t_opus(reps, jobs):
    arms = {"none-medium": dict(model="opus"), "u16k-medium": dict(model="opus", tpl="cm-16k"),
            "none-low": dict(model="opus", effort="low")}
    simple_test("opus", arms, graded(["q1"] if PILOT else ALLQ), 1 if PILOT else reps, jobs)


# ---------------- C. long sessions (phase 2): continue / clear / compact at N turns, 3 target questions after each fork ----------------
SESSION_POINTS = [5, 15, 30]  # N=60 only if N=30 stays below ~90k context


def t_session(reps, jobs):
    """One chain per rep in its own work copy: 30 fillers (12 whole-file reads + 18 lookups). At N in SESSION_POINTS the
    chain forks three ways (arm order shuffled per rep and N):
      continue: --resume <chain> --fork-session, then the next 2 questions resume that fork;
      clear:    new session in the same folder (= /clear), then 2 more questions resume it;
      compact:  /compact on a fork of the chain, then 3 questions resume the compacted fork.
    The main chain itself is never modified by a fork. Targets: 3 questions in a row, order rotated per rep."""
    points = [30] if PILOT else SESSION_POINTS
    nmax = max(points)
    test = "session"
    units = []
    for rep in range(1, (1 if PILOT else reps) + 1):
        def unit(rep=rep):
            k0 = (rep - 1) % len(QS.SESSION_TARGETS)
            targets = QS.SESSION_TARGETS[k0:] + QS.SESSION_TARGETS[:k0]
            wd = RUNS / (PILOT_NAME if PILOT else "main") / test / f"chain-r{rep}"
            if not wd.exists():
                wd.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(["cp", "-cR", str(template("plain")), str(wd)], check=True)
            sid, prev = None, None
            for i in range(1, nmax + 1):
                d = run_one(test, f"build-r{rep}-t{i:02d}", "plain", QS.FILLERS[i - 1], None, cwd=wd, resume=sid, prev_mu=prev,
                            extra={"_turn": i, "_rep": rep})
                if d is None:
                    log("session chain aborted", rep, i); return
                if sid and d.get("session_id") != sid:
                    log("WARNING session id changed on resume", sid, d.get("session_id"))
                if d.get("_compact"):
                    log("WARNING auto-compact inside the chain", rep, i, d["_compact"])
                sid, prev = d.get("session_id"), d["_mu_cum"]
                if i not in points:
                    continue
                ctx = d["_ctx_last_call"]
                order = ["continue", "clear", "compact"]; rng(test, rep, i).shuffle(order)
                for arm in order:
                    s2, p2 = None, None
                    if arm == "continue":
                        s2, p2 = sid, prev
                    elif arm == "compact":
                        c = run_one(test, f"N{i:02d}-compactcmd-r{rep}", "plain", "/compact", None, cwd=wd, resume=sid, fork=True,
                                    prev_mu=prev, extra={"_ctx_before": ctx, "_N": i, "_arm": "compactcmd", "_rep": rep, "_parent_sid": sid})
                        if c is None:
                            continue
                        s2, p2 = c.get("session_id"), c["_mu_cum"]
                    for k, q in enumerate(targets, 1):
                        r = run_one(test, f"N{i:02d}-{arm}-{k}{q}-r{rep}", "plain", QS.Q[q], QS.KEYS[q], cwd=wd, resume=s2,
                                    fork=(arm == "continue" and k == 1), prev_mu=p2,
                                    extra={"_ctx_before": ctx, "_N": i, "_arm": arm, "_pos": k, "_target": q, "_rep": rep,
                                           "_parent_sid": sid})
                        if r is None:
                            break
                        s2, p2 = r.get("session_id"), r["_mu_cum"]
        units.append(unit)
    jobs_run(units, jobs)


# ---------------- D. subagent in its intended case ----------------
def t_subagent(reps, jobs, variant=""):
    """variant "": natural prompt; "deep": investigate every failure (the documented high-volume case).
    Phase 2: subagent-raw dropped (design decision 14.10). Resumable: a saved main call is reused with its own work copy."""
    test = "subagent" + (f"-{variant}" if variant else "")
    units = []
    for rep in range(1, (1 if PILOT else reps) + 1):
        def unit(rep=rep):
            order = ["main", "sub"]; rng(test, rep).shuffle(order)
            for a in order:
                if have(test, f"{a}-f3-r{rep}"):
                    continue
                tools = READ_TOOLS + PYTEST_TOOLS + (["Agent", "Task"] if a == "sub" else [])
                main_p, deleg_p = {"": (QS.SUB_MAIN, QS.SUB_DELEGATE), "raw": (QS.SUB_MAIN_RAW, QS.SUB_DELEGATE_RAW),
                                   "deep": (QS.SUB_MAIN_DEEP, QS.SUB_DELEGATE_DEEP)}[variant]
                prompt = main_p + (deleg_p if a == "sub" else "")
                if have(test, f"{a}-main-r{rep}"):
                    d = json.loads((res_dir(test) / f"{a}-main-r{rep}.json").read_text()); cwd = pathlib.Path(d["_cmd"]["cwd"])
                else:
                    cwd = fresh_copy("plain", test, f"{a}-r{rep}")
                    d = run_one(test, f"{a}-main-r{rep}", "plain", prompt, QS.SUB_KEYS["main"], cwd=cwd, tools=tools)
                    if d is None:
                        continue
                sid, prev = d.get("session_id"), d["_mu_cum"]
                for f, fp in QS.SUB_FOLLOW.items():
                    r = run_one(test, f"{a}-{f}-r{rep}", "plain", fp, QS.SUB_KEYS[f], cwd=cwd, tools=tools, resume=sid, prev_mu=prev)
                    if r is None:
                        break
                    sid, prev = r.get("session_id"), r["_mu_cum"]
        units.append(unit)
    jobs_run(units, jobs)


def t_memory(reps, jobs):
    """Private-codebase check (design decision 14.10): no tools at all, the model must answer from memory. Should fail or be wrong."""
    qs = ["q1", "q4", "q7"]
    for q in qs:
        for m in ("sonnet", "opus"):
            run_one("memory", f"{m}-{q}-r1", "plain", QS.Q[q] + " You cannot open any files: answer from what you know, "
                    "best guess is fine.", QS.KEYS[q], model=m, tools=[], args=["--tools", ""])


# ---------------- E. caveman skill (design decision 14.10): terse answers -> fewer output tokens ----------------
CAVE = "/caveman "  # documented manual activation (README "How to invoke"); loads the whole SKILL.md


def t_caveman(reps, jobs):
    """(a) 10 explanation questions, default (plain, no skill) vs caveman (skill installed + /caveman), interleaved."""
    units = []
    qs = ["q1", "q7"] if PILOT else ALLQ
    for rep in range(1, (1 if PILOT else reps) + 1):
        for q in qs:
            def unit(rep=rep, q=q):
                order = ["default", "caveman"]; rng("caveman", q, rep).shuffle(order)
                for a in order:
                    p = QS.Q_EXPLAIN[q]
                    run_one("caveman", f"{a}-{q}-r{rep}", "plain" if a == "default" else "caveman",
                            (CAVE + p) if a == "caveman" else p, QS.KEYS[q])
            units.append(unit)
    jobs_run(units, jobs)


def t_caveman_session(reps, jobs):
    """(b) one ~10-turn session per arm per rep (explanation questions, order rotated per rep). The caveman chain
    activates with /caveman on turn 1 only (the skill says it persists). The two chains advance turn by turn,
    arm order shuffled per turn, so both arms share the same time window. Resumable."""
    test = "caveman-session"
    nt = 3 if PILOT else len(ALLQ)
    units = []
    for rep in range(1, (1 if PILOT else reps) + 1):
        def unit(rep=rep):
            k0 = (3 * (rep - 1)) % len(ALLQ)
            qs = (ALLQ[k0:] + ALLQ[:k0])[:nt]
            st = {}
            for a in ("default", "caveman"):
                wd = RUNS / (PILOT_NAME if PILOT else "main") / test / f"{a}-r{rep}"
                if not wd.exists():
                    wd.parent.mkdir(parents=True, exist_ok=True)
                    subprocess.run(["cp", "-cR", str(template("plain" if a == "default" else "caveman")), str(wd)], check=True)
                st[a] = {"wd": wd, "sid": None, "prev": None, "ok": True}
            for i, q in enumerate(qs, 1):
                order = ["default", "caveman"]; rng(test, rep, i).shuffle(order)
                for a in order:
                    s = st[a]
                    if not s["ok"]:
                        continue
                    p = QS.Q_EXPLAIN[q]
                    if a == "caveman" and i == 1:
                        p = CAVE + p
                    d = run_one(test, f"{a}-t{i:02d}{q}-r{rep}", "plain" if a == "default" else "caveman", p, QS.KEYS[q],
                                cwd=s["wd"], resume=s["sid"], prev_mu=s["prev"], extra={"_turn": i, "_rep": rep, "_target": q})
                    if d is None:
                        log("caveman-session chain aborted", a, rep, i); s["ok"] = False; continue
                    if s["sid"] and d.get("session_id") != s["sid"]:
                        log("WARNING session id changed on resume", s["sid"], d.get("session_id"))
                    s["sid"], s["prev"] = d.get("session_id"), d["_mu_cum"]
        units.append(unit)
    jobs_run(units, jobs)


# ---------------- env record ----------------
def t_env(reps, jobs):
    s = json.loads(pathlib.Path(os.path.expanduser("~/.claude/settings.json")).read_text())
    info = {"date": dt.datetime.now().isoformat(), "claude_version": subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip(),
            "user_settings_keys": sorted(s), "model": s.get("model"), "modelSettings": s.get("modelSettings"),
            "autoCompactWindow": s.get("autoCompactWindow"), "user_CLAUDE_md": os.path.exists(os.path.expanduser("~/.claude/CLAUDE.md")),
            "python": sys.version.split()[0],
            "account_note": "Claude account was switched on 13.10.2026 (coordinator); plan tier not recorded here. Limits/usage "
                            "windows may differ from the 11.10 run.",
            "loads_in_every_run": "user settings above (model/effort overridden by explicit --model/--effort); 39 user/plugin "
                                  "skills (init.skills, 40 with the local project-rules skill); claude.ai connectors (4 servers, 19 tools when "
                                  "connected) unless --strict-mcp-config; no ~/.claude/CLAUDE.md"}
    try:
        import werkzeug, importlib.metadata as md
        info["werkzeug"] = md.version("werkzeug"); info["pytest"] = md.version("pytest")
    except Exception as e:
        info["werkzeug"] = str(e)
    (RES / "env.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(info, indent=1))


def t_verify(reps, jobs):
    """Bare "ok" once per template with no MCP: proves each CLAUDE.md / skill / settings variant loads (token deltas)."""
    arms = {t: dict(tpl=t) for t in (("plain", "noise", "noise-deny", "brain") if PILOT else
                                     ("plain", "cm-short", "cm-8k", "cm-16k", "skill", "noise", "noise-deny", "brain"))}
    simple_test("verify", arms, {}, 0, jobs, bare_reps=reps)


def t_denyprobe(reps, jobs):
    """Does a Read(./vendor/**) deny also hide vendor/ from repo-wide Glob and Grep (and Bash grep)? Ungraded probe."""
    arms = {"noise": dict(tpl="noise"), "deny": dict(tpl="noise-deny")}
    simple_test("denyprobe", arms, {"p": (QS.DENY_PROBE, None)}, reps if not PILOT else 1, jobs)


def t_subagent_raw(reps, jobs):
    t_subagent(reps, jobs, "raw")


def t_subagent_deep(reps, jobs):
    t_subagent(reps, jobs, "deep")


TESTS = {"caveman": t_caveman, "caveman-session": t_caveman_session, "memory": t_memory, "verify": t_verify, "denyprobe": t_denyprobe, "subagent-raw": t_subagent_raw, "subagent-deep": t_subagent_deep, "env": t_env, "claudemd": t_claudemd, "effort": t_effort, "models": t_models, "mcp": t_mcp, "deny": t_deny,
         "flatmap": t_flatmap, "naming": t_naming, "session": t_session, "subagent": t_subagent, "opus": t_opus}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("tests", nargs="+")
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--reps", type=int, default=2)
    a = ap.parse_args()
    PILOT = a.pilot
    for d in (TPL, RUNS, RES):
        d.mkdir(parents=True, exist_ok=True)
    names = list(TESTS) if a.tests == ["all"] else a.tests
    try:
        for t in names:
            log("=== start", t, "pilot" if PILOT else f"reps={a.reps}", f"jobs={a.jobs}")
            TESTS[t](a.reps, a.jobs)
        log("=== done", names)
    except Stopped as e:
        log("=== STOPPED", e, RL_STATE)
        sys.exit(3)
