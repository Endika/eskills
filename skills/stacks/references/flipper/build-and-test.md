# Build & test — FAP Makefile + host tests

Source of truth: `flipper-habit-flow/Makefile` (the lean `$(OBJS)` pattern) and
`flipper-trivia-zero/Makefile` (the same, plus a Python pack pipeline). Use the lean
pattern for new apps; trivia's per-test hand-written rules are the verbose variant.

## The Makefile

Per-app `Makefile` at the repo root. Host-test toolchain is gcc; the `.fap` is built by the
firmware's `fbt` (or `ufbt` in CI).

```make
PROJECT_NAME = habit_flow
FAP_APPID = flipper_habit_flow

FLIPPER_FIRMWARE_PATH ?= /home/<YOUR_PATH>/flipperzero-firmware
PWD = $(shell pwd)

CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -I.

.PHONY: all help test prepare fap clean clean_firmware format linter
all: test

# clang-format / cppcheck targets → see formatting.md

# --- host tests: compile domain + test TU with gcc, run the binary ---
OBJS = habit_date.o habit.o test_habit.o
test: $(OBJS)
	$(CC) $(CFLAGS) -o test_habit $(OBJS)
	./test_habit

habit.o: src/domain/habit.c include/domain/habit.h
	$(CC) $(CFLAGS) -c src/domain/habit.c -o habit.o
# … one .o rule per domain unit under test, plus the test_*.o TU

# --- build the .fap via the firmware tree ---
prepare:        # symlink this repo into the firmware's applications_user
	@if [ -d "$(FLIPPER_FIRMWARE_PATH)" ]; then \
		mkdir -p $(FLIPPER_FIRMWARE_PATH)/applications_user; \
		ln -sfn $(PWD) $(FLIPPER_FIRMWARE_PATH)/applications_user/$(PROJECT_NAME); \
	fi

clean_firmware:
	@[ -d "$(FLIPPER_FIRMWARE_PATH)/build" ] && rm -rf $(FLIPPER_FIRMWARE_PATH)/build || true

fap: prepare clean_firmware clean
	@cd $(FLIPPER_FIRMWARE_PATH) && ./fbt fap_$(FAP_APPID)

clean:
	rm -f *.o tests/*.o test_habit
```

Notes:

- `FLIPPER_FIRMWARE_PATH ?=` is overridable; CI sets it / uses the ufbt action instead.
- `fap` chains `prepare → clean_firmware → clean` so the build is reproducible.
- trivia splits its many tests into separate `test_*` binaries and a `test:` aggregate
  target; same idea, more targets.

## Host tests (no mocks)

`tests/test_*.c`, plain C, `<assert.h>` + `printf`, compiled and run on the host. They
exercise **`domain/` only** — which is why `domain/` must not include furi. In-memory
structs act as fakes; no mocking framework. (The _why_ — fewer high-signal tests, no
mock-only tests — is in `standards`; this file only shows the FAP-specific wiring.)

Real example — `flipper-habit-flow/tests/test_habit.c`:

```c
#include "include/domain/habit.h"
#include "include/domain/habit_date.h"
#include <assert.h>
#include <stdio.h>

static void test_toggle_and_streak(void) {
    Habit h;
    hf_habit_set_defaults(&h, "Run");
    bool m = false;
    assert(h.streak == 0);
    hf_habit_toggle_today(&h, &m);
    assert(h.completed_today && h.streak == 1 && !m);
}
// main() calls each test_* and prints a pass line
```

trivia goes further: a `tests/embedded_pack_stub.c` stands in for the generated data pack,
and `test_pack_integration.c` exercises reader → pool end-to-end against it — an
integration-flavored test over an in-memory fake, exactly the `standards` preference.
