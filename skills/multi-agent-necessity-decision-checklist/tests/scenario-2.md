# Scenario 2 — Multi-jurisdiction compliance research + contract-redline pipeline (plausibly multi-agent, with a stated non-performance factor)

## Input

A legal-tech startup's engineer pastes this:

> "We're building a tool that takes a vendor contract and (a) researches current regulatory requirements in up to 6 different jurisdictions in parallel — each jurisdiction has totally different statutes, citation formats, and source databases — and (b) produces redline suggestions against each jurisdiction's requirements, which then get reviewed by a human lawyer per jurisdiction before anything is sent to a client.
>
> We're planning one research agent per jurisdiction (6 of them, each scoped to that jurisdiction's law and sources) plus one drafting agent that takes all 6 research outputs and produces the consolidated redline doc. No single-agent version of this has worked well in our early tests — when one agent tried to hold all 6 jurisdictions' context at once, it started mixing up citation formats and requirements across jurisdictions.
>
> Constraints: this runs as an overnight batch job per contract, so latency isn't tight — minutes to an hour is fine. Cost budget is generous since each contract review replaces hours of paralegal time. We're a 9-person eng team and already have LangSmith tracing wired up across our other multi-agent pipelines. One more thing: our legal/compliance team specifically wants each jurisdiction's research kept in an isolated audit trail for liability reasons — that's a firm requirement, not just a technical preference."

They ask: "Does a 6-researcher-plus-1-drafter split make sense here, or are we still over-architected?"

## Expected output characteristics

- **Verdict line** should land in **multi-agent justified** (high total), driven by: high decomposability (6 genuinely independent jurisdiction research tasks), high specialization need (different statutes/citation formats/sources per jurisdiction, explicitly stated), real parallelism value (6 jurisdictions can research concurrently), generous cost/latency budget (explicitly batch, minutes-to-hour, generous cost), and decent debugging capacity (LangSmith tracing already wired up, explicitly stated). Verification/critique need is present (human lawyer review per jurisdiction already downstream) but should be scored based on whether an independent critique agent adds beyond that human step, not assumed automatically high.
- **Criteria table** ties each score to the specific facts given (e.g., citing the stated context-mixing failure from their early single-agent test as evidence for specialization need, not a generic statement).
- **Multi-agent tax estimate** for a 7-agent system (6 researchers + 1 drafter), noting the token/latency multiplier is a real cost but explicitly weighed against the generous stated budget rather than treated as a blocker.
- **Non-performance factors** section must appear and explicitly surface the compliance/audit-trail requirement, stated separately from the numeric score, with a note that this alone could justify the per-jurisdiction split even independent of the technical score.
- Final paragraph should name decomposability/specialization and the compliance requirement as the two strongest drivers, and should not recommend collapsing the jurisdictions into one agent given the team's own stated evidence (context-mixing failure) against it.

## Pass / fail criteria

- PASS if the verdict is multi-agent justified, the compliance/audit-trail requirement is surfaced in its own separate section (not folded into the score), the criteria table references the scenario's specific evidence (context-mixing failure, tracing already in place, batch budget), and the tax estimate is framed as an estimate against a stated generous budget rather than a reason to recommend single-agent.
- FAIL if the model recommends single-agent-with-tools or hybrid despite this evidence, if it folds the compliance requirement into the numeric score instead of listing it separately, if it ignores the team's own stated test result (context mixing) when scoring specialization need, or if debugging capacity is scored low despite LangSmith tracing being explicitly stated as already in place.
