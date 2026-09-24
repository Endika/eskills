#!/usr/bin/env python3
"""Warn (never block) when a commit adds lines that carry generated-code tells.

Reads the PreToolUse payload on stdin and, for `git commit`, scans the lines the
commit would add against the mechanical half of
skills/standards/references/code-tells.md. Everything that needs judgment
(defensive noise, needless abstraction, duplicated helpers) stays in that list
for review; only phrases that almost never appear in code a person meant to
write are matched here. Markdown is skipped: prose is the ai-tells hook's job.
"""

import json
import os
import re
import shlex
import subprocess
import sys

# Pictographs, plus the warning sign and three dingbats generated scripts favour. Plain
# check marks (U+2713) stay out: they are ordinary CLI output.
EMOJI = "[" + "".join(map(chr, (0x26A0, 0x2705, 0x274C, 0x2728))) + chr(0x1F300) + "-" + chr(0x1FAFF) + "]"

# (label, pattern) — matched per added line. Spaces are written as `\ ` so this file does
# not trip its own patterns when committed.
TELLS = [
    ("comment addressed to the reader", r"(?:#|//|/\*|\*|--)\s*(?:In\ a\ real(?:\ world)?\ (?:application|app|project|implementation|scenario)"
                                        r"|Replace\ (?:this\ )?with\ (?:your|the\ actual)"
                                        r"|You\ (?:may|might)\ want\ to\ (?:adjust|change|replace|add))"),
    ("leftover placeholder", r"\byour[-_\ ]?api[-_\ ]?key(?:[-_\ ]?here)?\b|\bYOUR_[A-Z_]+_HERE\b"
                            r"|(?:#|//)\s*TODO:?\s*[Ii]mplement\ (?:this|me|logic|here)\b"),
    ("step-by-step banner", r"^\s*(?:#|//|--)\s*Step\ \d+\s*:"),
    ("emoji in log output", r"(?:\bprint(?:ln|f)?|console\.(?:log|info|warn|error)|\blog(?:ger)?\.\w+|\becho)\b.*"
                            + EMOJI),
    # Bare or `Exception` only: `except ValueError: pass` is an ordinary idiom, and an empty JS
    # `catch {}` is usually a guarded localStorage read — both measured, see code-tells.md.
    ("swallowed exception", r"^\s*except(?:\s+(?:Exception|BaseException)(?:\s+as\s+\w+)?)?\s*:\s*pass\b"),
]
# `except ...:` then `pass` on the next added line — the same swallow, split in two.
EXCEPT_OPEN = re.compile(r"^\s*except(?:\s+(?:Exception|BaseException)(?:\s+as\s+\w+)?)?\s*:\s*$")
PASS_ONLY = re.compile(r"^\s*pass\s*$")

RELEVANT = re.compile(r"""\bgit\s+(?:-C\s+("[^"]+"|'[^']+'|\S+)\s+)?commit\b""")
# Short options of `git commit` that take a value: whatever follows them in a cluster is that
# value, so `-mRefactor` carries no `-a`.
TAKES_VALUE = set("mcCFtuS")
SKIP_SUFFIXES = (".md", ".markdown", ".rst", ".txt")
MAX_DIFF_BYTES = 2 * 1024 * 1024
MAX_HITS_SHOWN = 8


def commits_all(rest):
    """True when the commit options include -a/--all; `rest` is the command after `commit`."""
    try:
        tokens = shlex.split(re.split(r"&&|\|\||[;|]", rest, maxsplit=1)[0])
    except ValueError:
        return False
    skip = False
    for tok in tokens:
        if skip:
            skip = False
        elif tok == "--all":
            return True
        elif tok.startswith("-") and not tok.startswith("--"):
            for i, ch in enumerate(tok[1:], 1):
                if ch == "a":
                    return True
                if ch in TAKES_VALUE:
                    skip = i == len(tok) - 1
                    break
    return False


def added_lines(diff):
    path = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            # Git ends the path with a tab when it holds a space, and quotes it when
            # core.quotePath would escape it.
            name = line[4:].rstrip("\t")
            if name.startswith('"') and name.endswith('"'):
                name = name[1:-1]
            path = name[2:] if name.startswith("b/") else None
        elif line.startswith("+") and path and not path.lower().endswith(SKIP_SUFFIXES):
            yield path, line[1:]


def scan(diff):
    hits, prev_except, prev_path = [], False, None
    for path, line in added_lines(diff):
        if path != prev_path:
            prev_except, prev_path = False, path
        for label, pattern in TELLS:
            found = re.search(pattern, line)
            if found:
                hits.append(f"{label} in {path}: “{found.group(0).strip()[:80]}”")
                break
        else:
            if prev_except and PASS_ONLY.match(line):
                hits.append(f"swallowed exception in {path}: “except: pass”")
        prev_except = bool(EXCEPT_OPEN.match(line))
    return hits


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # never let a malformed payload get in the way of the command

    command = (payload.get("tool_input") or {}).get("command") or ""
    commit = RELEVANT.search(command)
    if not commit:
        return 0
    cwd = os.path.join(payload.get("cwd") or os.getcwd(), commit.group(1).strip("\"'") if commit.group(1) else "")

    base = "HEAD" if commits_all(command[commit.end():]) else "--cached"
    git = ["git", "-c", "core.quotePath=false", "diff", "--no-color", "-U0", base]
    try:
        out = subprocess.run(git, cwd=cwd, capture_output=True, timeout=4)
    except (OSError, subprocess.TimeoutExpired):
        return 0
    if out.returncode != 0:
        return 0  # not a repo, no HEAD yet — the commit itself will say what's wrong

    raw = out.stdout
    truncated = len(raw) > MAX_DIFF_BYTES
    hits = scan(raw[:MAX_DIFF_BYTES].decode("utf-8", errors="replace"))

    notes = []
    if truncated:
        notes.append(f"only the first {MAX_DIFF_BYTES // 1024 // 1024} MB of the diff were scanned")
    if len(hits) > MAX_HITS_SHOWN:
        notes.append(f"{len(hits) - MAX_HITS_SHOWN} more matches not listed")
    if not hits:
        if truncated:
            print(json.dumps({"systemMessage": f"eskills — code-tells: {notes[0]}, no matches there"}))
        return 0

    listed = "; ".join(hits[:MAX_HITS_SHOWN]) + (f" ({'; '.join(notes)})" if notes else "")
    print(json.dumps({
        "systemMessage": f"eskills — generated-code tells in the lines this commit adds: {listed}",
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                "The lines this commit adds match tells from eskills:standards → "
                f"references/code-tells.md — {listed}. Remove the leftover or handle the error "
                "for real, re-stage, and commit again. The command was NOT blocked; if a match "
                "is a false positive, keep the code and carry on."
            ),
        },
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
