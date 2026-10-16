#!/usr/bin/env python3
"""Design decision 14.10 (phase 2): simulate a PRIVATE codebase so the model cannot answer from memory.

Builds a renamed copy of the 11.10 Flask snapshot ("tessel") in the scratchpad (outside your project):
    python3 make_private_repo.py            -> SCRATCH/src-private/tessel
Deterministic: same input -> same output. The Flask source is kept untouched for reference.

Rules are applied in order to every UTF-8 text file AND to every path component (files/dirs named flask*, blueprint*).
Mode "sub" = plain substring (case as written), "word" = regex word boundary (\\b...\\b; "_" counts as a word char, so
run_wsgi_app from werkzeug is NOT touched by the wsgi_app rule). Every renamed name was checked absent from the installed
werkzeug/jinja2/click/itsdangerous/blinker/markupsafe/pytest code, except names that appear there only in docs/comments
or in an unrelated object (jinja2 Environment.handle_exception: Flask never calls it). Library names kept on purpose:
LocalProxy, CallbackDict (werkzeug), max_content_length (werkzeug Request property), json.loads, SERVER_NAME.
"""
import os, pathlib, re, shutil, sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = pathlib.Path(os.environ.get("FLASK_SRC", "./flask")).resolve()  # a Flask main checkout (3.2.0.dev, Oct 2026)
SCRATCH = pathlib.Path(os.environ.get("UL_SCRATCH", "./scratch")).resolve()  # work copies live here, outside your project
OUT = SCRATCH / "src-private" / "tessel"

RULES = [  # (mode, old, new) in order; longer / containing names first
    ("word", "do_teardown_appcontext", "run_app_teardowns"),
    ("sub", "teardown_appcontext", "on_app_teardown"),
    ("word", "_default_template_ctx_processor", "_base_template_vars"),
    ("sub", "context_processor", "ctx_injector"),
    ("sub", "SecureCookieSession", "SignedCookieSession"),
    ("sub", "errorhandler", "fault_handler"),
    ("word", "handle_user_exception", "route_user_fault"),
    ("word", "handle_http_exception", "route_http_fault"),
    ("word", "handle_exception", "route_unhandled_fault"),
    ("word", "_find_error_handler", "_pick_fault_handler"),
    ("word", "process_response", "finalize_reply"),
    ("word", "save_session", "persist_session"),
    ("word", "open_session", "restore_session"),
    ("word", "should_set_cookie", "cookie_needs_write"),
    ("word", "with_appcontext", "needs_app_scope"),
    ("word", "ScriptInfo", "LaunchInfo"),
    ("word", "find_best_app", "locate_main_app"),
    ("word", "_called_with_wrong_args", "_bad_factory_args"),
    ("sub", "add_url_rule", "attach_route_rule"),
    ("word", "wsgi_app", "wsgi_entry"),
    ("word", "full_dispatch_request", "run_full_request"),
    ("word", "dispatch_request", "run_view"),
    ("word", "from_prefixed_env", "load_env_prefixed"),
    ("word", "TaggedJSONSerializer", "TypedCookieSerializer"),
    ("word", "JSONTag", "TypeMarker"),
    ("word", "_cv_app", "_app_var"),
    ("word", "_cv_request", "_req_var"),
    ("word", "MethodView", "VerbView"),
    ("word", "as_view", "to_view_func"),
    ("word", "update_template_context", "fill_template_scope"),
    ("word", "create_url_adapter", "build_url_binder"),
    ("word", "DefaultJSONProvider", "StandardJSONProvider"),
    ("word", "get_send_file_max_age", "static_cache_seconds"),
    ("sub", "SEND_FILE_MAX_AGE_DEFAULT", "STATIC_CACHE_SECONDS_DEFAULT"),
    ("word", "before_app_request", "before_any_request"),
    ("word", "get_signing_serializer", "make_signer"),
    ("sub", "SECRET_KEY_FALLBACKS", "SECRET_KEY_HISTORY"),
    ("sub", "url_for", "link_for"),
    ("sub", "current_app", "active_app"),
    ("sub", "BLUEPRINT", "BUNDLE"), ("sub", "Blueprint", "Bundle"), ("sub", "blueprint", "bundle"),
    ("sub", "FLASK", "TESSEL"), ("sub", "Flask", "Tessel"), ("sub", "flask", "tessel"),
    ("sub", "Pallets", "Tidework"), ("sub", "pallets", "tidework"),
]
_COMPILED = [(re.compile(r"\b" + re.escape(o) + r"\b") if m == "word" else None, o, n) for m, o, n in RULES]


def rn(s):
    """Apply the rename rules to a string (used for file contents, paths, and the question/key texts)."""
    for rx, o, n in _COMPILED:
        s = rx.sub(n, s) if rx else s.replace(o, n)
    return s


def build(out=OUT):
    if out.exists():
        return out
    tmp = out.with_name(out.name + ".building")
    n_text = n_bin = 0
    for p in sorted(SRC.rglob("*")):
        rel = p.relative_to(SRC)
        if any(part in (".git", ".pytest_cache", "__pycache__") for part in rel.parts) or p.is_dir():
            continue
        dst = tmp / rn(str(rel))
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            txt = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(p, dst); n_bin += 1; continue
        dst.write_text(rn(txt), encoding="utf-8"); n_text += 1
    # cli.get_version calls importlib.metadata.version("tessel"); an editable install leaves this in src/
    eg = tmp / "src" / "tessel.egg-info"; eg.mkdir(parents=True, exist_ok=True)
    (eg / "PKG-INFO").write_text("Metadata-Version: 2.1\nName: tessel\nVersion: 3.2.0.dev0\n")
    tmp.rename(out)
    print(f"built {out}: {n_text} text files renamed, {n_bin} binary copied")
    return out


if __name__ == "__main__":
    build()
