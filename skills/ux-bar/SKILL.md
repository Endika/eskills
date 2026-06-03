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

## Accessibility floor (WCAG 2.2 AA)

POUR: Perceivable, Operable, Understandable, Robust. The checks that catch most barriers:

- **Contrast:** small text **4.5:1**, large text / UI components **3:1**. A sub-AA choice is a finding unless named on purpose (e.g. coral fill + white text sits at ~3:1 — kept, with the darker `#E8472F` fallback documented).
- **Semantics first:** use the real element (`button`, `a`, `nav`, `label`) before a `div` + ARIA. Correct Name / Role / Value; text alternatives for icons and images.
- **Keyboard:** every interactive element reachable and operable by keyboard, with a **visible focus indicator** (SC 2.4.11). No keyboard traps; logical focus order.
- **Target size:** interactive targets **≥ 24×24 CSS px** (SC 2.5.8).
- **Dynamic state:** announce async changes via `aria-live`/live regions; descriptive errors with how to fix (SC 3.3.3).
- **Reflow:** usable up to 400% zoom without loss of content or function.

## UX checks

- Destructive actions confirm or are undoable; loading/empty/error states exist.
- Graceful degradation: a missing key/integration hides the feature, it doesn't crash.

## Output

When reviewing, report findings as `file:line → which rule → the fix`. Default to passing
only what you actually checked.
