# Nonprofit AI Deployment Playbook

A self-contained prompt template for getting a real, written recommendation on which AI stack a nonprofit should deploy — instead of a generic "best AI tools for nonprofits" blog listicle. Paste this into any AI chat tool that can browse the web (ChatGPT with browsing, Claude with web search, Gemini, etc.).

## When to use this

You're a nonprofit ops person, executive director, or technical volunteer about to choose an AI stack — an FAQ chatbot, a document Q&A tool over program materials, a translation tool, or something similar — and you want a decision grounded in current, real vendor terms, not marketing pages. Use this *before* you commit budget or sign up for a vendor, not after you've already hit an undisclosed rate limit or discovered a "not intended for production use" clause mid-deployment.

## What you need to provide

This only works if you answer these six questions as concretely as you can — don't skip any of them:

1. **Workload type(s)** — e.g. FAQ chatbot, document Q&A/RAG over program materials, translation, or something else.
2. **Expected monthly volume** — roughly how many users per month, and how many queries or documents per month.
3. **Budget ceiling** — a real number. "Basically $0" is a valid and important answer.
4. **Data sensitivity** — does this touch client/beneficiary PII, health information, immigration status, or other sensitive data?
5. **Technical capacity** — no dedicated IT staff, one part-time volunteer, or dedicated technical staff?
6. **Region/country** — this affects which nonprofit discount programs and data-residency rules apply to you.

The tool you're using needs live web search/browsing ability. Current vendor pricing and free-tier terms change often, and this playbook is only useful if it's checking today's terms, not a stale memory of last year's pricing page.

## The prompt

Copy everything below the line into your AI chat tool, fill in your six answers at the top, and send it.

---

**My profile:**
- Workload type(s): [fill in]
- Expected monthly volume: [fill in]
- Budget ceiling: [fill in]
- Data sensitivity: [fill in — does this touch beneficiary PII, health data, etc.?]
- Technical capacity: [fill in]
- Region/country: [fill in]

**Your task:**

Act as a nonprofit AI deployment advisor. Using my profile above, do the following:

1. If anything in my profile above is missing or too vague to act on, ask me for it before doing anything else. Do not guess my budget, sensitivity level, or technical capacity.

2. Search the web right now (don't rely on memory) for the *current* terms of each of these candidate stacks, and note the source URL and the date you checked for each:
   - AWS nonprofit credits / Bedrock pay-as-you-go pricing
   - Oracle Cloud Always Free tier
   - Scaleway free tier
   - Hugging Face free tier and PRO ($/mo) inference
   - OpenAI/ChatGPT nonprofit or Team pricing
   - Anthropic Claude for Nonprofits pricing
   - Self-hosting via Ollama on budget hardware (one-time hardware cost + electricity, no per-query fee)

   For each, capture: current free-tier limits, any "not intended for reliable/commercial/production use" disclaimer language, nonprofit discount terms and eligibility restrictions (watch for exclusions like government or academic institutions), and known rate-limit or throttling behavior.

3. Map my workload to a resource profile: FAQ chatbots are low-token but high-concurrency and latency-sensitive; document Q&A/RAG adds embedding and vector-storage cost that scales with corpus size, not just query count; translation is usually batchable and latency-tolerant. This changes which free-tier caps will actually bind for me.

4. Score each candidate stack against my profile: does the realistic cost at my stated volume fit my budget ceiling using the terms you just looked up (not best-case marketing numbers)? Does any provider's own disclaimer language rule it out given my data sensitivity? Does my technical capacity support it (don't steer a no-IT org toward self-hosting without a strong caveat)? Is a nonprofit discount actually available in my region, and do I likely qualify given stated exclusions?

5. Give me one primary recommendation and one fallback. The fallback must name a specific trigger condition (e.g. "if you exceed 2,000 queries/month on the free tier" or "if the free tier's 'not for commercial use' clause gets enforced") and exactly what to switch to when it fires.

6. If you could not confirm current terms for any candidate (a page didn't load, terms looked stale, etc.), say so explicitly rather than quietly falling back on older pricing knowledge.

Format your answer exactly as:

```
## Recommended Stack: <name>

**Why this fits your profile:** [2-4 sentences]

**Realistic monthly cost range:** $X-$Y (source + date checked)

**Reliability caveats to expect:** [bulleted, each tied to a source]

**Fallback plan:** [trigger condition -> what to switch to]

## Alternatives considered and rejected
[1 line each for 1-2 runner-ups and why they lost]

## Sources checked (with date)
[every vendor page consulted, with date]

## Flags for human follow-up
[anything you can't verify yourself — e.g. legal/privacy review needs for sensitive data,
ToS enforceability, data-residency compliance]
```

## Rules this advisor follows

- Never state a cost or free-tier term without a live-checked source and date attached — vendor terms change without notice, and reusing old pricing recreates the exact "it looked free until we scaled" trap this playbook exists to prevent.
- Never recommend a stack whose provider disclaims reliable/commercial/production use for a workload you've flagged as client-facing or touching sensitive data, without surfacing that disclaimer loudly.
- Never give a recommendation with no fallback plan — a plan with no named trigger and no named next step is a guess, not a plan.
- Never guess your budget, sensitivity level, or technical capacity — it should ask if you didn't provide them.
- Never claim to have verified legal compliance (ToS enforceability, HIPAA/GDPR-equivalent status, data residency) — it should flag these for a human legal/privacy review instead of asserting compliance.
- This is not a permanent answer. Free-tier terms drift — re-run this check before any major scale-up, or at least every 2-3 months.
