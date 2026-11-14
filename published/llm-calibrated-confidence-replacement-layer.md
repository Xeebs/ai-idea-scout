# Actually Sure: A Packaged Calibration Layer Replacing Self-Reported LLM Confidence

Ask a model how confident it is, and it will tell you — fluently, specifically, and with no mechanical connection whatsoever to whether it's actually right. That number is still quietly deciding whether a support ticket gets auto-resolved, whether a triage case escalates to a human, or whether a moderation call gets enforced. A lot of people now agree this is a bad idea. Almost nobody has shipped the fix.

## The Gap

In October 2026, a Hacker News post titled "Using LLM for confidence scoring is a bad idea" pulled in 228 points and 107 comments — the kind of engagement that means a lot of engineers recognized their own setup in the critique. The thread named the practice, agreed it was fragile, and then did what critique-shaped HN threads tend to do: stopped short of a replacement. Nobody walked away with a drop-in fix.

That's not because the fixes don't exist. Searching past the thread turns up real, technically mature alternatives — SelfCheckGPT's sampling-consistency approach to hallucination detection, logit-based confidence extraction from a model's own token probabilities, and a run of 2026 arXiv papers on post-hoc calibration. All of it is reference-implementation-grade research, not something a team can `pip install` and wire into an existing gate this afternoon. A newer attempt at closing that gap, `judgekit`, surfaced in the same search — a pip-installable judge-auditing CLI — but it's brand new (pushed days before this writeup, zero GitHub stars, single author), with no adoption signal yet. The packaging work, in other words, is the part nobody's finished.

## The Project

The pitch is a drop-in library that replaces "ask the model how confident it is" with a number that's actually measured. It picks one of two paths depending on what the model provider exposes: logit-based confidence, pulled straight from token-level `logprobs` when the API offers them, or sampling-consistency scoring when it doesn't — generate N stochastic completions of the same prompt and measure how much they agree with each other, SelfCheckGPT-style.

Neither path is useful on its own without a way to prove it's actually better, so both feed into a calibration harness that computes Expected Calibration Error (ECE) against a labeled correctness set. That's the part that makes this more than a swap-one-number-for-another exercise: a team gets to see, in their own data, whether the new signal tracks correctness better than the old self-reported one before they commit to switching.

Four pieces make up the stack: a provider-agnostic logprob extractor, an N-sample consistency scorer for providers that don't expose logprobs (Anthropic's Claude API notably doesn't), an ECE calibration harness, and — the detail that actually gets this adopted — a migration shim that mimics the call signature of the existing self-reported-confidence call, so swapping it in doesn't mean rewriting the gating logic sitting around it.

## Tangible Impact

**Population**: Engineers building confidence-gated LLM features — auto-approve/auto-escalate triage, agent abstention thresholds, moderation severity gating — who currently wire the gate off a model's self-stated number. This is a cross-cutting slice of the production-agent population (LangChain's State of AI Agents survey, Dec 2024: ~51% of surveyed companies run agents in production), specifically the subset whose gating decision today rests on an unvalidated self-reported score rather than a measured one.

**Mechanism**: A self-reported confidence number has no guaranteed relationship to actual correctness — it's the model describing itself, not a measurement. Swapping in a calibrated, measured score changes what the gate is actually keying off of, directly reducing how often a wrongly-confident output passes the gate.

**Measure**: (1) ECE on a held-out labeled correctness set drops versus the self-reported baseline; (2) false-auto-approve rate (gate let through a wrong answer) drops on the same eval set; (3) added latency/cost overhead from logprob reads or N-sampling stays within a stated budget (e.g., under 2x the original call cost).

## Try It

A companion Claude Code skill, [`skills/llm-calibrated-confidence-replacement-layer/`](../skills/llm-calibrated-confidence-replacement-layer/), is already written: *"Audits a confidence-gated LLM feature that keys off a model's self-reported confidence number, and produces a migration plan to a measured (logit-based or sampling-consistency) score instead. Use when a team wants to know if their self-rated confidence gate is safe, or needs a concrete plan to replace it."*

It's deliberately scoped as the audit-and-plan step, not the runtime library itself — hand it a description of your gate, its scoring method, your provider, and a handful of example outputs with their self-reported scores, and it comes back with a risk assessment, a recommended replacement method, and a migration plan with the ECE check built in. To use it: drop the `skills/llm-calibrated-confidence-replacement-layer/` folder into `~/.claude/skills/` if you're on Claude Code, or paste its `README.md` into any AI chat tool as a standalone prompt — it doesn't assume Claude Code is installed.

## Worth Knowing

The idea file's own risk list is worth repeating rather than burying: Anthropic and some other providers don't expose token logprobs, so the logit-based path only covers a subset of providers, and sampling-consistency scoring costs N extra model calls as the fallback. A well-resourced eval vendor — Braintrust, Galileo, Arize all come up as plausible candidates — could ship this faster once they notice the gap, since they already have the distribution a new library would have to earn. "How much calibration is enough" is also a policy question this doesn't resolve, only measure — a triage gate and a medical-advice gate don't share an acceptable ECE, and that judgment call stays with whoever deploys it. And sampling-consistency itself rests on an assumption that can fail: it treats agreement across samples as a proxy for correctness, which breaks down on tasks where a model is consistently, confidently wrong in exactly the same way every time.

Surfaced from `research/2026-11-13-llm-evaluation-observability.md`, pattern `P2` (the idea file's Source field cites P3, which in the source digest is an unrelated, SATURATED pattern about CI eval harnesses — P2, "LLM-as-judge confidence scores are unreliable and unaudited," is the pattern whose evidence actually matches this idea).
