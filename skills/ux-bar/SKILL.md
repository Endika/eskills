---
name: ux-bar
description: Use when building or reviewing UI to apply my design and UX bar on top of frontend-design — semantic color and design-system rules (coral is brand; positive=owed, warn=owes, danger=error/delete).
---

# ux-bar

## Overview

My design/UX bar. It layers on top of `frontend-design` (reference it for the craft) and
adds the rules I care about. Usable standalone on a diff, and invoked by the quality stage
of `eskills:task-flow`.

## Semantic color — the rule I break most often

- **Brand is brand, never status.** Coral (`#FF5A47` light / `#FF7A66` dark) is the brand.
  Coral conventionally reads as "owe / alert" in money apps, so brand color must **never**
  also mean a debt or an error.
- Map status to its own semantic token:
  - "te deben" / credit / owed-to-you → **`pos`** (green)
  - "tú debes" / owes → **`warn`** (amber)
  - error / delete / destructive / alert → **`danger`** (red)
- Use brand **sparingly** — icon, hero, primary CTA — not to paint balances or errors.

## Design-system discipline

- **Use tokens, never hardcoded palette values** (no raw `slate-/violet-/rose-NNN`).
  Surfaces, text, border, brand all go through semantic CSS variables so light/dark flip
  for free.
- Ship light **and** dark; verify both. Respect `system` as the default preference.

## Accessibility floor

- Check contrast: small text needs **AA 4.5:1**. Flag anything below it.
- A conscious exception is allowed only if named explicitly (e.g. coral fill + white text
  sits at ~3:1 — kept on purpose, with the darker `#E8472F` fallback documented). An
  *unflagged* sub-AA choice is a finding.

## UX checks

- Destructive actions confirm or are undoable; loading/empty/error states exist.
- Graceful degradation: a missing key/integration hides the feature, it doesn't crash.

## Output

When reviewing, report findings as `file:line → which rule → the fix`. Default to passing
only what you actually checked.
