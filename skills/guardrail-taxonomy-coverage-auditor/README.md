# Coverage Map: Nine-Category Guardrail Taxonomy Auditor

A paste-in prompt that audits a team's guardrail/gateway stack against nine enforcement-point categories and tells you exactly which ones have zero or thin coverage — before a security review finds out for you, or an incident does.

## Why this exists

Teams assembling guardrails from NeMo Guardrails, Guardrails AI, LLM Guard, a gateway plugin, and custom tool-authorization code tend to invest heavily wherever the mature OSS tooling is easiest to bolt on (usually tool authorization and access control) while leaving other enforcement points — content inspection, egress, spend limits — completely untouched. From the outside, the system looks "fully guardrailed." It usually takes a manual, multi-week internal audit for a team to discover the blind spot. This prompt does that enumeration in one pass.

It is a point-in-time, self-reported design-review audit — not a penetration test, not a scanner that reads your actual running config, and not a continuous CI check. It only tells you what's missing based on what you describe.

## When to use it

- You believe your agent/LLM system is "guardrailed" but have never checked that belief against a full category list.
- You're prepping for a security review and want a coverage map before someone else finds the gaps.
- You just noticed you're strong in one area (say, tool permissions) and want to know if you're blind somewhere else.

Don't use this to judge whether an existing guardrail's accuracy has decayed over time, or to design how failures should escalate — those are different jobs.

## What to hand the AI

Paste a plain-language inventory of your stack. For each piece, give:

1. Its name.
2. Where it sits in the request/response path (before the prompt reaches the model, before a tool call executes, on the model's final response, etc.).
3. What it actually checks or restricts, in behavioral detail — not just a product name. "A gateway plugin" is not gradable. "A gateway plugin that runs a PII classifier on the model's output and redacts matches before the response goes to the user" is.

Also include, even if you don't think of them as "guardrails": any allow-lists, rate limits, spend caps, network egress rules, or sandboxing/isolation settings.

If you have them: any past incident or near-miss tied to a specific piece of the stack, and whether each control is enforced inline (blocks/modifies in real time) or observational only (logs/alerts after the fact).

## The prompt

```
You are auditing my AI agent/LLM system's guardrail coverage against nine
enforcement-point categories. Here is my guardrail/gateway stack:

[PASTE: one entry per control — name, where it sits in the request/response
path, and what it actually checks/restricts in behavioral detail. Include
allow-lists, rate limits, spend caps, egress rules, and sandboxing settings
even if you don't think of them as "guardrails." Note whether each is
enforced inline or observational-only if you know.]

Do the following:

1. List every distinct control you found in my description, in your own
   words, before mapping anything.

2. Map each control against these nine categories (a control can map to
   two if it genuinely spans both, with a one-line note explaining the
   split):
   - Inbound content — filtering what comes into the model (prompt
     injection, jailbreaks, unsafe input).
   - Outbound content — filtering what the model produces before it
     reaches a user or downstream system (toxicity, PII leakage).
   - Topic scope — restricting what subjects/tasks the agent engages
     with at all, independent of content safety.
   - Tool authorization — which tools/functions the agent may call,
     and under what conditions.
   - Reachability — which systems/endpoints the agent's tool calls can
     actually reach, regardless of authorization policy on paper.
   - Egress — controls on what data can leave the execution
     environment (exfiltration prevention), distinct from outbound
     content filtering — this is about where data goes, not what it says.
   - Spend/rate limits — caps on token spend, API cost, or call
     frequency per session/user/time window.
   - Sandboxing — isolation of code execution or tool-call side effects
     from the host environment.
   - Post-hoc audit — logging and reconstructability of what the agent
     did after the fact, independent of real-time blocking.

3. Grade each category COVERED / THIN / NONE / UNKNOWN. Never grade from
   a control's name alone:
   - NONE: nothing in my description maps here.
   - THIN: something maps here, but it's checkbox-level (a static
     allow/deny list, observational-only logging with no blocking, or
     incidental coverage from something built for a different purpose).
   - COVERED: substantive logic — a classifier/model-based check, a
     threshold, an enforced rule with real consequences.
   - UNKNOWN: my description is too vague to grade. Ask me a clarifying
     question instead of guessing generously.

4. For every category that isn't COVERED, give one line on what's
   missing and one concrete, specific next step I could take this week
   — not a vendor pitch.

5. Open your answer with a one-paragraph summary: how many categories
   are COVERED / THIN / NONE / UNKNOWN, and whether this matches the
   common failure shape of "deep on access control (tool auth,
   reachability, sandboxing), blind on content" (or the inverse) — name
   it explicitly if it fits.

6. Then give a nine-row table: Category | Grade | Mapped control(s) |
   Why this grade | Next step (if not COVERED).

7. Close with a short caveat: this taxonomy is one reasonable grouping,
   not an industry standard (no standard has converged yet); this audit
   is based only on what I described and doesn't verify runtime
   behavior — a control graded COVERED on paper can still be silently
   misfiring in production.

Never invent what a control does beyond what I stated. Never let a
COVERED grade imply strong implementation — just that it's substantively
described and enforced. Every one of the nine categories must appear in
your table, even if graded NONE.
```

## What you get back

- A one-paragraph headline: how many of the nine categories are genuinely covered versus thin, missing, or unclear, including a direct call-out if your stack matches the "strong on access control, blind on content" shape (or its inverse) — the specific failure mode that this prompt was built to catch.
- A nine-row table mapping every category to your actual controls (or the absence of one), with a specific next step for anything short of fully covered.
- A closing caveat reminding you this is a self-reported, point-in-time read — not proof the covered categories work correctly in production.

## Limitations

This grades what you describe, not what's actually running. If your description is generous or outdated, the audit will be too — garbage in, garbage out, same as any self-reported audit. It also doesn't verify runtime behavior: a classifier graded COVERED can still be misconfigured or silently failing. Treat a NONE or THIN result as a prioritized list of things to go verify directly, not as the final word.
