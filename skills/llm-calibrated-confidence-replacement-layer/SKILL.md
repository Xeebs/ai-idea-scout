---
name: llm-calibrated-confidence-replacement-layer
description: Audits a confidence-gated LLM feature that keys off a model's self-reported confidence number, and produces a migration plan to a measured (logit-based or sampling-consistency) score instead. Use when a team wants to know if their self-rated confidence gate is safe, or needs a concrete plan to replace it.
---

# Actually Sure: Confidence-Gate Audit & Migration Plan

## When to use this
Use this when someone has (or is about to build) a feature where an LLM's own stated confidence number ("I'm 85% sure", a 1–10 self-rating, a `confidence: 0.9` field it fills in) controls a downstream decision — auto-approve vs. send-to-human, escalate vs. don't, block vs. allow, abstain vs. answer. The trigger moment is specifically *before* committing engineering time to either (a) trusting that number as-is, or (b) building a runtime replacement — this skill is the design/audit pass that tells them whether the number is trustworthy and, if not, what to build instead.

This is not for building the runtime scoring library itself (that's a separate engineering task — see Guardrails). It produces the audit finding and the migration plan a team acts on.

## Inputs
**Data source**: Manual — the user pastes a description of their current confidence-gated feature and its scoring method, plus 5–10 example outputs with their self-reported scores (the sampling/logprob calculations this skill recommends run against the team's own live model API, which is outside this skill's scope — this skill only reasons about what the team pastes).

Specifically, ask for (and do not proceed without at least items 1–3):
1. **What the gate controls** — e.g., "auto-approve a support ticket resolution", "decide whether to escalate a triage case to a human", "set moderation severity".
2. **How the current score is produced** — the exact prompt instruction or field (e.g., "we ask the model to end its answer with `Confidence: X%`" or "we ask it to self-rate 1–10").
3. **Which model/provider** is generating the score (e.g., "GPT-4o via OpenAI API", "Claude Sonnet via Anthropic API", "a locally hosted Llama 3 via vLLM").
4. **5–10 example outputs**: each one the model's actual answer, its self-reported confidence number, and — if the team has it — a known-correct/known-wrong label. If no labels are available, say so explicitly; the audit still runs, just without the calibration-gap illustration in step 3 of the Procedure.
5. **Current gate threshold** (e.g., "we auto-approve above 80%") and any stated cost/latency budget for a replacement (e.g., "can't add more than 2x latency").

If any of 1–3 is missing, ask for it before producing output — a generic answer not anchored to their actual gate is the failure mode this skill exists to avoid.

## Procedure
1. **Classify the gate type and stakes.** Identify whether this is a low-stakes gate (e.g., routing convenience) or high-stakes (e.g., medical, legal, financial, moderation decisions that affect people). State this classification explicitly in the output — it changes how much calibration rigor to recommend before go-live.

2. **Name the specific unreliability mechanism for this case.** Self-reported confidence is the model describing itself in the same generation pass that produced the answer, with no mechanical link between the number and actual correctness — it reflects instruction-following and prompt framing as much as or more than the model's actual certainty. Connect this generically-true fact to the team's specific setup: e.g., if they self-rate 1-10 with no calibration instructions, note models tend to cluster scores in a narrow high range regardless of actual correctness, which is especially dangerous for an auto-approve gate because it compresses the signal right where the gate threshold lives.

3. **If labeled examples were provided, run an informal calibration spot-check.** Bucket the 5–10 examples by self-reported score (e.g., "90-100%" bucket, "70-89%" bucket) and compare bucket-average self-reported confidence to the actual fraction correct in that bucket. State explicitly that this is illustrative, not a statistically valid Expected Calibration Error (ECE) measurement — 5–10 points is too few for that; the real ECE check happens in Step 5 with a larger labeled set. Report the directional finding only (e.g., "your 90%+ bucket was right 3 of 4 times — directionally the self-reported number is already running hot, which is the cheapest evidence I can show you from only {count} examples").

4. **Recommend a replacement scoring method based on the stated provider.** Ask or infer whether the provider exposes token-level `logprobs`/`top_logprobs` on completions (OpenAI-style APIs and most self-hosted serving stacks like vLLM do; Anthropic's Claude API does not expose this as of this skill's writing). 
   - If logprobs are exposed: recommend **logit-based confidence** — extract the probability mass on the generated answer tokens (or just the decision token, if the gate reduces to a binary/categorical choice). State the advantage: no extra API calls, negligible added latency/cost.
   - If logprobs are not exposed: recommend **sampling-consistency scoring** (SelfCheckGPT-style) — generate N stochastic completions (temperature > 0) of the same prompt and measure agreement across them (exact match for categorical outputs; semantic similarity for free text). Recommend a specific N (start at N=5 for most gates; N=10 if the stated stakes from Step 1 are high and the cost budget allows) and explicitly state the cost multiplier this adds (N extra model calls) against the budget they gave you in Input 5. If no budget was given, ask before finalizing N.
   - If the provider wasn't stated clearly, do not guess — ask, then resume.

5. **Draft the migration plan**, as a numbered sequence the team can actually execute:
   a. Assemble a labeled evaluation set of real examples from their own traffic — target 50–100 minimum (5–10 is only enough for the Step 3 spot-check, not a go/no-go decision) — each with a known-correct/known-wrong label.
   b. Compute Expected Calibration Error (ECE) for the current self-reported score on that set, as the baseline to beat.
   c. Implement the recommended method from Step 4 behind the same call signature as the current self-report call, so the surrounding gate logic doesn't need to change shape — only the number flowing into it changes.
   d. Compute ECE for the new method on the same labeled set.
   e. State the go/no-go rule explicitly: ship the replacement only if its ECE is materially lower than the baseline AND the false-auto-approve rate (gate let a wrong answer through) drops or holds on the same set — a lower ECE with a worse false-approve rate is not a win for an auto-approve gate specifically.
   f. Set the new gate threshold by re-running a threshold sweep against the new score's distribution — flag explicitly that the old threshold (e.g., "80%") was tuned for the self-reported scale and will not carry over meaningfully to a logit probability or an agreement fraction.
   g. Recommend a rollback trigger (e.g., "if false-auto-approve rate on live traffic exceeds the eval-set rate by more than 2x in the first week, revert").

6. **Compile findings into the Output format** below.

## Output format
A single structured report with these sections, in this order:
1. **Gate summary** — one line restating what was audited (gate type, stakes classification, provider/model).
2. **Why the current score is a risk here** — 2–4 sentences, specific to their setup (Step 2 output).
3. **Spot-check finding** — the bucketed comparison from Step 3, or "no labeled examples provided, skipping" if none were given.
4. **Recommended replacement method** — logit-based or sampling-consistency, with the specific reasoning (provider capability, cost budget) and, if sampling-consistency, the recommended N and its cost multiplier stated as a number (e.g., "N=5 means 5x the model calls for this gate specifically").
5. **Migration plan** — the lettered sequence from Step 5, written as concrete action items, not restated theory.
6. **Open questions** — anything the skill had to flag rather than assume (missing provider info, missing budget, missing labels) that the team must resolve before executing the plan.

## Guardrails
- Never state a precise ECE number, "calibrated" claim, or go/no-go verdict from fewer than ~30 labeled examples — 5–10 examples only support the directional spot-check in Step 3, not a decision.
- Never recommend sampling-consistency scoring without stating the N-call cost multiplier as an explicit number against the user's stated or requested budget.
- Never assume a provider exposes logprobs — Anthropic's Claude API does not; ask rather than guess if the user didn't specify.
- Never recommend carrying over the old gate threshold to the new score unchanged — the scales are not comparable (a self-reported percentage, a token logit probability, and a sampling agreement fraction are three different units).
- Never write or claim to have tested runtime code — this skill produces an audit finding and a migration plan, not a working implementation. If the user wants the implementation, say that's a separate engineering task and hand off the plan as the spec for it.
- Never skip asking for the gate type, current scoring method, and provider when any is missing — a generic answer not anchored to the team's actual setup is the exact failure mode this skill exists to prevent.
