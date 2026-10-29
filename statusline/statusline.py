#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

GREEN, YELLOW, RED, BLUE, DIM, RESET = (
    "\033[32m", "\033[33m", "\033[31m", "\033[36m", "\033[2m", "\033[0m"
)


def last_main_usage(path):
    # Only the tail is read: transcripts grow to tens of MB.
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            f.seek(max(0, f.tell() - 2_000_000))
            lines = f.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        if '"assistant"' not in line or '"usage"' not in line:
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if entry.get("type") != "assistant" or entry.get("isSidechain"):
            continue
        usage = (entry.get("message") or {}).get("usage")
        if usage and entry.get("timestamp"):
            return entry["timestamp"], usage
    return None


def git_branch(cwd):
    def git(*args):
        return subprocess.run(
            ["git", "-C", cwd, *args], capture_output=True, text=True, timeout=1
        ).stdout.strip()

    try:
        top = git("rev-parse", "--show-toplevel")
        if not top:
            return None
        branch = git("branch", "--show-current") or git("rev-parse", "--short", "HEAD")
        dirty = "*" if git("status", "--porcelain", "--untracked-files=no") else ""
    except (OSError, subprocess.TimeoutExpired):
        return None
    return f"{os.path.basename(top)}: {branch}{dirty}"


def short(n):
    return f"{n / 1_000_000:g}M" if n >= 1_000_000 else f"{round(n / 1000)}k"


def minutes(seconds):
    m = int(seconds // 60)
    return f"{m // 60}h{m % 60:02d}m" if m >= 60 else f"{m}m"


def main():
    data = json.load(sys.stdin)
    model = data.get("model") or {}
    window = data.get("context_window") or {}
    parts = [model.get("display_name") or model.get("id") or "?"]

    found = last_main_usage(data.get("transcript_path") or "")
    tokens = None
    if found:
        _, usage = found
        tokens = (
            usage.get("input_tokens", 0)
            + usage.get("cache_read_input_tokens", 0)
            + usage.get("cache_creation_input_tokens", 0)
        )

    size = window.get("context_window_size")
    if not size:
        size = 1_000_000 if "1m" in (model.get("id") or "").lower() else 200_000
    pct = window.get("used_percentage")
    if pct is None and tokens is not None:
        pct = tokens / size * 100

    if pct is None:
        parts.append(f"{DIM}ctx —{RESET}")
    else:
        color = GREEN if pct < 50 else YELLOW if pct < 80 else RED
        used = f" ({short(tokens)}/{short(size)})" if tokens is not None else ""
        parts.append(f"{color}ctx {pct:.0f}%{RESET}{used}")

    cwd = (data.get("workspace") or {}).get("current_dir") or data.get("cwd")
    branch = git_branch(cwd) if cwd else None
    if branch:
        parts.append(f"{YELLOW if branch.endswith('*') else DIM}{branch}{RESET}")

    if found:
        ts, usage = found
        created = usage.get("cache_creation") or {}
        five_min_only = created.get("ephemeral_5m_input_tokens", 0) > 0 and not created.get(
            "ephemeral_1h_input_tokens", 0
        )
        ttl = 300 if five_min_only else 3600
        last = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        elapsed = (datetime.now(timezone.utc) - last).total_seconds()
        if elapsed < ttl:
            parts.append(f"{GREEN}🔥 cache {minutes(ttl - elapsed)}{RESET}")
        else:
            parts.append(f"{BLUE}❄️ cache cold ({minutes(elapsed)} ago){RESET}")
    else:
        parts.append(f"{DIM}cache —{RESET}")

    print(" · ".join(parts))


if __name__ == "__main__":
    main()
