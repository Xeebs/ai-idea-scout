# Calibration Check: Verifying a Judge's Runtime Call Actually Matches What Was Calibrated

- **Status**: PROPOSED
- **Date**: 2026-11-19
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-19-llm-evaluation-observability.md · P1
- **Maturity verdict**: OPEN — GitHub + web search found only PostHog's own internal bug-fix PRs (the cited evidence) and a brand-new 0-star personal side project (`judge-drift-sentinel`, created 2026-11-08) that answers a different question (score-movement attribution via a frozen human anchor set, not runtime-vs-calibration config verification). Langfuse's published judge-calibration skill only compares judge labels to ground truth, with no check that the production judge call uses the same prompt/tool-catalog/context as calibration. No credible implementation closes this specific gap.
- **Format**: BOTH
- **Data Sources**: CONNECTED — the Project wraps the team's own eval platform's existing judge-execution path: it reads the stored calibration snapshot (the exact prompt, context window, and tool catalog used when the judge was calibrated) and intercepts the actual runtime judge call the pipeline is already making, diffing the two. No new external API is introduced; it inspects calls and config the platform already has. The Skill Angle is MANUAL — the user pastes the calibration config and the runtime judge-call config (both as JSON or code snippets) for a one-shot audit.

## The Gap
PostHog/posthog PR #136283 (2026-11-16) added judge calibration against live traffic; its direct follow-up PR #136602, same day, had to fix it because "calibration sent a few hundred characters of each call, without the tool catalog" and "its copy of the judge's system prompt had drifted from the runtime one." A team believed its judge was validated when the thing actually scored in production was a different call entirely. Corroborating skepticism: Hacker News "Using LLM for confidence scoring is a bad idea" (228 points/107 comments) reflects broader distrust of unverified judge scores. PostHog patched this once, inside its own product, as a bug fix — not as a reusable safeguard any other eval platform or in-house harness can adopt.

## The Project
A vendor-neutral verification layer that sits between a team's judge-calibration step and its runtime judge-call code. On every calibration run, it snapshots the exact prompt, context length, tool catalog, and model/version used. On every runtime judge invocation, it diffs the live call against the most recent matching snapshot and flags any divergence — stale system prompt, missing tool catalog, truncated context, model swap — before the score is trusted. Divergences surface as a structured warning attached to the eval run, not a silent pass.

Components: a calibration-snapshot recorder (hooks into the calibration step); a runtime-call interceptor (hooks into the judge-invocation step); a diff engine comparing prompt/context/tool-catalog/model fields; a reporting surface (CI annotation or dashboard badge: "this score's judge diverged from calibration by X").

## Tangible Impact
**Population**: Engineering teams running LLM-as-judge eval pipelines who rely on a calibration pass to trust their judge's scores — users of auto-judge-drafting products (PostHog AI evals and similar) and teams running their own in-house calibrated judges that gate releases or dashboards on judge scores. PostHog's own fix was prompted by this clustering as a real production bug within one two-week window, suggesting the failure mode is common wherever calibration and runtime are separate code paths.
**Mechanism**: Today, a team's confidence in a judge score rests on an unverified assumption that the judge was actually validated against what it runs in production; a silent divergence (missing tool catalog, stale prompt, truncated context) means every downstream decision — a release gate, a dashboard trend, a regression alert — is trusting a score from an effectively uncalibrated judge. The verifier makes that assumption checkable and loud instead of silent.
**Measure**: Number of real prompt/context/tool-catalog divergences caught per team per month (baseline: 0, since nothing currently checks this); % of eval runs with a verified-matching calibration snapshot before vs after adoption; time from a judge-config change (e.g., a prompt edit) to detection of a calibration/runtime mismatch (target: same CI run, vs. undetected today).

## Why Now
LLM-judge eval volume scaled enough in 2026 that calibration pipelines became common practice, but calibration and runtime are still built as two separate code paths across every platform examined — meaning the exact class of bug PostHog just patched internally is structurally likely to recur anywhere else the same pattern exists, and no shared tool exists yet to catch it generically.

## Skill Angle
Trigger: a team wants a one-shot sanity check on whether their calibrated judge matches what actually runs in production, without installing continuous middleware. Inputs: the calibration-step config (prompt, context sample, tool catalog used during calibration — pasted as JSON or code) and the runtime judge-call config (same fields, pasted from the live invocation code or a logged call). Output: a field-by-field diff report naming exactly which fields match, which diverge, and the likely production impact of each divergence (e.g., "runtime includes 3 tools absent from calibration — judge may score differently on tool-related failures than validated"). The skill is the one-off audit; the project is the continuous interceptor running on every eval.

## MVP Sketch
2–3 weeks, 1–2 people: build the snapshot recorder and interceptor for one eval framework (start with a thin wrapper around raw OpenAI/Anthropic SDK calls, since most in-house harnesses call providers directly), plus a diff engine covering prompt text, context length, and tool-catalog presence. Validate by deliberately introducing a PostHog-style drift (edit the runtime prompt without updating calibration) and confirming the tool flags it before the next eval run completes.

## Risks & Open Questions
- If PostHog's fix becomes a documented best practice that other platforms copy ad hoc, the market for a shared tool shrinks — worth validating demand beyond the one evidenced platform before building broadly.
- Diffing "meaning," not just literal text, is hard — a prompt that's semantically equivalent but reworded shouldn't false-positive; the MVP's literal-diff approach may need a semantic-similarity layer later.
- Teams using fully closed eval SaaS products may have no hook point to intercept the runtime call at all, limiting addressable surface to self-hosted/in-house harnesses.
- Could be judged solved-enough if teams simply re-run calibration on every prompt change rather than verifying drift after the fact — worth checking whether that workaround is already common practice.
