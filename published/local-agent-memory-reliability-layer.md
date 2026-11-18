# Steady Memory: A Hardened, Packaged Persistent-Memory Layer for Local Small-Model Agents

A dozen different developers have independently rebuilt the same memory stack for their local AI assistant — Mem0, Qdrant, sqlite-vec, some combination of the three — and every single one of them shipped it with the same unfixed bug class: silent write failures. Not one of those dozen repos has more than a single star. The problem isn't that nobody's tried. It's that trying alone, from scratch, every time, is exactly why nobody's gotten past a fragile personal script.

## The Gap

Ask a local, small model to remember you across sessions and you run into a wall the model itself can't climb — it has no state beyond its context window, so anything resembling memory has to be bolted on from outside. A Mem0 + Ollama + Qdrant integration guide found in the wild is upfront about what that bolting-on actually costs: the author flags that their setup is explicitly "not the official @mem0/openclaw-mem0 plugin" and warns that "the embedding dimensions in config must match the embedding model, or writes silently fail" — meaning your assistant can lose a memory and never tell you. An LM Studio community plugin takes a simpler route, storing memory as a plain markdown file, but its own author concedes reliability "depends on the model's tool-use ability, and larger models are more reliable" — which is a polite way of saying it gets worse exactly where local, small-model users live. Layered on top of both: a LocalLLaMA-sourced finding that naively stuffing full conversation history into context "actively harmed recall at every tested model size," meaning the community hasn't even settled on the right architecture, let alone built a trustworthy implementation of any one approach.

This isn't a one-off complaint. A GitHub search for "local agent persistent memory," "mem0 ollama," and "sqlite-vec agent memory" turns up a dozen-plus separate repos — `ollama-mem0-AI-chatloop-ts`, `self-learning-agent`, `mem0-broker`, `mem0-personal-ai-agent`, `ai-memory-assistant`, `mem0-persistent-ai-memory`, and more — each a solo DIY integration, each sitting at 0–1 stars. Many hands have built this. None have built it robustly. No packaged, widely-adopted solution exists today.

## The Project

Steady Memory is a packaged memory layer purpose-built for local small-model agents running on Ollama, llama.cpp, or LM Studio. It wraps storage and retrieval behind a simple record/query API — the same basic shape every one of those dozen solo repos already reaches for — but closes the exact failure modes the community's own write-ups flagged as missing:

- **Embedding-dimension-mismatch detection before a write is accepted** — the specific silent-failure class the Mem0+Ollama+Qdrant guide author warned about, caught before it happens rather than discovered weeks later as a gap in recall.
- **Write confirmation, never a silent failure** — every write either succeeds and says so, or fails loud.
- **A degraded-mode fallback to flat-file storage** when the local model's own tool-calling reliability is too weak to trust structured memory calls — a real, documented failure mode at smaller model sizes, not a hypothetical one.

The bet is narrow and specific: don't try to solve which memory architecture is "right" — the LocalLLaMA full-history-harms-recall finding shows that's still genuinely unresolved — just make whatever architecture a builder picks fail loudly instead of silently, and keep working even when the underlying model's tool-use is shaky.

## Tangible Impact

**Population**: Hobbyist and privacy-conscious individuals running personal AI assistants on local hardware via Ollama or LM Studio who want the assistant to remember context (journaling, personal projects, health or financial notes) across sessions without a cloud memory service touching that data. Ollama alone reported roughly 8.9 million monthly active developers as of July 2026 (TechCrunch), a substantial share of whom are individual/hobbyist builders rather than enterprise teams — exactly the audience building and re-building the fragile DIY memory stacks this digest documents.

**Mechanism**: Today these builders hand-wire Mem0/Qdrant/sqlite-vec integrations with documented fragility — silent write failures on dimension mismatch, reliability that degrades with model size — and every public attempt stops at a 0–1-star solo repo, meaning the next builder starts from zero again. A packaged layer with built-in failure detection and a degraded-mode fallback removes the silent-failure class entirely and gives these builders a working default instead of a DIY integration they must personally debug from scratch.

**Measure**: (1) Silent-write-failure rate on a fault-injection test harness (intentionally mismatched embedding configs, dropped writes, degraded tool-calling) versus the documented failure rate of the DIY stacks cited above. (2) Recall accuracy retained across a multi-session benchmark at varying local model sizes (1B/3B/7B/13B), showing the layer compensates for weaker tool-use reliability at small sizes. (3) Adoption — number of community integrations (Open WebUI plugins, LM Studio plugin ecosystem) within 6 months of release.

## Try It

No companion Claude Code skill has been built for this idea yet — it's tagged `Format: BOTH` in the idea file (the runtime memory layer as a project, plus a separable one-shot "audit my existing DIY memory integration" skill), but only the project side exists so far. If a skill lands in `skills/local-agent-memory-reliability-layer/` in a future cycle, it will let you paste a description of your own Mem0/Ollama/Qdrant setup or LM Studio memory plugin config and get back a concrete fix checklist against the exact failure modes named above.

## The Catch

The dozen existing 0–1-star attempts cut both ways: they could mean weak demand for a *packaged* solution specifically — developers content to DIY and move on — rather than weak execution. The adoption number in the measures above is the actual test of which is true, not a given. A degraded-mode fallback also adds its own complexity, which, left unbounded, could introduce new failure modes rather than removing them. And the biggest external risk is structural: Mem0, LM Studio, or Ollama itself could ship an official hardened plugin at any time — several of the cited DIY authors are explicitly working around the absence of exactly that today, which means the gap this project fills could close from above, not from a competitor project.

---

Surfaced from `research/2026-11-14-small-and-local-models.md`, pattern `P4`.
