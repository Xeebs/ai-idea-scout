# Small Shield: A Purpose-Built Adversarial Hardening Layer for Small Local Models in Agent Stacks

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Small & local models
- **Source**: research/2026-11-12-small-local-models-2.md · P2
- **Maturity verdict**: PARTIAL (fragmented research exists — Hermes Labs' little-canary decoy-model defense, Meta's SecAlign adapters, CourtGuard's multi-agent classifier, SecFid's measurement critique, and Brazilian red-team papers showing 45–62% attack success against Qwen2.5-1.5B/SmolLM2 — but no single maintained, productized hardening layer purpose-built for small-model-in-agent-stack deployments exists yet)
- **Format**: BOTH
- **Data Sources**: CONNECTED — intercepts the agent stack's existing local-model inference endpoint (Ollama's `/api/generate`, llama.cpp server's OpenAI-compatible HTTP API, or vLLM's local server — all mature, widely-deployed APIs) via a middleware reverse proxy or framework callback hook (LangChain/LangGraph `on_llm_start`/`on_llm_end`); no manual paste of prompts or outputs is required for the runtime layer. The companion skill's only manual input is the user pasting their agent's system prompt and a sample of its tool-call schema.

## The Gap
Practitioner caveats on router/cascade cost-cutting threads (dev.to, Tom Tunguz, r/AI_Agents, an NVIDIA-cited analysis) repeatedly flag that small models used as agent-stack components are more vulnerable to prompt injection than frontier models — "less trained on adversarial inputs" — but that risk shows up only as a passing caveat, never its own fix. WebSearch found real research attacking the problem — little-canary's decoy-model defense (69.2%→98.6% refusal lift on a 208-prompt set), SecAlign's 8B/70B adapters, CourtGuard's classifier, and red-team papers quantifying 45–62% attack success against the exact small models people route through — but these are scattered research artifacts, not something a developer wiring a cheap local model into an agent loop can install today.

## The Project
A drop-in hardening sidecar for small local models used as agent-stack components: input-side decoy/honeytoken probing (adapting little-canary's approach) to detect injection attempts before they reach the model, an output-side classifier calibrated on the published small-model attack-success data (rather than a generic large-model guardrail tuned for a different false-positive/negative tradeoff), and an optional SecAlign-style adapter for teams who can afford a light fine-tune pass. It runs as a reverse-proxy/middleware layer in front of Ollama/llama.cpp/vLLM, so a small model chosen for cost or privacy reasons gets protection sized for its actual threat profile instead of either nothing or an oversized guardrail that erases the savings.

Core components: (1) an injection-probe layer combining decoy prompts and known-attack-pattern matching, (2) a small-model-calibrated output classifier benchmarked against the published red-team attack set, (3) an optional SecAlign-style adapter users can apply to their own weights, (4) a published, reproducible benchmark harness so the project's own claimed attack-success reduction is independently verifiable rather than self-reported, like the research it draws from.

## Tangible Impact
**Population**: Developers and small teams deploying sub-7B local models as autonomous agent-stack components (routers, tool-calling agents, first-pass classifiers) specifically because of cost or privacy constraints — the same population generating the router/cascade threads cited in this digest's P1. Proxy for scale: r/LocalLLaMA has 680k+ members, and router/cascade posts in this digest cite savings claims up to 99%, implying wide and growing adoption of small-model-in-the-loop architectures.
**Mechanism**: Today these teams either ship with no small-model-specific hardening (inheriting the 45–62% attack-success exposure measured in the red-team papers) or bolt on a large-model guardrail whose latency/cost is disproportionate to the small model's own footprint, undermining the reason they chose a small model at all. A purpose-built, lightweight hardening layer calibrated to the actual threat profile lets them keep the cost/latency win while closing the named gap.
**Measure**: (1) attack success rate on the project's own red-team benchmark (baseline 45–62%, reported before/after reduction); (2) added latency/memory overhead as a percentage of the small model's own inference cost (target: single digits, so hardening doesn't eat the savings that justified using a small model); (3) false-positive rate on benign agent tool-call traffic.

## Why Now
Small-model-as-router/cascade architectures went from niche to mainstream enough in the last 30 days to generate a dedicated arXiv cost-tactics taxonomy (2604.12301) and multiple practitioner writeups — the attack surface this closes is scaling right alongside the pattern it protects, not a hypothetical future risk.

## Skill Angle
A companion audit skill: given a pasted system prompt and tool-call schema for an agent stack using a small local model, the skill walks through the known small-model attack classes (drawn from the red-team paper's taxonomy) and flags which ones the stack has no mitigation for, recommending the specific countermeasure (decoy probing, output classifier, adapter fine-tune) from the research corpus. This differs from the project: the skill is a one-time design-review aid run before building; the project is the actual runtime middleware deployed after.

## MVP Sketch
Two weeks, 1–2 people: build the reverse-proxy sidecar for Ollama's API, implement decoy-prompt injection detection plus a classifier few-shot-calibrated on the published small-model red-team attack set, and run it against that same public attack set to produce a first before/after number. Stack: Python, FastAPI proxy, a small fine-tuned classifier (DistilBERT-class) for output screening.

## Risks & Open Questions
- The published red-team attack sets (Brazilian papers) may not be fully public/reproducible — verify licensing/availability before committing the benchmark design to them.
- Risk the hardening layer's own latency overhead erases the cost benefit it's meant to preserve — needs measuring early, not assumed.
- SecAlign-style adapters require fine-tuning access to the specific small model; not every deployment can retrain, so this component may need to stay optional/best-effort rather than core.
- If a well-resourced vendor (e.g., Ollama or vLLM) ships a built-in hardening layer during development, this could flip from PARTIAL to SATURATED quickly — worth re-checking before investing beyond the MVP.
