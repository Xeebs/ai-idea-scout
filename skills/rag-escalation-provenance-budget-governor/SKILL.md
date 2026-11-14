---
name: rag-escalation-provenance-budget-governor
description: Drafts a concrete, enforceable policy spec — escalation trigger conditions, a context-budget cap, and a provenance schema — for a team deciding whether/how to let a quote-grounded or no-RAG agent escalate to external retrieval. Use when a team is designing (not yet building) the rules for an opt-in, auditable retrieval-escalation layer, before any infrastructure gets written.
---

# Budget Gate: Escalation Policy Drafter

## When to use this
A team has an agent that today answers only from first-party/quote-grounded sources (or has no retrieval at all) and is weighing whether to let it escalate to an external retrieval source — web search, a vector DB, an internal knowledge base — for broader coverage. They want the *rules* for that escalation (when it fires, how much context it can pull, how it stays auditable) written down before an engineer starts wiring it into a pipeline. This is a design/review step, not the runtime middleware itself: the output is a spec a human reads and hands to an engineer, or pastes into the project's own config.

## Inputs
**Data source**: Connected — this skill itself calls no API and reads no live data; it asks the user to name the external retrieval source(s) their agent already has lined up (e.g., a web-search API such as Tavily, Exa, or Bing Search API, or an internal vector DB client). The drafted policy is written against that named, already-mature connector, not a new retrieval integration this skill builds — carrying forward the parent idea's Connected classification.

The user provides, in their own words:
1. **Current retrieval posture** — one of: quote-grounded/first-party only, generic always-on RAG, or no retrieval yet.
2. **The named external retrieval source(s)** being considered for escalation (e.g., "Tavily web search", "internal pgvector store of policy docs").
3. **Risk profile** — what's at stake if an escalated answer is wrong or unsourced (e.g., "compliance research for external auditors", "sales prospect fact-checking", "casual internal Q&A"). This drives how strict the trigger and cap get.
4. **Model/context constraints** — the model's context window and any existing token budget already spent on system prompt, history, etc., so the cap recommendation is a number that actually fits, not an arbitrary round figure.
5. *(Optional)* Any volume/latency constraint (queries/day, acceptable added latency per escalation).

If (1), (2), or (3) is missing, ask for it before drafting — a policy spec with a guessed risk profile is worse than no spec, because it reads as authoritative.

## Procedure
1. **Classify risk tier** from input 3: HIGH (external/regulatory scrutiny, money, legal exposure, published claims), MEDIUM (internal decisions, customer-facing but correctable), LOW (internal exploration, no downstream consequence). Say which tier and why in one line.
2. **Draft the escalation trigger** — the condition that flips retrieval from off to on for a single query, stated as a concrete, checkable rule, not a vibe:
   - HIGH tier: trigger only when first-party/quote-grounded search returns below a named minimum supporting-quote count (default: fewer than 2) **and** the query is independently flagged as in-scope for external sourcing (a named allow-list of topics/claim types) — i.e. two conditions must both hold, not one.
   - MEDIUM tier: trigger when first-party search returns below the minimum count (default: fewer than 1), no allow-list gate required.
   - LOW tier: trigger on simple confidence/quote-count shortfall alone, user-adjustable.
   - Always state the default thresholds as numbers the user can override, and name what "flagged as in-scope" means concretely for their domain if HIGH tier.
3. **Recommend a context-budget cap** — a hard token (or passage-count) ceiling for what an escalation may pull in, computed from input 4: reserve the model's existing system-prompt + history + output budget, cap the escalation slice at a stated fraction of what's left (default: no more than 15% of total context window, or 25% of whatever headroom remains after reserved blocks — whichever is smaller), and state the enforcement action on overrun: truncate lowest-relevance-ranked passages first, then if still over cap, abort the escalation and surface "insufficient budget" rather than silently truncating mid-passage.
4. **Draft the provenance schema** — the minimum field set every retrieved passage must carry, tagged per passage and surviving into the final response:
   - `source` (named origin: URL/doc ID), `retrieved_at` (timestamp), `claim_id` (which generated claim this passage backs — not just "used somewhere"), `trust_tier` (a label the team defines, e.g. primary/secondary/unverified), `content_hash` (for audit-log integrity).
   - Flag any field the user's stated setup can't currently populate (e.g., no trust-tier taxonomy exists yet) as an open gap, not a silent omission.
5. **State the audit-log requirement** — one line: every escalation decision (fired or not, and why) plus the budget actually spent gets written to an append-only log, keyed by query ID, regardless of risk tier.
6. **Assemble and return the spec** in the Output format below. Do not add infrastructure recommendations (database choice, library picks) beyond what's needed to state the cap/schema — that's the runtime project's job, not this skill's.

## Output format
```
## Escalation Policy Spec — <team/system name>

**Risk tier**: HIGH | MEDIUM | LOW — <one-line reason>
**Retrieval source(s) in scope**: <named connector(s), as given>

### 1. Escalation Trigger
<concrete rule, with numeric defaults and override note>

### 2. Context-Budget Cap
- Cap: <N tokens or passages, with the fraction/reservation math shown>
- Overrun handling: <truncation order, then abort behavior>

### 3. Provenance Schema (per retrieved passage)
| Field | Required | Notes |
|---|---|---|
| source | yes | |
| retrieved_at | yes | |
| claim_id | yes | |
| trust_tier | yes/gap | <flag if taxonomy doesn't exist yet> |
| content_hash | yes | |

### 4. Audit Log Requirement
<one line>

### Open Gaps
<anything the user's current setup can't yet support, so the engineer who implements this knows what to build first>
```

## Guardrails
- Never recommend defaulting retrieval to always-on — the entire point of this skill is that escalation stays an exception, triggered by a named condition, not a default pipeline stage.
- Never invent the user's risk profile, connector name, or context-window size — ask rather than assume, and never silently substitute a "typical" value.
- Always give the cap as a concrete number with the math shown, never "a reasonable budget" with no figure.
- Always name an overrun-handling behavior; a cap with no stated enforcement action isn't a cap.
- Flag schema fields the user's current setup can't populate yet as open gaps — do not quietly drop them from the schema to make the spec look complete.
