# Voice Agent Conversational Eval Gap Auditor

A self-contained prompt template for auditing how a team currently tests/evaluates a voice agent (phone bot, IVR replacement, voice assistant), surfacing conversation-level blind spots, and drafting a failure-mode taxonomy tailored to their actual call types. Paste the block below into any AI chat tool (Claude, ChatGPT, etc.) along with your answers to the input questions.

## When to use this

Use this when you already have (or are close to launching) a voice agent and want to know what your current testing/eval setup is missing *before* you build or buy a fuller evaluation framework. This is a one-time review and drafting exercise — it produces a report, not a running eval pipeline. It is not for scoring one specific call transcript in isolation, and it's not useful if you have no voice agent and no eval setup to describe yet.

## Data source

**Manual.** You type or paste your eval setup description, your call types, and (optionally) example transcripts directly into the chat. Nothing here connects to a telephony platform, call-logging system, or eval tool automatically — if you want that, you'd need to export what you need from those systems yourself first.

## What to hand over before running this

1. **What you currently measure** — e.g., ASR word-error rate, LLM response quality/relevance scoring, TTS naturalness scores, any existing end-to-end or multi-turn checks. If the honest answer is "nothing systematic," say that.
2. **How you measure it** — automated scripts, human review, or an LLM-as-judge setup. If it's an LLM judge: which model, and has anyone ever checked its scores against human ratings on a sample of real calls?
3. **Your call types** — the distinct kinds of calls your agent handles (e.g., appointment booking, billing support, outbound sales, dispatch/triage, tech support troubleshooting). List each one.
4. *(Optional, improves the output a lot)* 2-5 example call transcripts or detailed summaries — real or representative of what actually happens on your calls.
5. *(Optional)* Any known pain points, complaints, or past incidents tied to specific calls.

If you can't yet answer 1-3, don't run this yet — the report would just be guesswork.

## The prompt

```
You are auditing my voice agent's evaluation setup for conversation-level blind spots and drafting a failure-mode taxonomy. Here is my setup:

1. What we currently measure: <describe — ASR accuracy? LLM response quality? TTS naturalness? Any end-to-end/multi-turn checks? Or "nothing systematic" if true>
2. How we measure it: <automated scripts / human review / LLM-judge — if LLM-judge, name the model and whether it's ever been checked against human ratings, on what sample size, how often it runs>
3. Our call types: <list each distinct kind of call the agent handles>
4. (Optional) Example transcripts or summaries: <paste 2-5 if you have them>
5. (Optional) Known pain points or past incidents: <describe if any>

Please do the following, in order:

1. Classify what I described into four buckets: ASR/transcription accuracy, LLM/dialogue quality, TTS/voice naturalness, and conversation-level/end-to-end (multi-turn). Note explicitly if any bucket is empty.

2. Run this gap checklist against my setup, scoring each item Covered / Partial / Missing with a one-line reason tied to exactly what I told you (don't invent detail I didn't give):
   - Any multi-turn/full-call check, or only per-component scoring?
   - If an LLM-judge is used: has it ever been checked against human ratings on a held-out set? (No check = Partial at best, regardless of how sophisticated the setup sounds.)
   - Context retention across turns tested?
   - Interruption/barge-in handling tested?
   - Goal resolution tested (did the check verify the caller's actual stated goal was resolved, not just that responses were locally sensible)?
   - Tool-call / human-handoff failure modes covered?
   - Digit/slot capture tested (if relevant to my call types)?

3. For each of my call types, draft 4-8 failure modes specific to that call type's actual interaction pattern (not generic boilerplate) — each with a one-line definition and an example trigger pattern you'd see in a transcript.

4. If I gave you transcripts, map 2-3 concrete moments from them onto the taxonomy as worked examples.

5. Rank the gaps you found by estimated impact (a missing conversation-level/goal-resolution check outranks a missing TTS-naturalness check) and give me 3-5 concrete, prioritized next steps, cheapest/fastest first where possible.

Output as a single Markdown report with these sections in order: Coverage Scorecard (table), Top Gaps (ranked list with a "what this is costing you" line each), Call-Type Failure-Mode Taxonomy (one table per call type), Worked Examples (or a note that none were supplied), Recommended Next Steps.

Rules: never score anything Covered on a bare claim without evidence of validation; never invent statistics I didn't give you; never recommend a specific paid vendor as "the" fix — describe the capability gap in vendor-neutral terms; never give me a generic taxonomy — tie every failure mode to my actual call types.
```

## What you get back

A single Markdown report:
- **Coverage Scorecard** — a table scoring each testing layer Covered/Partial/Missing with a reason
- **Top Gaps** — ranked, each with a one-line "what this is costing you" statement
- **Call-Type Failure-Mode Taxonomy** — one table per call type you named, with failure modes, definitions, and example trigger patterns
- **Worked Examples** — real moments from your transcripts mapped onto the taxonomy, if you supplied any
- **Recommended Next Steps** — 3-5 prioritized, concrete actions

## Limits

This is a review and drafting aid, not a working evaluation harness — it will not score real calls for you or replace a human-calibrated judge. It only knows what you tell it; vague or incomplete input produces a vague or incomplete report. It's most useful as the step right before deciding whether to build, adopt, or buy a fuller voice-agent eval system.
