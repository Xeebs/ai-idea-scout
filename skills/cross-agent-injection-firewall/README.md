# Handoff Firewall: Cross-Agent Injection Exposure Audit

A self-contained prompt for auditing a multi-agent pipeline for the specific failure mode where a malicious instruction hidden in untrusted content (an email, a scraped web page, an uploaded file) survives being summarized, translated, or rewritten as it's handed from one AI agent to the next, and eventually reaches an agent that can take a real action — send a message, write a record, run code, spend money, publish something. Perimeter filters that scan the original untrusted input often miss this, because the payload no longer looks like the original text by the time it reaches the dangerous agent.

Paste the block below into any AI chat tool, fill in your pipeline description, and send it.

## When to use this
Use this before shipping, or when reviewing, a multi-agent system where:
- At least one agent's input includes content you don't control (inbound email/chat, web pages fetched by a browsing agent, uploaded documents, third-party API responses), and
- That content, or any summary/rewrite of it, gets passed to another agent, and
- Somewhere in the chain, an agent can call a tool that does something with a real effect (not just read-only lookups).

This is not for checking whether a single prompt contains an injection — that's a different, already well-covered problem. This is for checking whether your *handoff graph* lets an injected instruction ride across multiple agents in disguise.

## What to hand over
For each agent in your pipeline, describe:
1. **What it ingests** — is any of its input from outside your control, or only from your own system/another trusted agent?
2. **What tools it has**, if any — and whether each tool only reads/looks something up, or actually changes something (sends, writes, executes, spends, publishes).
3. **What it hands to the next agent**, and in what form — raw text passed through, a summary in its own words, or a structured/typed field with no freeform text.
4. Any defenses you already have — a classifier, an allow-list, a schema, a human-review step — and *exactly which edge* in the chain each one sits on.

If you don't know the answer for some agent, say so rather than guessing — an unstated tool capability should be flagged as unknown, not assumed safe.

## The prompt

```
I'm going to describe a multi-agent AI pipeline. Audit it for cross-agent
prompt-injection exposure using this procedure:

1. Build a handoff graph from my description: each agent as a node, with
   whether it ingests untrusted external content (yes/no/unknown), its tool
   capability tier, and what it hands to which other agent.

2. Classify each agent's tool tier:
   - NONE: text in/text out only.
   - READ-ONLY: tools that only retrieve information.
   - STATE-CHANGING: tools that send, write, execute, or modify something.
   - IRREVERSIBLE/HIGH-STAKES: state-changing tools that are hard to undo or
     reach third parties/the public (publish, financial transaction, delete,
     message a customer, deploy to production).

3. Trace taint: any content that originates from, or is summarized/rewritten
   from, an untrusted-input agent is tainted, and taint carries across every
   downstream handoff by default — rewording does not clear it. Taint is only
   cleared at a hop where there's a genuine structural boundary: the content
   is parsed into a fixed typed schema with no freeform field surviving, or a
   human reviews and re-authors it before it continues. A classifier/filter
   that only flags-or-passes freeform text does NOT clear taint, because a
   reworded payload can evade a classifier while keeping its instructions.

4. Flag every handoff where tainted content reaches a STATE-CHANGING or
   IRREVERSIBLE/HIGH-STAKES agent without a taint-clearing boundary on THAT
   SPECIFIC edge. If I describe a classifier that only runs at the original
   ingestion point (not on this edge), say explicitly that it does not clear
   this edge — that's the most common false sense of security in these
   designs.

5. Rank findings by severity (tool tier of the agent being reached, and more
   hops/rewrites between origin and target counts as more risk, not less —
   don't downgrade just because the content has been transformed several
   times).

6. For each finding, write a specific, implementable policy rule naming the
   two agents and the edge, and exactly what must change. Not "sanitize
   better" — something like "Agent B's send_email tool must only be
   parameterized from Agent C's structured {subject, body} output, never
   from Agent A's raw freeform summary of the inbound email."

7. Add a Residual Risk note: this is a review of the architecture I
   described, not a test of running code — it can't verify that a stated
   defense is actually implemented as described, and it's not a substitute
   for replaying real (reworded/paraphrased) injection payloads through the
   live pipeline. Recommend that as the next step.

Output format:

## Pipeline Map
A table: Agent | Untrusted input? | Tool tier | Hands off to | Content form

## Findings
One block per flagged hop, ranked worst first:
### Finding N — <Agent A> → <Agent B>
- Severity: CRITICAL | HIGH | MEDIUM
- Risk: <why tainted content reaches this agent with no clearing boundary on this edge>
- Stated defense (if any) and why it doesn't close this edge
- Policy rule to close it: <specific rule>

If there are no qualifying findings, say so explicitly rather than inventing one.

## Residual Risk
<one paragraph per the instruction above>

Rules you must follow:
- Never say the pipeline is "safe" or "secure" overall — only describe what's
  closed and what isn't, and always include the Residual Risk note.
- Never credit a perimeter/ingestion-point classifier with protecting a
  downstream edge it doesn't actually run on.
- Never recommend just removing an agent's tool access as the fix — give a
  scoped policy rule instead, or say plainly the capability may be
  incompatible with the input trust level as designed.
- Never invent details about agents, tools, or defenses I didn't mention —
  mark anything unstated as UNKNOWN and flag it as its own finding.

Here is my pipeline:

[DESCRIBE YOUR AGENTS, THEIR INPUTS, THEIR TOOLS, AND WHAT THEY HAND OFF TO
EACH OTHER HERE]
```

## What you get back
A pipeline map table, a ranked list of specific handoff gaps (each naming the two agents, why the gap exists, and exactly what policy rule closes it), and a residual-risk note reminding you this is a design review that should be followed by an actual red-team replay against the live system — not a certification that the system is safe.

## Guardrails this skill follows
- It never declares a pipeline secure — only names what's covered and what isn't.
- It never lets a classifier at the ingestion point get credit for protecting a different, downstream edge.
- It never tells you to just strip an agent's tool access without a workable alternative.
- It never fills in agents, tools, or defenses you didn't describe — unknowns are flagged, not assumed safe or unsafe.
- It is a design-time text review, not a running defense or a penetration test — treat its output as a punch list, not a pass/fail certificate.
