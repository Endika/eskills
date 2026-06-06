# Privacy notice — fill-in template + DSR + processor disclosure

A short, honest privacy notice for a B2C PWA. Keep it plain-language; over-long policies are
a dark pattern. Pick the posture, fill the blanks, delete what doesn't apply.

## Template

```markdown
# Privacy — <App>

_Last updated: YYYY-MM-DD_

## Who we are

<App> is run by <controller name / contact email>. Questions or requests: <email>.

## What we collect and why

<!-- OFFLINE posture: -->

This app runs **entirely on your device**. We do not collect, store, or transmit your data.
Anything you enter stays in your browser and never reaches a server we control.

<!-- SERVER-BACKED posture: -->

To let you <core function>, we store:

- <data, e.g. event name, participant labels, expense amounts> — to <purpose>.
- <account email, if any> — to <purpose>.

Lawful basis: <contract / legitimate interest>. Participants added by an organiser are
processed under legitimate interest; we store only a display label, nothing more.

<!-- AI-PROCESSOR posture (add to the above): -->

To turn <input> into <output>, your <audio/text> is sent to AI providers for processing.
We send only what is needed and do not attach identifiers we don't have to.

## Who we share it with (processors)

| Processor              | Purpose              | Location / transfer          |
| ---------------------- | -------------------- | ---------------------------- |
| Supabase               | database / hosting   | <EU region> — set this       |
| <Plausible/Umami/…>    | cookieless analytics | <EU>                         |
| OpenAI / Anthropic / … | transcription / LLM  | US — transfer via <SCCs/DPF> |

We do **not** use tracking cookies or advertising; our analytics is cookieless and stores
no personal data, so there is no cookie-consent banner.

## How long we keep it

<retention, e.g. "events are kept up to N days / N versions of history, then pruned">.

## Your rights

You can access, correct, or delete your data. <How: e.g. "delete the event from the app",
or "email us at <email>">. We respond within one month.
```

## DSR (data-subject request) handling checklist

When someone asks to access/delete their data:

- [ ] **Identify the data** — which records relate to this person (use the schema PII tags).
- [ ] **Erasure path is real** — for no-login apps, "delete the event/record in the app" must
      actually remove it server-side, not just hide it. Verify it does.
- [ ] **Processors too** — if data was sent to a processor (analytics is cookieless/no-PII so
      usually nothing; AI providers: check their retention — most don't train on API data and
      purge within N days, state it).
- [ ] **Respond within one month** (GDPR Art. 12).
- [ ] **No new PII created** while handling the request (don't log their email in a ticket).

## Processor disclosure — keep this list current

Every third party that touches personal data must be: (1) under a DPA, (2) listed in the
notice, (3) covered for transfer if outside the EU. Re-check when you add an SDK or API.

- **Supabase** — DPA available; pick an **EU region** at project creation (can't change later).
- **Cookieless analytics** (Plausible/Umami/PostHog-EU) — DPA; EU hosting; no PII, no cookies.
- **AI APIs** (OpenAI/Anthropic/Google/Azure) — DPA + US transfer mechanism; confirm
  no-training-on-API-data + retention window; this is the heaviest disclosure (mintza).
