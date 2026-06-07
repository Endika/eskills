---
name: ux-bar
description: Use when building or reviewing UI to apply my design and UX bar on top of frontend-design — semantic color, design-system rules (coral is brand; positive=owed, warn=owes, danger=error/delete), and responsive / horizontal-overflow checks.
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

## Responsive & horizontal overflow

The responsive bug I hit most. Symptom → cause → fix:

- **Grid/flex items don't shrink → the page overflows.** A grid/flex item defaults to
  `min-width: auto`, so it refuses to go below its content's intrinsic min-size and drags the
  whole track wider than the viewport. Fix: `min-width: 0` **on the item** (the grid/flex
  child) — not on the inner element.
- **Native controls keep an intrinsic width.** `<select>`/`<input>` carry a min width
  (~longest option / ~20ch) that ignores `min-width:0` on the control itself. Put
  `min-width:0` on its grid/flex **container**; `width:0` on the control alone does nothing.
- **Intrinsic grids beat breakpoints:** `repeat(auto-fit, minmax(min(BASIS, 100%), 1fr))`.
  The `min(BASIS,100%)` is essential — it stops the column floor (`BASIS`) from overflowing
  below that width. Wraps N→1 with no magic media query.
- **`overflow-x: clip` is a mask, not a fix.** It hides the overflow (and preserves
  `position:sticky`, unlike `hidden`), but the element is still too wide. Find and shrink the
  real culprit; keep clip only as defense-in-depth.
- **A header narrower than the content = overflow elsewhere.** On mobile, horizontal overflow
  expands the layout viewport, so a `max-width`/centered header stops lining up with
  full-width cards. Don't fix the header — find what overflows.

**Measure, don't eyeball.** For any "not responsive" report: render at real widths and check
`documentElement.scrollWidth > clientWidth`. Bisect the culprit by hiding each child
(`display:none`) and re-measuring; confirm the fix by injecting the candidate style and
re-measuring **before** editing. Verify down to **320px** (real floor; Galaxy Fold cover
~280px) in every view. Harness: `eskills:stack-gotchas` → "mobile rendering in WSL".

## UX checks

- Destructive actions confirm or are undoable; loading/empty/error states exist.
- Graceful degradation: a missing key/integration hides the feature, it doesn't crash.
- **Inclusive copy:** UI strings follow the inclusive-language rule in `eskills:standards` —
  neutral/collective wording (no `niños/as`, no `-x/-e`), no assumed gender or family shape.
  Report offenders `file:line → fix`.

## Output

When reviewing, report findings as `file:line → which rule → the fix`. Default to passing
only what you actually checked.
