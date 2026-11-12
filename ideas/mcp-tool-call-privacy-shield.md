# Shade: An In-Flight Privacy Shield for MCP Tool Calls

- **Status**: PROPOSED
- **Date**: 2026-11-11
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-11-tool-use-mcp-ecosystem.md · P7
- **Maturity verdict**: OPEN — GitHub searches ("MCP guardrail context", "MCP data leak guard", "MCP PII redaction proxy", "LLM tool call data leak prevention") returned zero relevant repos beyond the digest's own single find. No WebSearch evidence of a dedicated product or paper either. Genuine multi-channel search came up empty.
- **Format**: PROJECT — downgraded from BOTH on 2026-11-12: skill-synthesizer found 6+ close public equivalents already auditing MCP tool manifests for leak/poisoning risk pre-connection (OWASP Secure Agent Playbook's "MCP Server Security Review" play, Agensi's tool-definition security gate, PolicyLayer's `mcp-precheck`, claudskills.com's `mcp-risk-review`, Invariant Labs' `mcp-scan` poisoning auditor, plus several GitHub static scanners) — NOVELTY_FAIL per `.claude/rules/skill-format.md`. The runtime in-flight shield project remains unaffected (separate OPEN verdict).

## The Gap

HN's "In-memory privacy shield to prevent context leaks in MCP tools" (2026-10-20, 10 points, 1 comment, github.com/rohan-protocol/sdk) is one low-traction project with a single comment — early-stage, not integrated as a default anywhere. Verdict search across GitHub (four distinct query phrasings) and the web found no other attempt at all, confirming this is a genuinely open gap rather than one more entrant in a crowded field.

## The Project

A transparent interceptor — SDK middleware or a local sidecar proxy — sitting between the agent runtime and every outbound/inbound MCP tool call. It inspects call arguments and results for sensitive content (full conversation history inadvertently stuffed into a tool argument, a secret echoed back in a tool result, PII crossing a trust boundary into a third-party MCP server) and redacts or blocks before the call leaves the local process, or before the result re-enters model context. Policy is configurable per-field and per-server rather than a single global on/off switch.

## Tangible Impact

**Population**: Teams deploying agents with third-party MCP tool integrations inside regulated or sensitive environments — e.g. healthcare software teams wiring agents to EHR-adjacent MCP tools, fintech support teams wiring agents to ticketing/CRM MCP tools — where a leaked SSN, account number, or API key in a tool call is a reportable incident. This is a growing subset of the thousands of orgs drawing from the registry's 20,000–30,000 listed MCP servers as adoption climbs in regulated industries.
**Mechanism**: Today nothing inspects what actually crosses the MCP wire; sensitive values that slip into a tool argument or get echoed back in a result travel through third-party server logs and back into model context unexamined. The shield intercepts both directions against configurable PII/secret patterns and redacts or blocks before the leak completes, shrinking the leak surface from "every tool call, unexamined" to "only what policy explicitly allows through."
**Measure**: % of planted-secret test calls caught and redacted on a red-team harness; added latency per tool call; count of real incidents/near-misses logged post-deployment vs. a pre-deployment baseline period.

## Why Now

MCP's trust model keeps third-party server code opaque at call time, and as registry adoption climbs past 20,000+ servers (per P5) and regulated-industry orgs begin adopting MCP, the leak surface has only grown — while the one existing attempt (`rohan-protocol/sdk`) is too early and low-traction to rely on.

## Skill Angle

An "audit this server for leak risk before I connect it" skill: given a server's manifest/tool definitions, Claude reviews each tool's declared input/output schema for fields that could carry sensitive context (free-text blobs, unbounded "context" parameters, unbounded string outputs) and returns a per-tool risk rating plus suggested redaction rules to seed the project's runtime policy. This is a pre-deployment review task, distinct from the always-on runtime shield itself.

## MVP Sketch

2–4 weeks, 1–2 people: an SDK wrapper at the tool-call boundary implementing regex plus lightweight NER-based PII/secret detection on call arguments and results, with a configurable allow/redact/block policy, applied to 2–3 real MCP servers. Experiment: run a red-team set of 50 planted-secret prompts through agent flows with and without the shield, measuring catch rate and false-positive rate on benign calls.

## Risks & Open Questions

- A well-resourced MCP client vendor could ship this as a built-in feature, obsoleting a standalone project quickly.
- Argument-level redaction can break legitimate tool functionality if over-aggressive, degrading usability.
- Detection is inherently heuristic/pattern-based and will miss novel leak shapes.
- Adds latency to every tool call, a potentially hard sell for already-slow agent loops.
