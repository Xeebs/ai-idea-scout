# Local Omni-Model Cascade Migration Assessor

Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your voice-agent architecture details, and it will produce a go/no-go assessment for migrating from a cascaded STT+LLM+TTS vendor stack to a self-hosted local audio-native omni-model (e.g. LFM3-Audio-2B and similar models that do speech-to-text, reasoning, and text-to-speech in one process with native tool-calling).

## When to use this

You're running a voice agent built on separate vendors — a speech-to-text API (Deepgram, Whisper, AssemblyAI...), an LLM (GPT, Claude...), and a text-to-speech API (Cartesia, ElevenLabs...) — and you're wondering whether a single local omni-model could replace all three, cut your per-minute vendor costs, and remove a network hop per turn. You want a reasoned answer *before* spending a few weeks building a migration spike, not after.

## What to hand over

This is manual input — you paste your own architecture details, nothing is fetched from any connected account. Give it:

1. **Your current stack and cost**: STT vendor + model, LLM vendor + model, TTS vendor + model, and either the combined per-minute cost or enough info (vendor + published rate) to estimate it.
2. **Your call volume**: monthly call-minutes, or your peak number of concurrent calls if you don't track minutes.
3. **Your tool/function list**: every tool or function your agent calls, with a note on whether any of them rely on **parallel tool calls** (the LLM calling two functions in one turn) or **streaming partial arguments** (using an argument value before the full tool call has finished streaming — e.g. updating a UI mid-utterance).
4. Optional but useful: measured p50/p95 latency numbers (stage-by-stage if you have them), and any GPU hosting budget/constraint you're already working with.

If you're missing the cost, volume, or tool list, say so when you hand this over — the assessment should ask for it rather than guessing.

## What it does (procedure)

1. **Reads your architecture** and extracts the vendor costs, volume, and tool list.
2. **Audits every tool** against the real limitation of today's local audio-native omni-models: by default, assume **no parallel tool calls and no streaming partial arguments** unless you've confirmed your specific model version supports them. Each tool gets classified:
   - *Likely compatible* — simple, single tool call per turn, no partial-arg dependency.
   - *Needs redesign* — uses parallel calls or partial-arg streaming that could be refactored to sequential/complete-arg calls.
   - *Blocking* — depends on a capability that can't be reproduced without vendor confirmation; no workaround found.
3. **Estimates hosting tier and capacity.** Using a reference baseline (one 24GB GPU like an RTX 4090 serves roughly 8-15 concurrent real-time sessions, clearly labeled as a default to validate with a real load test), it converts your call volume into a GPU count.
4. **Estimates the cost delta.** Your current vendor cost (rate × monthly minutes) against the amortized hardware + electricity cost of running your own GPU(s). Any number you didn't supply (GPU price, electricity rate, vendor rate) is labeled explicitly as a reference default, not a verified price — confirm your own numbers before trusting the delta.
5. **Estimates the latency delta.** If you gave stage-by-stage numbers, it sums the network/serialization overhead of each cascade hop (~150-400ms per vendor round-trip, rule of thumb) against a single local inference hop. If you only gave end-to-end numbers, the comparison is marked directional, not a hard figure.
6. **Produces a verdict**: GO, CONDITIONAL-GO, or NO-GO.
   - NO-GO if any tool is Blocking with no workaround.
   - CONDITIONAL-GO if the economics favor migrating but some tools need redesign, or your hosting budget doesn't cover the GPU count the volume requires.
   - GO only if every tool is compatible or has a clear redesign path, and the hosting tier fits your stated budget.
7. **Lists what to validate before you actually migrate** — specifically: tool-call accuracy under barge-in (someone interrupting mid-response), voice quality (MOS) on your actual accents/use case, measured end-to-end latency on real hardware, and measured cost on your real volume. This assessment is a projection to decide whether the spike is worth running — it is never a substitute for running it.

## Output format

A single report with these sections, always in this order:

1. **Verdict** — one line (GO / CONDITIONAL-GO / NO-GO) plus a one-sentence reason.
2. **Cost comparison** — a table: current vendor stack and monthly cost vs. projected hardware/electricity monthly cost and GPU count, with the dollar and percentage delta.
3. **Latency estimate** — current vs. projected, marked as measured or directional depending on what you provided.
4. **Tool-calling compatibility audit** — a table listing every tool, the feature(s) it uses, its classification, and the reasoning.
5. **Hosting tier recommendation** — GPU count and the concurrency assumption behind it, flagged as a default pending a real load test.
6. **Required validation before migrating** — the specific benchmarks to run and what result would flip the verdict.
7. **Confidence & caveats** — what was missing or assumed, and how it affects how much to trust the verdict.

## Guardrails — what this will never do

- Never present a cost or latency number as guaranteed — every figure is a projection pending the benchmark it recommends you run.
- Never assume a tool is compatible by default. The default is "no parallel tool calls, no streaming partial args" unless you explicitly confirm your model version supports them.
- Never invent vendor, GPU, or electricity prices without labeling them clearly as reference defaults that need your own numbers to confirm.
- Never issue a GO verdict while any tool is still classified Blocking.
- Never skip the concurrency/capacity math — a cost comparison that ignores how many calls a single GPU can actually serve at once is misleading.
- If you haven't given your volume, cost, or tool list, it should ask you for it rather than filling in a guess.

## Why this exists

In late 2026, several small local audio-native "omni" models (e.g. LFM3-Audio-2B) became capable enough to run STT, reasoning, and TTS in one process on a single consumer GPU, with native tool-calling. A wave of hobbyist projects appeared independently showing this works as a proof of concept, but none of them answer the question a team actually needs answered first: *given our specific tools and call volume, does switching actually save money and hold up on the tool-calling features we rely on* — without spending weeks building the migration to find out the hard way.
