# Flask (3.2.0.dev) — repo guide

Source is in `src/flask/`, tests in `tests/`, docs in `docs/`. Notes for fast orientation live in `brain/`.

## Rule
Answer from the relevant `brain/` note. Open source files only if the note does not contain the answer.

## Index
- `brain/architecture.md` — class layering (Scaffold/App/Flask/Blueprint), AppContext, proxies, extension points.
- `brain/request-lifecycle.md` — `wsgi_app` through dispatch, error handling, response finalizing, teardown.
- `brain/sessions.md` — `SessionInterface`, signed-cookie sessions, load/save flow, cookie config.
- `brain/cli.md` — `flask` command, app discovery, `run`/`shell`/`routes`, dotenv, plugins.
- `brain/config.md` — `Config` loaders, `default_config` keys, instance path, who reads which key.
- `brain/where-things-live.md` — file-by-feature map, tests/fixtures, docs, tooling, conventions.

## Commands
- Tests: `pytest`. Full matrix: `tox`. Typing: `tox -e typing`. Style: `pre-commit run --all-files`.
