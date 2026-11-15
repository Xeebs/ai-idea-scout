---
name: vibe-tune-prompt-only-small-model-finetuner
description: Before running any fine-tuning job, judges whether a narrow repeated task (given a task description plus 10-100 real example input/output pairs) is actually worth fine-tuning a small local model for — and if so, sizes the synthetic training set and recommends a base model size tier. Use when a developer has a small local model already in use and a repeated narrow task, and wants a go/no-go call before spending GPU time on training.
---

# Vibe-Tune Pre-Training Advisor

## When to use this
A developer or small team already runs (or plans to run) a small local model (Qwen2.5, Llama-3.2, SmolLM2 class, roughly 0.5B-8B parameters) for a narrow, repeated task — a classification rule, a structured-extraction format, a tone/style rewrite — and is deciding whether to fine-tune that model on their own real examples, or whether fine-tuning would be wasted effort. This skill is the one-time advisory judgment that runs *before* any training job: it does not train anything, call a teacher model, or run QLoRA itself. Use it the moment someone says something like "I have a prompt that mostly works and 30 examples, should I fine-tune a small model for this?"

## Inputs
**Data source**: Manual — the user pastes (a) a short task description in plain language (what the model should do, input format, output format) and (b) 10-100 real example input/output pairs, as a pasted table, CSV, or JSONL. Nothing is read from any connector or API in the MVP version of this skill.

Before starting, confirm you have:
1. The task description.
2. All of the user's real examples (not a subset) — the full count and content matter for every calculation below.
3. Whether the user has already tried few-shot prompting with these same examples in-context, and if so, roughly how accurate that was. If they haven't tried it, say so explicitly rather than guessing.

## Procedure
Work through these gates in the order given (0, then 2, then 1, then 3, then 4 — Gate 2 is evaluated before Gate 1 on purpose, see below). Stop and report at the first gate that produces a recommendation other than "proceed."

**Gate 0 — Eval sanity check.** Scan the pasted examples for internal contradictions: the same or near-identical input mapped to different outputs, inconsistent output formatting (e.g. some outputs are JSON, some are prose), or an output field that's ambiguous from the task description alone. If you find contradictions affecting more than ~10% of examples, stop here: recommend **BUILD A MINI-EVAL FIRST**, name the specific contradictions found, and suggest the user resolve them (pick one canonical format, re-label the conflicting rows) before anything else — fine-tuning on contradictory data teaches the model the contradiction.

**Gate 2 — Knowledge vs. behavior check (always evaluate this one, even if Gate 1 below is about to stop the process).** Read the task description and examples: is the model's failure mode a *knowledge gap* (it doesn't know a fact, a current price/rate/threshold, a customer's account history — especially if the examples hinge on specific values that could change over time) or a *behavior/format gap* (it already has the knowledge it needs but won't consistently follow the output format, tone, or decision rule)? Knowledge gaps are a RAG problem, not a fine-tuning problem, no matter how many examples exist — if this is a knowledge gap, your eventual recommendation will be **STICK WITH PROMPTING + RAG**, not fine-tuning, and no later gate can override that. Only behavior/format gaps can ever proceed to a FINE-TUNE verdict.

**Gate 1 — Prompt-ceiling check.** If Gate 2 found a knowledge gap, skip straight to reporting **STICK WITH PROMPTING + RAG**: recommend the user test prompting with the relevant reference material retrieved into context, not just bare few-shot, and explain that fine-tuning would bake in current values that go stale. Otherwise (behavior/format gap), check whether the user has already tried putting a representative sample of their examples in-context as few-shot prompts and measuring accuracy. If NOT tried, stop here: recommend **STICK WITH PROMPTING (for now)** and specifically suggest running that few-shot test first, since it costs nothing and may already solve the problem. If they HAVE tried it and report it's still unreliable (wrong format, wrong labels, inconsistent on edge cases) on a meaningful fraction of cases, proceed to Gate 3.

