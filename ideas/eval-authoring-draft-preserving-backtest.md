# No Lost Drafts: A State-Preserving, Backtest-at-Creation Layer for Eval Authoring

- **Status**: PROPOSED
- **Date**: 2026-11-20
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-20-llm-evaluation-observability.md · P3
- **Maturity verdict**: PARTIAL — backtesting against past traffic is mature and multiply-implemented (LangSmith/LangChain's dataset-from-production backtesting, PromptLayer's backtesting-prompt-changes, Sift's cached route backtesting), but none of these combine it with preserving an in-progress draft across a method switch at creation time itself. Langfuse's "restore evaluator versions" lets you test a restored draft before saving, and Glean's agent lifecycle has discard/rollback, but neither addresses losing state mid-switch during initial authoring. PostHog fixed its own case as an internal UX pass (PR #129476).
- **Format**: BOTH — the always-on draft-state cache plus historical-traffic backtest-at-creation requires persistent storage and read access to a trace store; a one-shot "review this eval-authoring flow for state-loss and backtest gaps" is a separable design-review task.
- **Data Sources**: CONNECTED — reads historical production traces via the platform's existing trace-export API (the same class of API as PostHog's own, Langfuse's, or a generic OTel collector) to run the new eval against past traffic at creation time. The in-progress draft itself (prompt text or judge code) is the user's own authored content, persisted locally by this tool in session/local storage rather than read from any external source.

## The Gap
PostHog/posthog PR #129476 (2026-11-04, 6 comments): "People creating an evaluation lose their prompt or code when they switch method and back. A team roast of the eval creation flow found the create page and eval page dense and slow to act on: no way to cover past traffic at create time, pausing needs a trip through the configuration flow." This was surfaced by internal dogfooding, not an outside feature request, and fixed as a one-off UX pass inside one product. No generalized eval-authoring pattern — state-preserving method switching plus historical-traffic backtest at creation time, together — was found documented or packaged as a reusable spec or library.

## The Project
A drop-in authoring-flow layer two platforms or an in-house harness could adopt: (1) a draft-state cache that transparently snapshots an in-progress prompt-based or code-based eval definition whenever the user switches authoring method (or navigates away), restoring it exactly on return instead of discarding it; (2) a "backtest against past traffic" action available at the create step itself — not only after saving — that runs the draft against a window of historical trace data pulled from the platform's existing trace store and reports what it would have flagged historically, complementing (not replacing) the separate live-preview pattern this digest also surfaced (P2, a sibling idea in this ledger).

## Tangible Impact
**Population**: engineers and analysts authoring LLM evals on any platform's creation UI who switch between prompt-based and code-based judge definitions while drafting — a behavior PostHog's own internal dogfooding roast flagged as dense and slow enough to warrant a dedicated fix, suggesting it recurs for any team iterating on judge logic rather than writing it once correctly the first time.
**Mechanism**: removing the risk of losing drafted work on a method switch, and letting a draft be checked against real historical traffic before it is even saved, shortens the iterate-and-discard cycle that currently discourages trying both authoring styles before committing.
**Measure**: number of in-progress drafts lost to a method switch (target: zero, via the cache); % of newly-created evals that were checked against historical traffic before first save (vs. only after); time from first draft to a saved, validated eval.

## Why Now
Teams are authoring eval definitions far more frequently now that eval creation is agent- and API-driven rather than a rare manual task, which raises both the frequency of accidental draft loss and the value of catching a miscalibrated eval against historical data before it is ever saved, not just after.

## Skill Angle
Trigger: a platform or internal-tools team is designing or auditing its own eval-creation UI/flow. Inputs: a description or screenshot walkthrough of the current create flow, including how method switching and historical-traffic access (if any) work today. Output: a structured list of state-loss risks and backtest-at-creation gaps, each with a concrete fix sketch (e.g., "snapshot draft state in a keyed cache on every method-switch event"). This is the one-shot design-review version of the always-on draft-cache-plus-backtest layer the full project builds and runs live.

## MVP Sketch
2–4 weeks, 1–2 people: build the draft-state cache as a small client-side library (keyed snapshot/restore around a method-switch event) and one backtest-at-creation adapter against a toy trace store reproducing PostHog's described flow; validate by scripting a user switching methods twice mid-draft and confirming zero content loss, then running the restored draft against historical traffic before any save.

## Risks & Open Questions
- Overlaps with `eval-definition-live-preview-sandbox.md` (this cycle's P2) — must stay scoped to draft-state preservation and *historical* traffic at the creation step, leaving *live/going-forward* traffic preview to that sibling idea.
- A platform may fix draft-loss with a narrower in-house patch (as PostHog did) and see no need for a portable layer, same adoption risk as other "generalize a vendor's internal UX fix" ideas in this ledger.
- Backtesting against historical traffic at creation time could surface stale or unrepresentative data if the historical window isn't chosen carefully.
- Draft-state caching introduces its own failure mode (a stale cached draft silently overwriting a newer one) that needs an explicit versioning/conflict rule, not an afterthought.
