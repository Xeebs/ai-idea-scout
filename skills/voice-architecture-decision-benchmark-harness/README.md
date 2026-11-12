# Voice Architecture Triage

A same-day decision tool for the one fork every voice-agent team hits: build a **cascaded pipeline** (separate speech-to-text, LLM, and text-to-speech components, independently swappable) or a **unified speech-to-speech model** (one model that hears and speaks directly, lower theoretical latency but harder to debug and swap). Vendor blogs on this topic actively contradict each other on the headline numbers, so this tool doesn't try to cite a "winning" latency figure — it scores your specific use case against six factors that are well-established tradeoffs, and gives you a direction plus named risks, in minutes instead of the multi-week bake-off teams often end up re-deriving from scratch.

This is a paste-into-any-chat-tool prompt. It does not require Claude Code, any API access, or any installed software.

## When to use this

Use it when you're choosing a voice agent architecture and want a defensible first direction before investing engineering time in standing up both stacks to compare. Do not use it once you already have real latency/cost numbers from your own pilot — at that point you have better data than this triage can give you, so just compare your own numbers.

## What to hand the assistant

Everything below is information you type or paste yourself — this tool does not connect to any API, codebase, or account. Before running it, have answers ready (or be ready to answer follow-up questions) for:

1. **Domain and regulatory context** — e.g., healthcare intake, insurance claims, retail support, recruiting screening. Any compliance or audit requirement (HIPAA, mandatory call recording/retention, dispute resolution needs)?
2. **Languages and vocabulary** — which languages, and whether there's specialized/technical vocabulary, accents, or code-switching to handle.
3. **Latency and conversational feel** — does the product live or die on sub-second, natural back-and-forth with barge-in, or is a more deliberate pace acceptable (e.g., an intake form read aloud)?
4. **Tool-calling needs** — how many external systems the agent calls mid-conversation (lookups, bookings, CRM writes), and how costly a silent failure would be.
5. **Team size and expertise** — how many engineers, and whether they want to own three separate integrations (STT/LLM/TTS) or prefer one managed vendor.
6. **Vendor lock-in tolerance** — how costly it would be to switch architectures later if the chosen vendor changes pricing, quality, or direction.

## The prompt

Paste this into any AI chat tool, filling in your own details for the six items above (or leave them and answer the assistant's follow-up questions):

```
Act as a voice-agent architecture triage tool. I'm deciding between a cascaded
voice pipeline (separate STT, LLM, and TTS, independently swappable) and a
unified speech-to-speech model (one model handles listening and speaking,
lower theoretical latency, harder to debug/swap, more vendor lock-in).

Here is my use case:
1. Domain/regulatory context: <fill in>
2. Languages and vocabulary: <fill in>
3. Latency/conversational feel priority: <fill in>
4. Tool-calling needs: <fill in>
5. Team size and expertise: <fill in>
6. Vendor lock-in tolerance: <fill in>

If any of the above is missing or unclear, ask me directly before scoring —
don't guess.

Score each factor from -2 (strongly favors cascaded) to +2 (strongly favors
speech-to-speech) using this rubric:
- Compliance/observability: regulated/audit-required = -2, some internal QA
  need = -1, no compliance need = 0. (Never push this factor toward S2S.)
- Vocabulary specificity: narrow/technical/multi-language with code-switching
  = -2, moderate domain vocabulary = -1, everyday conversational = +1.
- Latency/naturalness priority: product lives or dies on snappy natural
  back-and-forth = +2, latency matters but isn't the differentiator = 0,
  a deliberate/slower pace is fine = -1.
- Tool-calling needs: many integrations where a silent failure is costly = -2,
  a couple of simple lookups = -1, no tool calls = 0.
- Team expertise/bandwidth: small team wants one managed vendor = +2, team
  has capacity and wants control of each component = -1.
- Lock-in tolerance: switching cost would be severe = -2, team is comfortable
  re-platforming later if needed = +1.

Sum the six scores. Recommend cascaded if the sum is -2 or lower, speech-to-
speech if +2 or higher, and a close call (lean toward whichever has fewer
severe risks for me) if between -1 and +1. State your confidence (High if at
least 4 of 6 factors agree with the sum's direction, Medium if 3 do, Low if
mixed or you had to assume anything).

Do not cite specific vendor latency numbers (e.g. "X is 320ms") — this space's
vendor-reported numbers contradict each other and are unverifiable here. Use
only the directional tradeoffs above, phrased as tendencies, not facts.

Then give me:
- A summary of my use case in 2-3 sentences
- The factor score table with one-line reasoning per factor
- The recommendation and confidence level
- 2-3 named risks of the recommended path (tied to specific factors)
- 2-3 named risks of the alternative path (tied to specific factors)
- What I should actually test before shipping this, to validate the call
  with real numbers instead of just this triage
```

## What you get back

A structured report with:
- A short restatement of your use case
- A six-row factor score table with the running total
- A clear recommendation (cascaded, speech-to-speech, or an honest "close call" with a tie-breaker) and a stated confidence level
- Named risks for both the recommended and alternative paths, each tied to a specific factor rather than generic pros/cons
- A concrete next step for validating the call with your own numbers (a small pilot, not another round of reading vendor blogs)

## Guardrails this tool follows

- It will not invent specific vendor latency figures — those numbers are contested across vendor blogs and not verifiable inside a chat session. It sticks to well-established directional tradeoffs.
- It will not score your case if more than one or two of the six inputs are missing — it asks you for the missing pieces instead of guessing.
- It will not present itself as a replacement for an actual side-by-side benchmark on your own call scripts — only as the fast judgment call to make before you invest in that benchmark.
- It will not force false confidence on a genuine toss-up — if your factors are mixed, it says so and gives you the tie-breaker consideration instead of picking an arbitrary winner.
- It will always call out regulatory/compliance signals (HIPAA, financial, legal discovery) explicitly in the risk section rather than folding them into generic "observability" language, because those carry legal exposure beyond engineering convenience.

## Limits

This triage is a prior, not a measurement. If you have the time and the stakes justify it, follow it up with a real pilot: run the same handful of representative call scenarios through both a cascaded stack and a speech-to-speech stack and compare the actual latency, cost, and failure modes on your own workload before locking in the architecture for production.
