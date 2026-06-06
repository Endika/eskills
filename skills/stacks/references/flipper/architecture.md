# Flipper Zero FAP — architecture

Distilled from `flipper-trivia-zero`, `flipper-habit-flow`, `flipper-nfc-stock`,
`flipper-hyper-focus-calc`. (TagTinker is a third-party fork, `fap_author="i12bp8"` — not a
source.) The core idea: **a clean-architecture FAP whose `domain/` is plain C, so the logic
is unit-tested on the host with gcc while `furi` stays quarantined in `platform/`.**

## Layered, furi isolated

Mirror `src/` and `include/` with the same layer dirs. Canonical layers:

- **`domain/`** — pure C business logic. **No `furi`, no I/O.** This is what host tests
  exercise. Always present.
- **`application/`** — services / use-cases that orchestrate domain (e.g. habit-flow's
  `hf_session_service`).
- **`persistence/`** — storage / file load-save. (trivia names this `infrastructure/` — an
  accepted alias; prefer `persistence/` for new apps.)
- **`platform/`** — the **furi isolation boundary**: thin wrappers over furi/RTC/random
  (`hf_rtc`, `random_port`). Domain calls plain-C signatures; only these files include furi,
  so everything below them compiles and tests on the host.
- **`ui/` + `scenes/` + `views/`** — GUI (scene manager, custom views).
- **`app/`** — entry point + app-state orchestration (`*_app.c`, the `entry_point`).
- **`data/` + `i18n/`** — embedded packs as generated C arrays (trivia's bilingual packs).

Rule of thumb: **if it includes `furi`, it lives in `platform/`, `ui/`, `scenes/`,
`views/`, or `app/` — never in `domain/`.** That single boundary is what makes the host
tests possible.

## application.fam

`apptype=FlipperAppType.EXTERNAL`, explicit `sources=[…]` list, `entry_point`,
`requires=[…]`, `stack_size`, `fap_category`, `fap_icon`, and the release-please-managed
`fap_version` (see `release-please.md`).

## The rest

- Build, host tests → `build-and-test.md`.
- `.clang-format` + cppcheck → `formatting.md`.
- Version triad + CI + catalog → `release-please.md`.
- Flipper build/release failures → `eskills:stack-gotchas` (Flipper section).
