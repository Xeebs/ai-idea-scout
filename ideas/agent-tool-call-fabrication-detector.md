# Did It Actually Happen: A Tool-Call Fabrication and Context-Corruption Detector for Production Agents

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-13-agentic-ai-autonomous-agents-ii.md · P5
- **Maturity verdict**: PARTIAL — research is live (a NeurIPS 2026 paper, "When Tools Fail, Agents Fabricate," and an arXiv preprint reporting a rule-based detector with high recall on one extraction workload) and narrow OSS attempts exist, but general observability platforms (Galileo, Langfuse, Arize) only capture traces and don't automate fabrication detection as a distinct flag.
- **Format**: BOTH — the project is an always-on cross-verification middleware; reviewing a pasted trace for fabrication red flags is a genuinely separable one-off diagnostic task.
- **Data Sources**: CONNECTED — reads the agent's own OTel/Langfuse execution traces (a mature, already-standard instrumentation layer) and, per integrated tool, cross-verifies a claimed action against the actual system-of-record's own confirmation API (e.g., an email provider's send log, a payment processor's transaction log); the cross-verification connector is tool-specific and would need to be built per integration, starting with 2-3 common high-stakes tools.

## The Gap
A vendor write-up cited in the digest calls fabricated tool results "a documented failure across major frameworks" — agents skipping actual tool execution and returning a plausible-looking result anyway — and another describes "context corruption that happened three turns ago and silently propagated forward through every subsequent decision," with nothing resembling a crash to alert anyone. A separately cited (flagged-unverified) figure claims tool-call errors account for 42% of pipeline failures reaching end users. Named observability tools in the same sources capture traces but detection of silent fabrication is still manual trace review, not an automated flag.

## The Project
A cross-verification middleware that sits between an agent and its highest-stakes tools: after every claimed tool call, it independently re-queries the tool's own system-of-record confirmation endpoint (not the agent's self-report) and flags any mismatch between what the agent claims happened and what actually happened. For context corruption specifically, it periodically probes the agent's working context against a small set of ground-truth facts injected early in the session and flags divergence before it compounds across turns.

Components: per-tool confirmation-endpoint adapters (starting with email-send and payment/refund); claim-vs-actual diff engine; periodic context-integrity probe; alert/report formatter naming the specific mismatch.

## Tangible Impact
**Population**: Teams running autonomous or semi-autonomous agents that take real-world actions with financial or operational consequences — support agents issuing refunds, coding agents claiming to have run a test suite, ops agents claiming to have sent a notification. The digest's cited (unverified-methodology) 42% figure on tool-call errors reaching end users signals this is already a majority-scale production issue even allowing for the number's uncertainty.
**Mechanism**: Without this, a fabricated "refund issued" or "tests passed" claim propagates silently until a customer complains or a bug ships days later, because nothing in current observability distinguishes "tool genuinely executed" from "model generated plausible text describing a tool execution." A verification layer that checks the claimed outcome against the actual system-of-record catches this at the moment it happens.
**Measure**: (1) detection latency for a seeded fabrication test case — seconds via the detector vs. the current days-scale "discovered via support ticket" path; (2) false-fabrication-flag rate on known-good production traces (precision); (3) fraction of a labeled fabrication-incident corpus the detector actually catches (recall), extending the "high recall on one workload" result cited in the digest's arXiv preprint across more tool types.

## Why Now
OTel GenAI tracing is now mature enough that per-call tool-execution metadata is captured without custom instrumentation, and the NeurIPS 2026 "When Tools Fail, Agents Fabricate" paper plus its companion rule-based-detector preprint show the detection approach is already validated on at least one real workload. Building the generalized, cross-tool, shippable version is newly tractable — it does not require a future model capability, only wiring existing traces to existing tool confirmation APIs.

## Skill Angle
Given a pasted agent trace or transcript excerpt (the tool call plus the agent's claimed result), Claude reviews it for known fabrication red flags — a result that doesn't match the tool's actual return schema, suspiciously fast turnaround for a known-slow operation, or hedging/confidence patterns documented in the NeurIPS paper — and flags a likely-fabricated call for human review. This is a one-off diagnostic review, distinct from the project's always-on, cross-verified production middleware.

## MVP Sketch
Pick two high-stakes tool types with their own confirmation endpoint (email-send via a real provider API, a mocked payment/refund API); build a middleware wrapper that re-queries each provider's own confirmation log after every claimed call and flags mismatches; run against a seeded test set of genuine vs. deliberately-fabricated traces (produced by prompting a model to skip execution and fabricate a result) and measure precision/recall. 3-4 weeks, 1-2 people.

## Risks & Open Questions
- Per-tool cross-verification doesn't generalize cheaply — each new tool type needs its own confirmation-source integration, risking a never-finished long tail.
- Distinguishing "model hallucinated a result" from "tool genuinely returned something unexpected" may need ground truth that isn't always available outside the seeded test cases.
- Conceptually adjacent to this pipeline's existing "Quiet Break" (aggregate metric-drift detection) and "Tell the Model" (failure-surfacing middleware) ideas — needs to stay clearly differentiated as catching successful-looking fabrication, not aggregate drift or genuine tool failures.
- Legitimately fast or edge-case tool responses could trigger false positives if the confirmation check isn't tuned per tool's real latency/response profile.
