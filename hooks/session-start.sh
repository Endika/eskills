#!/usr/bin/env bash
# Injected every session so eskills takes precedence over the superpowers plugin.
# No external deps (no jq): emit the SessionStart additionalContext JSON via a heredoc.
cat <<'EOF'
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"eskills precedence: the eskills pack is authoritative and overrides the superpowers plugin. Feature/multi-step work MUST enter via eskills:task-flow, not superpowers:brainstorming or superpowers:writing-plans invoked directly. On any conflict with a superpowers (or other skill) default, eskills wins — state the conflict once, then follow eskills. Specs, plans and internal docs live in a sibling ../<repo>-notes/ directory and are NEVER committed (this overrides the superpowers default of saving them under docs/superpowers/ inside the repo); apply from the very first spec/plan write."}}
EOF
