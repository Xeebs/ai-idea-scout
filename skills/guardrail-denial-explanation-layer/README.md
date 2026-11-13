# Guardrail Denial Explanation Layer

A copy-drafting prompt for turning a raw AI guardrail/policy-engine denial event into plain-language, end-user-facing explanation copy — a short UI message, an expanded "why was this blocked?" panel, and a suggested next step — while deliberately keeping security-sensitive categories (jailbreak/bypass attempts) vague enough not to teach anyone how to evade the filter.

Paste the whole block below into any AI chat tool (Claude, ChatGPT, Copilot, etc.), then paste your guardrail's denial payload under it.

## When to use this

Use this when you operate an AI product with a guardrail or policy engine (NeMo Guardrails, Guardrails AI, a moderation API, a custom rule engine, anything that emits a "blocked" event with a rule ID or category) and you have one denial event — or a short batch of them — that currently shows the end user a silent block or a raw error code instead of an explanation. Also use it for a one-off: a user asked "why was I blocked?" and you have the log line but no ready copy to answer with.

This is **not** for building the backend adapter that normalizes denial events across vendors (that's engineering work), and it's **not** for deciding what should get blocked in the first place (that's guardrail/policy design). It only drafts the message shown to the end user *after* a block has already happened.

## Data source

**Manual** — you paste the raw denial payload yourself (a JSON blob, a log line, or a plain description). In principle this kind of drafting could eventually be fed automatically by a guardrail backend's own event stream (NeMo Guardrails, Guardrails AI, a moderation API, reasongate-style rule engines), but no single mature connector exists across vendors today, so the realistic way to use this is to copy/paste the payload you already have.

## What to hand over

1. **The raw denial payload** (required) — whatever your guardrail backend emitted: JSON, a log line, or a description, containing at least a rule ID/name or a category/policy name. Don't use this skill without at least that much — if you can't identify the category, get that first.
2. **What the user was trying to do** (required, unless already obvious from the payload) — the actual request or action that triggered the block, described in enough detail to reference naturally in the copy.
3. **A confidence score or severity level**, if your backend produces one (optional, but improves how hedged vs. definitive the copy sounds).
4. **Your brand voice / tone** (optional) — paste a style guide excerpt or a couple of example product sentences, or just say "formal" / "casual and warm" / etc. If you skip this, the draft defaults to a neutral, respectful tone and says so.
5. **Whether your team already considers this category security-sensitive** (optional) — if you don't say, the drafting follows the sensitivity rule below on its own and flags the call.

## What the assistant will do

1. Parse the payload for rule ID/name, category, confidence/severity, and any triggering snippet. If no category or rule name is present at all, it will stop and ask for one rather than guess.
2. Classify the denial into one of two sensitivity tiers:
   - **HIGH** — anything about detecting an attempt to manipulate, bypass, or extract the system's own instructions or safety behavior (jailbreak attempts, prompt injection, disallowed-content extraction via obfuscation, role-play-to-bypass).
   - **LOW** — everything else (PII/sensitive-data handling, off-topic/out-of-scope requests, standard content-policy categories, rate/scope limits).
   - If it's genuinely ambiguous, it defaults to HIGH (safer to under-explain) and says so.
3. For **LOW**-tier denials: draft a specific explanation naming the actual policy category in plain language, referencing the real request, plus a concrete next step the user can take.
4. For **HIGH**-tier denials: draft a deliberately generic explanation that confirms a safety block happened without revealing the exact trigger, phrase, or technique that caused it — still giving the user a legitimate general next step.
5. Match the tone to whatever brand voice you provided; otherwise default to neutral/respectful and say so explicitly.
6. Produce **two versions**: a one-sentence inline message (for a toast or tooltip) and a 2–4 sentence expanded explanation (for a "why was this blocked?" detail panel).
7. List any assumptions it made because something was missing from your input.
8. Add a review flag recommending human (ideally security/trust-and-safety) review on every HIGH-tier draft, and on any LOW-tier draft where the category match itself was ambiguous.

## Output format

The assistant will always return exactly this structure:

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
<bulleted list of anything inferred because an input was missing - "none" if nothing was inferred>

## Review flag
<"Recommend security/trust-and-safety review before shipping" with a one-line reason, or "No review flag - low-sensitivity category with clear policy match">
```

## Guardrails (things it will refuse to do)

- It will never invent a rule ID, category, or confidence score that wasn't in your input — missing fields get marked "not provided," never fabricated.
- It will never reveal, in a HIGH-tier draft, the specific trigger phrase, exact matched pattern, or detection mechanics — that information can teach someone how to craft a bypass.
- It will always state the sensitivity tier and its one-line reasoning, even for categories that look obviously benign, so you can disagree with the call.
- It will never claim the drafted copy has been security-reviewed or is cleared to ship — HIGH-tier and ambiguous LOW-tier drafts always carry a review flag.
- It will never imply it has live access to your guardrail backend or that a cross-vendor adapter already exists — it only works from whatever payload you paste, one event (or small batch) at a time.
- It will always produce both the short and expanded message — never just one.

## How to use this prompt

Paste this entire README into your AI chat tool, then add your denial payload and any of the optional context above. Example opener:

> Here's a denial event from our guardrail: `{"rule": "pii_disclosure_v3", "category": "pii_disclosure", "confidence": 0.94}`. The user was asking the support bot to look up a customer's account using their SSN. We use a formal, enterprise tone. Draft the denial copy.
