---
name: guardrail-denial-explanation-layer
description: Drafts a plain-language, end-user-facing explanation (short UI message + expanded "why was this blocked" panel + suggested next step) from a raw guardrail/policy-engine denial event, with a security-sensitivity check that keeps jailbreak/bypass-category explanations deliberately vague. Use when a team has a guardrail block event (rule ID, category, confidence) and needs user-facing copy for it, or when a developer is answering one specific "why was I blocked" incident.
---

# Guardrail Denial Explanation Layer

## When to use this
A team is building or operating a product that enforces guardrails (NeMo Guardrails, Guardrails AI, a custom policy engine, a moderation API, reasongate-style rule engines) and has a specific denial event — or a small batch of them — that currently surfaces to the end user as a silent block or a raw error code. The trigger is someone saying something like "here's our guardrail's denial payload, what should we actually show the user", "we need denial copy for this policy category", or "a user asked why they got blocked, here's the log line — what do I tell them."

This is a one-shot copy-drafting skill for a specific payload or small batch, not a running service — it does not consume a live event stream, auto-detect guardrail categories it hasn't been told about, or manage a template library across releases. Do not reach for this for: writing the backend adapter/normalizer itself (that's an engineering task, not a drafting task), or for guardrail *rule design* (deciding what to block) — this skill only drafts the message shown after a block has already happened.

## Inputs
**Data source**: Connected in principle, Manual in practice today — the idea behind this skill assumes a guardrail or policy engine emits a structured denial event (rule ID, triggered category, confidence score), reached via whichever backend produced it (NeMo Guardrails violation events, Guardrails AI validator failures, reasongate's rule-based denials, a moderation API response, or a custom app's own block event). No single mature cross-vendor connector exists yet, so for this skill the user pastes the raw denial payload directly — this is the realistic form the input takes until that normalization layer exists.

Required from the user (ask for whatever is missing before drafting):
1. **The raw denial payload** — whatever the guardrail backend emitted: a JSON blob, a log line, or a plain description containing at minimum a rule ID or rule name and the triggered category/policy name. Non-negotiable; do not draft a message without at least a category or rule name to anchor it.
2. **The user-facing context** — what the user was trying to do when blocked (the request or action, in enough detail to reference it naturally in the explanation) — ask for this if the payload alone doesn't make it clear.

Strongly requested, ask explicitly if missing:
3. **Confidence score or severity level**, if the backend produces one — affects how hedged vs. definitive the drafted message should sound.
4. **Brand voice / tone guidelines** — a style guide excerpt, example product copy, or a one-line description ("warm and casual" vs. "formal enterprise"). If not provided, default to neutral, respectful, non-condescending tone and say so in the output.
5. **Whether this category is considered security-sensitive** by the team (e.g. jailbreak/prompt-injection/bypass-attempt detection) — if not stated, the skill makes its own call per the sensitivity rule below and flags that call for review.

## Procedure
1. **Parse the payload.** Extract rule ID/name, category, confidence/severity, and any triggering snippet or matched phrase. If the category or rule name is entirely absent, stop and ask for it rather than guessing a plausible-sounding one.
2. **Classify the sensitivity tier:**
   - **HIGH** — the category is about detecting an attempt to manipulate, bypass, or extract the system's own instructions or safety behavior (jailbreak attempts, prompt injection, role-play-to-bypass, extraction of system prompt/rules, attempts to get disallowed content via obfuscation/encoding).
   - **LOW** — everything else (PII/sensitive-data disclosure, off-topic/out-of-scope requests, content policy categories like violence/hate/sexual content in an otherwise cooperative request, rate/scope limits, confidential-data handling).
   - If genuinely ambiguous, default to HIGH (safer to under-explain than over-explain) and say so explicitly in the output.
3. **For LOW tier:** draft a specific explanation that names the actual policy category in plain language and references the user's real request, plus one concrete, actionable next step (e.g., "rephrase without including the customer's SSN", "ask about X instead, which is in scope").
4. **For HIGH tier:** draft a deliberately generic explanation that confirms a safety/policy block occurred without naming the specific trigger phrase, technique, or exact rule logic that caused it, and offers a legitimate general next step (e.g., "try rephrasing your request" or "contact support if you believe this is an error") without hinting at what would or wouldn't trip the filter.
5. **Match tone** to any provided brand voice guidelines — mirror formality, sentence length, and vocabulary from the examples given; otherwise use a neutral, respectful default and state that default was used.
6. **Produce two length variants**: a short inline message (one sentence, fits a toast/tooltip) and an expanded explanation (2–4 sentences, fits a "why was this blocked?" detail panel).
7. **Flag incomplete inputs.** If anything required was missing and you proceeded with a reasonable assumption, list the assumption explicitly so the team can correct it before shipping.
8. **Add a review flag** on every HIGH-tier draft, and on any LOW-tier draft where the category itself is ambiguous, recommending a human (ideally someone from security/trust-and-safety) review before the copy ships.

## Output format
Always return this structure:

```
## Denial Summary
**Category**: <parsed category/policy name>
**Rule**: <rule ID/name, or "not provided">
**Confidence/severity**: <value, or "not provided">
**Sensitivity tier**: HIGH | LOW — <one-line reason for the classification>

## Short message (UI inline)
<one sentence, ready to paste into a toast/tooltip>

## Expanded explanation (detail panel)
<2-4 sentences: what happened, why, in plain language appropriate to the tier>

## Suggested next step for the user
<one concrete action>

## Assumptions made
<bulleted list of anything inferred because an input was missing — "none" if nothing was inferred>

## Review flag
<"Recommend security/trust-and-safety review before shipping" with a one-line reason, or "No review flag — low-sensitivity category with clear policy match">
```

## Guardrails
- Never invent a rule ID, category, or confidence score that wasn't in the input — if a field is missing, say "not provided" rather than fabricating a plausible-sounding value.
- Never reveal, in a HIGH-tier draft, the specific trigger phrase, exact matched pattern, or the mechanics of how the detector works — doing so can teach a reader how to craft a bypass. When unsure whether a detail is safe to include, leave it out and say why in the Review flag.
- Never skip the sensitivity classification step, even when the category looks obviously benign — always state the tier and the one-line reason, so a reviewer can disagree with the call.
- Never claim this skill performed a security review or that drafted copy is cleared to ship — every HIGH-tier draft and every ambiguous LOW-tier draft gets a Review flag recommending human sign-off.
- Never draft copy implying the backend adapter/normalizer exists if the user hasn't described one — this skill works from whatever payload is pasted, one event (or small batch) at a time; it does not claim live integration with any named guardrail product.
- Never collapse the two length variants into one — a toast message and a detail-panel explanation serve different moments and should both be produced.
