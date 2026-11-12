# Outbound Gate: A Generic Tool-Call Quality Guardrail for Agent Outreach

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-12-ai-safety-and-guardrails-in-production.md · P6
- **Maturity verdict**: PARTIAL — MailDignity (maildignity.com) is the only tool found that gates outbound AI-drafted outreach at the API/MCP tool-call layer for tone/slop rather than deliverability; it is a solo, unvalidated Show HN launch (5 points, no comment thread) scoped to email. Deliverability-focused competitors (Apollo, Landbase, Coldreach, FirstSales, Salesflow) address infrastructure/throttling/spam-filter avoidance, not AI-generated content quality at the tool-call control point.
- **Format**: PROJECT

## The Gap
A solo Show HN launch ("I made a guardrail against AI outreach slop (API/MCP)", harryden, 2026-11-07) is the only tool addressing content-quality gating at the point an agent actually sends an outbound action, and it is scoped narrowly to email. No channel-agnostic version exists: as agents increasingly take outbound actions across Slack, support tickets, CRM notes, and social replies, there is no shared control point catching low-quality generated content before it is sent, regardless of which channel's API the agent calls.

## The Project
A channel-agnostic MCP/tool-call-layer middleware that intercepts any outbound agent action — email send, Slack or Discord message, support-ticket reply, social post, CRM note — before it reaches the destination API, and scores it against a configurable rubric (generic phrasing, templated-personalization failure, hallucinated specifics, tone/brand-voice mismatch) using a cheap classifier, blocking or flagging low-quality outbound actions. The differentiator from MailDignity is being channel-agnostic at the generic tool-call boundary rather than tied to one email API, with a per-deployment configurable brand-voice rubric and a full audit trail of blocked vs. allowed outbound actions.

## Tangible Impact
**Population**: small-to-mid-size companies (sales teams, support organizations, dev-tool companies) deploying AI agents to autonomously send outbound communications at scale — a fast-growing population given the 2026 rise of AI SDR and AI-support-agent tooling — specifically teams without a dedicated trust-safety function to manually review every agent-drafted outbound message before send.
**Mechanism**: without a quality gate at the point of action, agents degrade brand reputation and recipient trust by sending generic, repetitive, or subtly wrong outbound content at volume — the "AI slop" complaint the original Show HN launch named. A channel-agnostic gate at the tool-call layer catches this before send, independent of which API or channel the agent uses, giving a team one control point instead of a per-channel bolt-on they would otherwise have to build separately for each tool.
**Measure**: reduction in recipient complaint, unsubscribe, or report rate on gated vs. ungated outbound batches; precision of the gate (percentage of blocked or flagged actions a human reviewer agrees were genuinely low-quality); time to add a new outbound channel to the gate (should stay low given the channel-agnostic design, versus building a bespoke per-channel filter).

## Why Now
MCP's 2026 standardization of tool-call interception points makes a generic middleware gate newly cheap to build once and apply across channels; the MailDignity launch (November 2026) validates demand for exactly this control point but leaves the channel-agnostic, brand-voice-configurable version unbuilt.

## MVP Sketch
An MCP proxy or middleware that wraps common outbound tool calls (email send, Slack post, ticket reply) across two or three popular agent frameworks, a lightweight scoring model (a few-shot classifier or small fine-tuned model) for genericness, slop, and tone mismatch against a configurable brand rubric, and a block/flag/allow decision with full logging. Experiment: run a batch of real agent-drafted outreach messages through the gate and measure agreement between the gate's decisions and human quality judgments on the same batch.

## Risks & Open Questions
- MailDignity or a well-funded sales-tooling vendor could generalize to multi-channel first, closing this exact gap quickly.
- Quality/slop scoring is inherently subjective and likely needs per-customer calibration, raising onboarding cost and risking inconsistent judgments across deployments.
- False blocks on legitimate agent output could frustrate adoption more than the slop problem it is meant to solve, especially early before the rubric is well-calibrated.
- Teams may prefer to fix outbound quality upstream (better prompts/fine-tuning) rather than add a downstream gate, reducing the addressable need.
