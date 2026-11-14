# Scenario 1 — Customer support escalation triage, committed to LangGraph

## Input (as a user would paste it)

> We're building a multi-agent system for customer support ticket triage. A
> "classifier" agent reads the incoming ticket and tags it (billing,
> technical, account-security). Depending on the tag, it routes to one of
> three specialist agents (billing-agent, tech-agent, security-agent) that
> draft a response. If the security-agent flags the ticket as a real
> security incident, it needs to loop back and re-route to a human-escalation
> step instead of auto-responding. Otherwise the specialist's draft goes to
> a final "QA agent" that checks tone/policy compliance before sending. We
> need to be able to show auditors exactly which path a given ticket took,
> since security-flagged tickets are subject to compliance review. We're
> already committed to LangGraph.
>
> Fixed order or dynamic routing: dynamic — the classifier's tag determines
> the next step, and the security flag can force a loop back.
> Authority structure: no single agent has final say over all others, but
> each step is a clear handoff, not a negotiation — the classifier doesn't
> negotiate with the specialist, it just routes.
> Parallel sub-tasks needed: no, each ticket follows one path at a time.
> Traceability needs: high — compliance review requires knowing exactly
> which path a ticket took.
> Framework: LangGraph.

## Expected output characteristics

- **Recommendation**: Graph (not Workflow, not Swarm, not Hierarchical) — the dynamic routing by classifier tag, the conditional loop-back on security flag, and the high traceability requirement all point to Graph. A pass must name Graph specifically and must NOT recommend Swarm (no peer negotiation present) or plain Workflow (routing isn't fixed-sequence) or Hierarchical-Supervisor (no single agent directs/owns the outcome).
- **Criteria table**: must address all five criteria with task-specific answers — in particular, must correctly identify "dynamic routing + conditional loop-back" as pulling toward Graph, and "high traceability" as reinforcing Graph over Swarm.
- **Conflicts noted**: should note that authority structure is ambiguous (handoff-based, not a clear negotiation OR single-supervisor model) but should not let that override the clear signal from determinism + traceability — a pass correctly resolves this toward Graph rather than getting stuck.
- **Framework mapping**: must map Graph → LangGraph's `StateGraph` with conditional edges (per the SKILL.md's translation table), not a generic LangGraph answer.
- **Biggest risk**: should mention something like growing branch complexity or state management overhead as the graph grows, not a generic disclaimer.
- **Fail conditions**: recommending two patterns as equally valid without naming a tie-breaker; skipping the criteria table; omitting the framework mapping when LangGraph was explicitly named; exceeding ~300 words substantially; inventing a LangGraph primitive not in the mapping table.
