---
name: local-to-cloud-confidence-escalation-router
description: One-shot advisory judgment that decides whether a local-model workload is worth building confidence-based cloud escalation for, picks a confidence-scoring method suited to the task shape, and drafts a starting threshold policy with explicit validation caveats — for someone weighing whether to build the "run local, escalate hard cases to cloud" pattern before writing any middleware.
---

# Local-to-Cloud Confidence Escalation Advisor

## When to use this
Use this the moment someone already running (or about to deploy) a local model — Ollama, llama.cpp, LM Studio, or similar — for a specific task asks something shaped like: "should I build escalation to a cloud model for this," "what confidence method should I use to decide when to escalate," "help me pick a threshold for falling back to GPT-4/Claude," or "is self-consistency or entropy the right signal here." This is a design/decision task, not a runtime: it produces a recommendation, a method choice, and a draft threshold — not working middleware, and not a measured cost/accuracy curve from live inference. Reach for it once per task before any engineering work to actually wire escalation in. It does not replace running an actual benchmark harness against the team's own eval set — it tells them whether that work is worth doing and where to start.

## Inputs
**Data source**: Manual — the user pastes a task description, names the local model (and cloud model, if decided), and optionally pastes a labeled sample of request/response pairs marked correct/incorrect by a human reviewer. There is no connector: this skill never calls the local runtime, the cloud API, or any logging system itself — if the user wants live traffic considered, they paste a representative excerpt as text. (The parent idea's middleware/benchmark-CLI project would connect directly to the team's local runtime and cloud API; this skill is the separate one-time advisory half and stays manual by design.)

Ask for, if not already given:
1. **Task description** — what the local model does (classification, extraction, support-ticket triage, codegen, summarization, open-ended chat, etc.) and the format of a typical output.
2. **Local model identity** — name/size and serving stack (e.g. "Llama 3.1 8B via Ollama", "Phi-3-mini via llama.cpp").
3. **Cloud model target**, if already decided (e.g. GPT-4o, Claude Sonnet) — affects nothing in the method choice but matters for the cost framing.
4. *(Optional, strongly recommended)* **A labeled sample** of 10-50 real request/response pairs from the local model, each marked correct or incorrect by a human. Without this, the recommendation is explicitly flagged as directional/unvalidated.
5. *(Optional)* **Constraints** — budget ceiling, latency ceiling, or an accuracy floor relative to an all-cloud baseline (e.g. "must stay within 5% of all-cloud accuracy").

If the user gives a task description but no sample and doesn't volunteer one, ask once whether they can paste 10+ labeled examples before proceeding — do not silently skip to a directional-only answer.

## Procedure
1. **Classify the task shape**, which determines which confidence signal is even viable:
   - **Closed-form / few discrete valid outputs** (classification, routing, structured extraction, yes/no, multiple-choice-shaped) → self-consistency sampling (re-run the same prompt N=3-5 times, score agreement/majority-vote) is the strongest default; token-probability or logprob-based confidence is a cheaper alternative *only if* the serving stack exposes logprobs (Ollama and llama.cpp both support this via API flags — note this explicitly).
   - **Open-ended generation** (summarization, free-text drafting, codegen, multi-step reasoning) → token-probability signals are noisy and not recommended as primary; recommend self-consistency via semantic similarity across N samples (not exact match) as the default, and name zero-shot confidence estimation (the model rating its own output against a rubric) as a secondary option while flagging explicitly that self-reported confidence is known to be poorly calibrated and should not be the sole signal.
   - If the task mixes both shapes (e.g. extract-then-summarize), say so and recommend scoring the closed-form sub-step only, since that's where a reliable signal exists.
2. **If a labeled sample was provided**: walk through the pasted request/response pairs and, for each, reason through what the chosen confidence signal would likely have flagged (e.g. "these 3 incorrect answers all show low agreement across restated phrasings; these 2 correct answers show high agreement") — this is a text-based estimation from the pasted data, not live model execution, and must be labeled as such. If the sample is under 10 examples, or is all-correct or all-incorrect (no contrast to calibrate against), say explicitly that the sample is too thin/skewed to support a threshold number and stop short of inventing one.
3. **Draft a starting threshold** only when the sample supports it (step 2) or, absent a sample, offer a published-heuristic starting point (e.g. "3-of-5 agreement" or "logprob below X on a 0-1 scale") explicitly labeled DIRECTIONAL — NOT VALIDATED ON YOUR DATA. Every threshold, validated or not, carries the instruction: run it against live traffic and recalibrate before trusting it in production.
4. **Make the build/don't-build call**:
   - **DON'T BUILD YET** — the sample shows the local model already correct on nearly all cases, the task is low-stakes, or there's no labeled sample at all and the user hasn't described a costly failure mode. Building escalation infrastructure for a rarely-wrong, low-stakes task is a cost with no measured return.
   - **BUILD** — the sample shows a real, non-trivial error cluster, or the user describes a clearly costly failure mode (e.g. incorrect answers reach a customer, trigger a downstream action), and the task shape from step 1 supports a usable confidence signal.
   - **NEED MORE DATA** — task/stakes description alone isn't enough to call it either way; name exactly what sample size or stakes detail would resolve it.
5. **Name what this skill did not do**: it did not run inference, did not measure real cost/latency/accuracy, and did not build the middleware or benchmark harness. List the concrete next engineering steps (wire the escalation call, log every escalation decision with its confidence score, re-run this advisory judgment after 2-4 weeks of logged production data to recalibrate).

## Output format
```
## Recommendation: BUILD | DON'T BUILD YET | NEED MORE DATA

### Task Shape
Closed-form | Open-ended | Mixed — one line why, and which signal types this rules in/out.

### Confidence Method
Primary: <self-consistency | logprob/entropy | zero-shot estimator>, why it fits the task shape above.
Secondary (if any) + its known weakness.

### Starting Threshold
<value or range> — VALIDATED ON N LABELED EXAMPLES | DIRECTIONAL — NOT VALIDATED ON YOUR DATA
Explicit instruction: measure on live traffic before trusting this number.

### Evidence Basis
- Labeled sample size and what it showed (if provided), OR
- "No sample provided — recommendation based on published heuristics only."

### Risks Specific to This Task
2-4 bullets tied to the task shape and stakes described.

### Next Steps (out of scope for this skill)
- Wire the escalation call into the local inference path.
- Log every escalation decision with its confidence score for recalibration.
- Build/run a benchmark harness across threshold values on a real eval set before shipping to production.
```

## Guardrails
- Never invent a specific accuracy, cost, or percentage-savings number without a labeled sample behind it — unlabeled recommendations are always marked DIRECTIONAL, never presented as measured.
- Never recommend self-reported confidence (the model rating its own output) as the sole or primary signal — it is known to be poorly calibrated; always pair it with a stated weakness or prefer self-consistency/logprob signals instead.
- Never call a threshold "validated" from fewer than 10 labeled examples, or from an all-correct/all-incorrect sample with no contrast to calibrate against.
- Never claim this skill ran inference, executed the local or cloud model, or produced a measured cost/accuracy curve — it reasons over pasted text only; the benchmark CLI is separate project-track work this skill does not perform.
- Never scope-creep into recommending cloud-to-cloud model routing (that's RouteLLM's/OpenRouter's solved problem) — stay scoped to the local-model-to-cloud escalation decision.
- Never output BUILD for a task the user describes as low-stakes with a near-perfect local sample — a real DON'T BUILD YET outcome must stay reachable.
