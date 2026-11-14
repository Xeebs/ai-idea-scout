---
name: local-omni-model-cascade-replacement
description: Assesses whether a team should migrate a cascaded STT+LLM+TTS voice-agent stack to a self-hosted local audio-native omni-model, producing a go/no-go verdict, cost/latency projection, and a tool-calling compatibility audit. Use when someone is weighing dropping per-minute voice vendors for a local model and wants a reasoned recommendation before committing engineering time.
---

# Local Omni-Model Cascade Migration Assessor

## When to use this
A team currently running a cascaded voice-agent pipeline (separate STT vendor, LLM, and TTS vendor — e.g. Deepgram + GPT-4o + Cartesia, or Twilio transcription + an LLM + ElevenLabs) is asking "should we switch to one of these local audio-native omni-models (LFM3-Audio-2B or similar) that do STT, reasoning, and TTS in one process with native tool-calling?" Use this skill when they want a reasoned go/no-go *before* spending engineering time on a migration spike — not after they've already built it.

## Inputs
**Data source**: Manual — the user pastes their current voice-agent architecture (vendor STT/LLM/TTS endpoints and model names, current per-call or per-minute cost, p50/p95 latency numbers if measured, monthly call-minute volume) and the list of tool/function definitions the agent calls (name, what it does, and whether it relies on parallel tool calls or streaming partial arguments). No external connector is used — this is a one-time architecture description the user types or pastes from their own dashboards/code, not live account data.

Minimum viable input to produce a verdict:
1. Current vendor stack + combined per-minute cost (or enough to estimate it: vendor names + published rates).
2. Monthly call-minute volume (or concurrent-call peak, if volume isn't tracked).
3. A list of the tools/functions the agent calls, each flagged if it uses parallel tool calls or streaming partial arguments.

If any of these three is missing, ask for it before producing a verdict — do not guess tool behavior or volume.

## Procedure
1. **Parse the architecture.** Extract: STT vendor+cost, LLM vendor+cost, TTS vendor+cost (or combined per-minute rate), current p50/p95 latency if given, and monthly call-minute volume.
2. **Audit each tool/function definition** against known local audio-native omni-model limitations. Default assumption (state this explicitly in output) unless the user confirms otherwise for their specific model/version: **no parallel tool calls, no streaming partial arguments, single-turn tool_call emission only**. Classify each tool:
   - **Likely compatible**: single tool call per turn, no streaming args needed, simple schema.
   - **Needs redesign**: relies on parallel calls or partial-arg streaming that must be refactored into sequential/complete-arg calls.
   - **Blocking**: the tool's correctness depends on a capability (e.g. mid-utterance partial args driving a live UI) that cannot be reproduced without the model vendor confirming support.
3. **Estimate capacity and hosting tier.** Use a reference baseline (state it's a default, ask the user to correct if they have real numbers): one 24GB consumer GPU (e.g. RTX 4090) serves roughly 8-15 concurrent real-time audio-omni sessions depending on model size and context length. Convert the user's peak concurrent calls (derive from monthly minutes ÷ (30 days × avg call-minutes-per-day-per-line) if not given directly, or ask) into a GPU count: `GPUs needed = ceil(peak_concurrent_calls / 10)` (midpoint of the range), flagged as an estimate to validate with a load test.
4. **Estimate cost delta.** Current cost = combined per-minute vendor rate × monthly minutes. Projected cost = amortized GPU hardware cost (reference: ~$1,800 for a 24GB card, 3-year amortization ≈ $50/month per card) + estimated electricity (reference: ~$30-60/month per card at typical datacenter/office power rates) + any existing inference infra the user already pays for (ask if unclear — don't double-count). Always label vendor rate card numbers and GPU/electricity figures not supplied by the user as **reference defaults, not verified prices**.
5. **Estimate latency delta.** If the user gave stage-by-stage p50/p95, sum cascade network+serialization hops (rule of thumb: +150-400ms per vendor network round-trip) vs. a single local inference hop. If they only gave end-to-end numbers, state the comparison is directional only, not a hard number, pending the benchmark in step 7.
6. **Form the verdict**: GO / CONDITIONAL-GO / NO-GO.
   - **NO-GO** if any tool is classified Blocking and no workaround is identified.
   - **CONDITIONAL-GO** if cost/latency projection favors migration but one or more tools need redesign, or capacity math requires more GPUs than the stated hosting budget allows.
   - **GO** only if all tools are Likely compatible or Needs-redesign-with-clear-path, and the hosting tier fits the stated budget.
7. **Always close with required validation steps** — this skill produces a projection, never a final decision. Name the specific benchmark the idea's project component would run (tool-call accuracy under barge-in, MOS, latency, cost) and recommend running it on the actual call-scenario mix before committing budget.

## Output format
A single markdown report with these sections, in order:
1. **Verdict** — one line: `GO` / `CONDITIONAL-GO` / `NO-GO` + one-sentence reason.
2. **Cost comparison** — table: Current (vendor, rate, monthly cost) vs. Projected (hardware, electricity, monthly cost, GPU count) vs. Delta ($/month, % change).
3. **Latency estimate** — current (stage breakdown if available) vs. projected single-hop estimate, labeled directional or measured based on input quality.
4. **Tool-calling compatibility audit** — table: Tool name | Feature(s) used | Classification (Compatible/Needs redesign/Blocking) | Reasoning.
5. **Hosting tier recommendation** — GPU count, concurrency assumption used, and the one line flagging it's a reference default pending load test.
6. **Required validation before migrating** — bulleted list of the specific benchmarks to run and what result would overturn the verdict.
7. **Confidence & caveats** — what inputs were missing or assumed, and how that affects confidence in the verdict.

## Guardrails
- Never state a cost or latency delta as a guaranteed outcome — every number is a projection pending the benchmark named in step 7.
- Never classify a tool as "Compatible" by default — the default assumption is NO parallel tool calls and NO streaming partial args unless the user explicitly confirms their specific model version supports it.
- Never fabricate vendor pricing, GPU prices, or electricity rates not supplied by the user without clearly labeling them as reference defaults that need the user's own numbers to confirm.
- Never issue a GO verdict while any tool is classified Blocking — downgrade to CONDITIONAL-GO or NO-GO instead.
- Never skip the capacity/concurrency conversion — a cost comparison that ignores how many calls one GPU can actually serve concurrently is misleading, not just incomplete.
- If volume, cost, or the tool list is missing, ask for it rather than guessing a number to fill the gap.
