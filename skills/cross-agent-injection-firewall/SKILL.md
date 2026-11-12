---
name: cross-agent-injection-firewall
description: Audits a described multi-agent pipeline for cross-agent prompt-injection exposure — flags every handoff where content derived from untrusted input can reach a tool-capable agent without a containment boundary, and names the specific policy rule that closes each gap. Use before building/shipping a multi-agent system that ingests external content (emails, web pages, documents, user uploads) and hands work between agents, especially when any agent downstream can call tools.
---

# Handoff Firewall: Cross-Agent Injection Exposure Audit

## When to use this
Someone is designing, reviewing, or about to ship a multi-agent pipeline where at least one agent ingests content from outside the system's control (inbound email, scraped web pages, uploaded documents, API responses from third parties) and that content — or a summary/transformation of it — gets handed to another agent, and *some* agent in the chain can call tools that do something real (send email, write to a database, execute code, make a purchase, publish content, call an external API). The trigger is a "review this pipeline before we ship it" or "did we miss an injection path" moment — this is a design-time text audit, not a runtime scanner and not a replacement for an actual red-team test.

This is specifically about the **multi-hop** case: content gets rewritten/summarized/translated as it moves between agents, which lets an injected instruction survive a perimeter classifier at the ingestion point and still reach a dangerous tool two or three hops later in different words. A single-agent "does this one prompt contain an injection" check is a different, already well-covered problem — don't use this skill for that; use it for the handoff graph.

## Inputs
The user provides a description of the pipeline's data flow. At minimum, for each agent in the chain:
1. **What it ingests** — specifically whether any of its input originates outside the operator's control (external text, files, web content, third-party API responses) or exclusively from another agent/the system's own trusted config.
2. **What tools/capabilities it has**, if any (read-only lookup vs. an action with a real-world effect: sending a message, writing a record, executing code, spending money, publishing something, calling an external system).
3. **What it hands to the next agent**, and in what form (raw text passthrough, a summary, a structured/typed field, a tool-call parameter).
4. *(Optional)* Any stated defenses — a classifier, an allow-list, a schema, a human-approval step — and exactly where in the chain each one sits.

If the user gives a diagram or code instead of prose, work from that; if any agent's tool access or input source is genuinely unstated, mark it `UNKNOWN` in the output rather than assuming it's safe.

## Procedure
1. **Build the handoff graph.** List every agent as a node. For each, record: untrusted-input? (yes/no/unknown), tool-capability tier, and the edge(s) to whatever it hands off to.
2. **Classify tool-capability tier per agent:**
   - `NONE` — no tool calls, text in/text out only.
   - `READ-ONLY` — tools that only retrieve information (search, lookup, read a file).
   - `STATE-CHANGING` — tools that write, send, execute, or modify something (send email/message, write to DB, run code, call a paid API, modify a ticket/record).
   - `IRREVERSIBLE/HIGH-STAKES` — state-changing tools whose effect is hard or impossible to undo, or that reaches third parties/the public (publish externally, financial transaction, delete data, send to a customer, deploy to production).
3. **Trace taint.** Any content that passes through, derives from, or is summarized/paraphrased from an untrusted-input agent is *tainted*, and taint propagates across every downstream hop by default — paraphrasing does not clear it. Taint is only cleared at a hop where the user has described a genuine structural boundary: e.g., content is parsed into a fixed, typed schema with no freeform field surviving, or a human reviews and re-authors the content before it continues. A classifier/filter that merely flags-or-passes freeform text does **not** clear taint — per the attack this skill is built around, a reworded payload evades perimeter classifiers and still carries its instructions in different words.
4. **Flag every hop where tainted content reaches a `STATE-CHANGING` or `IRREVERSIBLE/HIGH-STAKES` agent without a taint-clearing boundary on that specific edge.** A classifier that runs only at the original ingestion point (not on this edge, not re-validating the transformed content) does not count as clearing the edge — note this explicitly when the user describes exactly that setup, since it's the most common false sense of security.
5. **Rank findings by severity** = the tool tier of the agent being reached (`IRREVERSIBLE/HIGH-STAKES` > `STATE-CHANGING` > `READ-ONLY`, which is a Low note, not a Finding) combined with how many hops/transformations separate the tainted content from its origin (more hops = more plausible that wording changed enough to evade a classifier, so flag it, don't downgrade it).
6. **For each flagged gap, write a specific, implementable policy rule** naming the two agents/edge involved and what must change — never a generic "add more filtering." Good: "Ticketing-agent's `send_email` tool parameters must be populated only from the structured `{subject, body}` fields the schema-parser agent emits, never from the raw LLM output of the summarizer agent that touched the inbound email." Bad: "sanitize inputs better."
7. **Add a residual-risk note.** This audit evaluates the *described* architecture, not the actual running system — it cannot see whether a stated defense is really implemented as described, and it cannot substitute for replaying real attack payloads through the live pipeline. Say so every time, and recommend an attack-replay eval (seed it with paraphrased/domain-rewritten versions of a known injection, not just the literal string) as the next step before trusting the design.

## Output format
```
## Pipeline Map
| Agent | Untrusted input? | Tool tier | Hands off to | Content form |
|-------|-------------------|-----------|---------------|---------------|
| ...   | ...                | ...       | ...           | ...           |

## Findings
### Finding 1 — <Agent A> → <Agent B>
- Severity: CRITICAL | HIGH | MEDIUM (tool tier of the reached agent + hop distance)
- Risk: <why tainted content reaches this agent without a clearing boundary on this edge>
- Stated defense (if any) and why it doesn't close this edge: <...>
- Policy rule to close it: <specific, named rule>

(repeat per finding, ranked CRITICAL → MEDIUM; omit agents/edges with no finding)

## Residual Risk
<one paragraph: this is a design-time text review; recommend an attack-replay eval before trusting the design; name what could not be verified from the description alone>
```
If zero hops qualify as findings (every tainted-content edge into a state-changing agent has a genuine clearing boundary), say so explicitly and still include the Residual Risk note — don't manufacture a finding to seem thorough.

## Guardrails
- Never conclude a pipeline is "safe" or "secure" — this is a design review of a text description, not a test of running code; always frame findings as exposure to close, and the Residual Risk note is mandatory, not optional boilerplate.
- Never credit a perimeter/ingestion-point classifier with closing a downstream edge it doesn't run on — that is the exact failure mode (domain-camouflaged payloads evading single-point detectors) this skill exists to catch. If the user insists the classifier "covers everything downstream," flag that assumption explicitly rather than accepting it.
- Never recommend "remove the agent's tool access" as the fix when the workflow clearly needs that capability — give a scoped, workable policy rule instead (schema constraints, human-in-the-loop gate on the specific edge, structured-output requirement), or say plainly that the capability may be incompatible with the stated input trust level.
- Never invent details about agents, tools, or defenses the user didn't describe; mark anything genuinely unstated as `UNKNOWN` and flag it as a finding of its own ("tool access of Agent C is unstated — cannot clear this edge until known") rather than assuming the safer or more dangerous case.
- Do not treat this as equivalent to the actual taint-propagation middleware — the output is a prioritized list of gaps and policy rules for humans or engineers to implement, not a running defense.
