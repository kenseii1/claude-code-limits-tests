"""Questions, answer keys and session fillers for the usage-limits v2 test (Flask repo, 3.2.0.dev, same source as 11.10).

Grading: KEYS[q] is a list of groups; every group must match, a group matches if ANY of its strings
appears in the final answer (case-insensitive). Every key string was checked by grep in repo-src/flask/src
on 2026-10-14 (see NOTES.md "Answer keys").
"""

# ---------- A. 10 graded "how does X work" questions ----------
Q = {  # q1-q5: same wording as the 11.10 run.py; q6-q10 new
    "q1": "In this repo, when a view raises an exception, how does Flask decide which error handler runs? List the methods involved in call order, with file paths. Be brief.",
    "q2": "In this repo, how does the session cookie get written at the end of a request? List the functions involved in call order, with file paths. Be brief.",
    "q3": "In this repo, I want to add a custom CLI command that needs the app (and app context). Which decorator should I use, and which class loads the app for CLI commands? Give file paths. Be brief.",
    "q4": "In this repo, how does a blueprint get its URL rules onto the app when it is registered? Name the classes and methods involved, with file paths. Be brief.",
    "q5": "In this repo, what happens between the WSGI server calling the app and the view function running? List the main methods in order, with file paths. Be brief.",
    "q6": "In this repo, how are environment variables like FLASK_SECRET_KEY or FLASK_DB__HOST turned into config values, including type conversion and nested keys? Name the method and the conversion function, with file paths. Be brief.",
    "q7": "In this repo, the default session can store tuples, bytes and datetimes in a JSON cookie and get them back with the right types. How does that work? Name the classes involved, with file paths. Be brief.",
    "q8": "In this repo, how do current_app, g and request find the right object for the current context? Name the mechanism and the objects involved, with file paths. Be brief.",
    "q9": "In this repo, how does a class-based view with get() and post() methods become a view function and route each HTTP method to the right handler? Name the classes and methods, with file paths. Be brief.",
    "q10": "In this repo, how do request, session and g become available inside every Jinja template, and how can an app add its own variables? Name the functions and the decorator involved, with file paths. Be brief.",
}
KEYS = {
    "q1": [["handle_user_exception"], ["_find_error_handler"]],
    "q2": [["process_response"], ["save_session"]],
    "q3": [["with_appcontext"], ["ScriptInfo"]],
    "q4": [["BlueprintSetupState"], ["add_url_rule"]],
    "q5": [["wsgi_app"], ["full_dispatch_request"], ["dispatch_request"]],
    "q6": [["from_prefixed_env"], ["json.loads"]],  # tightened 14.10 ("loads" alone also matched prose)
    "q7": [["TaggedJSONSerializer"], ["JSONTag"]],
    "q8": [["LocalProxy"], ["ContextVar", "_cv_app"]],
    "q9": [["MethodView"], ["as_view"], ["dispatch_request"]],
    "q10": [["context_processor"], ["update_template_context", "_default_template_ctx_processor"]],
}

