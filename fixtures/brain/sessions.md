# Sessions

All in `src/flask/sessions.py`. Default is a signed-cookie session (client side, not encrypted).

## Classes
- `SessionMixin(MutableMapping)`: `permanent` property, flags `modified`, `accessed`, `new`.
- `SecureCookieSession(CallbackDict, SessionMixin)`: sets `modified`/`accessed` on change.
- `NullSession(SecureCookieSession)`: returned when no `SECRET_KEY`; writes call `_fail`
  (RuntimeError telling you to set the secret key).
- `SessionInterface`: base API. `open_session(app, request)`, `save_session(app, session,
  response)`, `make_null_session`, `is_null_session`, `should_set_cookie`,
  `get_expiration_time`, and `get_cookie_name/domain/path/httponly/secure/samesite/partitioned`
  (each reads the matching `SESSION_COOKIE_*` config key).
- `SecureCookieSessionInterface`: class attrs `salt="cookie-session"`, `digest_method`
  (sha1 via `_lazy_sha1`), `key_derivation="hmac"`, `serializer=session_json_serializer`,
  `session_class`. `get_signing_serializer(app)` builds an itsdangerous
  `URLSafeTimedSerializer` using `SECRET_KEY_FALLBACKS` + `secret_key` (current key last in
  list -> top for itsdangerous); returns None when no key.

## Flow
- Load: lazily in `AppContext._get_session` (`src/flask/ctx.py`); also forced during
  `AppContext.push` for requests. `open_session` returning None -> `make_null_session`.
  Bad/expired signature -> fresh empty session. Max age = `PERMANENT_SESSION_LIFETIME`.
- `AppContext.session` property sets `session.accessed = True` (drives `Vary: Cookie`).
- Save: `Flask.process_response` (`src/flask/app.py` ~L1394) calls
  `session_interface.save_session` unless it is a null session.
  Empty+modified -> `delete_cookie`; empty -> nothing; else `set_cookie` when
  `should_set_cookie` (modified, or permanent and `SESSION_REFRESH_EACH_REQUEST`).
- Payload encoding: `TaggedJSONSerializer` in `src/flask/json/tag.py` (tags for tuple,
  bytes, Markup, UUID, datetime, dict with `" di"` key) exposed as `session_json_serializer`.

## Related
- Config keys: `SECRET_KEY`, `SECRET_KEY_FALLBACKS`, `SESSION_COOKIE_*`,
  `SESSION_REFRESH_EACH_REQUEST`, `PERMANENT_SESSION_LIFETIME`, `MAX_COOKIE_SIZE`
  (defaults in `Flask.default_config`, see config.md).
- Flash messages use the session: `flash` / `get_flashed_messages` in `src/flask/helpers.py`.
- Swap implementation: set `app.session_interface = MyInterface()` (class attr on `Flask`).
- Test helper: `FlaskClient.session_transaction` in `src/flask/testing.py`.
- Tests: `tests/test_basic.py` (session cases), `tests/test_session_interface.py`.
