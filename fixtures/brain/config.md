# Config

## Config class — `src/flask/config.py`
- `Config(dict)`: `__init__(root_path, defaults)`. Loaders:
  `from_envvar`, `from_prefixed_env` (default prefix `FLASK`, i.e. `FLASK_*` vars; JSON-parses values,
  `__` nests into dicts), `from_pyfile`, `from_object` (only UPPERCASE attrs),
  `from_file(path, load=json.load/tomllib.load)`, `from_mapping`, `get_namespace`.
- `ConfigAttribute` descriptor: exposes a config key as an app attribute
  (e.g. `app.secret_key`, `app.testing`, `app.permanent_session_lifetime` — declared in
  `src/flask/sansio/app.py` / `src/flask/app.py`).

## Where the app gets it
- `Flask.default_config` (dict literal, `src/flask/app.py` ~L206). Keys: `DEBUG`, `TESTING`,
  `PROPAGATE_EXCEPTIONS`, `SECRET_KEY`, `SECRET_KEY_FALLBACKS`, `PERMANENT_SESSION_LIFETIME`
  (31 days), `USE_X_SENDFILE`, `TRUSTED_HOSTS`, `SERVER_NAME`, `APPLICATION_ROOT`,
  `SESSION_COOKIE_*` (NAME, DOMAIN, PATH, HTTPONLY, SECURE, PARTITIONED, SAMESITE),
  `SESSION_REFRESH_EACH_REQUEST`, `MAX_CONTENT_LENGTH`, `MAX_FORM_MEMORY_SIZE` (500_000),
  `MAX_FORM_PARTS` (1000), `SEND_FILE_MAX_AGE_DEFAULT`, `TRAP_BAD_REQUEST_ERRORS`,
  `TRAP_HTTP_EXCEPTIONS`, `EXPLAIN_TEMPLATE_LOADING`, `PREFERRED_URL_SCHEME`,
  `TEMPLATES_AUTO_RELOAD`, `MAX_COOKIE_SIZE`, `PROVIDE_AUTOMATIC_OPTIONS`.
- `App.make_config(instance_relative)` (`src/flask/sansio/app.py` ~L480): copies
  `default_config`, sets `DEBUG` from `get_debug_flag()`, root = `instance_path` if
  `instance_relative_config=True` else `root_path`; instantiates `config_class`.
- Instance folder: `App.auto_find_instance_path` -> `<prefix>/var/<name>-instance` when
  installed, else `instance/` next to the package/module (`find_package` in
  `src/flask/sansio/scaffold.py`). `Flask.open_instance_resource` reads from it.

## Config consumers (read at runtime, not cached unless noted)
- Sessions: see sessions.md. Request limits: `Request.max_content_length`,
  `max_form_memory_size`, `max_form_parts` in `src/flask/wrappers.py`
  (per-request override, fall back to config). Cookie size: `Response.max_cookie_size`.
- `Flask.run` reads `SERVER_NAME`, `DEBUG`; `FLASK_DEBUG` env overrides `app.debug`.
- `Flask.create_url_adapter`: `SERVER_NAME`, `APPLICATION_ROOT`, `PREFERRED_URL_SCHEME`.
- `Flask.handle_exception`: `PROPAGATE_EXCEPTIONS`/`TESTING`/`debug`.
- Template: `TEMPLATES_AUTO_RELOAD`, `EXPLAIN_TEMPLATE_LOADING` (`create_jinja_environment`).

## Gotchas
- `app.debug` setter also updates `config["DEBUG"]` and jinja auto reload.
- Keys must be UPPERCASE to be loaded from objects/files.
- Tests: `tests/test_config.py`, `tests/test_instance_config.py`.
