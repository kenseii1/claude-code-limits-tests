# Where things live

## Source (`src/flask/`)
| Need | File |
|---|---|
| Flask class, WSGI entry, dispatch, error handling | `app.py` |
| Sans-IO app base (config, url_map, registration) | `sansio/app.py` |
| Decorators shared with blueprints | `sansio/scaffold.py` |
| Blueprints | `sansio/blueprints.py`, `blueprints.py` |
| Contexts (`AppContext`) | `ctx.py` |
| `current_app`, `g`, `request`, `session` proxies | `globals.py` |
| Request/Response subclasses | `wrappers.py` |
| Sessions | `sessions.py` |
| Config | `config.py` |
| CLI (`flask` command) | `cli.py`, `__main__.py` |
| `url_for`, `flash`, `send_file`, `abort`... | `helpers.py` |
| Jinja integration | `templating.py` |
| JSON provider / tagged serializer | `json/provider.py`, `json/tag.py` |
| `View`, `MethodView` | `views.py` |
| Signals | `signals.py` |
| Test client / CLI runner | `testing.py` |
| Logger setup | `logging.py` |
| Dev-time error helpers | `debughelpers.py` |
| Type aliases (`ResponseReturnValue`, `RouteCallable`) | `typing.py` |
| Public exports | `__init__.py` |

## Tests (`tests/`)
- `conftest.py` fixtures: `app`, `app_ctx`, `req_ctx`, `client`, `test_apps`, autouse `leak_detector`.
- Files named `test_<module>.py` mirror the source module (`test_basic.py` is the big one).
- Fixture apps: `tests/test_apps/` (`cliapp`, `blueprintapp`, `helloworld`, ...).
- Typing checks: `tests/type_check/` (run by mypy, not pytest).
- Run: `pytest` (config in `pyproject.toml`; `filterwarnings = error`, so new warnings
  fail tests). Full matrix: `tox`. Typing: `tox -e typing` (strict mypy). Style: ruff
  (isort force-single-line) via `pre-commit`.

## Docs / meta
- `docs/` Sphinx rst (`api.rst` lists public API; `lifecycle.rst`, `reqcontext.rst`,
  `appcontext.rst`, `config.rst`, `cli.rst`, `patterns/`, `tutorial/`). Build: `tox -e docs`.
- `CHANGES.rst`: changelog; add an entry for user-visible changes.
- `examples/`: `tutorial/` (flaskr), `javascript/`, `celery/`.
- `.github/workflows/`: `tests.yaml`, `pre-commit.yaml`, `publish.yaml`, `lock.yaml`, `zizmor.yaml`.
- `pyproject.toml`: deps, tox envs, ruff/mypy/pytest config. `uv.lock`: pinned deps.

## Conventions
- `from __future__ import annotations`; `import typing as t`; one import per line.
- New public names must be exported in `__init__.py` and documented in `docs/api.rst`.
- `@setupmethod` guards registration methods after first request (`_check_setup_finished`).
