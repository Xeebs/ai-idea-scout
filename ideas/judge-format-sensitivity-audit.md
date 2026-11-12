# Format Check: A Judge Output-Format Sensitivity Audit for LLM-as-Judge Setups

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-12-llm-evaluation-observability-ii.md · P6
- **Maturity verdict**: PARTIAL — an arXiv paper ("Judge Circuits Explain Format-Induced Inconsistency in LLM-as-a-Judge") diagnoses that the same judge model scores systematically differently depending on requested output format (1-5 Likert vs. True/False); related research code (`github.com/penfever/bias-bounded-evaluation`, `github.com/UW-Madison-Lee-Lab/LLM-judge-reporting`) measures or corrects for this narrowly, and practitioner posts recommend manual mitigations (format-neutrality rubric language, rewrite-in-three-formats bias tests) — but nothing packages this as an adopted, production-usable audit tool.
- **Format**: SKILL — the whole job is "given this judge prompt, test it across output formats and report the sensitivity" — a one-shot analysis with no persistent state or infrastructure required.
- **Data Sources**: MANUAL — the user pastes their existing LLM-as-judge prompt/rubric text and a handful (10-30) of example inputs they want scored, so the skill can re-run the judge across multiple output-format variants on the same inputs and compare. No mature cross-vendor connector exists for reading live judge configurations uniformly across eval platforms, and the object being tested (a specific prompt's design) is inherently something the user authored and hands over directly rather than something a connector would fetch.

## The Gap
The cited arXiv paper argues that judge-score comparisons may partly be measuring a brittle output-formatting stage rather than the underlying judgment — the same model produces different scores depending on whether it's asked for a 1-5 scale or a True/False label. Related academic code measures bias including format sensitivity, and practitioner mitigation advice exists (format-neutral rubric phrasing, testing the same judge across three output formats), but every source treats this as a manual, ad hoc check a sophisticated team runs themselves — there's no accessible tool that takes a team's actual judge prompt and tells them, concretely, how much their scores would shift if they'd picked a different output format.

## The Project
A skill that takes a team's judge prompt/rubric and a batch of example inputs, runs the judge across 2-3 common output-format variants (Likert scale, binary pass/fail, free-text-then-extracted-score) on the identical inputs, and reports the score divergence per variant — flagging specifically whether the team's current format choice is unusually unstable compared to the alternatives, and whether a format-neutrality rewrite of the rubric (per the practitioner mitigation pattern) measurably narrows that divergence.

## Tangible Impact
**Population**: ML/eval engineers building or maintaining an LLM-as-judge setup used in a CI gate, production quality dashboard, or model/vendor comparison report — the same audience reading the judge-bias research (arXiv papers, Google's public statements on judge subjectivity) but with no accessible way to check whether their *specific* judge prompt's output-format choice is itself a source of noise, as opposed to a deeper bias issue.
**Mechanism**: Today a team either doesn't know format sensitivity is a factor in their judge's variance, or knows the research exists but has no concrete number for their own setup, so they can't tell whether a surprising score swing between two model/prompt versions reflects a real quality difference or just format-induced noise. The audit turns "is my judge format brittle" into a measured divergence percentage specific to their prompt, with a concrete before/after if they adopt the format-neutrality fix.
**Measure**: (1) measured score divergence (e.g., standard deviation or rank-correlation shift) across output-format variants on the same inputs, reported per judge setup audited; (2) divergence reduction after applying the format-neutrality rubric rewrite, targeting a visible narrowing on the pilot's own data; (3) number of judge setups where the audit surfaces format sensitivity large enough to plausibly explain a previously-unexplained score swing the team had already noticed.

## Why Now
The underlying research (the Judge Circuits paper) crystallized the mechanism in 2026, and running the same judge prompt across a handful of format variants on a small batch of inputs is cheap and fast with current model pricing — nothing here waits on new capability, only on someone packaging the check.

## MVP Sketch
A script that takes a judge prompt template and a CSV/JSON of 10-30 example inputs, generates the three format variants (Likert, binary, free-text-then-extract) by substituting the output-instruction portion of the prompt, runs all three against the same inputs via the team's chosen model API, and computes per-item and aggregate score divergence, outputting a short report with a recommendation. Experiment: run it against one real production judge prompt with a known or suspected score-stability issue, and confirm the audit's divergence number is directionally consistent with what the team already informally observed. 1-2 weeks, 1 person.

## Risks & Open Questions
- This only catches format-induced variance, not the broader position/self-preference bias the related "Judge Check" idea in this repo addresses — a team could pass this audit cleanly and still have a badly biased judge for other reasons, so this needs to be positioned as one check among several, not a complete judge-trust audit.
- Format-neutrality rubric rewriting is itself an underspecified craft with no settled best practice; the mitigation half of this skill risks being weaker than the diagnostic half.
- A small (10-30 item) batch may not be large enough to detect subtle divergence reliably, and running larger batches across three format variants triples judge-call cost for the audit itself.
- A well-resourced eval vendor (Braintrust, Galileo, judicator) could fold this specific check into an existing broader bias-audit feature, narrowing this skill's differentiation window.
