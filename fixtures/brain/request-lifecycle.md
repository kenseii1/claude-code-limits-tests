# Request lifecycle

Every handler method below takes `ctx: AppContext` as its first arg (3.2 change).
All in `src/flask/app.py` unless noted.

1. Server calls `Flask.__call__` -> `Flask.wsgi_app(environ, start_response)` (~L1566).
2. `ctx = self.request_context(environ)` -> `AppContext.from_environ` (`src/flask/ctx.py`):
   builds `app.request_class(environ)`, sets `request.json_module = app.json`, and calls
   `app.create_url_adapter(request)` (bound `MapAdapter`; failure stored as `routing_exception`).
3. `ctx.push()` (`ctx.py`): sets `_cv_app`, sends `appcontext_pushed`, opens session
   (`_get_session`), then `match_request()` -> sets `request.url_rule`, `request.view_args`
   or `request.routing_exception`. Nested pushes counted via `_push_count`.
4. `full_dispatch_request(ctx)`:
   - sends `request_started`
   - `preprocess_request`: `url_value_preprocessor`s, then `before_request` funcs (a non-None
     return short-circuits the view)
   - `dispatch_request`: raises routing exception, auto-OPTIONS via
     `make_default_options_response`, else `ensure_sync(view_functions[rule.endpoint])(**view_args)`
   - any exception -> `handle_user_exception` -> `handle_http_exception` / registered handler
     (found by `_find_error_handler` in `src/flask/sansio/app.py`)
5. `finalize_request`: `make_response(rv)` (str/bytes/dict/list/tuple/Response/generator
   rules), `process_response` (after_request funcs LIFO, `ctx._after_request_functions`,
   **`session_interface.save_session`**), sends `request_finished`.
6. Unhandled exception in step 3-5: `handle_exception` (logs via `log_exception`, sends
   `got_request_exception`, returns 500 or re-raises if `PROPAGATE_EXCEPTIONS`/debug).
7. `response(environ, start_response)` returns the WSGI iterable.
8. `finally`: honours `werkzeug.debug.preserve_context`; `ctx.pop(error)` ->
   `do_teardown_request` (teardown_request funcs, `request_tearing_down`), `request.close()`,
   `do_teardown_appcontext` (`appcontext_tearing_down`), reset `_cv_app`, `appcontext_popped`.
   Teardown errors collected with `_CollectErrors` (`src/flask/helpers.py`).

## Notes
- Async views: `ensure_sync` / `async_to_sync` (needs `asgiref`).
- `stream_with_context` (`helpers.py`) keeps the context alive for generator responses.
- `copy_current_request_context`, `after_this_request` live in `ctx.py`.
- Blueprint hooks are merged per-endpoint-prefix at registration
  (`Blueprint._merge_blueprint_funcs`, `src/flask/sansio/blueprints.py`); lookup uses
  `request.blueprints`.
- Tests: `tests/test_basic.py`, `tests/test_reqctx.py`, `tests/test_appctx.py`,
  `tests/test_user_error_handler.py`.