# ---------- Naming the file: 10 vague symptom tasks + the same tasks with file and function named ----------
VAGUE = {
    "s1": "Users say that session data they change inside a nested dict (session['cart']['items'].append(x)) is lost on the next request. In this repo, where would you look and why? Be brief.",
    "s2": "A background job that calls url_for crashes with 'Unable to build URLs outside an active request'. In this repo, where would you look and why, and what config fixes it? Be brief.",
    "s3": "We registered a 404 error handler on a blueprint, but for unknown URLs the default 404 page shows instead. In this repo, where would you look and why? Be brief.",
    "s4": "A function we registered with teardown_appcontext sometimes gets an exception argument and sometimes None. In this repo, where would you look to see when it is called and with what? Be brief.",
    "s5": "Our JSON responses come back with keys sorted alphabetically and we want insertion order. In this repo, where would you look and why? Be brief.",
    "s6": "Large uploads are rejected with 413 and we want a bigger limit on one route only. In this repo, where is the limit decided and can it be changed per request? Be brief.",
    "s7": "Browsers keep using old static CSS files after a deploy. In this repo, where would you look to see how long static files are cached and why? Be brief.",
    "s8": "`flask run` fails to find our app: our module has create_app(config_name) with a required argument. In this repo, where would you look and why? Be brief.",
    "s9": "A login check we put in our admin blueprint runs for every request in the whole app, not just the admin pages. In this repo, where would you look and why? Be brief.",
    "s10": "After we rotated SECRET_KEY, every user was logged out. In this repo, where would you look and how can we rotate keys without that? Be brief.",
}
NAMED_PREFIX = {
    "s1": "Look at SecureCookieSession and SessionInterface.should_set_cookie in src/flask/sessions.py. ",
    "s2": "Look at Flask.url_for and Flask.create_url_adapter in src/flask/app.py. ",
    "s3": "Look at App._find_error_handler in src/flask/sansio/app.py and Flask.handle_http_exception in src/flask/app.py. ",
    "s4": "Look at Flask.do_teardown_appcontext in src/flask/app.py and AppContext.pop in src/flask/ctx.py. ",
    "s5": "Look at DefaultJSONProvider in src/flask/json/provider.py. ",
    "s6": "Look at Request.max_content_length in src/flask/wrappers.py. ",
    "s7": "Look at Flask.get_send_file_max_age in src/flask/app.py and Blueprint.get_send_file_max_age in src/flask/blueprints.py. ",
    "s8": "Look at find_best_app and _called_with_wrong_args in src/flask/cli.py. ",
    "s9": "Look at Blueprint.before_app_request in src/flask/sansio/blueprints.py and Scaffold.before_request in src/flask/sansio/scaffold.py. ",
    "s10": "Look at SecureCookieSessionInterface.get_signing_serializer in src/flask/sessions.py. ",
}
NAMED = {k: NAMED_PREFIX[k] + v for k, v in VAGUE.items()}
SKEYS = {
    "s1": [["modified"], ["SecureCookieSession", "should_set_cookie", "save_session", "CallbackDict"]],
    "s2": [["create_url_adapter"], ["SERVER_NAME"]],
    "s3": [["_find_error_handler", "app_errorhandler"]],  # pilot 14.10: a correct answer may only name the fix (app_errorhandler)
    "s4": [["do_teardown_appcontext"]],
    "s5": [["DefaultJSONProvider"], ["sort_keys"]],
    "s6": [["max_content_length"], ["wrappers"]],
    "s7": [["get_send_file_max_age"], ["SEND_FILE_MAX_AGE_DEFAULT"]],
    "s8": [["find_best_app"]],
    "s9": [["before_app_request", "app.before_request"]],  # either registration explains an app-wide hook
    "s10": [["SECRET_KEY_FALLBACKS"], ["get_signing_serializer", "SecureCookieSessionInterface"]],
}

# ---------- C. Long sessions: 30 ungraded realistic lookups (kept away from the target topics) ----------
FILLERS = [
    "In this repo, where is the Flask logger created and what handler does it add by default? Brief, with file path.",
    "Which signals does this repo define, and in which file? Just list the names.",
    "Where is the `flask routes` CLI command implemented and how does it sort its output? Brief.",
    "What does Config.from_pyfile do when the file is missing and silent=True? Point to the code.",
    "How does get_flashed_messages filter by category? Brief, with file path.",
    "Where is send_from_directory defined in this repo and what does it delegate to?",
    "How does abort work in this repo and where does it come from?",
    "Where is stream_with_context defined and what does it do with the context? Brief.",
    "What does the FlaskClient test client add on top of Werkzeug's client? List the main additions.",
    "How does app.test_cli_runner() invoke CLI commands? Name the class and file.",
    "Where is jsonify defined and what does it call internally?",
    "How does DefaultJSONProvider serialize dates, UUIDs and dataclasses? Point to the function.",
    "What does has_request_context check? File path and one line.",
    "Where does the `flask shell` command build its namespace, and which hook lets apps add to it?",
    "How does load_dotenv decide which .env files to load? Brief.",
    "What does Flask.make_shell_context return by default?",
    "Where is render_template_string defined and which internal helper renders it?",
    "Which Jinja loader does Flask use to find templates across blueprints? Name the class and file.",
    "What does Config.from_mapping do with lowercase keys?",
    "Where are the template_filter and template_global decorators defined?",
    "How does Flask.run behave when FLASK_RUN_FROM_CLI is set? Point to the code.",
    "What does copy_current_request_context do and where is it defined?",
    "Which exceptions does debughelpers.py define and when are they raised?",
    "How does add_template_test register a test? File and one line.",
    "Where does the app compute its instance_path by default?",
    "What does Request.on_json_loading_failed do in debug mode vs normal mode?",
    "How does get_template_attribute work? Brief.",
    "How does Flask.open_resource resolve the path, and which modes does it allow?",
    "What does Flask.async_to_sync use under the hood?",
    "Which keys in Flask.default_config are about JSON or templates? Just list them.",
]
SESSION_TARGETS = ["q4", "q1", "q2", "q5", "q9"]  # target per rep rotates through this list

