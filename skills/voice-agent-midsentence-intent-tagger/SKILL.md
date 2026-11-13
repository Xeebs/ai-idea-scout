---
name: voice-agent-midsentence-intent-tagger
description: Drafts a domain-specific tag taxonomy (intent, dialog act, entities, PII, profanity, safety-risk) and per-tag confidence-threshold/action policy for a streaming voice-agent tagger, so mid-sentence actions only fire where the cost of being early is actually worth it. Use when a team is designing or revising what their voice agent should react to before the full utterance finishes, not when running the live tagger itself.
---

# Tag Taxonomy Architect

## When to use this
Someone is building (or already running) a voice agent that tags intent/dialog-act/entities/PII/profanity/safety-risk word-by-word off a streaming ASR partial-transcript feed, and needs to decide *what tags exist for their domain* and *which ones are allowed to trigger an action before the speaker finishes talking*. Reach for this at design time — before wiring the runtime tagger, or whenever revisiting the taxonomy after a round of real call logs show false triggers or missed early signal. This skill does not run against live audio or a live transcript stream; it produces the design document a human (or the runtime tagger's config loader) consumes.

## Inputs
**Data source**: Manual — the user describes the domain in prose and pastes example transcripts/call snippets and a list of actions the agent can actually take. (The parent idea's runtime tagger itself is Connected — it taps a streaming ASR provider's partial-transcript events, e.g. Deepgram `interim_results`, AssemblyAI real-time streaming, Azure Speech partial results, all mature today. This skill is the separate one-shot design task: it never touches the live ASR stream, only what the user pastes.)

The user provides:
1. **Domain description** — what the voice agent does (e.g., "support hotline for a telecom provider's billing and outage line", "crisis counseling intake line", "restaurant reservation line").
2. **Example utterances or call transcripts** — ideally 10-20 real or realistic lines/snippets, including a few that are ambiguous or ramble before the real intent lands. If none are provided, the skill proceeds on domain description alone but flags every tag's example phrasing as invented and unvalidated.
3. **Available actions** — what the agent can actually do when a tag fires (e.g., "look up account by phone number", "escalate to human agent with full transcript", "redact and continue logging", "nothing automated yet, just flag for review"). Without this, threshold decisions have no real action to attach to, so ask for it before proceeding.

If domain description or available actions is missing, ask for it rather than inventing a generic taxonomy — a taxonomy with no attached actions is not usable output.

## Procedure
1. **Extract domain-specific intents** from the description and any pasted transcripts. Build an exhaustive-as-possible list including a catch-all "Unclear/Other" intent. For each, write the shortest partial utterance that would reasonably make the intent clear before the sentence ends (e.g., for "cancel subscription": "I want to cancel my—").
2. **Define dialog-act tags** relevant to the domain (statement, question, command, confirmation, backchannel, correction/self-repair — voice-specific, since callers interrupt themselves). Keep this list short; most domains need 5-8.
3. **Define entity and number types** the agent needs mid-utterance (account numbers, dates, dollar amounts, phone numbers, addresses — whatever the available actions actually consume).
4. **Define PII types to flag/redact** based on the domain's regulatory exposure (card numbers and SSNs for billing/telecom; health details and names/locations for crisis lines; always include at minimum name + callback number unless the user says otherwise).
5. **Define safety-risk categories** specific to the domain. Always include at least one safety-risk category even if the domain description doesn't mention risk (self-harm/distress indicators for crisis lines; threats, fraud indicators, or abusive-caller flags for support lines) — every voice domain has a hostile or distressed caller edge case. Only drop this if the user explicitly says it's out of scope.
6. **For every tag across all five categories above**, assign:
   - **Mid-sentence eligibility**: Eligible (safe to act on partial evidence) or End-of-turn only (consequence is irreversible enough that acting early is never worth it, regardless of confidence — e.g., actually canceling an account, confirming a refund, ending the call).
   - **Confidence threshold** (0.0-1.0, approximate — this is a first-draft number for the replay harness to tune, not a measured value) for triggering the attached action.
   - **Action on trigger**: None (log only) / Inform planning (agent considers it but doesn't act) / Immediate action (agent acts now), tied to one of the user's stated "available actions."
   - **One-line rationale** grounded in asymmetric cost: a safety-risk tag should bias toward a *lower* threshold and earlier trigger because a false negative (missed distress) costs far more than a false positive (an unnecessary check-in); a billing-intent tag attached to an irreversible action should bias toward a *higher* threshold or End-of-turn only, because a false positive (wrong account action) costs real rework.
7. **Call out gaps explicitly**: any tag whose example phrasing was invented rather than drawn from pasted transcripts, and any threshold that is a placeholder pending validation against real call logs (per the parent idea's replay-harness approach: re-running recorded conversations token-by-token to check how early each tag's confidence crosses threshold without false-triggering).

## Output format
A single markdown document:

```
# Tag Taxonomy: <domain>

## Intent tags
| Tag | Definition | Example partial trigger | Mid-sentence eligible? | Threshold | Action on trigger | Rationale |

## Dialog-act tags
(same columns)

## Entity / number tags
(same columns, threshold/action often N/A — informational)

## PII tags
(same columns — action is almost always "redact before logging")

## Safety-risk tags
(same columns — lowest thresholds in the document go here, with rationale)

## Validation gaps
- <tags with invented example phrasing, needing real transcripts>
- <thresholds that are placeholders pending replay-harness tuning>

## Open questions
- <anything the domain description left ambiguous that changes the taxonomy>
```

## Guardrails
- Never mark a tag "Immediate action" when its consequence is irreversible (account cancellation, refund confirmation, call termination) without flagging that this needs explicit human/business sign-off before shipping — this skill drafts a design, it does not authorize a runtime decision.
- Never invent example transcript phrasing when the user provided real transcripts — pull examples from what they pasted; only fall back to invented phrasing when none was given, and mark it as invented in Validation gaps.
- Always include at least one safety-risk category unless the user explicitly scopes it out — silently omitting it because the domain "sounds low-risk" (e.g., reservations) is the failure mode that lets an abusive or distressed caller go untagged.
- Never present the thresholds as measured or validated — they are first-draft numbers for a human to tune against real call logs or the replay harness described in the parent project; say so every time.
- Do not conflate this skill with the runtime tagger itself: this skill produces a config/design document for a human or a config loader to consume, not a deployed model, and it never processes live audio or a live transcript stream.
