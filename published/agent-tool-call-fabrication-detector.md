# Did It Actually Happen: A Tool-Call Fabrication and Context-Corruption Detector for Production Agents

Your support agent says it issued the refund. Your coding agent says the test suite passed. Your ops agent says it sent the notification. None of that means any of it actually happened — and right now, almost nothing in production agent stacks can tell the difference between "the tool genuinely ran" and "the model generated a plausible sentence describing a tool running."

## The Gap

A vendor write-up cited in the source research calls fabricated tool results "a documented failure across major frameworks" — agents skipping real tool execution and returning a convincing-looking result anyway. A separate write-up in the same research describes "context corruption that happened three turns ago and silently propagated forward through every subsequent decision," with nothing resembling a crash to alert anyone. A separately cited, flagged-as-unverified figure claims tool-call errors account for 42% of pipeline failures that reach end users — uncertain as a precise number, but consistent with this already being a majority-scale production problem, not an edge case.

The named observability players in the same sources — Langfuse, Arize Phoenix, Braintrust, LangSmith, Datadog LLM Observability — all capture traces well. None of them, per the sources themselves, automates a distinct "this looks fabricated" flag. Catching it today means a human reading trace logs by hand, after something has already gone wrong downstream.

## The Project

The fix is a cross-verification layer that sits between an agent and its highest-stakes tools. After every claimed tool call, it independently re-queries the tool's own system-of-record confirmation endpoint — not the agent's self-report — and flags any mismatch between what the agent claims happened and what the system of record says actually happened. For context corruption specifically, it periodically probes the agent's working context against a small set of ground-truth facts injected early in the session, catching divergence before it compounds silently across turns.

The core components: per-tool confirmation-endpoint adapters, starting with the two highest-stakes categories — email-send and payment/refund; a claim-vs-actual diff engine; a periodic context-integrity probe; and an alert/report formatter that names the specific mismatch rather than just raising a generic warning.

Research backing the detection approach is already live: a NeurIPS 2026 paper, "When Tools Fail, Agents Fabricate," studies this exact failure mode, and a companion arXiv preprint reports a rule-based detector with high recall on one extraction workload. What doesn't exist yet is the generalized, cross-tool, shippable version — this project is that.

## Tangible Impact

**Population**: Teams running autonomous or semi-autonomous agents that take real-world actions with financial or operational consequences — support agents issuing refunds, coding agents claiming to have run a test suite, ops agents claiming to have sent a notification. The cited (unverified-methodology) 42% figure on tool-call errors reaching end users signals this is already a majority-scale production issue even allowing for the number's uncertainty.

**Mechanism**: Without this layer, a fabricated "refund issued" or "tests passed" claim propagates silently until a customer complains or a bug ships days later — because nothing in current observability distinguishes "tool genuinely executed" from "model generated plausible text describing a tool execution." A verification layer that checks the claimed outcome against the real system of record catches this at the moment it happens, not days later via a support ticket.

**Measure**: (1) detection latency for a seeded fabrication test case — seconds via the detector versus the current days-scale "discovered via support ticket" path; (2) false-fabrication-flag rate on known-good production traces (precision); (3) fraction of a labeled fabrication-incident corpus the detector actually catches (recall), extending the "high recall on one workload" result from the cited arXiv preprint across more tool types.

## Why Now

OTel GenAI tracing is now mature enough that per-call tool-execution metadata is captured without custom instrumentation, and the NeurIPS 2026 paper plus its companion detector preprint show the detection approach is already validated on at least one real workload. Building the generalized, cross-tool, shippable version doesn't require a future model capability — it only requires wiring existing traces to existing tool confirmation APIs, which makes this newly tractable rather than newly necessary.

## Try It

A companion Claude Code skill, [`skills/agent-tool-call-fabrication-detector/`](../skills/agent-tool-call-fabrication-detector/), covers the manual-diagnostic half of this idea: *"Reviews a pasted agent execution trace or transcript for signs that a tool call was fabricated (the model generated a plausible result without the tool actually running) or that context corruption from an earlier turn silently propagated forward. Use when a production agent's claimed action (refund issued, email sent, tests passed, PR merged) is in doubt and you need a fast triage before you go check the real system of record."*

Give it a pasted trace excerpt — the tool call, its parameters, the raw response, and the agent's claim built on top of it — and it runs six fabrication checks (schema conformance, timing plausibility, missing identifiers, hedge/confidence mismatch, parameter-result consistency, templated repetition) and scores each call LIKELY GENUINE / SUSPICIOUS / LIKELY FABRICATED, naming the real-world source to go verify against. To use it: drop the `skills/agent-tool-call-fabrication-detector/` folder into `~/.claude/skills/` for Claude Code, or paste the prompt template from its `README.md` into any AI chat tool.

It is deliberately limited to that one-off, text-only review — it has no live connection to any tracing platform or tool API. The always-on, cross-verified production middleware described above is separate infrastructure; the skill is the fast manual first pass you run when something already looks off, not a replacement for building the real thing.

## Risks & Open Questions

- Per-tool cross-verification doesn't generalize cheaply — each new tool type needs its own confirmation-source integration, which risks a long tail that never gets finished.
- Distinguishing "model hallucinated a result" from "tool genuinely returned something unexpected" may need ground truth that isn't always available outside seeded test cases.
- This sits conceptually close to this pipeline's own "Quiet Break" (aggregate metric-drift detection) and "Tell the Model" (failure-surfacing middleware) ideas, and needs to stay clearly differentiated as catching successful-*looking* fabrication, not aggregate drift or genuine tool failures.
- Legitimately fast or edge-case tool responses could trigger false positives if the confirmation check isn't tuned to each tool's real latency and response profile.

Surfaced from `research/2026-11-13-agentic-ai-autonomous-agents-ii.md`, pattern `P5`.
