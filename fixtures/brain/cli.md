# CLI

All in `src/flask/cli.py` (click based). Entry point: `[project.scripts] flask = "flask.cli:main"`
(`pyproject.toml`); `python -m flask` -> `src/flask/__main__.py`.

## App discovery
- `FlaskGroup(AppGroup)` is the root group; `main()` calls it. `--app/-A`, `--debug/--no-debug`,
  `--env-file/-e` are eager options handled by `_set_app`, `_set_debug`, `_env_file_callback`.
- `ScriptInfo` holds `app_import_path`, `create_app`, `load_dotenv_defaults`; `load_app()`
  imports the app lazily and caches it. Raises `NoAppException`.
- `locate_app` -> `prepare_import` (path -> module name, adjusts `sys.path`) ->
  `find_best_app` (looks for `app`/`application` var, single Flask instance, or
  `create_app`/`make_app` factory) or `find_app_by_string` (handles `module:name`,
  `module:factory(args)`; uses `_called_with_wrong_args`).
- Without `--app`, falls back to `FLASK_APP`, then `wsgi.py` / `app.py`.

## Built-in commands
- `run_command` (`flask run`): options `--host`, `--port`, `--cert`/`--key`
  (`CertParamType`, `_validate_key`), `--reload`, `--debugger`, `--with-threads`,
  `--extra-files` / `--exclude-patterns` (`SeparatedPathType`). Wraps werkzeug `run_simple`;
  prints banner via `show_server_banner`. Sets `FLASK_RUN_FROM_CLI` in `make_context`.
- `shell_command` (`flask shell`): uses `app.make_shell_context()` (+ `@shell_context_processor`).
- `routes_command` (`flask routes`): `--sort`, `--all-methods`.
- Plugins: entry point group `flask.commands`, loaded in `FlaskGroup._load_plugin_commands`.
- App commands: `app.cli` is an `AppGroup` (created in `Flask.__init__`); blueprints have
  `Blueprint.cli` and `cli_group`. `@app.cli.command()` wraps in `with_appcontext`.
  `FlaskGroup.get_command` loads the app to find them; `list_commands` likewise.

## Dotenv
- `load_dotenv(path=None, load_defaults=True)`: loads `.flaskenv` then `.env` (the latter
  wins), explicit `-e` file wins over both; never overrides vars already in `os.environ`.
  Needs `python-dotenv` (optional extra `dotenv`). Disabled by `FLASK_SKIP_DOTENV`
  (`get_load_dotenv` in `src/flask/helpers.py`).
- `FLASK_DEBUG` is set by `--debug`; read by `get_debug_flag` (`helpers.py`).

## Testing
- `FlaskCliRunner` (`src/flask/testing.py`) via `app.test_cli_runner()`.
- Tests: `tests/test_cli.py`; fixture apps in `tests/test_apps/cliapp/`.