# ---------- D. Subagent test: verbose test run + 3 follow-ups in the same session ----------
PYTEST_CMD = "PYTHONPATH=src python3 -m pytest tests -v"
SUB_MAIN = (f"Run the full test suite with: {PYTEST_CMD} and diagnose the failures: how many tests fail, "
            "and what is the main root cause? Do not fix anything.")
SUB_DELEGATE = (" Use a subagent to run the test suite and report back a short summary of the failures; "
                "do not run the suite yourself.")
SUB_MAIN_RAW = (f"Run the full test suite with exactly: {PYTEST_CMD} (do not pipe, filter or truncate its output) and "
                "diagnose the failures: how many tests fail, and what is the main root cause? Do not fix anything.")
SUB_DELEGATE_RAW = (" Use a subagent to run the test suite (exactly that command, unfiltered) and report back a short summary "
                    "of the failures; do not run the suite yourself.")
# "deep" variant (added 14.10 after the pilot): Claude Code truncates one Bash result to ~10k chars and the models pipe
# pytest through tail themselves, so a single verbose run never floods the main context. The documented subagent case
# is a high-volume multi-call investigation whose details are not needed later: read every failing traceback + source.
SUB_MAIN_DEEP = (f"Run the full test suite with: {PYTEST_CMD}. Then, for every failing test, find the exact cause: read its "
                 "traceback and the Flask source involved, and group the failures by root cause. Report how many tests "
                 "fail and what the main root cause is. Do not fix anything.")
SUB_DELEGATE_DEEP = (" Use a subagent to run the suite and do this whole investigation, and have it report back a short summary "
                     "of the groups; do not run the suite or read the tracebacks yourself.")
SUB_FOLLOW = {
    "f1": "Which of the failing tests are NOT caused by that main root cause? Name them and say briefly why each fails.",
    "f2": "Which Werkzeug version is installed in this environment, and what minimum version does the project's pyproject.toml require?",
    "f3": "Which line of Flask's own source makes the failing call, and which argument there does the installed Werkzeug reject?",
}
SUB_KEYS = {
    # first pytest run in a fresh copy: 24 failed + 1 error (test_open_resource_exceptions[a] fails only on the first run,
    # deterministic, checked 5x 14.10); later runs in the same copy: 23 failed + 1 error. Both count as correct.
    "main": [[r"re:\b2[34]\b[^.\n]{0,30}fail"], ["partitioned", "werkzeug"]],
    "f1": [["test_async_view"], ["test_limit_config"]],
    "f2": [["3.0.3"], ["3.1"]],
    "f3": [["sessions.py"], ["partitioned"]],
}

# ---------- B. Short relevant CLAUDE.md (~1 KB, written for this repo) ----------
SHORT_CLAUDE_MD = """# Flask repo guide

Flask web framework, version 3.2.0.dev. Source in `src/flask/`, tests in `tests/`, docs in `docs/`.

## Where things live
- `src/flask/sansio/`: request-independent core. `scaffold.py` (Scaffold: route/error/hook registration shared by app and blueprints), `app.py` (App: config, URL map, error handler lookup), `blueprints.py` (Blueprint, BlueprintSetupState).
- `src/flask/app.py`: Flask class, the WSGI request cycle (wsgi_app, dispatch, responses, teardown, url_for).
- `src/flask/ctx.py` + `globals.py`: AppContext and the current_app/g/request/session proxies.
- `src/flask/sessions.py`: cookie sessions. `json/`: JSON provider and the tagged session serializer.
- `src/flask/cli.py`: the `flask` command, app discovery. `config.py`: Config loaders.
- `src/flask/templating.py`, `views.py`, `wrappers.py`, `helpers.py`, `testing.py`.

## Commands
- Tests: `PYTHONPATH=src python3 -m pytest tests`.
"""

BARE = "Reply with just: ok"

DENY_PROBE = ("Do exactly these three steps from the repo root and paste each raw result, nothing else: "
              "1) Glob with pattern **/sessions.py. 2) Grep (files_with_matches) for 'def save_session' over the whole repo. "
              "3) Bash: grep -rl 'def save_session' . ")


