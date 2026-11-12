# Published

One row per idea promoted all the way to a public writeup. Written and maintained by the `publisher` subagent (`.claude/agents/publisher.md`).

| Date | Slug | Hook | Topic | Has skill |
|------|------|------|-------|-----------|
| 2026-11-11 | agent-run-vcr | Deterministic record/diff/rewind for agent executions, framework-agnostic | Agentic AI & autonomous agents / Multi-agent architectures | no |
| 2026-11-11 | llm-span-cardinality-cost-governor | Drop-in truncation/sampling/classification policy so full prompt-capture tracing stops blowing up the observability bill | LLM evaluation & observability | no |
| 2026-11-12 | tiered-judge-calibration-pipeline | A three-tier deterministic+judge+human-gold pipeline that turns "how much do I trust this LLM judge" into a continuously measured number | LLM evaluation & observability | no |
| 2026-11-12 | tiered-guardrail-severity-composer | A declarative severity-tier composer and benchmark so fail-open/fail-closed guardrail logic stops being hand-rolled and unvalidated | AI safety & guardrails in production | no |
| 2026-11-12 | guardrail-accuracy-drift-monitor | Treats guardrail check accuracy itself as a monitored, drifting metric instead of discovering decay only after an incident | AI safety & guardrails in production | no |
| 2026-11-12 | ai-merge-trust-label-framework | A shared GitHub Action for trust-label-gated AI PR merges instead of every team re-deriving the same bespoke script | AI safety & guardrails in production | no |
| 2026-11-12 | agent-escalation-policy-engine | Scores proposed agent actions on ambiguity/reversibility/blast-radius to decide proceed/ask/refuse, with a labeled benchmark | Multi-agent architectures | yes |
| 2026-11-12 | voice-agent-speculative-tool-calling-middleware | Fires likely tool calls from partial transcripts to kill the multi-second dead-air gap in voice agents | Voice & multimodal agents | no |
| 2026-11-12 | voice-interruption-classification-policy-engine | Classifies barge-ins as correction/backchannel/noise/DTMF/timeout/escalation instead of a binary stop-or-don't toggle | Voice & multimodal agents | no |
| 2026-11-12 | lossless-context-state-manager | Context as diffable, restorable commits instead of irreversible lossy compaction | Context engineering & memory | no |
| 2026-11-12 | mcp-skill-trust-attestation-layer | A layered allow/warn/block policy gateway that vets MCP servers and skills together before an agent loads them, with an auditable decision ledger | Tool use & MCP ecosystem | no |