**Gate 3 — Example sufficiency and diversity check.** Classify the task into one of: (a) classification with a fixed label set, (b) structured extraction (fixed output fields), (c) style/tone rewrite, (d) other/mixed. Then count the distinct output patterns in the examples — for classification, the number of distinct labels actually represented; for extraction, the number of distinct field-combination patterns; for rewrite, treat it as 1 pattern unless there are clearly distinct sub-styles. Compute examples-per-pattern = total examples / distinct patterns. If examples-per-pattern < 2 for any pattern, or total examples < 10, stop here: recommend **BUILD A MINI-EVAL FIRST** (really: collect more real examples for the underrepresented patterns before attempting synthetic expansion) — synthetic expansion from a single seed example per pattern tends to drift.

**Gate 4 — Task stability check.** Ask (or infer from the task description) whether the task's rules are likely to change within weeks (e.g. a policy that updates monthly) versus stable (a format or classification rule unlikely to change). If clearly unstable, note this as a caveat in the final recommendation even if the verdict is FINE-TUNE — retraining cost will recur.

**If all gates pass, compute the recommendation:**
- Recommendation: **FINE-TUNE**.
- Synthetic training set target = `max(300, 40 × distinct_patterns)`, capped at 1500. State the number and the formula inputs (distinct pattern count) so the user can sanity-check it.
- Base model size tier, chosen by task type and input/output length from the examples:
  - Classification, short inputs (under ~200 tokens per example), fixed label set ≤10: **0.5B-1.5B tier** (e.g. Qwen2.5-0.5B or 1.5B, SmolLM2-1.7B).
  - Structured extraction with fixed fields, or style/tone rewrite, inputs ~200-800 tokens: **1.5B-3B tier** (e.g. Qwen2.5-3B, Llama-3.2-3B).
  - Mixed/multi-step tasks (extraction + classification + generation in one pass), or inputs over ~800 tokens: **3B-8B tier** (e.g. Qwen2.5-7B, Llama-3.1-8B) — flag explicitly that this is at or beyond the "cheap local model" sweet spot this workflow targets, and the user should weigh whether a larger model via prompting/RAG is simpler than fine-tuning at this size.
- Confidence: **high** if examples-per-pattern ≥ 5 across all patterns and the user already has a measured few-shot baseline; **medium** if examples-per-pattern is 2-4; state it plainly either way.

## Output format
Always produce exactly this structure, filled in for whichever gate stopped the process (or the full recommendation if all gates passed):

```
## Vibe-Tune Advisory

**Recommendation**: FINE-TUNE | STICK WITH PROMPTING (for now) | STICK WITH PROMPTING + RAG | BUILD A MINI-EVAL FIRST

**Why**: 2-4 sentences naming the specific gate(s) that drove this call and what was found in the user's own examples/task description.

**If FINE-TUNE:**
- Task type: <classification | structured extraction | style/tone rewrite | mixed>
- Distinct patterns found: <N>, examples-per-pattern: <N>
- Synthetic training set target: ~<X> examples (40 x distinct patterns, floor 300 / cap 1500)
- Recommended base model tier: <tier + named example models> — one-line reasoning
- Confidence: high | medium, with the reason
- Task stability caveat: <none | note>
- Next step: feed this task description, these examples, and this target size/base model into an actual fine-tuning pipeline (e.g. the Vibe Tune project, or any QLoRA tool) — this skill does not train anything itself.

**If anything else:**
- The specific gap found (contradiction, untried prompting, knowledge gap, insufficient examples)
- The concrete next action to take before fine-tuning is worth revisiting
```

## Guardrails
- Never recommend FINE-TUNE if total examples are under 10, or if any distinct pattern has fewer than 2 real examples — say so and stop at Gate 3 instead.
- Never recommend FINE-TUNE as a fix for a knowledge gap — that's a RAG problem; say so explicitly at Gate 2.
- Never skip the prompt-ceiling check (Gate 1) — if the user hasn't tried few-shot prompting with their own examples, that is always the cheaper next step, regardless of how confident the user sounds about needing fine-tuning.
- Never present the synthetic-set-size or base-model numbers as guarantees — they are sizing heuristics for planning, not promises of final accuracy. Always pair the FINE-TUNE recommendation with a confidence level.
- Never run, simulate, or claim to have run any training job, teacher-model expansion, or evaluation — this skill's output is a written advisory only.
- Never ask the user to paste real customer PII or regulated data into a hosted chat tool to use this skill — if the examples look like they contain real customer names, account numbers, or health/financial data, flag that risk before proceeding and suggest anonymizing first.
