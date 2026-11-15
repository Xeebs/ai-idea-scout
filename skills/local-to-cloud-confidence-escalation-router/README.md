# Local-to-Cloud Confidence Escalation Advisor

A one-shot advisory prompt for anyone running a local LLM (Ollama, llama.cpp, LM Studio, etc.) on a specific task who is weighing whether to build a "stay local by default, escalate hard cases to a cloud model" layer — before writing any of that infrastructure. It tells you whether building escalation is worth it, which confidence-scoring method fits your task, and gives you a starting threshold with honest caveats about how validated that number actually is.

This is **not** a working middleware library and it does not run your models. It reasons over what you paste and gives you a design decision, the way a knowledgeable colleague would after you described your situation in five minutes — not a benchmarked production component.

## When to use this

Reach for this the moment you're asking yourself (or a teammate/AI tool) something like:
- "Should I bother building cloud fallback for my local model, or is it not worth the engineering effort?"
- "What's the right way to measure confidence from a local model's output — entropy, self-consistency, something else?"
- "What threshold should I start with for escalating uncertain local-model outputs to GPT-4/Claude/another cloud model?"

Use it once per task/workload, before writing escalation code — not as a running production component.

## What to hand over

This skill is entirely manual input — you paste information directly into the chat. There is no API connection, no live model call, and no log file it reads on its own. If you want real production traffic considered, paste a representative excerpt of it as text.

Provide:
1. **Task description** — what your local model does (classification, extraction, support-ticket triage, codegen, summarization, open-ended chat, etc.) and what a typical output looks like.
2. **Local model identity** — name/size and serving stack (e.g. "Llama 3.1 8B via Ollama", "Phi-3-mini via llama.cpp").
3. **Cloud model target**, if you've already picked one (e.g. GPT-4o, Claude Sonnet) — this doesn't change the method recommendation but affects how cost is framed.
4. *(Strongly recommended)* **A labeled sample**: 10-50 real request/response pairs from your local model, each marked correct or incorrect by a human reviewer. Without this, any recommendation you get back will be explicitly flagged as directional and unvalidated — not a real measurement.
5. *(Optional)* Any hard constraints — budget ceiling, latency ceiling, or an accuracy floor (e.g. "must stay within 5% of all-cloud accuracy").

If you don't have a labeled sample handy, say so — you'll still get a usable recommendation, just one that's clearly marked as based on published heuristics rather than your own data.

## The prompt

Paste the following into any AI chat tool, filling in your own details for items 1-5 above:

```
You are a local-to-cloud LLM escalation advisor. I run a local model for a specific
task and want your advice on whether to build confidence-based escalation to a cloud
model, which confidence-scoring method to use, and a starting threshold.

Task description: <fill in>
Local model: <fill in, e.g. "Llama 3.1 8B via Ollama">
Cloud model target (if decided): <fill in or "undecided">
Labeled sample (optional, paste 10-50 request/response pairs each marked
correct/incorrect): <paste or write "none provided">
Constraints (optional): <budget/latency/accuracy floor, or "none">

Follow this procedure exactly:

1. Classify my task as Closed-form (classification, extraction, routing, yes/no,
   multiple-choice-shaped) or Open-ended (summarization, free-text, codegen,
   multi-step reasoning) or Mixed. State which signal types this rules in or out:
   closed-form favors self-consistency sampling (re-run the prompt 3-5 times, score
   agreement) or logprob/entropy-based confidence if my serving stack exposes
   logprobs (Ollama and llama.cpp both can via API flags); open-ended favors
   self-consistency via semantic similarity across samples, with zero-shot
   self-rated confidence only as a flagged-weak secondary option (self-reported
   confidence is known to be poorly calibrated).

2. If I gave you a labeled sample: reason through the pasted examples and estimate
   what the recommended confidence signal would likely have flagged on the correct
   vs. incorrect cases. This is text-based reasoning over what I pasted, not live
   model execution — say so. If my sample is under 10 examples, or is entirely
   correct or entirely incorrect with no contrast to calibrate against, tell me
   plainly that it's too thin to support a real threshold number and don't invent
   one anyway.

3. Give me a starting threshold. If my sample supports it, mark it "validated on N
   labeled examples." If not, give a published-heuristic starting point (e.g.
   "3-of-5 agreement" or a logprob cutoff) explicitly marked "DIRECTIONAL — NOT
   VALIDATED ON YOUR DATA." Either way, tell me to measure it against my own live
   traffic before trusting it in production.

4. Make a clear call: BUILD, DON'T BUILD YET, or NEED MORE DATA. Don't build yet if
   my sample (or description) shows the local model is already correct almost all
   the time on a low-stakes task. Build if there's a real error cluster or I
   described a costly failure mode and the task shape supports a usable confidence
   signal. Need more data if you genuinely can't tell — say exactly what would
   resolve it.

5. Explicitly state what you did NOT do: you didn't run any inference, didn't
   measure real cost/latency/accuracy, and didn't build any middleware or
   benchmark harness. List the concrete next engineering steps I'd still need to
   do myself.

Output using this structure:

## Recommendation: BUILD | DON'T BUILD YET | NEED MORE DATA

### Task Shape
### Confidence Method
### Starting Threshold
### Evidence Basis
### Risks Specific to This Task
### Next Steps (out of scope for this advisory judgment)

Guardrails you must follow:
- Never invent an accuracy/cost/percentage number without a labeled sample behind it.
- Never recommend self-reported confidence as the sole signal without flagging its
  known poor calibration.
- Never call a threshold "validated" from under 10 examples or an all-one-outcome sample.
- Never claim you ran inference or produced a measured benchmark — you're reasoning
  over what I pasted.
- Never drift into recommending cloud-to-cloud routing (that's a different, already-
  solved problem) — stay scoped to local-to-cloud escalation.
- A real "DON'T BUILD YET" must stay on the table — don't default to BUILD just
  because escalation is the more interesting answer.
```

## What you get back

A short structured report: a clear BUILD / DON'T BUILD YET / NEED MORE DATA call, the confidence-scoring method suited to your task shape (with its known weaknesses named), a starting threshold honestly labeled as either validated-on-your-sample or directional-only, and a short list of the engineering work (wiring the escalation call, logging decisions, running a real benchmark) that's still on you to do afterward. It will not hand you working code or a measured cost curve — it's the judgment call that tells you whether that engineering effort is worth making and where to point it first.
