# Scenario 1 — Customer-support ticket triage bot (likely over-architected)

## Input

A solo founder is building a customer-support automation tool for a 12-person e-commerce company. They pasted this into the chat:

> "We're building a support bot. Right now the plan (copied from a CrewAI tutorial) is: an intake agent that reads the ticket and classifies it, a research agent that looks up the customer's order history and relevant docs, a drafting agent that writes the reply, and a QA agent that reviews the draft before it goes out. Four agents total, each with its own system prompt.
>
> Task: read an incoming support ticket, figure out what the customer needs, pull their order info, and draft a reply for a human to approve before sending.
>
> Constraints: this runs on each ticket as it comes in, so it needs to reply within about 10-15 seconds for the draft to be useful to our support team. We're a 2-person eng team with no agent tracing/observability set up yet. Token cost matters since we handle ~2,000 tickets/day. No compliance or team-ownership reason for the split — we just followed the tutorial's structure."

They ask: "Is this overkill, or does the 4-agent split make sense?"

## Expected output characteristics

- **Verdict line** present, in the required format, likely landing in **single-agent-with-tools** or low **hybrid** band given: low decomposability (classify → lookup → draft is one continuous chain, each step depends on the last), low-to-moderate specialization need (one agent with order-lookup and docs-lookup tools can hold this), real verification need (a QA review step has merit — human approval already exists downstream, though, which should be weighed), low parallelism value (steps are sequential, not parallelable), tight cost/latency budget (10-15s target plus 2,000 tickets/day cuts against multi-agent), low debugging capacity (no tracing set up — explicitly stated).
- **Criteria table** with all six rows, each scored and justified by specifics from the input (e.g. "Parallelism value: 0-1/5 — steps are a linear chain: classify, then look up, then draft; nothing here runs concurrently"), not generic text.
- **Multi-agent tax estimate** that references the stated 4-agent plan specifically (e.g., "~4 handoff points" or similar) and gives token/latency multiplier ranges labeled as estimates, flagging that at 2,000 tickets/day a 3-15x token multiplier is a real cost difference worth testing.
- **Non-performance factors** section either omitted or explicitly stating "none stated" — the user said there's no compliance/ownership reason, so the model must not invent one.
- Final paragraph should name debugging capacity and decomposability (or latency budget) as the criteria most pulling the recommendation toward single-agent, and note that collapsing intake+research+drafting into one agent with an explicit QA-review step (possibly handled by the existing human approval, or a lightweight second pass) would likely cut tokens/latency without losing much.

## Pass / fail criteria

- PASS if the verdict is single-agent-with-tools or low-hybrid, the six criteria are all scored with reasons tied to the specific input (sequential pipeline, no tracing, tight latency budget, no stated compliance reason), the tax estimate references the proposed 4-agent count, and no fabricated non-performance reason is introduced.
- FAIL if the verdict is "multi-agent justified," if any criterion score lacks a justification tied to this scenario's specifics, if the tax estimate presents numbers as measured rather than estimated, or if a compliance/ownership reason is invented despite the user stating there is none.
