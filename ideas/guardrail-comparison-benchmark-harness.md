# Guard Off: A Self-Service Benchmarking Harness for Comparing Guardrail Implementations

- **Status**: PROPOSED
- **Date**: 2026-11-14
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-14-ai-safety-and-guardrails-in-production.md · P1
- **Maturity verdict**: PARTIAL — real benchmarking work exists (an academic SoK at arXiv 2506.10597, a GuardBench pre-deployment framework with 4,200 jailbreak prompts reporting ASR/FP/P95 latency, and Artificial Analysis/NVIDIA's F1-vs-latency vendor benchmark site), but none is a self-service tool a team can run with its own prompt set. The one matching GitHub project, `Virtue-Research/guard-eval-harness`, has 19 stars and was last pushed 2026-06-26.
- **Format**: BOTH
- **Data Sources**: MANUAL + CONNECTED (hybrid) — the team uploads/pastes its own adversarial-plus-benign prompt set (CSV/JSONL, one prompt per row with an expected label) since no generic "your prompt set" source exists to read this from automatically. The harness then calls out to each guard under test through its own already-mature connector: Llama Guard 4 via HF Inference or a local vLLM endpoint, NeMo Guardrails via NVIDIA's open-source Python library, Presidio via its own package, and a custom rule/classifier guard via a configurable HTTP endpoint the team provides. Every guard integration already exists maturely; the new work is the orchestration layer that runs one prompt set uniformly across all of them.

## The Gap
GitHub PR `dsailajakrishna0-ship-it/customer-compass-v3` #77 (2026-11-13) shows a team building a one-off, single-repo harness from scratch to compare its rule guard, ML classifier, Llama Guard 4, and NeMo Guardrails on one adversarial set, printing a single detection-rate/false-positive/latency table. No existing tool lets a team drop in its own prompt set and get that same standardized comparison across the popular guard options — teams either trust vendor self-reports or re-derive this harness themselves.

## The Project
A CLI/library with a pluggable adapter per guard type (rule-based, ML classifier, Llama Guard, NeMo Guardrails, Presidio, custom endpoint). A team supplies a prompt set labeled attack/benign, lists which guards to include with their connection details, and the harness runs every prompt through every guard, producing one table: detection rate, false-positive rate, p50/p95 latency, and (where pricing is known) per-1k-prompt cost, side by side. The adapter layer — not the table renderer — is the centerpiece: each adapter normalizes a wildly different API shape (a local classifier's raw score, NeMo's rail decision, Presidio's entity list) into one pass/fail/score contract so the comparison is apples-to-apples instead of each vendor's own self-reported number on its own prompt set.

Components: prompt-set schema and loader · one adapter per guard type · a runner that executes the full cross-product and records latency/cost · a comparison-table renderer · a CI mode so re-running on a new release of any guard catches a regression.

## Tangible Impact
**Population**: platform/ML engineering teams evaluating which guardrail(s) to adopt for a production LLM app with user-facing safety requirements — the same population currently re-deriving this from scratch, per the sourcing PR. A proxy for scale: the combined ~18k GitHub stars across NeMo Guardrails, Guardrails AI, and LLM Guard implies thousands of teams already assembling partial guardrail stacks who face this exact "which one actually works on our content" decision.
**Mechanism**: today a team either trusts a vendor's self-reported benchmark (run on a prompt set that may not resemble their own domain) or spends days hand-building a comparison harness, as the sourcing PR's own team did. A self-service harness that runs a team's *own* adversarial-plus-benign prompts — which matters because false-positive rate is highly domain-dependent (this same digest's P1 context and the repo's own technical-content-false-positive idea both confirm this) — turns that multi-day build into a config-and-run task.
**Measure**: (1) time from "we need to pick a guard" to a comparison table on the team's own data (target: under a day, versus the multi-day custom build the sourcing PR shows); (2) number of guard options a team actually evaluates before adopting one (more options considered vs. defaulting to whichever guard a blog post mentioned); (3) post-adoption production false-positive rate versus the harness's pre-adoption prediction on the same prompt distribution.

## Why Now
Four maintained guard options (rule engines, ML classifiers, Llama Guard 4, NeMo Guardrails) plus Presidio for PII are all mature and API-accessible today, and a live, dated PR (2026-11-13) shows a real team hand-building exactly this comparison right now — the components exist, only the reusable harness wrapping them doesn't.

## Skill Angle
Trigger: a user describes their guard stack (which guards, how each is invoked) and pastes a sample of 10-20 representative adversarial/benign prompts. The skill drafts the harness config (adapter mappings, expected-label format) and, if the user pastes raw per-guard outputs, scores them into the same detection/FP/latency table by hand — a one-shot version usable before committing to wire up the full runnable harness. The project is the maintained, re-runnable CI tool; the skill is the design/first-pass-scoring aid that proves the comparison is worth automating.

## MVP Sketch
2-3 weeks, 1-2 people. Build adapters for the four guard types named in the sourcing PR plus Presidio, a 200-prompt seed adversarial/benign set (reusing a public jailbreak corpus like a JailbreakBench subset for the attack half), and the comparison runner. Single experiment: run the seed set through all five guards and confirm the harness reproduces each guard's own published or commonly-cited detection rate within a reasonable margin, validating the adapters are faithful before a team trusts the tool on its own data.

## Risks & Open Questions
- A guard vendor (NVIDIA/NeMo, Meta/Llama Guard) could ship its own comparison dashboard and absorb this gap once it's named clearly.
- Normalizing wildly different guard output shapes (a score vs. a rail decision vs. an entity list) into one pass/fail contract risks losing nuance that matters for a specific team's threshold tuning.
- Latency numbers are highly dependent on self-hosting vs. hosted-API choices per guard; the comparison must clearly separate infra-dependent latency from inherent guard latency or it misleads.
- A team's own adversarial prompt set quality bounds the whole result — a thin or stale seed set gives false confidence, same failure mode as the single-vendor self-report this project is meant to replace.
