# Flipper FAP — gotchas

## Flipper FAP: release-please leaves application.fam un-bumped

- **Symptom:** one leg of the triad stays behind on release — e.g. `application.fam`'s
  `fap_version`, OR `include/version.h`'s constant — while the others bump → catalog/CI
  mismatch, and an in-app "version" string shows the stale number.
- **Means:** the `generic` updater only replaces a version on a line that **itself carries**
  the `x-release-please-version` marker. The marker must be **INLINE on the same line** as
  the value — `fap_version="x.y.z"  # x-release-please-version` and
  `#define APP_VERSION "x.y.z" // x-release-please-version`. A marker on a **separate line
  above** the `#define` (or a missing/edited marker) makes the updater silently no-op that
  file. (Hit on flipper-tutu: version.h had the marker on its own line and stuck at 0.1.0
  while fam/manifest advanced.)
- **Fix:** put the marker inline on each version-bearing line; sync the lagging file to the
  current version once by hand; keep the triad `application.fam` ↔ `include/version.h` ↔
  `.release-please-manifest.json` aligned. See `stacks/references/flipper/release-please.md`.

## Flipper FAP: catalog submission rejected on version/commit

- **Symptom:** the official catalog CI fails the entry.
- **Means:** the manifest `commit_sha` points at a later **fix** commit instead of the
  tagged **release** commit, or the entry version ≠ `fap_version`.
- **Fix:** point `commit_sha` at the release commit; make the catalog version equal
  `fap_version`. (Catalog-update-flow memory + `stacks` → flipper.)

## Flipper FAP: host test won't compile (furi symbols)

- **Symptom:** `make test` fails to compile with undefined furi references.
- **Means:** a file under test (transitively) includes `furi` — furi isn't available on the
  host gcc build; the layering leaked.
- **Fix:** keep `domain/` pure C and move the furi-touching code behind a plain-C signature
  in `platform/`. Only test `domain/`. See `stacks/references/flipper/architecture.md`.

## Flipper FAP: cppcheck flags entry points as unusedFunction

- **Symptom:** `make linter` errors on `unusedFunction` for `main.c` / `*_app.c` / port files.
- **Means:** those functions are called by the firmware, not within the TU — a cppcheck
  false positive, not dead code.
- **Fix:** add a path-scoped `--suppress=unusedFunction:<path>` (or inline
  `// cppcheck-suppress`), never disable the check globally. See
  `stacks/references/flipper/formatting.md`.

## Flipper FAP: blank/stale UI when launched from favourites or quick-buttons

- **Symptom:** the screen is blank or frozen (UI never refreshes) when the app is opened
  from a **desktop favourite** or a **quick-press button** shortcut — but it works fine
  when opened from the **Apps menu**. (Reported by catalog users on two of my apps.)
- **Means:** the app only calls `view_port_update()` in reaction to input — the main loop
  blocks on `furi_message_queue_get(..., FuriWaitForever)` and paints nothing until a key
  is pressed. The Apps menu **masks** it: the loader's background hourglass animation
  forces a GUI redraw, so the first frame appears. Favourites/quick-buttons skip that
  loader → nothing triggers the draw. The app was leaning on an external redraw ("a bug"),
  not driving its own.
- **Fix:** force the redraw from the app itself. (1) Draw once immediately after
  `gui_add_view_port(...)` with `view_port_update(view_port)`. (2) Don't depend on input to
  paint: either give the queue a **finite timeout** (`furi_message_queue_get(q, &e, 50)`)
  and call `view_port_update()` **every loop tick**, or call it after **every** state
  change (including the initial state). Same fix for a `ViewDispatcher`/`SceneManager` app:
  ensure the first scene transition happens before the loop blocks. See
  `stacks/references/flipper/architecture.md`.
