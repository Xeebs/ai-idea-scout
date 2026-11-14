# Boundary Diff: Context-Loss Diffing at Agent-to-Agent Handoffs

- **Status**: EXPLORING
- **Date**: 2026-11-14
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-14-multi-agent-architectures.md · P1
- **Maturity verdict**: PARTIAL — mature, maintained observability products (LangSmith, Langfuse, Arize Phoenix) already cover general cross-agent tracing, and OpenTelemetry GenAI conventions now define `invoke_agent`/handoff spans. But a 2026 dev.to evaluation of "every AI agent observability tool on the market" concludes none of them do boundary-level context diffing — they show *that* a handoff happened, not *what context was lost* at it. The specific diffing capability is a DIY gap inside an otherwise saturated general-tracing market.
- **Format**: BOTH — continuous payload capture and diffing across live handoffs is PROJECT-shaped infrastructure; diffing two pasted payloads from a single suspect handoff is a separable one-shot analysis task.
- **Data Sources**: CONNECTED (project) — reads the sender's full output payload and the receiver's actual input payload at each handoff via the OTel GenAI spans major frameworks already emit (LangGraph node transitions, CrewAI task delegation, AutoGen/AG2 group-chat turns); this is a mature, already-adopted instrumentation substrate this project adds a content-diff layer on top of, not a from-scratch connector. MANUAL (skill) — user pastes the sender's full output text and the receiver's actual received input text for one specific handoff.

## The Gap
Practitioner write-ups (fiddler.ai, atlan.com, qawerk.com) report teams saying ordinary logging "doesn't capture why an agent handed off, what context was dropped at the boundary, or whether guardrail state transferred." One cited example has Agent B emitting a 14,000-token context while Agent C's input is silently truncated to 8,000 tokens with no visibility into the loss — a failure mode that trips no error, no crash, and no heartbeat alert, because nothing is actually broken in a liveness sense; the content is just gone. Existing tracing tools show the handoff occurred; none diff what crossed it against what was sent.

## The Project
An instrumentation layer that captures the exact payload an agent emits and the exact payload the next agent actually receives at every handoff, then diffs them: byte/token-count delta, truncation markers, field-level drops (for structured payloads), and transformation flags (reformatting, summarization, redaction) applied in between. On a flagged handoff, a report shows precisely what was lost — not just that a handoff happened — so a silent context-loss bug (a truncation limit, a lossy serializer, a dropped tool-result field) is visible the moment it starts happening instead of surfacing days later as an unexplained downstream quality drop.

Components: a payload-capture middleware wrapping each framework's handoff point; a diff engine (size delta, structured-field diff, truncation/transformation classifier); a threshold-based flagging rule (e.g. >15% content loss with no corresponding summarization tag); a report view linking a flagged handoff back to the specific run/trace it occurred in.

## Tangible Impact
**Population**: Engineering teams operating production multi-agent pipelines on LangGraph, CrewAI, or AutoGen/AG2 that pass large context packets between agents (research-synthesis chains, document-processing pipelines, support-triage handoffs) — the same population already using Langfuse/LangSmith/Arize Phoenix for general tracing, per those products' own multi-agent docs, but left without visibility into this specific failure class.
**Mechanism**: Today, silent truncation or field loss at a handoff produces no alert — it only becomes visible when a downstream agent's output quality degrades and an engineer manually reconstructs what each agent actually saw. Automated payload diffing surfaces the loss at the moment it happens, with the specific content and the specific boundary named, replacing a reactive quality investigation with a proactive flag.
**Measure**: (1) percentage of handoffs with unflagged, unintentional content loss above a declared threshold, detected automatically vs. previously invisible, on a pilot team's pipeline; (2) time from a downstream quality complaint to identified root-cause boundary, before vs. after; (3) reduction in "missing context" hallucination incidents traceable to an upstream truncation, measured on a held-out incident log.

## Why Now
OTel GenAI semantic conventions matured in 2026 and major frameworks now emit standardized handoff spans carrying actual payload content, not just metadata — the raw substrate for content diffing exists today in a way bespoke per-framework logging didn't support a year ago, which is why practitioners are still hand-rolling "wish I had this" workarounds instead of reaching for a shipped tool.

## Skill Angle
Given a pasted sender-output payload and the corresponding receiver-input payload from one suspect handoff, produce a diff report: what was dropped, truncated, or transformed between the two, with a severity flag if the loss looks unintentional (e.g., a mid-sentence cutoff, a missing structured field) versus a deliberate summarization. Useful immediately on a single suspected bad handoff, before any continuous instrumentation is installed.

## MVP Sketch
Wrap one framework's handoff points (start with LangGraph) to capture sender-output and receiver-input payloads for every edge; build a diff engine computing size delta and a truncation/field-drop classifier; test by running a known pipeline with an injected truncation limit on one edge and confirming the tool flags exactly that edge with the correct loss description, versus a control run reading raw logs manually. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- Overlaps conceptually with this repo's existing "Breadcrumb" idea (correlation-ID + heartbeat tracing to localize *which* handoff broke a run) — this project is deliberately complementary, not duplicative: Breadcrumb answers "which handoff failed and when" for crashing/divergent runs, this answers "what content was silently lost" even on a run that never crashes. The two could eventually share an instrumentation layer, but the diffing logic and the failure signal they detect are distinct.
- Mature observability vendors (Langfuse, Arize Phoenix) could ship this as a feature quickly once named explicitly, since they already capture the payload content this needs.
- Storing full payload content at every handoff for diffing has real storage/privacy cost at scale — needs a sampling or redaction strategy, not naive full capture.
- Distinguishing "unintentional loss" from "deliberate summarization" reliably (without false-positiving on every legitimate compression step) is the hardest design problem, not the diffing mechanics themselves.
