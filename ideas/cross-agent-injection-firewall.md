# Handoff Firewall: Containing Prompt Injection That Rides Between Agents

- **Status**: PROPOSED
- **Date**: 2026-06-10
- **Topic**: Multi-agent architectures
- **Source**: research/2026-06-10-multi-agent-architectures.md · P8
- **Maturity verdict**: PARTIAL — Single-request injection defense is shipped (Azure Prompt Shield, Bedrock prompt-attack detection, layered-defense guides) and the cross-agent case has research-stage countermeasures — privilege separation (arXiv 2603.13424), control-flow-hijacking defenses (arXiv 2510.17276), and the LLMSecurity/awesome-agent-skills-security corpus — but arXiv 2605.22001 shows current detectors are evaded by domain-camouflaged cross-agent payloads and no containment tool for inter-agent propagation has shipped. GitHub searches for "prompt injection defense multi-agent" / "inter-agent trust boundary" returned zero repos.
- **Format**: BOTH — the taint-propagation middleware is PROJECT-shaped, but auditing a described pipeline's handoffs for missing containment is a one-shot review task.

## The Gap
"Domain-Camouflaged Injection Attacks Evade Detection in Multi-Agent LLM Systems" (arXiv 2605.22001, 38pts on HN, 2026-05-22) demonstrates that an attacker can poison one agent's input and have the payload — rewritten in the system's own domain language — ride handoffs past per-request detectors into downstream agents with tool access. The attack is documented and reproducible; the defense is not: shipped guardrails inspect single requests at the perimeter, research countermeasures are paper artifacts, and GitHub searches for inter-agent trust-boundary tooling return zero repos.

## The Project
A trust-boundary middleware for inter-agent messages: every handoff carries a taint label tracing which content derives from untrusted input (web pages, user uploads, emails), and policy rules constrain what tainted content can do downstream — e.g., "instructions originating from fetched documents cannot trigger tool calls in any subsequent agent." The propagation model is the centerpiece: instead of re-classifying each message in isolation (the approach 2605.22001 defeats), the firewall tracks provenance across hops, so a camouflaged payload still carries its untrusted lineage when it reaches the agent with the dangerous tools. Ships with an attack-replay eval seeded from the paper's domain-camouflage method, so defenses are measured, not asserted.

Components: taint-propagation layer wrapping handoffs (OpenAI Agents SDK + LangGraph adapters); policy engine (tainted-content capability rules); detector hook points for existing classifiers; red-team eval harness reproducing domain-camouflaged multi-hop attacks.

## Tangible Impact
**Population**: Security and platform engineers responsible for multi-agent systems that ingest untrusted external content with tool access downstream — customer-support pipelines reading inbound email, document-processing chains, web-browsing research agents. Concretely: the AppSec teams at the ~half of surveyed companies already running agents in production (LangChain survey, 1,300+ professionals) whose architectures chain agents over untrusted input — plausibly the low thousands of teams, each of which currently has zero shippable defense for the multi-hop case per the verdict's empty GitHub searches.
**Mechanism**: Today these teams either accept the documented attack surface or bolt per-request classifiers onto each agent — which 2605.22001 shows camouflaged payloads evade; provenance tracking changes the game from "recognize the attack text" (brittle) to "untrusted content cannot acquire tool-invoking authority no matter how it's worded" (structural), turning an open vulnerability class into an enforceable policy.
**Measure**: (1) Block rate on the reproduced domain-camouflaged attack suite: ≥95% with the firewall vs. the measured detector-only baseline the paper defeats. (2) False-positive rate on benign multi-agent workloads <2%, so the policy is adoptable. (3) Added latency per handoff <50ms, keeping it production-viable.

## Why Now
The attack paper landed inside the 30-day window and was discussed on HN — the vulnerability is now public knowledge with no shipped countermeasure, which is exactly when defenders look for tooling. The research ingredients (privilege separation, control-flow integrity for agents) were published in the last quarter and need only engineering assembly, not new model capability.

## Skill Angle
Given a description of a multi-agent pipeline's data flow (which agents ingest untrusted content, which have tool access, what gets handed off where), audit it for domain-camouflaged-injection exposure: flag every hop where untrusted content could reach a tool-capable agent without a containment boundary, and name the specific policy rule that would close each gap. A one-shot security review, useful before anyone builds the actual middleware.

## MVP Sketch
A Python middleware for one framework (OpenAI Agents SDK) implementing taint labels on handoff content plus a single policy ("tainted text cannot parameterize or trigger tool calls"), evaluated against a reproduction of the paper's camouflaged attacks on a three-agent email-triage pipeline. Experiment: if taint propagation blocks ≥95% of multi-hop attacks the baseline detector misses, with <2% false positives, the structural approach is validated; if benign workflows constantly trip the policy, it's unusable — kill it. 3–4 weeks for 1–2 people.

## Risks & Open Questions
- Microsoft/AWS could extend Prompt Shield/Bedrock guardrails to multi-hop provenance and own this — the strongest already-solved risk; hyperscalers move fast on publicized attacks.
- Taint tracking through an LLM is fundamentally leaky: the model paraphrases tainted content into "clean" tokens, and label granularity (whole-message vs. span) may be either useless or unmanageable.
- Capability restrictions on tainted content may break the very workflows multi-agent systems exist for (e.g., "summarize this document and file a ticket about it").
- Demand is inferred from the attack's existence, not from victims asking for help — no complaint-shaped signal in the corpus yet.