# =====================================================================================================================
# PHASE 2 (design decision 14.10): private codebase. Everything above is written in Flask terms and kept for reference
# (_old-phase1/questions-flask.py). The renamed repo "tessel" is built by make_private_repo.py; the SAME rename
# function is applied here to every prompt and key, so names match the renamed source exactly.
# Keys untouched by the rename on purpose (library or stdlib names): LocalProxy, ContextVar, CallbackDict, json.loads,
# max_content_length, wrappers, modified, sort_keys, SERVER_NAME, werkzeug, partitioned, test names, versions.
# =====================================================================================================================
from make_private_repo import rn as _rn


def _deep(x):
    if isinstance(x, str):
        return x if x.startswith("re:") else _rn(x)
    if isinstance(x, list):
        return [_deep(i) for i in x]
    if isinstance(x, dict):
        return {k: _deep(v) for k, v in x.items()}
    return x


FILLERS_P1 = _deep(FILLERS)  # phase-1 short lookups (~1.1-1.4k tokens of history per turn)
Q, KEYS = _deep(Q), _deep(KEYS)
VAGUE, NAMED_PREFIX, SKEYS = _deep(VAGUE), _deep(NAMED_PREFIX), _deep(SKEYS)
NAMED = {k: NAMED_PREFIX[k] + v for k, v in VAGUE.items()}
SUB_MAIN, SUB_DELEGATE, SUB_MAIN_DEEP, SUB_DELEGATE_DEEP = map(_deep, (SUB_MAIN, SUB_DELEGATE, SUB_MAIN_DEEP, SUB_DELEGATE_DEEP))
SUB_MAIN_RAW, SUB_DELEGATE_RAW, SUB_FOLLOW, SUB_KEYS = map(_deep, (SUB_MAIN_RAW, SUB_DELEGATE_RAW, SUB_FOLLOW, SUB_KEYS))
SHORT_CLAUDE_MD, DENY_PROBE = _deep(SHORT_CLAUDE_MD), _deep(DENY_PROBE)

# ---------- C. Long sessions, phase 2: heavier fillers (design decision 14.10) ----------
# 12 whole-file reads (source, tests, docs) interleaved with 18 phase-1 lookups. All kept away from the 3 target
# questions (q4 bundles: sansio/bundles.py; q7 tagged JSON: json/tag.py + sessions.py; q9 views.py): no filler reads
# those files or their tests/docs. Target order rotates per rep to balance position effects.
HEAVY = [
    "Read the whole file src/tessel/cli.py from top to bottom (all of it) and give me a one-line summary of each class and function in it.",
    "Read all of src/tessel/helpers.py and list every public function in it with one line on what it does.",
    "Read the whole of src/tessel/ctx.py and summarize, in a short list, what each class and function in it is for.",
    "Read the full file src/tessel/config.py and list every method of Config with a one-line description.",
    "Read the whole test file tests/test_cli.py and tell me which CLI features it covers, as a short grouped list.",
    "Read all of tests/test_templating.py and list which template features are tested, as a short grouped list.",
    "Read the whole docs page docs/config.rst and list the built-in config keys it documents, with their defaults.",
    "Read the whole docs page docs/errorhandling.rst and summarize its main recommendations in 5-8 bullets.",
    "Read the full docs page docs/cli.rst and summarize what it says about custom commands and app discovery.",
    "Read all of src/tessel/testing.py and list its classes and methods with one line each.",
    "Read the whole test file tests/test_helpers.py and list which helper functions it tests.",
    "Read the full docs page docs/web-security.rst and list the security headers and cookie options it recommends.",
]
_LOOKUP_IDX = [0, 1, 2, 4, 5, 6, 8, 10, 11, 12, 16, 17, 20, 22, 24, 25, 28, 29]  # 18 of the 30 phase-1 lookups
_HEAVY_AT = [2, 4, 6, 8, 10, 12, 14, 17, 20, 23, 26, 29]  # turn numbers (1-based) of the whole-file reads
FILLERS, _h, _l = [], iter(HEAVY), iter(_LOOKUP_IDX)
for _t in range(1, 31):
    FILLERS.append(next(_h) if _t in _HEAVY_AT else FILLERS_P1[next(_l)])
SESSION_TARGETS = ["q4", "q7", "q9"]  # asked 3 in a row after every fork; order rotated per rep

# ---------- E. caveman (design decision 14.10): the same 10 questions asking for an explanation (where a terse style can cut output) ----------
assert all(v.endswith("Be brief.") for v in Q.values())
Q_EXPLAIN = {k: v[: -len("Be brief.")] + "Explain how it works, step by step." for k, v in Q.items()}
