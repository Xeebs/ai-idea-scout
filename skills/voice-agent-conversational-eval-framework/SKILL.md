---
name: voice-agent-conversational-eval-framework
description: Audits a team's existing voice-agent evaluation setup for conversation-level blind spots (unvalidated judges, component-only testing, missing multi-turn failure modes) and drafts a call-type-specific failure-mode taxonomy. Use when someone describes how they currently test/eval a voice agent and wants to know what they're missing before building or buying a fuller eval framework.
---

# Voice Agent Conversational Eval Gap Auditor

## When to use this
Reach for this skill the moment someone describes how they currently evaluate a voice agent (phone bot, IVR replacement, voice assistant) and asks something like "what are we missing?", "is our testing good enough before we scale this up?", or "help us build a failure taxonomy for our call types." It is a pre-commitment review step — for a team deciding whether to adopt or build a full conversational eval framework, not a tool that runs evals itself. Do not use this for evaluating a single call transcript in isolation (that's a different task) or for teams that have no voice agent in production or pre-launch yet.

## Inputs
**Data source**: Manual — the user describes/pastes their current eval setup and call types directly in the conversation; this skill does not connect to any call-logging platform, eval tool, or telephony API. (The parent idea file for this skill did not specify a Data Sources classification; this skill scope defaults to Manual because the audit is a one-shot review of whatever the user chooses to describe, with no connector assumed mature or in scope.)

Required from the user:
1. **What they currently measure** — e.g., ASR word-error rate, LLM response correctness/relevance scoring, TTS naturalness, any existing end-to-end or multi-turn checks.
2. **How they measure it** — automated scripts vs. human review vs. LLM-as-judge (and if LLM-judge: which model, whether it was ever checked against human ratings, sample size, how often it runs).
3. **Their call types / use cases** — e.g., appointment booking, billing support, outbound sales, triage/dispatch, tech support troubleshooting.

Optional but strongly improves output quality:
4. 2-5 example call transcripts or detailed summaries (real or representative).
5. Known pain points, past incidents, or complaints tied to specific calls.

If (1)-(3) are not provided, ask for them before producing output — do not guess at a team's setup.

## Procedure
1. **Classify current coverage by layer.** Sort what the user described into four buckets: ASR/transcription accuracy, LLM/dialogue quality, TTS/voice naturalness, and conversation-level/end-to-end (multi-turn). Note explicitly if a bucket has nothing in it.
2. **Run the gap checklist** against each bucket and against the conversation layer specifically:
   - Is there *any* multi-turn/full-call check, or only per-component scoring? (Per-component-only is the single most common gap — flag it first if found.)
   - If an LLM-judge is used anywhere: has it ever been checked against human ratings on a held-out set? An LLM-judge with no human-calibration check is a gap regardless of how sophisticated it sounds.
   - Context retention across turns — is loss of earlier-turn context ever tested?
   - Interruption/barge-in handling — tested or untested?
   - Goal resolution — does any check verify the *stated caller goal* was actually resolved, not just that the agent responded sensibly turn-by-turn?
   - Tool-call / handoff failures — are failures in tool invocation or human-handoff moments covered?
   - Digit/slot capture (for call types involving account numbers, dates, confirmations) — tested or untested?
3. **Score each checklist item** `Covered` / `Partial` / `Missing`, each with a one-line rationale that cites what the user actually said (never invent detail they didn't give you).
4. **Draft the failure-mode taxonomy**, tailored to the call types the user named. For each call type, list the 4-8 failure modes most likely to matter (drawing on the checklist categories above, applied concretely to that call type — e.g., for "appointment booking": wrong-date confirmation, ambiguous time-zone handling, failure to detect a rescheduling intent mid-call). Give each a one-line definition and an example trigger pattern (what in a transcript would indicate this failure).
5. **If transcripts were provided**, map 2-3 concrete moments from them onto taxonomy entries as worked examples — this is the single most convincing part of the output, don't skip it when material exists.
6. **Rank the gaps** from the checklist by estimated blast radius (a `Missing` on conversation-level/goal-resolution outranks a `Missing` on TTS naturalness) and write 3-5 concrete, prioritized next steps — ordered cheapest/fastest first where feasible.

## Output format
A single Markdown report with these sections, in this order:

1. **Coverage Scorecard** — table: `Layer | Status (Covered/Partial/Missing) | Why`
2. **Top Gaps** — numbered, ranked list, each with a one-sentence "what this is costing you" statement
3. **Call-Type Failure-Mode Taxonomy** — one table per call type: `Failure Mode | Definition | Example Trigger Pattern`
4. **Worked Examples** — only if transcripts were supplied; otherwise state "No transcripts supplied — provide 2-5 real or representative calls to generate worked examples."
5. **Recommended Next Steps** — 3-5 bullets, ordered by priority, each naming a concrete action (not "improve your eval process")

## Guardrails
- Never score a layer `Covered` on the strength of a bare claim like "we have an LLM judge" — it is `Partial` at best until the user confirms it was checked against human ratings, and the report must say so explicitly.
- Never invent call volume, CSAT, incident counts, or any other statistic the user didn't provide. If a metric would strengthen the report, ask for it or state it's unknown.
- Never name or recommend a specific paid vendor/platform as "the" fix — describe the capability gap in vendor-neutral terms; the user decides whether to build or buy.
- Never produce a taxonomy that is generic boilerplate detached from the stated call types — every failure mode must be phrased in terms of that specific call type's actual interaction pattern.
- Never skip asking for inputs (1)-(3) and proceed on assumptions — a gap report built on guessed setup details is worse than no report.
- This skill produces a review/drafting artifact only. It does not run evaluations, score real calls, or replace a human-calibrated judge — say so plainly if the user seems to expect the report itself to be a working eval harness.
