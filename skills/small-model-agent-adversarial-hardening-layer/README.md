# Small Shield Audit: Small-Local-Model Agent Hardening Review

A self-contained prompt for auditing an agent stack that uses a small local model (generally sub-7B — Qwen2.5-1.5B, SmolLM2, Phi-3-mini, Gemma-2B/9B, Llama-3.2-1B/3B, or similar, run via Ollama, llama.cpp, or vLLM) as an autonomous component: a router, a tool-calling agent, or a first-pass classifier. Published red-team results found 45–62% attack success against exactly this class of model — measurably worse than frontier models on the same attacks — but that fact usually shows up as a one-line caveat on cost-savings threads and never gets turned into something you can actually check your own stack against. This prompt turns it into a checklist.

This is a **design-time text review**: you paste your system prompt and tool schema, and it walks a fixed list of small-model-specific attack classes and tells you which ones you have no mitigation for, with the specific fix recommended — not a generic large-model security lecture, and not a live penetration test.

Paste the block below into any AI chat tool, fill in your details, and send it.

## When to use this
Use this before deploying, or when reviewing, an agent stack where:
- The model doing the work is small and local (sub-7B class, run on your own infrastructure for cost or privacy reasons), and
- It has real agency in the loop — it routes requests, calls tools, or gates what reaches a larger model or a real action, not just a one-off chat reply.

Don't use this for a frontier/large-model deployment (GPT-4-class, Claude, Gemini-Pro-class) — the whole point of the countermeasures recommended here is that they're sized for a small model's weaker adversarial training and tighter cost/latency budget; applying them to a large model is pointless, and applying large-model-grade guardrails to a small model defeats the reason you chose it.

## What to hand over
1. **Your agent's full system prompt text.**
2. **Your tool/function-call schema** — tool names, parameter types, and descriptions.
3. *(Optional but recommended)* The specific small model name and parameter count you're running (e.g., "Qwen2.5-1.5B-Instruct via Ollama").
4. *(Optional)* Any defenses you already have in place — a filter, an allowlist, a classifier, rate limiting — and where exactly they sit.

If you don't have #3 or #4, say so — don't guess at your own setup to fill the prompt out; the audit marks unstated things as unknown rather than assuming you're covered.

## The prompt

