# Small Shield: A Purpose-Built Adversarial Hardening Layer for Small Local Models in Agent Stacks

Every "we cut our agent bill 75-99% by routing to a small local model" post has a buried line in it that nobody follows up on: the small model is also the weakest link in the chain. It gets mentioned once, as a footnote, then everyone moves on to the next cost-savings screenshot.

## The Gap

Small-model routing and cascading has gone mainstream — a dev.to writeup claims a Gemma-4 local router cut Codex/Claude Code token costs up to 99% in the best case, Tom Tunguz describes a small router model on a single Mac handling roughly four-fifths of background tasks, an aiweekly.co alert reports a 75% agent-cost cut via a router/synthesizer split, and an April-2026 arXiv taxonomy (2604.12301) names single-stage local/cloud routing as one of seven established cost-cutting tactics for coding-agent workloads. Buried inside that same wave of practitioner writeups is a caveat that keeps getting repeated and never resolved: small models are "more susceptible to prompt injection — they're less trained on adversarial inputs" than the frontier models they're routing around.

That caveat isn't hand-waving. Real research has quantified it: Brazilian red-team papers put attack success rates at 45-62% against exactly the small models people are routing through — Qwen2.5-1.5B and SmolLM2. And real defenses exist in pieces: Hermes Labs' "little-canary," an open-source decoy-model defense that self-reports lifting refusal rates from 69.2% to 98.6% on a 208-prompt set; Meta's SecAlign adapters for 8B/70B models; CourtGuard (arXiv 2510.19844), a multi-agent classifier; and a SecFid paper (ICML 2026 Spotlight) that goes as far as critiquing how the field even measures these defenses. What none of this adds up to is something a developer can actually install. It's five research threads that have never been stitched into one deployable layer sized for the models people are actually putting in the hot path of an autonomous agent.

## The Project

Small Shield is a drop-in hardening sidecar built specifically for small local models acting as agent-stack components — routers, tool-calling agents, first-pass classifiers — not a scaled-down version of a large-model guardrail. It sits as a reverse-proxy/middleware layer in front of Ollama, llama.cpp's server, or vLLM, intercepting the same inference endpoints the agent stack is already calling.

On the input side, it adapts little-canary's decoy/honeytoken approach to probe for injection attempts before they ever reach the model. On the output side, it runs a classifier calibrated against the published small-model attack-success data — not a generic large-model guardrail tuned for a completely different false-positive/false-negative tradeoff. For teams with the appetite for a light fine-tuning pass, there's an optional SecAlign-style adapter. And because the research this draws from is largely self-reported, the project ships its own published, reproducible benchmark harness, so its own claimed attack-success reduction can be independently checked rather than taken on faith — the same trust gap the SecFid paper calls out in everyone else's numbers.

The point of the whole design is proportionality: a team picked a small model for cost or privacy reasons, and the hardening layer has to protect it without being so heavy it erases the savings that justified the choice in the first place.

## Tangible Impact

**Population**: Developers and small teams deploying sub-7B local models as autonomous agent-stack components (routers, tool-calling agents, first-pass classifiers) specifically because of cost or privacy constraints — the same population generating the router/cascade threads cited in this digest's P1. Proxy for scale: r/LocalLLaMA has 680k+ members, and router/cascade posts in this digest cite savings claims up to 99%, implying wide and growing adoption of small-model-in-the-loop architectures.
**Mechanism**: Today these teams either ship with no small-model-specific hardening (inheriting the 45–62% attack-success exposure measured in the red-team papers) or bolt on a large-model guardrail whose latency/cost is disproportionate to the small model's own footprint, undermining the reason they chose a small model at all. A purpose-built, lightweight hardening layer calibrated to the actual threat profile lets them keep the cost/latency win while closing the named gap.
**Measure**: (1) attack success rate on the project's own red-team benchmark (baseline 45–62%, reported before/after reduction); (2) added latency/memory overhead as a percentage of the small model's own inference cost (target: single digits, so hardening doesn't eat the savings that justified using a small model); (3) false-positive rate on benign agent tool-call traffic.

## Try It

A companion Claude Code skill exists today at [`skills/small-model-agent-adversarial-hardening-layer/`](../skills/small-model-agent-adversarial-hardening-layer/): *"Audits a described agent stack built on a small local model (sub-7B, e.g. Qwen2.5-1.5B, SmolLM2, Phi-3-mini, Llama-3.2-3B) against a named taxonomy of attack classes small models are disproportionately weak against, and recommends the specific, proportional countermeasure for each gap."*

This is the design-review half of the idea, not the runtime middleware — run it *before* you build the sidecar described above. Paste your agent's system prompt and tool/function-call schema into the skill and it walks all seven attack classes (direct override, indirect injection via tool output, obfuscation, multi-turn context poisoning, tool-call hijacking, config extraction, and resource-exhaustion abuse), marking each COVERED, PARTIAL, or UNCOVERED with a named countermeasure for every gap it finds.

To use it: paste the contents of its `README.md` into any AI chat tool for a self-contained version, or drop the whole `skills/small-model-agent-adversarial-hardening-layer/` folder into `~/.claude/skills/` if you're running Claude Code. It is a static text review, not a live attack test — it says so itself, and recommends running the actual red-team attack set against your live stack as the real next step. Don't mistake a clean audit for a tested one.

Worth being honest about the risk here too: the published red-team attack sets this whole idea leans on come from Brazilian academic papers whose licensing and reproducibility haven't been verified yet, and if a well-resourced vendor like Ollama or vLLM ships a built-in hardening layer while this is being built, the gap could close fast. Neither kills the idea today, but both are reasons to check again before investing past the MVP.

Surfaced from `research/2026-11-12-small-local-models-2.md`, pattern `P2`.
