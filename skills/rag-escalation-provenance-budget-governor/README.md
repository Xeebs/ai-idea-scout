# Budget Gate: Escalation Policy Drafter

A self-contained prompt template for drafting the rules that govern when a quote-grounded (or no-retrieval) AI agent is allowed to escalate to external search/retrieval — and how much it's allowed to pull in when it does. Paste the block below into any AI chat tool along with your answers to the four questions.

## What this does

If your agent today only answers from first-party sources (or doesn't retrieve anything at all), and you're considering letting it reach out to a web-search API, a vector database, or some other external source for broader coverage, this produces a written policy spec covering three things most teams skip until something goes wrong:

1. **When escalation fires** — a concrete, checkable trigger condition, not "when it seems necessary."
2. **How much context an escalation may pull in** — a hard cap with the math shown, and what happens on overrun.
3. **What gets recorded about every retrieved passage** — a provenance schema so any claim in the final answer can be traced back to its source.

This is a *design* step — it produces a spec document, not working code. Hand the output to whoever implements your retrieval pipeline, or use it to review a design someone else already wrote.

## What to hand over before using this

Data source note: this is a one-shot design aid — it doesn't call any API itself. You tell it, in plain prose, which retrieval connector you already have lined up (a web-search API, an internal vector store, etc.); the policy it drafts is written against that named, already-existing connector, not a new integration.

Answer these four before you start:

1. **Current retrieval posture** — quote-grounded/first-party only, generic always-on RAG, or no retrieval yet?
2. **The external retrieval source(s) you're considering** for escalation (name the actual API/store — e.g. "Tavily web search," "our pgvector store of internal policy docs").
3. **Risk profile** — what's at stake if an escalated answer turns out wrong or unsourced? (e.g. "compliance research handed to external auditors," "sales prospect fact-checking," "internal exploratory Q&A.")
4. **Model/context constraints** — your model's context window size, and roughly how much of it is already spent on system prompt + conversation history before any retrieval happens.

Optional: expected query volume and how much added latency per escalation is tolerable.

If you're missing #1–#3, the tool should ask rather than guess — a policy spec built on a guessed risk profile is worse than no spec, because it *reads* as authoritative.

## The procedure (what the AI does with your answers)

1. **Classify risk tier**: HIGH (external/regulatory scrutiny, money, legal exposure, published claims), MEDIUM (internal decisions, customer-facing but correctable), or LOW (internal exploration, no downstream consequence) — stated with a one-line reason.
2. **Draft the escalation trigger**:
   - HIGH tier: fires only when first-party search returns fewer than 2 supporting quotes (default, overridable) **and** the query is flagged as in-scope for external sourcing via a named allow-list — both conditions required.
   - MEDIUM tier: fires when first-party search returns fewer than 1 supporting quote (default). No allow-list gate needed.
   - LOW tier: fires on a simple confidence/quote-count shortfall, user-adjustable.
3. **Recommend a context-budget cap**: reserve what's already spent on system prompt/history/output, then cap the escalation slice at whichever is smaller — 15% of the total context window, or 25% of remaining headroom. State the overrun behavior explicitly: truncate the lowest-relevance passages first; if still over cap, abort the escalation and surface "insufficient budget" rather than silently cutting a passage mid-sentence.
4. **Draft the provenance schema** — every retrieved passage must carry: `source` (named origin), `retrieved_at` (timestamp), `claim_id` (which generated claim it backs, not just "used somewhere"), `trust_tier` (a label you define, e.g. primary/secondary/unverified), `content_hash` (for audit-log integrity). Any field your current setup can't populate yet gets flagged as an **open gap**, not quietly dropped.
5. **State the audit-log requirement**: every escalation decision — fired or not, and why — plus the budget actually spent, written to an append-only log keyed by query ID, at every risk tier.

## Output format

```
## Escalation Policy Spec — <your team/system name>

**Risk tier**: HIGH | MEDIUM | LOW — <one-line reason>
**Retrieval source(s) in scope**: <named connector(s), as you gave them>

### 1. Escalation Trigger
<concrete rule, numeric defaults, override note>

### 2. Context-Budget Cap
- Cap: <N tokens or passages, with the math shown>
- Overrun handling: <truncation order, then abort behavior>

### 3. Provenance Schema (per retrieved passage)
| Field | Required | Notes |
|---|---|---|
| source | yes | |
| retrieved_at | yes | |
| claim_id | yes | |
| trust_tier | yes/gap | <flag if no taxonomy exists yet> |
| content_hash | yes | |

### 4. Audit Log Requirement
<one line>

### Open Gaps
<what your current setup can't support yet, so an implementing engineer knows what to build first>
```

## Rules this tool follows (don't let it skip these)

- It never recommends making retrieval always-on — escalation stays a logged exception triggered by a named condition, never a default pipeline stage.
- It never invents your risk profile, connector name, or context-window size — if you didn't give it, it asks, it doesn't assume a "typical" value.
- The budget cap is always a concrete number with the math shown — never "a reasonable budget" with no figure attached.
- Every cap comes with a stated overrun-handling behavior — a cap with no enforcement action isn't actually a cap.
- Schema fields your setup can't populate yet are flagged as open gaps, never silently dropped to make the spec look more finished than it is.

## Paste-ready prompt

> I'm designing an escalation policy for an AI agent that currently [quote-grounded only / generic RAG / no retrieval], considering escalating to [named retrieval source(s)]. The risk profile is: [describe what's at stake if wrong/unsourced]. My model's context window is [N tokens], and [system prompt + history] already use roughly [N tokens] of it before any retrieval. Using the Budget Gate procedure (risk tier → escalation trigger → context-budget cap with overrun handling → provenance schema → audit-log requirement), draft my Escalation Policy Spec in the output format above, flagging any schema field I can't currently populate as an open gap.
