# Tells of generated prose

The watchlist behind the "don't sound generated" rule in `comms`. Distilled from
Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
(WikiProject AI Cleanup), keeping what applies to email, issues, comments, release notes
and PR bodies, and dropping what is specific to editing an encyclopedia.

**The goal is not evading a detector.** Automated detection is unreliable and human
readers do barely better than chance, so writing to beat a classifier buys nothing. The
goal is prose that carries information: nearly every tell below is a phrase that fills
space where a fact should be. Cut it because it says nothing, not because it looks robotic.

## Words that signal padding

Dense clusters of these are the strongest single tell:

> additionally · boasts · bolstered · crucial · delve · emphasizing · enduring · foster ·
> garner · highlighting · intricate · interplay · landscape · meticulous · pivotal ·
> showcasing · tapestry · testament · underscore · vibrant · align with · enhance

Not one of them is banned on sight. The test is whether it survives the question "what
does this add that a plain verb wouldn't?"

## Constructions

- **Avoiding the copula.** "serves as", "stands as", "represents", "functions as",
  "operates as", "marks" where the sentence means **is**. Same for "features", "offers",
  "maintains", "boasts" where it means **has**.
- **Negative parallelism.** "not just X, but Y" · "it's not A, it's B" · "no X, no Y, just
  Z". One is a flourish; two in a page is a signature.
- **Trailing `-ing` clauses that analyze nothing**: "…, highlighting its importance",
  "…, underscoring the need", "…, ensuring quality", "…, reflecting broader trends".
- **Rule of three.** Triplets everywhere, including where the third item was invented to
  complete the rhythm.
- **Vague attribution**: "industry reports suggest", "experts argue", "observers have
  noted", "some critics argue" — attribution to nobody, quantity implied without a source.
- **Undue significance**: "a testament to", "plays a crucial role", "marks a pivotal
  moment", "leaves an indelible mark", "reflects a broader shift".
- **Promotional adjectives**: vibrant, rich, profound, groundbreaking, nestled, seamless,
  robust, "a diverse array of".
- **The challenge-and-future formula**: "Despite its X, it faces several challenges…",
  closing on an upbeat outlook nobody asked for.

## Meta and canned text

- **Talking to the reader about the act of writing**: "I hope this helps", "Let me know if
  you need anything else", "Feel free to reach out", a summary of what the message just
  said.
- **Knowledge-cutoff hedging**: "as of my last update", speculation about what sources may
  or may not exist.
- **Canned assurances instead of content** — the tell Wikipedia catches in edit summaries,
  and it maps exactly onto commit messages and PR bodies: "ensured all tests pass",
  "followed the existing conventions", "preserved the original behaviour", "avoided
  breaking changes". Say what changed, not that you were careful.
- **Placeholder text left standing**, or a bracketed note where the actual content goes.

## Formatting

- Bold used on whole sentences rather than on the two or three words that carry the point.
- Title Case In Headings; a heading that just repeats the subject line.
- Emoji as decoration or as bullet markers.
- Horizontal rules between every section.
- A table for something that is not tabular.
- Headings that contain only more headings, or skipped heading levels.
- An abrupt register shift mid-message — the half that was drafted and the half that was
  generated rarely sound alike.

## Where this list does not apply to me

- **Em dashes.** Wikipedia flags overuse; my own voice uses them deliberately and
  constantly, across every skill in this pack. The rule here is density, not abstinence —
  and a message where every sentence hinges on one has stopped being a style choice.
- **Curly quotes**, wikitext breakage, DOIs, categories and citation templates: artifacts
  of editing an encyclopedia, not of writing an email.
- **Rule of three** in a deliberately parallel list is fine. The tell is the invented
  third item.

## The actual test

Read it back and ask what a reader would learn that they didn't know. If a paragraph
survives being deleted, it was padding — and padding is what the entire list above is
made of.
