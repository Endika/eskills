---
name: comms
description: Use when writing text that leaves this machine with a person on the other end — an email, a comment or issue on a repo I don't own, a follow-up to a maintainer or an institution, release notes, a reply to a review bot. Not for commits and PR bodies (standards) or UI copy (ux-bar).
---

# comms

## Overview

My bar for outward text. The reader owes me nothing: not their attention, not a reply, not
a merge. So the message earns its own way in — short, specific, honest about what is and
isn't true — and then it stops. **Drafts are shown to me and sent by me.** This skill never
posts, mails or comments on its own.

## When to use

- An email, especially to an institution or someone who did me a favour.
- An issue, PR description or comment on a repo **I don't own**.
- A follow-up or ping to a maintainer, a researcher, a group.
- Release notes, a catalog entry, anything a user reads to decide something.
- A reply on a review-bot thread (Copilot, codex, CodeRabbit) in someone's PR.

## What this skill does not own

One canonical owner per rule — this one links, it doesn't copy.

- **Commit messages, PR titles and bodies** → `eskills:standards`.
- **UI strings and in-app copy** → `eskills:ux-bar`.
- **Inclusive language**, in every locale → `eskills:standards`, which is the single source
  for it. It applies to everything here too.

## Rules

- **One ask per message.** If there are two, the second one gets ignored — send it later or
  drop it. A message with no ask at all is fine; say so explicitly ("no need to reply").
- **One ping, then stop.** A follow-up is one short message, once, without urgency
  manufactured for the occasion. Never a batch of pings across several people or repos on
  the same day; never a second nudge because the first got no answer. Silence is an answer.
- **Claim only what's verified, and name the limit in the same breath.** "Sign recognition,
  with these limits" — never the capability I wish I had. An overclaim to a community
  that's tired of being promised things costs more than the whole message gains.
- **Don't post what the code already said.** If a review bot's point is already fixed in the
  diff, report that to me in chat — adding a reply to someone else's PR is noise they have
  to read.
- **Never invent a reference.** No filler `#NN`, no issue number, commit or release that I
  haven't checked exists. A wrong cross-reference notifies a stranger's thread.
- **Match the reader's language.** Upstream open source is English. Someone who wrote to me
  in Spanish, Euskara, Galician or Catalan gets an answer in that language.
- **Guest register upstream.** In a repo I don't own: describe the problem, offer the fix,
  accept the maintainer's call. No process lectures, no deadlines, no "any update on this?".
- **No AI footers or trailers anywhere** — same rule as commits, and it extends to emails,
  issues and comments.
- **Length is a courtesy.** Lead with the point. If it needs scrolling, it needs cutting or
  a link to the detail.

## Before it goes out

1. Every factual claim traced to something I checked — not to a plausible memory.
2. Exactly one ask, or an explicit none.
3. Would it still read fine forwarded to someone I didn't write it for?
4. Shown to me in full. Sending, posting or emailing is my action, not the agent's.

## Note on upstream mechanics

The PAT can't write to repos I don't own: no issue, no PR, no editing a body. So the
deliverable there is **the text, ready to paste**, and the claim is "here's the draft",
never "posted".
