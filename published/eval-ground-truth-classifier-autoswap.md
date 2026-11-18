# Swap Call: An Automatic Ground-Truth-Classifier Distillation Layer for LLM-as-Judge Pipelines

Airbnb published a benchmark this month with a blunt title: "Frontier quality at 1% of the cost." The claim is that for narrow, ground-truth-having classification tasks, a small trained classifier can match a frontier LLM judge's accuracy at a sliver of the inference bill. It's a compelling result — and it's also, as far as anyone can find, a one-off. Nobody has packaged the obvious next step: a tool that looks at a team's own eval tasks, figures out which ones actually have ground truth, trains the cheap classifier, proves it's safe, and swaps it in behind the existing judge-call interface.

## The Gap

Airbnb's write-up and a corroborating "skeptic's view" opinion piece both make the same point from different angles: closed-form tasks with real ground truth don't need a frontier model acting as judge — a trained classifier does the job for a fraction of the cost. But both are a single company's internal benchmark and a general argument, not something you can install. Digging further than the original digest turned up real adjacent work — vendor playbooks describing three-tier eval setups (heuristics, a distilled judge, a human gold set), ZeroEntropy's "distillation drift" playbook warning that distilled judges silently degrade as production input shifts away from what they were trained on, and LinkedIn's SAGE framework (arXiv 2602.07840), which distills a frontier teacher judge into cheaper student surrogates at reported 92x lower cost and over 10,000 QPS. None of it is the thing itself: an automated layer that detects ground-truth availability on a live eval task, trains and validates a student classifier, and reverts automatically when drift shows up. That's the gap.

## The Project

The idea is a closed-loop distillation-and-swap pipeline that sits in front of an existing eval harness's judge-call interface — promptfoo, deepeval, Langfuse, or a custom one. It scans a team's eval tasks for ones that already have sufficient labeled ground truth or a deterministic grader, trains a lightweight student classifier against the frontier judge's historical verdicts plus the real ground truth (the SAGE-style approach), validates agreement against a held-out gold set before any live traffic touches it, and only then swaps the classifier in behind the same interface the harness already calls — so nothing upstream has to change. The pipeline keeps watching afterward: a drift monitor tracks disagreement and input-distribution shift in production, and reverts to the LLM judge automatically the moment either crosses a declared threshold, which is exactly the failure mode ZeroEntropy's playbook documents happening silently when nobody's watching.

Components: a ground-truth-availability scanner, a SAGE-style student-classifier trainer, a held-out-gold-set agreement validator, a judge-call-compatible shim, and a distribution-drift monitor with auto-revert.

## Tangible Impact

**Population**: engineering teams running production LLM pipelines with narrow, ground-truth-having classification or scoring tasks evaluated via LLM-as-judge at scale (content-safety flags, support-ticket routing correctness, structured-field extraction correctness) — the exact pattern Airbnb's benchmark measured, and a pattern common enough that promptfoo and deepeval alone cross 46,000+ combined GitHub stars, suggesting a large population running this judge-call pattern today, most of whom have at least one eligible task they haven't identified or distilled.

**Mechanism**: converts a judge call costing full frontier-model price per evaluation into a classifier call at roughly 1% of that cost for every task where ground truth exists — automatically, with a safety net that reverts to the LLM judge the moment accuracy or input distribution drifts — so teams capture Airbnb-level savings without needing an internal ML team to replicate Airbnb's benchmark work from scratch.

**Measure**: (1) percent cost reduction per eligible eval task, targeting Airbnb's cited ~99%; (2) classifier-vs-frontier-judge agreement on a held-out gold set (within 2 points of F1/accuracy before swap-in is allowed); (3) time-to-detect and auto-revert when production distribution shifts, measured in evaluation runs rather than weeks of unnoticed degradation.

## Try It

A companion skill already exists at [`skills/eval-ground-truth-classifier-autoswap/`](../skills/eval-ground-truth-classifier-autoswap/): "Judges whether a specific LLM-as-judge eval task is a good candidate to distill into a cheap trained classifier, before a team commits to building the always-on distillation pipeline." It's the one-shot design-judgment half of this idea — the go/no-go call a team makes before building the runtime infrastructure above. Paste or upload the eval harness's judge-call export (or the judge prompt plus 15–30 example verdicts if no export exists), and it hands back a GO/CAUTION/NO-GO verdict, the gold-set size needed to validate safely, and a drift-monitoring recommendation — using the README in any AI chat tool, or by dropping the folder into `~/.claude/skills/` for Claude Code.

## Why Risks Remain Open

Airbnb's benchmark is single-company and task-specific — this project's own per-task agreement validation has to re-prove the result each time rather than assume it generalizes. Drift detection without a continuous stream of fresh ground truth degrades to plain input-distribution drift, which is a weaker signal than actual accuracy decay and may understate real degradation. An eval vendor could also productize SAGE-style distillation natively before this ships standalone, closing the gap from the platform side — and a fresh look at the landscape turned up close adjacent moves already underway: a "Codifying the Judge" paper on program-based judge distillation, and at least one small community tool (an unverified ClawHub skill called `llm-eval-router`) attempting a piece of this. Finally, "ground-truth availability" detection is itself fuzzy — tasks with partial or noisy ground truth risk a false-positive "eligible for distillation" call that silently degrades eval quality instead of improving cost.

---

Surfaced from `research/2026-11-18-llm-evaluation-observability.md`, pattern `P5`.
