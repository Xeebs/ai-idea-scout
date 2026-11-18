# Contract Layer: A Declarative Orchestration Spec and Static Validator for Multi-Agent Pipelines

A three-agent pipeline ships fine in the demo. Six weeks later, in production, agent B quietly receives a field agent A doesn't always produce — and nobody finds out until a downstream record is wrong. Nothing crashed. Nothing alerted. The pipeline just silently did the wrong thing, because the "contract" between agent A and agent B only ever existed as an assumption buried in two different prompts that nobody checked against each other.

## The Gap

Three independent 2026 analysis pieces converge on the same diagnosis from different angles. talvinder.com's "Orchestration Specs Like Symphony Are the Missing Layer for Multi-Agent Engineering" names the missing piece outright. ice-ice-bear.github.io's "Why Multi-Agent Orchestration Doesn't Work Well" and dev.to's "Multi-agent orchestration is just hope masquerading as architecture" both argue, independently, that today's orchestration failures aren't really about weak individual agents — they're about hand-coded connections between agents compounding failures with nothing checkable in between.

The tell that this is a real gap and not just three people venting: OpenAI thought it was worth solving, and shipped Symphony to prove it — but only for one narrow case. Symphony is a real, Apache 2.0, openai.com-announced spec, and it works, but it's a Linear-only adapter: poll an issue tracker, claim an issue, run a per-issue coding-agent session. A general search for a declarative, framework-agnostic contract layer for arbitrary agent-to-agent input/output/failure-handling — the equivalent of what OpenAPI does for REST or a type system does for function calls — turned up no existing implementation. Everyone agrees the layer should exist. Only one vendor built a slice of it, and that slice doesn't generalize.

## The Project

The core idea: a declarative spec format plus a static validator for multi-agent pipelines. Each agent node declares, in a small DSL (YAML or a typed Python builder), its expected input schema, its guaranteed output schema, and its failure-handling policy — retry-with-backoff, escalate-to-human, abort-pipeline, or fall-back-to-default. Before the pipeline ever runs, a validator checks that every node's declared inputs are actually satisfiable by its upstream nodes' declared outputs, on every declared path — including the failure paths, not just the happy path — and fails the build with a specific, located error if they aren't.

That's the centerpiece, deliberately: this isn't a wrapper feature bolted onto an existing orchestration framework, it's a contract layer any framework's runtime could be made to enforce. The planned pieces are a spec DSL and parser, a static compatibility checker that matches schemas across every edge (happy-path and failure-path alike), a CI-runnable validation command, a thin runtime adapter for one framework first — LangGraph, since it's where the richest existing multi-agent tooling already lives — that enforces the contract live and rejects a non-conforming handoff before it executes, and a migration guide for retrofitting a pipeline that already exists.

## Tangible Impact

**Population**: Engineering teams running hand-coded multi-agent pipelines on LangGraph, CrewAI, or AutoGen in production — the same population the three critique pieces are writing for, and the one OpenAI built Symphony to serve in its one narrow case. Broadly, any team past the demo stage, where "agent B assumed a field agent A doesn't always produce" has already caused or nearly caused a production incident.

**Mechanism**: Today, the contract between two agents in a pipeline exists only as implicit assumptions buried in each agent's prompt and code — nothing checks that agent A's output under a failure or edge-case path still satisfies what agent B expects, so a mismatch surfaces as a silent downstream failure discovered in production, sometimes much later than the deploy that introduced it. A declarative, statically-checked spec moves that same check to build/CI time, turning an undetected runtime compounding failure into a specific, located build error the person who introduced it sees immediately.

**Measure**: (1) Count of production incidents attributable to an agent-to-agent contract mismatch — a downstream agent receiving data it didn't expect, including on a failure path — before vs. after adoption on a pilot team's pipeline. (2) Percentage of pipeline changes that introduce a contract violation caught at CI time vs. discovered only in production. (3) Time for a new engineer to understand what a given agent in an existing pipeline actually guarantees, with the declared spec available vs. having to read the implementation.

## Try It

A companion Claude Code skill, [`skills/multiagent-declarative-orchestration-spec/`](../skills/multiagent-declarative-orchestration-spec/), is already written — it covers the drafting half of this idea, not the validator/runtime: *"Drafts a declarative contract spec (per-node input/output schemas plus per-edge failure-handling policy) for an existing multi-agent pipeline described in prose or code, and flags every handoff the description leaves ambiguous. Use when someone describes a LangGraph/CrewAI/AutoGen/hand-coded multi-agent pipeline and wants its implicit contracts made explicit and checkable."*

To use it: drop the `skills/multiagent-declarative-orchestration-spec/` folder into `~/.claude/skills/` if you're running Claude Code, then describe your pipeline — which agents exist, what each consumes and produces, and any failure handling you already have, in prose or a code excerpt. No Claude Code install? Paste the skill's `README.md` into any AI chat tool as a prompt template; it's written to stand alone. Either way, you get back a structured YAML spec of your pipeline's nodes and edges, a compatibility check across every edge (including failure paths), and — just as usefully — an explicit list of every place your own description left something ambiguous, phrased as a specific question rather than a vague "needs more detail" note.

## The Honest Risks

The strongest reason this might not be worth building independently: Symphony could just generalize. OpenAI has already shown it's willing to invest here, and if the next release of Symphony stops being Linear-only, an independent effort racing to adoption could lose to the incumbent before it gets traction.

There's also a real design tension baked into the premise. A spec that's too rigid for genuinely dynamic agent behavior — an agent whose output shape depends on what it discovers mid-task — could force teams into brittle schemas that don't match how LLM agents actually behave. Getting the DSL's expressiveness right for conditional and variable outputs is the hard design problem here, not the validator logic itself, and it's unsolved by design in the MVP sketch.

And adoption has its own friction: hand-authoring a spec duplicates information that's already implicit in the pipeline's code, which teams may simply resist doing. The real unlock — statically analyzing a team's existing LangGraph/CrewAI source to auto-derive the spec instead of requiring someone to write it by hand — is a materially larger build than the MVP and isn't in scope yet. Until that exists, the spec's value has to outweigh the cost of writing it from scratch, which is a harder sell than it sounds.

Surfaced from `research/2026-11-13-agentic-ai-autonomous-agents.md`, pattern `P7`.
