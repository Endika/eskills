# AI provider keys and models — gotchas

## A Google key works for Gemini but not for Cloud Speech, or the other way round

- **Symptom:** one Google key that used to serve both now fails on one API: Speech returns
  403 `API_KEY_SERVICE_BLOCKED` on Gemini, or a Gemini key is rejected by Speech.
- **Means:** AI Studio keys created since 2026-05-28 start with `AQ.` (53 characters). They
  are auth keys bound to a service account and work only for the Gemini API. Cloud
  Speech-to-Text needs a standard `AIza` key, and Gemini rejects unrestricted standard keys.
  One key can no longer cover both.
- **Fix:** ask for two keys, one per API, each with its own test in settings. Never fall
  back from Speech to an `AQ.` key: it can only fail, after uploading the audio. Parse
  Google's error body (`error.details[].reason`) so the interface can say which of
  "key blocked for this API" or "API not enabled" happened.
