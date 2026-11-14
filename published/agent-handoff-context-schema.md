# Handoff Envelope: a Typed Context Schema for Agent-to-Agent Handoffs

Three different builders shipped three different fixes for the same crack in multi-agent systems inside the same 30-day window — and none of them talked to each other. That's not a coincidence of timing. It's what happens when a real seam in the architecture has no agreed-upon fix, so everyone quietly reinvents one and ships it to Show HN hoping it sticks.

## The Gap

The seam is the handoff. When one agent finishes its piece of a pipeline and passes work to the next — researcher to writer, triage to specialist, planner to executor — what actually crosses that boundary today is either the full raw conversation transcript or an undocumented ad hoc dict. The receiving agent doesn't inherit decisions, it re-derives them, sometimes wrongly, sometimes by contradicting a call the upstream agent already made and rejected alternatives for.

In the 30 days leading up to this digest, three independent Show HN launches attacked exactly this: Open Envelope (52 points, 2026-05-28), TeamOlimpo (2026-06-07), and Agents-Collab.md (2026-05-29). Practitioners describe the current state bluntly — protocols are "interoperable at the protocol layer but amnesiac at the intelligence layer," and flatly, "nobody has one." A2A and ACP solved transport: agents can now find each other and exchange messages across frameworks. Nobody standardized what goes *inside* the envelope once it arrives.

A `gh search` turns up roughly eight handoff-protocol repos attempting a typed envelope, every one sitting at 0–3 stars — eugene001dayne/chain-thread, Lutren/agent-handoff-protocol, junkyard22/AHP, dakshjain-1616/Agent-Handoff-Protocol among them. OpenAI's own Agents SDK handoffs still pass raw conversation history rather than a structured decision/artifact schema. Fragmentary attempts, zero traction, no maintained spec — the textbook shape of a gap that's genuinely open, not just under-marketed.

This isn't a minor rough edge, either. Across annotated multi-agent failure taxonomies (Ema, Redis, orq.ai — 1,642 traces combined), inter-agent misalignment accounts for 32.3% of all recorded failures. The handoff is the single most failure-dense seam in the architecture, and it's running on prose.

## The Project

The centerpiece is the schema itself: a typed `Handoff` object with structured, JSON-Schema-validated fields for decisions made (and the alternatives rejected along the way), artifacts produced, errors encountered, open questions left for the receiver, and budget consumed. Everything else is in service of making that schema real and checkable rather than aspirational — adapters render the same envelope into OpenAI Agents SDK handoffs, LangGraph state, and CrewAI task contexts, so two agents built on different frameworks exchange a contract instead of each framework's native prose dump.

The part that keeps the schema honest is a conformance test suite: a handoff-fidelity eval that asks, concretely, "did the receiving agent actually get the decision history, or did it just get words?" That's the difference between a schema that's merely well-intentioned and one that's falsifiable.

Planned components: the schema spec itself (JSON Schema plus docs); a Python/TypeScript envelope library with validation and serialization; adapters for OpenAI Agents SDK, LangGraph, and CrewAI; and the fidelity eval, run head-to-head against raw-transcript handoffs.

## Tangible Impact

**Population**: Engineering teams running multi-agent pipelines that cross framework or team boundaries — the same cohort generating the failure data behind the 32.3% inter-agent-misalignment figure, and concretely the hundreds of teams represented by the three independent Show HN authors and the roughly eight zero-traction handoff repos, each of whom hand-rolled this same fix inside the last 30 days alone.

**Mechanism**: Today a handoff failure means the downstream agent re-derives or contradicts an upstream decision, and debugging it means a human reading two raw transcripts side by side looking for where the thread broke. A typed envelope makes the handoff inspectable instead — validate before sending, query after receiving — turning the most failure-dense seam in multi-agent systems from prose archaeology into a schema check.

**Measure**: (1) On the handoff-fidelity eval, downstream agents correctly answer at least 90% of questions about upstream decisions when given envelopes, against a measured baseline on raw transcripts. (2) Inter-agent misalignment failures in pilot teams' traces drop at least 30% after adoption. (3) At least two of the existing fragmentary-repo authors or Show HN builders adopt the shared spec instead of maintaining their own within 90 days.

## Why Now

Three independent reinventions inside a single 30-day window is about as clean a signal of proven, unmet demand as this kind of research turns up — the duct tape is being applied faster than anyone can standardize it, and no attempt has won yet. A2A and ACP shipping solid transport-layer interoperability makes the missing content layer newly conspicuous by contrast: the pipes work, the payload format still doesn't exist. And OpenAI's Agents SDK — passing raw history through its handoff primitive today — is a mainstream, well-used integration point ripe for someone to improve on rather than compete against from scratch.

## Try It

A companion Claude Code skill, [`skills/agent-handoff-context-schema/`](../skills/agent-handoff-context-schema/), is already written: *"Drafts a typed 'Handoff Envelope' schema (decisions made, rejected alternatives, artifacts, errors, open questions, budget spent) for a specific multi-agent pipeline, plus a validation checklist. Use when someone describes a pipeline where one AI agent hands work to another (same framework or across frameworks) and today that handoff is a raw text dump or ad hoc object, and they want a structured contract instead."*

To use it: drop the `skills/agent-handoff-context-schema/` folder into `~/.claude/skills/` if you're running Claude Code, and describe your pipeline — the agent roles involved and what each one currently hands the next. No Claude Code install? Paste the skill's `README.md` into any AI chat tool as a prompt template; it's written to stand on its own.

Unlike the full project, the skill doesn't require you to adopt a library or wait for ecosystem buy-in — it drafts a tailored envelope schema and validation checklist for your pipeline in one shot, useful the moment you can describe what your agents hand each other today.

## The Honest Risks

The strongest reason this might already be solved by the time anyone ships it: OpenAI or the A2A project itself could add a typed context schema to its handoff primitives and absorb the whole idea overnight. There's also a real chance schemas are inherently lossy for this use case — raw transcripts sometimes carry nuance a typed envelope strips out, and the fidelity eval could show raw history actually wins on some tasks. And standards need adopters: eight zero-star repos already suggest that everyone building a handoff schema wants *their* schema specifically, which is not a promising precedent for a ninth. Filling the envelope reliably also depends on the upstream agent accurately introspecting its own decisions — itself an LLM task that can fail quietly.

Surfaced from `research/2026-06-10-multi-agent-architectures.md`, pattern `P1`.
