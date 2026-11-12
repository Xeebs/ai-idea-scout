# Consumer-GPU World-Model Verifier

A self-contained prompt template. Paste the block below into any AI chat tool that can browse the web (ChatGPT with browsing, Claude with web search, Perplexity, Gemini, etc.) before you spend setup time trying a new "runs on consumer GPUs" interactive world-model or generative-video-game release.

## What this is for

New interactive "world model" releases (turn an image into a playable, real-time video game) ship constantly right now, and almost every one claims it runs on consumer hardware. The teams making these claims benchmark on their own best-case setup and have no incentive to publish unflattering numbers for cheaper cards. This prompt makes the AI actually go look for independent confirmation — not just repeat the vendor's own README back at you — before you spend an hour installing something that turns out to need a GPU three tiers above yours.

## What you need to provide

1. **The exact model/release name**, with a link if you have one (GitHub repo, Hugging Face page, arXiv page, or the specific post — Reddit, X, blog — where you saw the claim).
2. **Your exact GPU** — card name and VRAM if you know it (e.g. "RTX 3060 12GB"). Just the tier name is enough to start, but VRAM changes the verdict.
3. *(Optional)* The literal claim text you saw, if it came from a social post rather than the project's own page — paste it verbatim so the AI can check it against the source.

Nothing else is required. The AI does the web/GitHub research itself — you are not expected to have already found any benchmarks yourself.

## The prompt

```
You are verifying whether a specific local/interactive "world model" (image-to-playable-video) release
actually performs as claimed on my GPU, before I spend time installing it. Do not just repeat the
project's own marketing back to me — your job is to find independent confirmation or contradiction.

Model/release: [NAME + LINK IF YOU HAVE ONE]
My GPU: [e.g. RTX 3060 12GB]
Claim I saw (if any, paste verbatim): [OPTIONAL]

Do this:
1. Find the project's OWN stated hardware requirements and self-reported FPS/latency numbers — note
   exactly which GPU those numbers were measured on. Label this clearly as "vendor claim," not evidence.
2. Search specifically for INDEPENDENT evidence about my GPU tier (or the nearest comparable one):
   GitHub issues/discussions, Reddit/HN comments, blog or video write-ups, third-party reproduction
   repos. For each one found, give me: source, who said it, what GPU, what number, and the date.
3. Classify the result as one of:
   - Verified — an independent source confirms it hits a usable real-time bar (default: ≥15 FPS
     sustained with stable input latency, unless the project states its own bar — then use that bar)
     on my exact tier or a directly comparable one.
   - Unverified-but-plausible — only the vendor's own numbers exist for my tier; nothing contradicts
     them, but nobody outside the vendor has confirmed it.
   - Contradicted — independent reports show it does NOT hit a usable level on my tier, or the
     vendor's own materials actually only cover a higher tier than the claim implies.
   - No data — nothing findable on my tier either way.
4. Note the date of every piece of evidence you use, and flag it as possibly stale if the newest
   relevant evidence is more than ~60 days old — this category changes fast.
5. If my exact card isn't covered by anything you find, say so plainly. If you're extrapolating from
   a different card in the same family, label it clearly as an extrapolation.

Give me back exactly this format:

## [Model/release name] on [my GPU]

**Vendor claim**: <paraphrase + source + date>
**Independent evidence found**:
- <source, date, GPU tier, what it showed> (or "none found")

**Verdict**: Verified | Unverified-but-plausible | Contradicted | No data
**Bottom line**: <one sentence — try it / maybe with X caveat / skip it / can't tell yet>
**Freshness note**: newest evidence used is from <date> (fresh / possibly stale)

Rules you must follow:
- Never call the vendor's own benchmark numbers "independent evidence" — they go only in "vendor claim."
- Never invent a number, source, username, or date — if nothing turns up, say "No data."
- Always include the date of every source and apply the staleness flag.
- If you can't browse the web in this session, tell me that directly and ask me to paste any claim
  text or comment threads I've already found, instead of guessing from general knowledge.
```

## What you get back

A short structured report: the vendor's own claim (clearly labeled as unverified-by-itself), every independent data point the AI could actually find about your specific GPU tier with its source and date, a four-way verdict (Verified / Unverified-but-plausible / Contradicted / No data), one plain-language bottom line, and a freshness flag. If your exact card isn't covered by anything on the public record, the report says so instead of guessing.

## Good to know before you use it

- This checks *claims*, not safety — it doesn't review the installer code for you. Still sandbox/review any install script yourself.
- A "No data" or "Unverified-but-plausible" verdict is common for brand-new releases — that's a correct, honest answer, not a failure of the check.
- Re-run this before trying a release again a few weeks later if you skipped it the first time on "Unverified" — new independent reports show up fast in this category.
