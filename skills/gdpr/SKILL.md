---
name: gdpr
description: Use when building, shipping, or auditing one of my B2C apps for GDPR/privacy — classify the data posture (offline / Supabase-backed / ships-to-AI-processor), run the decision gates (personal data? lawful basis? processor DPA? transfer? minimization? DSR/erasure?), add a privacy notice, and add privacy-first cookieless analytics without triggering consent. EU GDPR; references security-bar for the controls.
origin: adapted from ECC healthcare-phi-compliance + hipaa-compliance
---

# gdpr

## Overview

Practical GDPR/privacy for my B2C PWAs — **not legal advice**, an engineering checklist.
First classify the app's **data posture**, then run the **decision gates**, then apply the
guidance for the gaps. Security controls (RLS, secrets, open-write) live in `security-bar` —
referenced, not restated. This skill owns privacy/compliance: lawful basis, minimization,
retention, data-subject rights, processors, transfers, the privacy notice, and analytics.

## When to use

- Building or shipping a feature that collects/stores/transmits personal data.
- Auditing an existing app for GDPR gaps, or writing its privacy notice.
- Choosing/adding analytics (read the analytics section first — it's coupled to consent).

## Step 1 — classify the data posture

My fleet splits three ways; the posture decides how much applies:

1. **Offline / on-device** (e.g. kartaak, converthub) — no server, no egress of user data.
   **Privacy by architecture.** GDPR surface ≈ minimal; the win is _stating_ it (a "runs on
   your device, we collect nothing" notice = trust + the easy compliance win).
2. **Server-backed** (e.g. EventSplit, Monete — Supabase) — I'm a **controller**. Personal
   data of users _and third parties_ (e.g. friends added to an event who never interacted
   with me). This is the real surface: lawful basis, minimization, retention, DSR, RLS.
3. **Client-side but ships to third-party processors** (e.g. mintza → OpenAI/Anthropic/
   Google/Azure) — heaviest: multiple **processors**, **international transfer (US)**, and
   possibly **special-category** content. Controller/processor split depends on BYO-key vs
   hosted — decide it explicitly.

## Step 2 — decision gates

Run these on the data path (adapted from ECC's HIPAA gates):

1. **Is this personal data?** (identifies a person directly or combined — name, email,
   expense tied to a named person, voice). If no → stop, nothing here applies.
2. **Lawful basis?** Name it: consent, contract, or legitimate interest (third-party names
   in a shared event = legitimate interest; document it).
3. **Does this processor / model provider need a DPA** before touching the data? (Supabase,
   any analytics tool, any AI API.) International transfer covered (SCCs / adequacy / DPF)?
4. **Minimum necessary?** Store the least that works (a display label, not full identity).
5. **DSR / erasure handled?** Can a person get their data deleted? For no-login apps,
   "delete the event" _is_ the erasure path — make it real and reachable.
6. **Auditable?** Only where proportionate — see the non-goal below.

## Step 3 — guidance for the gaps

- **Privacy notice** — every app gets one (even offline: "we collect nothing"). Use
  `references/privacy-notice.md`. Disclose every processor (Supabase, analytics, AI APIs)
  and any transfer.
- **Retention** — cap growing personal data; EventSplit's history/trash caps already act as
  de-facto retention — document them as the policy.
- **Tag PII at the schema level** (Supabase posture): `COMMENT ON COLUMN events.participant_name IS 'PII: name';`
  — makes personal-data columns explicit for audits and future migrations.
- **Security controls** (RLS, open-write, secrets, egress) → `eskills:security-bar`. Note:
  EventSplit's open-write RLS means anyone can read/delete personal data → that's a privacy
  exposure, fix per security-bar.

## Analytics — privacy-first, no consent banner

**No tracking ⇒ no cookie banner. Don't add one you don't need.** To get metrics _and_ keep
that win:

- **Use cookieless, no-PII, EU-hosted analytics** — Plausible / Umami / PostHog-EU
  (cookieless). No cookie/`localStorage` identifier, no cross-site → **no consent required.**
- **Do NOT use** GA4 / Meta Pixel / anything cookie- or fingerprint-based → that _requires_
  consent + a banner (the bloat we avoid).
- Per posture: offline apps can still ship cookieless pageviews; Supabase apps must disclose
  the analytics tool as a **processor**; mintza already ships to AI, so cookieless analytics
  adds negligible marginal exposure.

## Never expose PII in… (guardrail list)

Never put personal data in: **logs, analytics events, crash/error reports, LLM prompts,
URLs/query strings, `localStorage`/`sessionStorage`, or screenshots.** Prefer **opaque IDs**
over names/email. Never ship the `service_role` key client-side (→ `security-bar`).

```ts
// BAD — leaks PII into the error (and the error tracker)
throw new Error(
  `No member ${member.name} <${member.email}> in event ${event.title}`,
);
// GOOD — generic message; details logged server-side with opaque IDs only
logger.error("member lookup failed", { memberId: member.id, eventId });
throw new Error("Member not found");
```

For the AI-processor posture (mintza): send the model the **minimum** content needed, never
attach identifiers you don't have to, and disclose the provider + transfer in the notice.

## Not in scope here

- Security controls (RLS, secrets, authz, egress) → **`security-bar`**.
- Concrete failure recipes (open-RLS exposure, undisclosed transfer) → **`stack-gotchas`**.
- **Non-goal (arch-bar):** no HIPAA-grade _audit-everything_, session-timeout, or
  facility-RLS machinery — disproportionate for no-login B2C PWAs and fights minimization +
  the egress limit. Audit only where proportionate.
- Scope is **EU GDPR**; UK-GDPR is near-identical; CCPA is out of scope.
