#!/usr/bin/env python3
"""Warn (never block) when commit/PR/issue text carries generated-prose tells.

Reads the PreToolUse payload on stdin, pulls the human-authored text out of a
git/gh command, and matches it against the high-precision half of
skills/comms/references/ai-tells.md. Single padding words (crucial, robust,
delve) are deliberately NOT matched: on their own they produce false positives,
and a hook that cries wolf is a hook that gets disabled.

python3 is already required by `make check`, so this adds no new dependency.
"""

import json
import re
import sys

# (label, pattern) — each must be specific enough to survive a legitimate sentence.
TELLS = [
    ("Claude trailer or footer", r"Co-Authored-By:\s*Claude|Generated with \[?Claude Code|🤖"),
    ("canned assurance", r"ensur(?:ed|ing) (?:all )?(?:the )?tests? (?:pass|passed)"
                        r"|follow(?:ed|ing) (?:the )?existing conventions?"
                        r"|preserv(?:ed|ing) (?:the )?(?:original|existing) behaviou?r"
                        r"|no functional changes? (?:were )?(?:made|introduced)"),
    ("negative parallelism", r"\bnot just\b[^.]{0,60}\bbut\b|\bit'?s not\b[^.]{0,40}\bit'?s\b"),
    ("copula avoidance", r"\bserves as\b|\bstands as\b|\bfunctions as\b"),
    ("inflated significance", r"\ba testament to\b|\bplays? a (?:crucial|pivotal|key) role\b"
                              r"|\bmarks a pivotal\b|\bindelible mark\b"),
    ("analysis-free -ing clause", r",\s*(?:highlighting|underscoring|showcasing|ensuring|"
                                  r"reflecting|emphasizing|demonstrating)\b"),
    ("attribution to nobody", r"\bexperts (?:argue|say)\b|\bindustry reports\b"
                              r"|\bobservers have noted\b|\bsome critics argue\b"),
    ("pleasantry about the writing", r"\bI hope this helps\b|\bLet me know if you\b"
                                     r"|\bFeel free to reach out\b"),
]

# Where human text lives in the commands worth checking.
TEXT_FLAGS = re.compile(
    r"""(?:-m|--message|-b|--body|-t|--title|--notes)\s+
        (?:"((?:[^"\\]|\\.)*)"|'([^']*)')""",
    re.X,
)
RELEVANT = re.compile(r"\b(?:git\s+commit|gh\s+(?:pr|issue|release)\s+(?:create|edit|comment))\b")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # never let a malformed payload get in the way of the command

    command = (payload.get("tool_input") or {}).get("command") or ""
    if not RELEVANT.search(command):
        return 0

    text = " ".join(m.group(1) or m.group(2) or "" for m in TEXT_FLAGS.finditer(command))
    if not text.strip():
        return 0

    hits = []
    for label, pattern in TELLS:
        found = re.search(pattern, text, re.I)
        if found:
            hits.append(f"{label}: “{found.group(0).strip()}”")

    if not hits:
        return 0

    listed = "; ".join(hits)
    print(json.dumps({
        "systemMessage": f"eskills — generated-prose tells in this text: {listed}",
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                "The text in this command matches tells from eskills:comms → "
                f"references/ai-tells.md — {listed}. These are padding, not style: rewrite "
                "the line to say what changed and re-run. The command was NOT blocked; if a "
                "match is a false positive, keep the wording and carry on."
            ),
        },
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
