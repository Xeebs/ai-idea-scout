# Who Drifted: A Judge-vs-App Attribution Layer for Golden-Prompt Drift Alerts

- **Status**: EXPLORING (promoted 2026-11-20 cycle 290: evidence density — ≥2 independent threads)
- **Date**: 2026-11-20
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-20-llm-evaluation-observability-ii.md · P2
- **Maturity verdict**: PARTIAL — GitHub search for "judge drift" turned up a dozen+ small repos, almost all narrow/one-off (`homayoun-safarpour/judge-drift-sentinel`, days old, PyPI upload still pending; `avalyset/inspect-judge-drift`; `Priyanshi0907/llm-regression-detector`; several unlabeled student/POC repos). An arXiv paper (2606.15474, "Who Drifted: the System or the Judge?") proposes an attribution method academically, not as a shipped tool. No mainstream observability vendor (Galileo, Arize, Evidently, WhyLabs, Langfuse) was found tracking judge-version drift as a distinct signal separate from app-output drift.
- **Format**: BOTH
- **Data Sources**: CONNECTED (project) / MANUAL (skill) — the Project hooks directly into whatever judge/evaluator call an existing golden-prompt or canary scheduler already makes (OneUptime-style scheduled runs, in-house cron harnesses), reading the model id/version string, grading-prompt/rubric text, and scoring-logic version it already has in hand — no new external API, just recording metadata already present in the call path. The Skill Angle is MANUAL — the user pastes the current and prior run's judge-identity fields (model id, grading prompt/rubric text, scoring code version) and the two scores for a one-shot triage.

## The Gap
OneUptime's "How to Monitor Silent LLM Output Drift with Scheduled Golden-Prompt Runs" (2026-11-16) explicitly recommends "recording the returned model identifier and checking whether the evaluator itself changed before blaming the application" — a direct acknowledgment that teams currently conflate the two. A dev.to incident narrative (decimozs, "I broke a chatbot with a prompt change then I built the tool that would've caught it") describes debugging the app first, then hand-building a fix after getting burned. Both are one author's own ad hoc recipe or one-off tool, not a packaged product; PromptLayer's drift glossary and promptfoo's CI diffing both track app-level drift only, with no separate judge/evaluator-drift signal.

## The Project
A lightweight attribution layer that attaches to an existing golden-prompt/canary scheduler rather than replacing it. On every scheduled run it records a judge-identity bundle — model id/version, grading-prompt/rubric hash, scoring-logic version — alongside the score. When a score movement crosses the scheduler's own alert threshold, the layer first diffs the current judge-identity bundle against the prior run's: if the bundle changed, the alert is retagged "evaluator-side change — verify before investigating the app," naming exactly which field changed; if unchanged, the alert passes through as an app-side signal. A rolling judge-identity timeline lets flagged alerts be cross-referenced retroactively against known evaluator-version changes.

Components: judge-identity recorder (hooks into the judge call the scheduler already makes); a diff step run on each new score against rolling identity history; an attribution tag decorating the existing alert payload (not a new alerting system); a timeline view of judge-identity changes for audits.

## Tangible Impact
**Population**: Engineering teams running scheduled golden-prompt/canary drift checks (OneUptime-style guides, promptfoo-adjacent setups, in-house cron harnesses) whose judge/evaluator is itself an LLM call subject to silent provider-side model bumps or in-house prompt/rubric edits — the practitioner population evidenced directly by the OneUptime guide and the decimozs incident post.
**Mechanism**: Today, when a golden-prompt score moves, an engineer must manually determine whether the app or the judge changed before investigating — decimozs's own narrative shows debugging the app first and being wrong. Auto-tagging the alert with a judge-identity diff removes that manual triage step and the misdirected investigation time it causes.
**Measure**: (1) % of golden-prompt drift alerts correctly auto-tagged judge-side vs. app-side, validated against a labeled set of historical incidents; (2) reduction in median time-to-correct-root-cause for a drift alert versus the decimozs-style "debugged the app first" baseline; (3) number of false app-regression investigations avoided per month post-adoption.

## Why Now
Judge/evaluator model churn — frequent silent provider-side model-version bumps and in-house rubric iteration — accelerated through 2026 at the same time scheduled golden-prompt/canary checks became common practice (per OneUptime's Nov 2026 guide), making misattribution a now-frequent, not hypothetical, failure mode while no shipped tool tags for it.

## Skill Angle
Trigger: an engineer sees a golden-prompt/canary score move and wants a fast first-pass answer to "is this my app or my judge" before investigating. Inputs: the current and prior run's judge-identity fields (model id/version, grading prompt or rubric text, scoring code version) and both scores, pasted as text/JSON. Output: a one-shot verdict — "judge-identity unchanged, investigate the app" or "judge-identity changed: `<field, e.g. model id 'gpt-5.1-eval' → 'gpt-5.2-eval'>` — verify judge behavior before blaming the app" — plus a one-line note on what changed. The skill is the one-off triage question; the project is the thing that tags every alert automatically going forward.

## MVP Sketch
2 weeks, 1 person: build the judge-identity recorder as a thin wrapper logging `{model_id, grading_prompt_hash, scoring_logic_version}` alongside whatever an existing golden-prompt scheduler already logs for scores; add a diff-on-alert step that retags the alert. Validate with two synthetic scenarios: swap only the judge's model/prompt (app unchanged) and confirm the tool suppresses a false app-regression alarm; swap only the app's output (judge unchanged) and confirm the alert passes through untagged.

## Risks & Open Questions
- Many ad hoc in-house golden-prompt schedulers (like decimozs's) don't yet log judge-identity metadata consistently — adoption requires at least a few fields already present in the call path.
- Overlaps conceptually with this index's `judge-calibration-runtime-drift-verifier.md`, which diffs a runtime judge call against a stored calibration snapshot — differs in trigger (per-score-movement attribution vs. pre-flight calibration consistency) and mechanism (rolling identity history vs. one-time snapshot), but the two could converge into one product; worth tracking for consolidation if either ships first.
- The arXiv "Who Drifted" paper's attribution method is statistically rigorous (likelihood-based); if this MVP's simple identity-diff produces false "judge changed, ignore" dismissals on cosmetic rubric edits, a later version may need that approach.
- Could be judged solved-enough if teams simply pin their judge model/prompt version and treat any change as a manual re-baseline event — worth checking whether that workaround already covers most real-world cases.
