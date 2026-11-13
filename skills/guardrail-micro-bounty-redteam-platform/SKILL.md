---
name: guardrail-micro-bounty-redteam-platform
description: Triages a single red-team bounty submission against a self-hosted LLM guardrail (NeMo Guardrails, Guardrails AI, LLM Guard, or a custom webhook) — replays the payload against the live detector where possible, classifies it as a genuine novel bypass, a duplicate of a prior finding, or an unreproduced/false claim, and drafts the payout-or-rejection response to send the submitter. Use when running a manual or small-scale micro-bounty program and a new submission lands.
---

# Bypass Triage: Guardrail Micro-Bounty Submission Reviewer

## When to use this
Trigger this when a solo developer or small team running a self-hosted LLM guardrail (NeMo Guardrails, Guardrails AI, LLM Guard, or a homegrown detector behind a webhook) gets a red-team bounty submission — via a GitHub issue, a Discord DM, an email, or a bounty-board form — claiming an adversarial payload bypassed the guardrail, and needs to decide: pay it, reject it, or ask for more evidence. The tell is a submission that reads like "here's a prompt that gets past your filter, pay up" and the builder has no automated triage pipeline (the GitHub issue `ak10082247-max/canaryguard-402#2` is exactly this pattern — a one-off $5 USDC bounty triaged entirely by hand in the issue thread).

This is a one-shot judgment-and-drafting task for a single submission. It does not run a bounty program, hold escrow, process payment, or maintain a standing leaderboard — those require persistent infrastructure and are the full platform this skill is a companion to, not something this skill does.

## Inputs
**Data source**: Connected — the team's own self-hosted guardrail endpoint (NeMo Guardrails, Guardrails AI, LLM Guard, or a custom webhook), queried directly via its existing HTTP API to replay the submitted payload and get a fresh, authoritative verdict. This API already exists and is mature on the guardrail-product side for all four named targets; what doesn't exist yet is a single standardized connector across all of them, so the user supplies the endpoint URL, auth header, and request/response shape for their specific toolkit, and this skill adapts to it rather than assuming one schema.

If live replay isn't possible in this session (no API access, auth not available, or the user is triaging asynchronously), the skill falls back to the user pasting the guardrail's raw verdict output instead — but the output must say explicitly which mode was used, since a pasted verdict is weaker evidence than a live replay.

Required for every triage:
1. **The submission** — the exact adversarial payload text, the submitter's claimed bypass description (what it should have been flagged as and wasn't), and the submitter's claimed verdict/screenshot from the guardrail, pasted verbatim.
2. **Either** the guardrail endpoint (URL + auth + request format) to replay the payload live, **or** a pasted fresh verdict output if replay isn't available this session.
3. **The guardrail's stated detection scope** — what categories/policies it claims to catch (e.g. "prompt injection, PII leakage, jailbreak attempts" from its config or docs), pasted or linked.
4. **Prior submission history** — a pasted list or log of previously accepted and rejected bypass reports (payload summary, technique family, date, outcome). An empty history is valid for a first-ever submission; say so rather than skipping the dedupe step.

## Procedure
1. **Replay or verify the verdict.** If endpoint access is given, send the exact submitted payload to the live endpoint and record the fresh verdict. If only a pasted verdict is available, use it but flag `UNVERIFIED (no live replay)` throughout the output. If neither is given, stop and ask for one — never fabricate a verdict.
2. **Check reproducibility.** Compare the fresh (or pasted) verdict against the submitter's claim. If the guardrail now correctly flags the payload (contradicting the claim), the bypass does not reproduce — likely already patched, a transient fluke, or a false claim.
3. **Check scope.** Confirm the claimed bypass actually falls within a category the guardrail's stated detection scope claims to cover. A payload that slips through a category the guardrail never claimed to catch is out of scope, not a bypass.
4. **Dedupe against history by technique family, not exact string.** Compare the submission's underlying technique (e.g. "unicode homoglyph obfuscation," "nested-roleplay jailbreak template," "base64-encoded instruction smuggling") against the technique families already present in prior accepted/rejected submissions — not a literal text match. A payload using the same family with cosmetic changes (reordered words, synonym swaps, different surface topic) is a duplicate even if the string is new; a genuinely different technique achieving a similar outcome is not a duplicate even if superficially similar in intent.
5. **Classify** into exactly one of:
   - `PAY — GENUINE NOVEL BYPASS`: reproduces live or via a verified fresh verdict, in-scope, and not a technique-family duplicate.
   - `REJECT — DUPLICATE`: reproduces but matches a prior technique family already paid or already rejected as known.
   - `REJECT — NOT REPRODUCED`: fresh verdict contradicts the claim.
   - `REJECT — OUT OF SCOPE`: reproduces but the category was never in the guardrail's stated detection scope.
   - `NEEDS MORE INFO`: insufficient evidence to classify (e.g. no endpoint access and no usable pasted verdict, or the payload/claim is too vague to replay).
6. **Flag abuse/scope risk**, separately from the classification: if the submission shows signs of testing against a production system without authorization, or targets a system other than the one the bounty covers, note it as a standalone flag regardless of classification — this never changes the payout classification itself, but it must be visible to the builder.
7. **Draft the response.** Write a ready-to-send message to the submitter matching the classification — thanking them, stating the outcome and why, and (for `PAY`) noting that payout execution and amount are the builder's own decision/policy, never something this skill authorizes.

## Output format
```
## Bypass Triage Report

**Submission**: <one-line summary of the payload/claim>
**Evidence mode**: LIVE REPLAY | UNVERIFIED (pasted verdict only)
**Verdict**: PAY — GENUINE NOVEL BYPASS | REJECT — DUPLICATE | REJECT — NOT REPRODUCED | REJECT — OUT OF SCOPE | NEEDS MORE INFO

### Reproduction check
<fresh verdict obtained (or pasted), compared to submitter's claim>

### Scope check
<which stated detection category this does/doesn't fall under>

### Dedupe check
<technique family identified, and the specific prior entry it matches or confirmation none matches — note explicitly if history was empty>

### Abuse/scope risk flag
<NONE, or a specific concern — e.g. "payload references a third-party production domain not covered by this bounty">

### Draft response to submitter
<ready-to-send message>

### Caveats
- <e.g. "verdict is unverified — recommend a live replay before finalizing," or "payout amount/release is the builder's own decision; this report only establishes eligibility">
```

## Guardrails
- Never fabricate or assume a guardrail verdict — if neither live replay nor a pasted verdict is available, classify as `NEEDS MORE INFO` and ask for one, don't guess at what the guardrail would have said.
- Never treat exact-string novelty as sufficient for `PAY` — always run the technique-family dedupe check, since a cosmetically reworded duplicate is still a duplicate.
- Never authorize, execute, or state a specific payout amount — this skill establishes eligibility and drafts the message only; the actual payout decision and amount are the builder's.
- Never classify a submission as `REJECT — DUPLICATE` without naming the specific prior entry (or technique family) it matches — an unsupported duplicate rejection is exactly the kind of triage a submitter can reasonably dispute.
- Never silently drop the abuse/scope risk flag even when the classification is a clean `PAY` — authorization and classification are separate questions.
- Do not present this as a running bounty platform, leaderboard, or escrow system — it reviews one submission at a time and produces no persistent state.
