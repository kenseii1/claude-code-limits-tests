# Architecture

Flask 3.2.0.dev (Pallets), WSGI microframework. Package in `src/flask/`, built with flit.
Deps: werkzeug (routing/wrappers), jinja2, click, itsdangerous, blinker. Python >=3.11.

## Class layering (sans-IO base + WSGI subclass)
- `Scaffold` — `src/flask/sansio/scaffold.py`: shared by app and blueprint. Route decorators
  (`route`, `get`, `post`, ...), `add_url_rule`, `before_request`, `after_request`,
  `teardown_request`, `errorhandler`, `context_processor`, static folder, `@setupmethod`.
- `App(Scaffold)` — `src/flask/sansio/app.py`: no I/O. Config creation (`make_config`),
  `url_map`, `view_functions`, error handler lookup, `register_blueprint`, jinja env,
  `instance_path`, `json` provider, `debug` property.
- `Flask(App)` — `src/flask/app.py`: WSGI parts. `wsgi_app`, `__call__`, `run`,
  dispatching, `make_response`, `test_client`, `send_static_file`, `open_resource`.
- `Blueprint(Scaffold)` — `src/flask/sansio/blueprints.py` (`BlueprintSetupState`, `record`,
  `register`); thin WSGI subclass `Blueprint` in `src/flask/blueprints.py`.

## Other key pieces
- `AppContext` — `src/flask/ctx.py`. In 3.2 it REPLACES the old Request+App context split:
  one context per request or CLI command; `has_request` says if it carries a request.
  `RequestContext` is a deprecated alias (module `__getattr__`).
- Proxies — `src/flask/globals.py`: `_cv_app` ContextVar; `current_app`, `g`, `request`,
  `session`, `app_ctx` are `LocalProxy` onto it.
- `Request`/`Response` — `src/flask/wrappers.py` (subclass werkzeug; endpoint/blueprint props,
  max_content_length etc. read from app config).
- Sessions — `src/flask/sessions.py` (see sessions.md).
- Templating — `src/flask/templating.py`: `Environment`, `DispatchingJinjaLoader`
  (searches app then blueprint loaders), `render_template`, `stream_template`.
- JSON — `src/flask/json/provider.py` (`JSONProvider`, `DefaultJSONProvider`),
  `src/flask/json/tag.py` (`TaggedJSONSerializer` for session payload).
- Class views — `src/flask/views.py`: `View.as_view`, `MethodView`.
- Signals — `src/flask/signals.py` (blinker): `request_started`, `request_finished`,
  `got_request_exception`, `appcontext_pushed/popped`, `template_rendered`, `message_flashed`.
- Helpers — `src/flask/helpers.py`: `url_for`, `redirect`, `abort`, `flash`,
  `send_file`, `send_from_directory`, `stream_with_context`, `get_root_path`.
- Testing — `src/flask/testing.py`: `FlaskClient`, `FlaskCliRunner`, `EnvironBuilder`.
- Logging — `src/flask/logging.py`: `create_logger`, `default_handler`.
- Debug aids — `src/flask/debughelpers.py`.
- Public API re-exports — `src/flask/__init__.py`.

## Extension points (class attrs on Flask/App)
`request_class`, `response_class`, `session_interface`, `json_provider_class`,
`app_ctx_globals_class`, `jinja_environment`, `config_class`, `url_map_class`, `test_client_class`.

## Deprecation note
`Flask.__init_subclass__` (`src/flask/app.py`) wraps overridden dispatch/error/teardown
methods that lack the new `ctx: AppContext` second param (`add_ctx`/`remove_ctx`).
