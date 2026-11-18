# Reference Rail: A Packaged Starter Kit for the Security-Specialized Guardrail Model Architecture

On November 1st, 2026, a developer opened an issue against their own project, `LMA1980/jero-manager`, titled "Epic: [Arch Evaluation] Security, Guardrail, Prompt-Injection & Cyber-Defense Architectures." They weren't reporting a bug. They were doing something that should be unnecessary in 2026: starting a from-scratch research project to figure out how to structure guardrails around an LLM, because nothing they'd found told them how. The pattern they needed already exists, built, open-source, and running in production somewhere else. They just never found it.

## The Gap

The issue is explicitly an *evaluation* epic — the author is searching for how to architect security-specialized guardrail models (dedicated detector models doing inline prompt-injection and jailbreak checks, rather than general-purpose LLM prompts) and hasn't found a settled pattern to copy. That search failure is itself the signal: a real, working reference architecture already exists. Red Hat's TrustyAI Guardrails Orchestrator, built on the open-source FMS Guardrails Orchestrator project, coordinates detector-server REST services for span-aware pre- and post-inference detection. Independently, several vendor write-ups (digitalapplied, Openlayer, Lakera's own docs) converge on the same four-point insertion pattern — checks before the model call, around retrieval, after the model's answer, and around tool calls — without citing or crediting each other.

So the architectural knowledge isn't missing. What's missing is a packaged, discoverable version of it that a team evaluating their options would actually find before opening their own design epic. No NIST or OWASP canonical standard exists to anchor the search, either — so even a team that does the research ends up betting on a vendor-converged pattern rather than an authoritative one. This is a consolidation and discoverability gap, not an absence of working software, which is exactly why it's easy to miss if your only search term is "guardrail architecture" rather than "FMS Guardrails Orchestrator."

## The Project

The project is a reference-architecture starter kit built directly on top of — not competing with — the existing open-source FMS Guardrails Orchestrator. It pre-wires adapters for the specific security-specialized models teams already reach for (Llama Guard and Prompt Guard, Granite Guardian, and a pluggable slot for Azure Prompt Shield or any OpenAI-compatible detector endpoint), mapped explicitly onto the four-point pattern: pre-inference, retrieval-time, post-inference, and tool-call-time. It ships as a deployable Docker-compose starter plus a short decision questionnaire — a team answers a handful of questions about their stack (self-hosted vs. managed models, which detectors they already run, their latency budget), and the kit generates the orchestrator config and detector wiring that matches, instead of a team re-deriving the whole architecture the way the `jero-manager` epic is doing right now.

The components are: a deployment template for the FMS/TrustyAI orchestrator itself; pre-built detector-server adapters for each named model; a four-point coverage mapper that flags which of the four insertion points a team's *current* config actually covers (surfacing gaps like "you're checking tool outputs but not the user's own message" before an incident does); and the decision questionnaire that turns all of that into a concrete starter config rather than a research assignment.

## Tangible Impact

**Population**: Engineering teams at small-to-mid-size companies building production LLM apps who don't have a dedicated AI-security engineer to do the deep research needed to find the FMS/TrustyAI pattern before defaulting to a from-scratch design — the same population visible in independent evidence of multiple teams in the same month each hand-building a bespoke guardrail layer rather than adopting a shared one, and the `jero-manager` team itself as a direct, named instance of the gap.
**Mechanism**: Today, a team evaluating guardrail architecture either finds nothing and designs from scratch, or finds the FMS Guardrails Orchestrator but still has to do the detector-wiring and four-point-mapping work themselves with no packaged starting point. A discoverable, pre-wired starter kit collapses that research-and-wiring phase into answering a short questionnaire and deploying a generated config, directly shortening time-to-a-defensible architecture and reducing the odds a team ships with an unknowingly incomplete pattern — covering post-inference but missing tool-call-time, for instance.
**Measure**: time from "starting an architecture evaluation" to "a working, four-point-covering guardrail deployment," measured against a baseline of teams doing it from scratch; the percentage of the four insertion points actually covered by teams who adopt the kit versus a sample of existing from-scratch implementations; and adoption of the starter kit's detector-server pattern versus continued bespoke-implementation activity over time, as a proxy for whether the kit is actually closing the duplication problem.

## Try It

A companion Claude Code skill is already built: [`skills/guardrail-architecture-reference-adoption-kit/`](../skills/guardrail-architecture-reference-adoption-kit/).

> Maps a team's described LLM/agent guardrail setup against the four-point reference pattern (pre-inference, retrieval-time, post-inference, tool-call-time) and names concrete detector models or approaches for each gap. Use when someone is evaluating or redesigning their guardrail architecture and wants to know where they actually stand before building from scratch.

This is the one-shot assessment half of the idea — you paste in a description or config/code snippet of your current guardrail call sites and get back a coverage map, not the deployable orchestrator kit itself. To use it: paste the contents of `skills/guardrail-architecture-reference-adoption-kit/README.md` into any AI chat tool along with a description of your current guardrail setup, or drop the whole `skills/guardrail-architecture-reference-adoption-kit/` folder into `~/.claude/skills/` if you're running Claude Code.

One honest caveat worth carrying over: the core issue here may be search-engine discoverability and marketing as much as missing software. If that's the whole story, a starter kit alone won't fix the underlying awareness gap without real distribution effort behind it — docs, GitHub presence, SEO — not just better code.

---

Surfaced from `research/2026-11-13-ai-safety-guardrails-in-production.md`, pattern `P9`.
