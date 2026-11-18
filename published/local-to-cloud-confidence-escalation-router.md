# Confidence Gate: A Benchmarked Escalation-Decision Library for Local-to-Cloud Model Routing

Everyone building a local-first agent eventually hits the same fork in the road: run everything on the small model and eat the accuracy hit, or send everything to the cloud and give up the cost and latency win that made local attractive in the first place. The fix — score the local model's confidence and escalate only the hard cases to a frontier model — has been described in public at least three separate times in the last month. Nobody has shipped the part that actually makes it usable: the confidence-scoring step itself, as a library you can drop in and benchmark, instead of a design pattern you re-derive from someone else's blog post.

## The Gap

The "SLM-default, LLM-fallback" idea keeps surfacing independently, which is usually a sign something real is being hand-rolled over and over rather than reused. Strathweb's Azure-oriented write-up lays out scoring a local agent's output and escalating on low confidence, citing a 2025 survey on small language models for agentic systems. Tom Tunguz reported sending background work through a small on-device classifier so only the hardest tasks reach the cloud — and says it roughly tripled single-Mac throughput. Vendor posts from BetterClaw and CallSphere claim 60-80% of agent requests can stay local, though those figures are vendor-sourced and unverified, not independently benchmarked.

What's conspicuously missing is the connective tissue. OpenRouter — a company whose entire product is routing between models — says outright in its own blog that "we do not make that call for you" on this exact decision. Research-grade confidence-estimation code exists (`BuffaloTechRider/zero-shot-llm-confidence-estimation`, `NYCU-NLP-Lab/ConfDrivenInference`), and cloud-to-cloud routing is a solved problem (`lm-sys/RouteLLM`). But the specific step of scoring a *local* model's confidence and deciding whether to escalate to the cloud has no shared library behind it — just three bespoke, single-author implementations described in prose.

## The Project

The project is a drop-in middleware library that wraps a local model call, scores the response's confidence using a published technique — self-consistency sampling across N local generations, or a zero-shot confidence estimator adapted from the research above — and escalates the same request to a cloud model whenever confidence drops below a configurable threshold. The escalation is transparent to the calling app: same request in, same shape of response out, just sometimes answered by a different model.

The part that matters most isn't the middleware itself, though — it's the benchmark CLI that ships alongside it. Instead of adopting a vendor's unverified 60-80%-stays-local number on faith, a team runs its own eval set through local-only, cloud-only, and hybrid-escalation configurations and gets back an actual cost/latency/accuracy tradeoff curve. The threshold gets picked from measured data on *your* task distribution, not copied from someone else's marketing post. Components: a pluggable confidence-scoring adapter (entropy-based, self-consistency, or a logged zero-shot estimator), an escalation policy engine with per-task-type overrides, a passthrough layer that keeps escalation invisible to the calling code, and the benchmark CLI itself.

## Tangible Impact

**Population**: Indie developers and small teams building local-first or cost-sensitive agentic apps who today run either 100% local (losing accuracy on hard requests) or 100% cloud (forfeiting the cost/latency win) because no reusable confidence-escalation component exists — they'd otherwise hand-roll the Strathweb/Tunguz pattern themselves. Ollama alone reported roughly 8.9 million monthly active developers as of July 2026 (TechCrunch); a meaningful share run multi-step agentic workloads where this exact routing decision recurs.
**Mechanism**: Gives this population a measured, swappable confidence-escalation component instead of a bespoke implementation — they plug it into an existing local-model call, run the benchmark on their own task distribution, and pick a threshold with real cost/accuracy numbers instead of copying a vendor's unverified 60-80% figure.
**Measure**: (1) percentage of requests resolved locally at a declared accuracy floor (e.g., ≥95% of all-cloud accuracy) on a team's own eval set; (2) cost and p95 latency reduction vs. an all-cloud baseline at that floor; (3) time for a team to go from "nothing" to a calibrated threshold recommendation using the benchmark CLI, target under one hour.

Worth saying plainly: the headline numbers behind this idea are not fully verified. The 60-80%-stays-local figures are vendor claims, not independently measured, and small models are known to be poorly calibrated about their own confidence — meaning the self-consistency sampling this project leans on adds latency and cost that eats into the very savings it's trying to prove out. That's exactly why the benchmark CLI, not the middleware, is the part worth building first: it's the thing that tells you honestly whether the pattern holds up on your own workload before you commit to it.

## Try It

A Claude Code skill version of the advisory half of this exists at `skills/local-to-cloud-confidence-escalation-router/`. Its one-line description: "One-shot advisory judgment that decides whether a local-model workload is worth building confidence-based cloud escalation for, picks a confidence-scoring method suited to the task shape, and drafts a starting threshold policy with explicit validation caveats — for someone weighing whether to build the 'run local, escalate hard cases to cloud' pattern before writing any middleware."

To use it: paste the contents of `skills/local-to-cloud-confidence-escalation-router/README.md` into any AI chat tool and describe your task and local model setup, or — if you're using Claude Code — drop the whole `local-to-cloud-confidence-escalation-router/` folder into `~/.claude/skills/` and invoke it directly. It won't build the middleware or run the benchmark for you, but it will tell you which confidence-scoring method fits your task and sketch a starting threshold before you write any infrastructure.

---

Surfaced from `research/2026-11-14-small-local-models.md`, pattern `P1`.
