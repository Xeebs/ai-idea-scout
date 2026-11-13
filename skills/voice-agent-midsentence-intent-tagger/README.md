# Tag Taxonomy Architect

A self-contained prompt template for designing the tag taxonomy a streaming voice-agent needs to react mid-sentence — before the caller finishes talking — instead of waiting for end-of-turn. Paste the block below into any AI chat tool (Claude, ChatGPT, Gemini, etc.) along with your own domain details.

## What this is for

Voice agents that run on streaming ASR (Deepgram, AssemblyAI, Azure Speech, etc.) can see partial transcripts word-by-word before the speaker finishes a sentence. A "mid-sentence tagger" watches that stream and tags intent, dialog act (statement/question/command/backchannel), entities, numbers, PII, profanity, and safety-risk as each word arrives, so the agent can act early — pre-fetch an account lookup, flag a safety-risk utterance, redact PII before it's logged — instead of buffering the whole turn.

Building that runtime tagger is an engineering project. But *before* you build or tune it, you need to decide, for your specific domain: what tags exist, what counts as an early-but-safe trigger versus something that must wait for the full sentence, and what confidence threshold each tag needs before the agent is allowed to act on it. That design decision is what this skill produces — a first-draft taxonomy and threshold policy you then validate against real call logs, not a finished, measured config.

## Data source

**Manual.** You describe your domain in prose and paste example call transcripts/utterances and a list of actions your agent can actually take. This skill never connects to a live ASR stream or live call audio — the runtime tagger that *does* consume a live partial-transcript stream (Deepgram's `interim_results`, AssemblyAI's real-time API, Azure Speech's partial-result events — all mature, already-integrated connectors for most voice-agent teams) is a separate engineering component this skill's output feeds into, not something this skill operates.

## What to hand over

1. **Domain description** — what the voice agent does. Be specific: "support hotline for a telecom provider's billing and outage line" is usable; "customer service bot" is not.
2. **Example utterances or call transcripts** — ideally 10-20 real or realistic lines, including a few messy, self-correcting, or ambiguous ones ("uh, I wanted to— actually can you just check if my—"). If you don't have real transcripts, say so; the output will flag every example phrase as invented and unvalidated rather than pretending otherwise.
3. **Available actions** — what the agent can actually do automatically when a tag fires: look up an account, escalate to a human with context, redact and keep logging, pre-fetch data, flag for later review, or (if nothing is automated yet) just log the tag. Without this, there's nothing concrete to attach a threshold decision to.

If you're missing #1 or #3, the assistant should ask for them rather than generating a generic taxonomy — a taxonomy with no attached action isn't usable.

## The procedure (what the assistant should do with your inputs)

1. **List domain-specific intents**, including a catch-all "Unclear/Other." For each, write the shortest partial phrase that would reasonably make the intent clear before the sentence ends (e.g., for a cancellation intent: "I want to cancel my—").
2. **List dialog-act tags** relevant to the domain — statement, question, command, confirmation, backchannel, self-correction/interruption. Usually 5-8 tags; voice callers interrupt and self-correct more than chat users, so self-correction deserves its own tag.
3. **List entity/number types** the agent's available actions actually need (account numbers, dates, dollar amounts, phone numbers, addresses).
4. **List PII types to flag or redact**, based on the domain's regulatory exposure — card numbers and SSNs for billing/telecom, health details and precise locations for crisis or medical intake lines, and at minimum caller name + callback number for any domain unless told otherwise.
5. **List safety-risk categories.** Always include at least one, even for domains that sound low-risk (a reservation line still gets threatening or distressed callers) — only drop this if you explicitly say it's out of scope.
6. **For every single tag across all five lists above**, the assistant assigns:
   - **Mid-sentence eligibility**: *Eligible* (safe to act on partial evidence) or *End-of-turn only* (the consequence is irreversible enough — actually canceling an account, confirming a refund, ending a call — that acting early is never worth it no matter the confidence).
   - **Confidence threshold** (a first-draft 0.0-1.0 number, explicitly not a measured value) for triggering the attached action.
   - **Action on trigger**: None (log only) / Inform planning (agent considers it, doesn't act alone) / Immediate action (agent acts now) — tied to one of your stated available actions.
   - **One-line rationale** grounded in asymmetric cost: safety-risk tags should skew toward lower thresholds and earlier action because missing real distress costs far more than an unnecessary check-in; tags tied to irreversible actions should skew toward higher thresholds or End-of-turn only, because acting on a wrong guess costs real rework.
7. **Flag the gaps**: which example phrases were invented (no real transcript given) and which thresholds are placeholders pending validation against real call logs — a "replay harness" (re-running recorded calls token-by-token to see how early each tag crosses threshold without false-triggering) is the right follow-up before any of this ships.

## Output format

A single markdown document, structured as:

```
# Tag Taxonomy: <domain>

## Intent tags
| Tag | Definition | Example partial trigger | Mid-sentence eligible? | Threshold | Action on trigger | Rationale |

## Dialog-act tags
(same columns)

## Entity / number tags
(same columns — threshold/action often "N/A, informational only")

## PII tags
(same columns — action is almost always "redact before logging")

## Safety-risk tags
(same columns — expect the lowest thresholds in the whole document, with rationale)

## Validation gaps
- <tags whose example phrasing was invented, not drawn from real transcripts>
- <thresholds that are placeholders pending replay-harness tuning>

## Open questions
- <anything your domain description left ambiguous that changes the taxonomy>
```

## Guardrails (don't skip these)

- Never mark a tag "Immediate action" when its consequence is irreversible (account cancellation, refund confirmation, call termination) without flagging that it needs explicit human/business sign-off before shipping. This is a design draft, not a runtime authorization.
- Never invent transcript phrasing when real transcripts were provided — pull examples from what you pasted. Only invent phrasing when none was given, and mark it as invented.
- Always include at least one safety-risk category unless explicitly told to scope it out.
- Never present thresholds as measured — they are first-draft numbers meant to be tuned against real call logs, every time, no exceptions.
- This is a one-shot design document, not the running tagger — it doesn't process live audio or a live transcript stream, and it isn't a substitute for the replay-harness validation described above.

## Example prompt to paste

> Act as a Tag Taxonomy Architect for a streaming voice agent. My domain is: [describe your voice agent's domain]. Here are example call snippets: [paste 10-20 lines]. Here's what my agent can actually do when a tag fires: [list your available actions]. Following the procedure above, produce the full tag taxonomy document with intent, dialog-act, entity, PII, and safety-risk tags, each with mid-sentence eligibility, a confidence threshold, an action-on-trigger, and a rationale grounded in asymmetric cost. Flag every invented example and every placeholder threshold.
