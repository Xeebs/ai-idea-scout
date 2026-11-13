# Actually Sure: A Packaged Calibration Layer Replacing Self-Reported LLM Confidence

- **Status**: EXPLORING
- **Date**: 2026-11-13
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-13-llm-evaluation-observability.md · P3
- **Maturity verdict**: PARTIAL — WebSearch found real research-grade alternatives (SelfCheckGPT's sampling-consistency hallucination detection, logit-based confidence, post-hoc calibration methods in 2026 arXiv papers like ConfidenceBench) but all are reference implementations, not packaged production tools teams can drop in to replace self-reported confidence scoring.
- **Format**: BOTH — the runtime scoring library that wraps live model calls is persistent infrastructure; a one-time "audit and migration plan" for a team's existing confidence-gated feature is a separable judgment task.
- **Data Sources**: CONNECTED — the library calls the team's own LLM inference API directly (OpenAI-style `logprobs`/`top_logprobs`, mature today; or N-sample stochastic generation via the same completions endpoint, available on effectively every provider) to compute a calibrated score — it reads from the live model call already happening, not from anything the user pastes. The companion skill's audit mode is MANUAL within that: the user pastes a description of their current confidence-gated feature and a handful of example outputs with their self-reported scores.

## The Gap
A Hacker News post, "Using LLM for confidence scoring is a bad idea" (rumple.github.io, 2026-10-21, 228 points / 107 comments), drew heavy engagement calling out a common but fragile practice: asking a model to state its own confidence and treating that number as a quality or calibration signal. The high engagement with no agreed replacement in the thread shows the community knows the common practice is broken but hasn't converged on what to do instead. WebSearch corroborates real fixes exist in research form — SelfCheckGPT, logit-based scoring, 2026 calibration papers — but none ship as an adoptable production component.

## The Project
A drop-in library that replaces "ask the model how confident it is" with a measured score computed one of two ways depending on what the provider exposes: (1) logit-based confidence from token-level `logprobs` when available, or (2) sampling-consistency scoring (SelfCheckGPT-style: generate N stochastic completions, measure semantic/structural agreement) when it isn't. Both paths feed a calibration harness that validates the new score against a labeled correctness set using Expected Calibration Error (ECE), so a team can see, in their own numbers, that the new signal actually tracks correctness better than the self-reported one before they switch.

Components: provider-agnostic logprob extractor; N-sample consistency scorer; ECE calibration harness; a migration shim that accepts the same call signature as a self-reported-confidence call so swapping it in doesn't require rewriting the gating logic around it.

## Tangible Impact
**Population**: Engineers building confidence-gated LLM features — auto-approve/auto-escalate triage, agent abstention thresholds, moderation severity gating — who currently wire the gate off a model's self-stated number. This is a cross-cutting slice of the production-agent population (LangChain's State of AI Agents survey, Dec 2024: ~51% of surveyed companies run agents in production), specifically the subset whose gating decision today rests on an unvalidated self-reported score rather than a measured one.
**Mechanism**: A self-reported confidence number has no guaranteed relationship to actual correctness — it's the model describing itself, not a measurement. Swapping in a calibrated, measured score changes what the gate is actually keying off of, directly reducing how often a wrongly-confident output passes the gate.
**Measure**: (1) ECE on a held-out labeled correctness set drops versus the self-reported baseline; (2) false-auto-approve rate (gate let through a wrong answer) drops on the same eval set; (3) added latency/cost overhead from logprob reads or N-sampling stays within a stated budget (e.g., under 2x the original call cost).

## Why Now
The critique crystallized in October 2026 with 107 comments of engagement, and the alternative techniques (SelfCheckGPT, logit-based scoring, calibration methods) are all 2023–2026 research artifacts that are technically mature but never packaged — nothing here waits on a future model capability, only on someone doing the packaging work.

## Skill Angle
Trigger: a team already has a confidence-gated feature live (or is about to build one) and wants to know whether their current self-reported-confidence approach is actually safe before committing engineering time to a runtime swap. Inputs: a description of the gated feature and its current scoring method, plus 5–10 example outputs with their self-reported scores and (if available) known-correct/known-wrong labels. Output: a bias-risk note naming why self-reported scores are unreliable for this specific use case, a recommendation between logit-based and sampling-consistency scoring based on what the team's provider exposes, and a drafted migration plan including the ECE check to run before switching. The skill is the design/audit pass before committing to the runtime library; the project is the library itself.

## MVP Sketch
A Python wrapper around one provider's completions API that offers both a logprob-based and an N=5-sample consistency score behind the same call signature as a naive "ask the model to self-rate" call, plus an ECE calculator. Experiment: run both scoring methods and the self-reported baseline against a public QA benchmark with known-correct answers (e.g., a TruthfulQA subset), and show at least one calibrated method has materially lower ECE than self-reported confidence. 2–3 weeks, 1 person.

## Risks & Open Questions
- Anthropic and some other providers don't expose token logprobs broadly, narrowing the logit-based path to a subset of providers — sampling-consistency is the fallback but costs N extra calls.
- A well-funded eval vendor (Braintrust, Galileo, Arize) could package this faster once they notice the gap, given they already have the distribution.
- "How much calibration is enough" is use-case dependent — a triage gate and a medical-advice gate have very different acceptable ECE, and this idea doesn't resolve that policy question, only the measurement.
- Sampling-consistency scoring assumes correctness correlates with agreement across samples, which can fail on tasks where the model is consistently and confidently wrong in the same way every time.
