# GDPR — gotchas

## GDPR: open-RLS exposes personal data

- **Symptom:** any anon key holder can read/update/delete rows that contain names, email, or
  financial data (e.g. EventSplit's events blob).
- **Means:** open-write RLS (`SELECT/INSERT/UPDATE true`) isn't just a security bug — it's a
  **personal-data exposure / breach risk** under GDPR (unauthorized access to identifiable
  people, including third parties who never consented).
- **Fix:** restrict direct writes / enforce ownership in an RPC (the security fix →
  `eskills:security-bar`); then in the privacy notice, only claim protections you actually
  have. Don't document "your data is protected" while RLS is open. See `eskills:gdpr`.

## GDPR: undisclosed international transfer to an AI provider

- **Symptom:** the app sends user audio/text to OpenAI/Anthropic/Google/Azure, but the
  privacy notice (if any) doesn't mention it (mintza).
- **Means:** that's a **processor + international transfer (US)** with no disclosure and no
  transfer mechanism named — a GDPR gap, and possibly special-category data (voice).
- **Fix:** disclose every AI provider as a processor + name the transfer basis (SCCs/DPF) in
  the notice; confirm no-training-on-API-data + retention; send the model the **minimum**
  content, no needless identifiers. See `eskills:gdpr` (AI-processor posture).
