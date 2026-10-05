# CodeQL — gotchas

With `queries: security-and-quality`, the same handful of structural alerts comes back across
repos. Fixes checked over 52 alerts in 10 repos.

## `py/ineffectual-statement` on a `Protocol` method body

- **Means:** a bare `...` is flagged; one that follows a docstring isn't.
- **Fix:** replace `...` with `pass`. It still passes mypy `strict = true`. Don't invent
  docstrings to silence it.

## `js/missing-origin-check` in a worker

- **In a dedicated worker:** only its creator can message it, so an `event.origin` check is
  dead code. A runtime type guard on the message is worth having, but it doesn't close the
  alert, since the query wants the literal origin check. Dismiss it as a false positive.
- **In a service worker:** `ExtendableMessageEvent.origin` exists and the origin check is
  the right pattern. Add it; it closes the alert.

## `js/incomplete-multi-character-sanitization` on `/<[^>]+>/g`

- **Means:** a structural heuristic. With that exact regex one pass and a loop to a fixed
  point give the same output, because `[^>]+` can't skip a `>`.
- **Fix:** looping until nothing changes closes it. Don't claim `<<a>script>` got through
  before: both forms give `script>`.

## `js/file-system-race`

- **Fix:** drop the `existsSync(f)` check, read directly and handle `ENOENT`.

## `js/http-to-file-access` / `js/file-access-to-http`

- **Means:** the query flags that a remote-data-to-repo-file flow exists, not that it lacks
  validation. In a build script that flow is the job itself.
- **Fix:** none in code. Validating the shape is still worth doing, but the alert stays.
  Dismiss as `won't fix` with the reason written down.

## `py/incomplete-url-substring-sanitization`

- **Means:** almost always a mock or an assert comparing URLs with `in`.
- **Fix:** compare for exact equality against the production constants, and `raise` on the
  unexpected branch.
