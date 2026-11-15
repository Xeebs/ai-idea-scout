# Vibe-Tune Pre-Training Advisor

Paste this whole prompt into any AI chat tool (Claude, ChatGPT, etc.) along with your task description and examples. It gives you a go/no-go call on fine-tuning a small local model — BEFORE you spend any GPU time or write any training code.

## When to use this

You already run (or plan to run) a small local model — something in the Qwen2.5, Llama-3.2, or SmolLM2 family, roughly 0.5B to 8B parameters — for one narrow, repeated task: a classification rule, a structured-extraction format, a tone/style rewrite, that kind of thing. You have a prompt that mostly works, and you've got somewhere between 10 and 100 real examples of correct input/output pairs sitting around. You're wondering: is it actually worth fine-tuning a small model on these examples, or should you just keep prompting? This tool answers that question — it does not train anything, call any teacher model, or run any QLoRA job itself. It's purely the advisory step that comes before any of that.

## What to hand over

**Data source: Manual.** You paste everything directly into the chat — nothing here reads from any API, database, or connector.

Before running this, gather:
1. **A task description** — plain language: what should the model do, what does the input look like, what does the output look like.
2. **All of your real examples** — not a sample, all of them — as a pasted table, CSV, or JSONL of input/output pairs (10-100 rows).
3. **Whether you've already tried few-shot prompting** with these same examples stuffed into the prompt as context, and roughly how accurate that was. If you haven't tried this yet, say so — don't guess at a number.

## The prompt to paste

```
You are my pre-training advisor. I have a narrow, repeated task I'm running against a small local model, and I want your advisory judgment on whether fine-tuning is worth it before I spend any GPU time or write any training code. Do not train anything or simulate running anything — just give me the written recommendation below.

Here is my task description:
<paste task description>

Here are my real example input/output pairs (10-100 of them):
<paste examples as a table, CSV, or JSONL>

Have I already tried few-shot prompting with these examples in-context? <yes, it got roughly X% accurate / no, I haven't tried this yet>

Work through these checks in this exact order and stop at the first one that gives a verdict other than "proceed" (note: the knowledge-vs-behavior check comes before the prompt-ceiling check on purpose, because a knowledge gap overrides everything else no matter how many examples I have):

1. Eval sanity check: scan my examples for contradictions — same/near-identical input mapped to different outputs, inconsistent output formatting, or ambiguous output fields. If more than ~10% of examples look contradictory, tell me to fix the data first (recommendation: BUILD A MINI-EVAL FIRST) and name the specific contradictions.

2. Knowledge vs. behavior check: is my failure mode a knowledge gap (the model doesn't know a fact/current price/rate/threshold that could change over time) or a behavior/format gap (it knows enough but won't follow my format/tone/rule consistently)? If it's a knowledge gap, stop here: recommendation is STICK WITH PROMPTING + RAG, and explain that fine-tuning would bake in current values that will go stale. Only a behavior/format gap continues to check 3.

3. Prompt-ceiling check: if I haven't already tried few-shot prompting with my own examples in-context, tell me to try that first (recommendation: STICK WITH PROMPTING for now) since it costs nothing and might already solve this. If I have tried it and it's still unreliable on a meaningful fraction of cases, continue to check 4.

4. Example sufficiency check: classify my task as classification / structured extraction / style-tone rewrite / mixed. Count the distinct output patterns in my examples (distinct labels, distinct field-combinations, or distinct sub-styles). Compute examples-per-pattern. If any pattern has fewer than 2 real examples, or I have fewer than 10 total, tell me to collect more real examples first (recommendation: BUILD A MINI-EVAL FIRST).

5. Task stability check: is my task's rules likely to change within weeks, or is it stable? Note this as a caveat either way.

If I pass all checks, give me:
- Recommendation: FINE-TUNE
- Synthetic training set target = max(300, 40 x distinct_patterns), capped at 1500 — show me the math
- Recommended base model size tier based on my task type and example length:
  - Classification, short inputs (<200 tokens), <=10 labels -> 0.5B-1.5B tier (e.g. Qwen2.5-0.5B/1.5B, SmolLM2-1.7B)
  - Structured extraction or style/tone rewrite, 200-800 token inputs -> 1.5B-3B tier (e.g. Qwen2.5-3B, Llama-3.2-3B)
  - Mixed/multi-step tasks or inputs over 800 tokens -> 3B-8B tier (e.g. Qwen2.5-7B, Llama-3.1-8B), and flag that this is at or past the "cheap local model" sweet spot so I should weigh whether a bigger model via prompting is simpler
- Confidence: high if examples-per-pattern >= 5 everywhere and I already have a measured few-shot baseline, otherwise medium
- A task stability caveat if relevant

Give me the result in this exact format:

## Vibe-Tune Advisory

**Recommendation**: FINE-TUNE | STICK WITH PROMPTING (for now) | STICK WITH PROMPTING + RAG | BUILD A MINI-EVAL FIRST

**Why**: 2-4 sentences naming the specific check(s) that drove this call.

**If FINE-TUNE:**
- Task type:
- Distinct patterns found / examples-per-pattern:
- Synthetic training set target (with the math):
- Recommended base model tier (with named example models) and why:
- Confidence (high/medium) and why:
- Task stability caveat:
- Next step: feed this into an actual fine-tuning pipeline (QLoRA tool of your choice) — this advisory doesn't train anything.

**If anything else:**
- The specific gap found
- The concrete next action before fine-tuning is worth revisiting

If my examples look like they contain real customer names, account numbers, or health/financial data, warn me about pasting that into a hosted chat tool before going any further.
```

## What you get back

A short written verdict — not a trained model, not a script, not a training config. Either a clear "fine-tune, and here's the sizing" with a specific synthetic-example-count target and a specific small-model size recommendation, or a clear "not yet, here's the one thing to do first" (try few-shot prompting, add RAG, collect more examples, or fix contradictory labels).

## What this does not do

It does not generate synthetic training data, run QLoRA, evaluate a trained checkpoint, or produce a GGUF file. It is the single advisory judgment call that should happen before any of that — a 5-minute conversation that can save hours of wasted training runs on a task that either isn't ready for fine-tuning yet, or was never going to need it.
