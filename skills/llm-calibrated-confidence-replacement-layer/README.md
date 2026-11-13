# Actually Sure: Confidence-Gate Audit & Migration Plan

A self-contained prompt template for auditing a feature where an LLM's own self-reported confidence number (a "Confidence: 85%" line, a 1-10 self-rating, a `confidence` field it fills in) controls a downstream decision — and for producing a concrete plan to replace that number with something actually measured. Paste the block below into any AI chat tool (Claude, ChatGPT, etc.), fill in the bracketed inputs, and send it.

## When to use this

Use it when you have (or are about to build) a feature where an LLM's self-stated confidence gates a decision: auto-approve vs. send-to-human, escalate vs. don't, block vs. allow, answer vs. abstain. You want to know, before committing engineering time either way, whether that number is safe to trust — and if not, exactly what to build instead.

This produces an audit finding and a migration plan. It does not write the runtime scoring code for you — that's a separate engineering task the plan hands off to.

## What to paste

Copy everything in the box below, fill in every `[...]`, and send it as one message.

```
I need an audit of a confidence-gated LLM feature and a migration plan if the current approach is unsafe.

1. What the gate controls: [e.g., "auto-approve a support ticket resolution without human review"]
2. How the current confidence score is produced: [e.g., "we ask the model to end its answer with a line like 'Confidence: 85%'"]
3. Which model/provider generates it: [e.g., "GPT-4o via the OpenAI API" / "Claude Sonnet via the Anthropic API" / "a self-hosted Llama 3 via vLLM"]
4. Current gate threshold: [e.g., "we auto-approve anything self-rated above 80%"]
5. Cost/latency budget for a replacement, if any: [e.g., "can't add more than 2x latency or cost" / "no hard budget yet"]
6. 5-10 example outputs with their self-reported confidence score and, if you have it, a known-correct/known-wrong label:
   - Example 1: [answer text] | self-reported: [X%] | actual: [correct/wrong/unknown]
   - Example 2: ...
   (list as many as you have, 5-10 is enough)

Using this information:

1. Classify this gate's stakes (low/medium/high) based on what it controls, and state why.
2. Explain, specific to my setup (not generically), why the self-reported number from step 2 is or isn't a reliable signal for this gate.
3. If I gave you labeled examples, bucket them by self-reported score and compare each bucket's average self-reported confidence to its actual fraction correct. Tell me directionally whether the score is running hot (overconfident) or cold, and explicitly say this is a small-sample spot-check, not a real calibration measurement.
4. Recommend a replacement scoring method:
   - If my provider exposes token-level logprobs (OpenAI-style APIs, most self-hosted stacks like vLLM do; Anthropic's Claude API currently does not), recommend logit-based confidence scoring and explain how it would work for my specific gate.
   - If it doesn't, recommend sampling-consistency scoring (generate N stochastic completions and measure agreement) with a specific recommended N, and state the exact cost multiplier that adds (N extra calls) against my stated budget.
   - If you don't have enough information about my provider to tell, ask me rather than guessing.
5. Give me a step-by-step migration plan: how big a labeled eval set I need (not 5-10 — tell me the real minimum), how to compute Expected Calibration Error (ECE) as a baseline and after the switch, the go/no-go rule for shipping the replacement, why my old gate threshold won't carry over unchanged to the new score's scale, and a rollback trigger.
6. List any open questions you had to flag instead of assuming.

Format your answer as: Gate Summary, Why the Current Score Is a Risk, Spot-Check Finding, Recommended Replacement Method, Migration Plan, Open Questions.
```

## What you'll get back

A structured report with six sections:

1. **Gate summary** — one line restating what's being audited.
2. **Why the current score is a risk here** — specific to your setup, not generic LLM-calibration theory.
3. **Spot-check finding** — the bucketed comparison from your example outputs, or a note that none were provided.
4. **Recommended replacement method** — logit-based or sampling-consistency scoring, with the reasoning and, for sampling-consistency, the exact cost multiplier.
5. **Migration plan** — concrete steps: eval set size, ECE baseline and post-switch measurement, go/no-go rule, threshold re-tuning, rollback trigger.
6. **Open questions** — anything it had to flag rather than assume (missing provider info, missing budget, missing labels).

## Guardrails this is designed to respect

- It will not hand you a precise calibration verdict from 5-10 examples — that's only enough for a directional spot-check. It should tell you the real minimum (around 50-100 labeled examples) for an actual go/no-go decision.
- It will not recommend sampling-consistency scoring without telling you the exact N-call cost multiplier.
- It will not assume your provider exposes token logprobs — if you didn't say, it should ask (Anthropic's Claude API notably does not expose this).
- It will not tell you your old gate threshold (e.g., "80%") carries over unchanged to a new score — a self-reported percentage, a logit probability, and a sampling agreement fraction are different units and need a fresh threshold sweep.
- It produces an audit and a plan, not working code — if it starts writing an implementation instead of a plan, that's a sign it's drifted from the task; redirect it back to the plan.
- If you didn't give it the gate type, current scoring method, or provider, it should ask before answering rather than giving you a generic answer not anchored to your actual setup.
