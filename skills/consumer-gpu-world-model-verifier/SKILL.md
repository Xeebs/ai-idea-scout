---
name: consumer-gpu-world-model-verifier
description: Checks a specific local/interactive world-model release's claimed GPU-tier performance (e.g. "runs on RTX 3060") against independently found evidence before the user spends setup time trying it on their own card. Use when a user names a specific world-model/generative-video repo and their own GPU and asks "will this actually run on my card" or "is this claim real."
---

# Consumer-GPU World-Model Verifier

## When to use this
A user names a specific local/interactive world-model or generative-video-game release (e.g. a Reddit/HN/GitHub post, a Hugging Face model, an arXiv project page) and either states their own GPU or asks which GPU tier it genuinely needs — and wants to know whether the stated "works on consumer card X" claim is independently confirmed before they spend time installing it. This is a point-in-time due-diligence check, not a persistent benchmark database — run it fresh each time, since this category ships new releases and revised claims every few weeks.

## Inputs
**Data source**: CONNECTED — the skill reads the public web, GitHub, and Hugging Face (via search) to find the project's own stated hardware requirements and any independently published benchmark numbers or user reports about it. Web/GitHub search is a generic, already-mature capability built into most AI chat tools today (Claude's web search, ChatGPT browsing, Perplexity) — this skill does not require a bespoke API integration to be built. *Note: the parent idea file (`ideas/consumer-gpu-world-model-verifier.md`) does not carry a Data Sources field — it was missing from that idea, so this classification was derived directly from the Skill Angle section rather than copied.* The user must still manually supply two things no search can infer:
- The exact model/release name, with a link if they have one (repo, HF page, blog post, or the specific social-media post that made the claim).
- Their exact GPU (card name + VRAM, e.g. "RTX 3060 12GB" — tier alone, like "a 3060," is enough to start but VRAM matters for the verdict).
- Optional: the literal claim text they saw, if it came from a social post rather than the project's own README/page.

## Procedure
1. **Confirm the two required inputs** (model/release name + user's GPU). If either is missing, ask for it before proceeding rather than guessing.
2. **Find the vendor's own claim.** Search the project's README, model card, release notes, or landing page for its stated hardware requirements and any self-reported FPS/latency/resolution numbers, and note exactly which GPU(s) those numbers were measured on.
3. **Search for independent evidence** specifically about the user's GPU tier (or the nearest comparable tier): GitHub issues/discussions, Reddit/HN comments, YouTube or blog write-ups, third-party reproduction repos. Record, for each piece found: source, who said it, what GPU, what number, and the date.
4. **Classify the result**:
   - **Verified** — an independent source (not the vendor) confirms it hits a usable real-time bar on the user's exact tier or a directly comparable one. State the bar used (default: ≥15 FPS sustained with stable input latency, unless the project itself defines a different bar — then use the project's own bar and say so).
   - **Unverified-but-plausible** — only the vendor's own numbers exist for that tier, and nothing contradicts them, but nobody outside the vendor has confirmed it.
   - **Contradicted** — independent reports show it does *not* hit a usable level on that tier, or the vendor's own materials only actually cover a higher tier than the claim being checked implies.
   - **No data** — nothing findable on that tier either way.
5. **Check freshness.** Note the publish/commit date of every piece of evidence used. Flag anything the newest relevant evidence is older than ~60 days as possibly stale — this category's claims and releases change fast.
6. **If the user's exact card isn't covered**, say so explicitly. If extrapolating from a different card (e.g. applying 4060 evidence to a 4060 Ti), label it clearly as an extrapolation, not a confirmed result for that exact card.
7. **Write the compatibility report** (format below) and give one plain-language bottom line.

## Output format
```
## [Model/release name] on [user's GPU]

**Vendor claim**: <paraphrase + source link/name + date>
**Independent evidence found**:
- <source, date, GPU tier, what it showed> (repeat per finding, or "none found")

**Verdict**: Verified | Unverified-but-plausible | Contradicted | No data
**Bottom line**: <one sentence — try it / maybe, with X caveat / skip it / can't tell yet>
**Freshness note**: newest evidence used is from <date> ([fresh] / [possibly stale — category moves fast])
```

## Guardrails
- Never mark a claim "Verified" based solely on the vendor's own README/benchmark page — that is exactly the gap this skill exists to close. The vendor's own numbers always go in "Vendor claim," never in "Independent evidence."
- Never invent FPS numbers, usernames, repos, or dates that weren't actually found during search — if nothing turns up, say "No data," don't estimate one.
- Always state the date of every piece of evidence and flag staleness per step 5 — do not present a 3-month-old number as current without that flag.
- If the user's exact GPU isn't covered by anything found, say so plainly rather than silently extrapolating from a different tier.
- This is a research/compatibility check, not a safety audit of the installer — note once that the user should still review/sandbox any install script themselves; don't imply the skill vetted the code for safety.
- If search tools aren't available in the chat tool being used, say so and ask the user to paste the raw claim text plus any comment threads/benchmarks they've already found, rather than fabricating a verdict from general knowledge of the category.