```
I'm going to describe an agent stack built on a small local model (sub-7B
class — e.g. Qwen2.5-1.5B, SmolLM2, Phi-3-mini, Gemma, Llama-3.2-1B/3B — run
via Ollama, llama.cpp, or vLLM) that acts as an autonomous component: a
router, a tool-calling agent, or a first-pass classifier. Audit it using
this procedure. Published red-team research found 45-62% attack success
against this exact class of small model, measurably worse than frontier
models on the same attacks -- use that as context for why this matters, not
as a number you report back as if you measured it on my stack.

First confirm scope: if what I describe isn't a small/local model (it's a
frontier model, or I didn't give you a size), ask me for the model name and
size before doing anything else -- this audit is only calibrated for small
local models.

Then walk exactly these 7 attack classes against what I describe, and for
each one mark it COVERED (a specific named mitigation is described),
PARTIAL (something relevant but not structurally enforced), or UNCOVERED
(nothing addresses it) -- based only on evidence I actually gave you, never
assumed:

1. Direct instruction override ("ignore previous instructions," persona
   jailbreaks) -- small models have weaker refusal robustness than frontier
   models on the published attack set. Fix if gap: an output-side classifier
   calibrated on the small-model attack baseline, not a generic large-model
   guardrail.

2. Indirect injection via tool/retrieved content -- instructions hidden
   inside a tool's return value or a retrieved document. Small models
   conflate "data returned by a tool" with "an instruction from the
   operator" more readily than larger models. Fix if gap: explicit
   delimiter/provenance tagging in the system prompt distinguishing
   instructions from data, plus a decoy/honeytoken probe specifically on the
   tool-output channel.

3. Obfuscation/encoding (base64, leetspeak, translation, unicode tricks
   carrying the same payload) -- safety behavior trained on plain-text
   attacks doesn't generalize to obfuscated forms, and small models have had
   less adversarial training. Fix if gap: input normalization/decoding
   before the model sees it, plus an output classifier; a SecAlign-style
   adapter fine-tune if retraining is feasible.

4. Multi-turn context/memory poisoning -- a fake prior "assistant" turn or
   transcript injected into context/memory that the model continues. Small
   models pattern-match continuation of fake dialogue more readily. Fix if
   gap: decoy/honeytoken probing re-run every turn (not just the first), and
   provenance tagging that persists across turns.

5. Tool-call hijacking -- injected content causes an unintended tool call or
   attacker-controlled arguments to a legitimate tool. This is the
   agent-specific danger -- the model can act, not just talk. Fix if gap:
   validate tool-call arguments against the schema's allowlist before
   execution; add a secondary classifier reviewing proposed calls for any
   state-changing tool.

6. System-prompt/config extraction ("repeat your instructions," "what's your
   system prompt") -- used as reconnaissance for further attacks; small
   models leak more readily. Fix if gap: plant a honeytoken phrase in the
   system prompt that should never be echoed back -- any echo is a leak
   signal.

7. Resource-exhaustion via recursive tool-call abuse -- an injected
   instruction causes the agent to loop or call tools repeatedly, burning
   the cost savings that justified using a small model in the first place.
   None of the fixes above address this -- it needs a rate-limit/circuit-
   breaker at the proxy/middleware layer, a structural infra fix, not a
   model-side one. Flag it as its own category, never fold it into the
   others.

For each UNCOVERED or PARTIAL class, recommend the specific countermeasure
named above -- never a generic "add more filtering."

Rank findings by severity = what the reached tool/capability can actually
do (read-only vs. state-changing vs. irreversible) combined with
UNCOVERED-beats-PARTIAL. A COVERED class is not a finding.

Before finalizing, check that no recommendation is oversized for the stated
model's footprint -- a heavyweight large-model-grade guardrail ensemble
defeats the reason a small model was chosen. Flag it explicitly if an
existing or recommended defense is already disproportionate.

Output format:

## Stack Summary
Model: <name/size or UNKNOWN> | Tools described: <n> | Provenance
separation in system prompt: yes/partial/no

## Attack Class Audit
A table with all 7 rows every time (number, attack class, status, evidence,
countermeasure) -- include COVERED rows too, don't just list gaps.

## Prioritized Fixes
Top 3 highest-severity UNCOVERED/PARTIAL classes, each with the specific
named countermeasure. Fewer than 3 if fewer real gaps exist.

## Residual Risk
One paragraph: this is a text review of what I pasted, not a test of the
running model; it can't verify a stated mitigation actually works as
implemented; the 45-62% figure is published context for the cited attack
set against those specific models, not a measurement of my deployment;
recommend running an actual red-team attack set against the live stack next.

Rules you must follow:
- Never claim you measured attack success against my actual running model --
  only cite the published baseline as context.
- Never credit a vague "be careful with untrusted input" instruction with
  closing a specific class -- require a named structural mechanism or mark
  it PARTIAL at best.
- Never recommend frontier-model-grade guardrails for a small model -- stay
  proportional, and call out if something already isn't.
- Never fold the resource-exhaustion class into the decoy/classifier/adapter
  recommendations -- it needs a different layer (proxy rate limiting).
- Never invent tools, parameters, or defenses I didn't mention -- mark
  anything unstated as UNKNOWN and flag it as its own finding.
- Always run all 7 classes every time, even the obviously-covered ones.

Here is my stack:

Model: [NAME AND PARAMETER COUNT, OR "UNKNOWN"]
System prompt: [PASTE IN FULL]
Tool/function schema: [PASTE TOOL NAMES, PARAMETERS, DESCRIPTIONS]
Existing defenses (if any): [DESCRIBE OR WRITE "NONE"]
```

## What you get back
A stack summary, a 7-row table scoring every attack class as covered/partial/uncovered with the evidence and the specific fix, a top-3 prioritized fix list, and a residual-risk note reminding you this is a design review that should be followed by running an actual red-team attack set against your live deployment.

## Guardrails this skill follows
- It never reports the published 45-62% small-model attack-success figure as if it measured your specific deployment.
- It never lets a vague "be careful" instruction count as closing a specific attack class without a named structural mechanism.
- It never recommends a guardrail stack sized for a frontier model onto a small local model — recommendations stay proportional to what you're actually running.
- It never treats the resource-exhaustion/tool-loop-abuse class as solved by the same fixes as the other six — that one needs a proxy-level rate limit, not a model-side mitigation.
- It never invents tools, parameters, or defenses you didn't describe — anything unstated comes back as its own flagged finding, not an assumption either way.
- It is a one-time, pre-deployment design review of the text you paste, not a running defense and not a substitute for live red-team testing.
