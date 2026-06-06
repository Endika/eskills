# Formatting & lint

Source of truth: `flipper-trivia-zero/.clang-format` (also habit-flow, hyper-focus-calc)
and the `linter:` targets in their Makefiles. `flipper-nfc-stock` and TagTinker ship
**without** `.clang-format` — that's the divergence to standardize away: every new FAP gets
one.

## .clang-format

Flipper firmware style — LLVM base, 4-space indent, 100-col limit:

```yaml
BasedOnStyle: LLVM
IndentWidth: 4
ColumnLimit: 100
AllowShortFunctionsOnASingleLine: None
IndentCaseLabels: true
```

`make format` runs `clang-format -i` over the tracked `*.c`/`*.h`:

```make
FORMAT_FILES := $(shell git ls-files '*.c' '*.h' 2>/dev/null)
ifeq ($(strip $(FORMAT_FILES)),)
FORMAT_FILES := $(shell find . -type f \( -name '*.c' -o -name '*.h' \) ! -path './.git/*' | sort)
endif
format:
	clang-format -i $(FORMAT_FILES)
```

CI enforces it as a dry-run gate (fails on drift):

```sh
git ls-files '*.c' '*.h' | xargs clang-format --dry-run --Werror
```

## cppcheck

`make linter` runs cppcheck `--enable=all --inline-suppr` over the real sources, with
**targeted suppressions** for the false-positives this layout provokes — notably
`unusedFunction` on `main.c` / `*_app.c` entry points (they're called by the firmware, not
locally) and `missingIncludeSystem`. From `flipper-habit-flow`:

```sh
cppcheck --enable=all --inline-suppr -I. \
  --suppress=missingIncludeSystem \
  --suppress=constParameterPointer:src/app/hf_views.c \
  --suppress=unusedFunction:main.c \
  src/domain/habit.c src/domain/habit_date.c \
  src/persistence/habit_store.c src/platform/hf_rtc.c \
  src/application/hf_session_service.c \
  src/app/habitflow_app.c src/app/hf_views.c main.c tests/test_habit.c
```

Prefer **inline `// cppcheck-suppress` or path-scoped `--suppress`** over disabling a check
globally — keep the signal. List the sources explicitly so cppcheck doesn't wander into the
firmware tree.
