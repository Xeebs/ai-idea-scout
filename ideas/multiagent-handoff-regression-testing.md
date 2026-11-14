# Contract Watch: Captured-Traffic Regression Testing for Agent-to-Agent Handoffs

- **Status**: EXPLORING
- **Date**: 2026-11-14
- **Topic**: Multi-agent architectures
- **Source**: research/2026-11-14-multi-agent-architectures.md · P4
- **Maturity verdict**: PARTIAL — WebSearch and `gh search repos "agent handoff testing"` found no dedicated, adopted off-the-shelf product. What exists: a cluster of vendor/consultancy DIY recipes (Braintrust's three-level testing, Autonoma, ITECS fixture replay, qawerk, a Testomat.io Claude Code + Playwright pipeline using a handoff.json contract), one narrow research prototype, and PromptSentry (which bundles "multi-agent handoff testing" as one minor feature inside a broader red-teaming toolkit, not a dedicated regression tool). The MAST study (Cemri et al., NeurIPS 2025) reports handoff/specification issues as the largest multi-agent failure cluster (~41.8%), confirming the gap is real and large.
- **Format**: BOTH — the continuously-updated golden-corpus CI harness is PROJECT-shaped infrastructure; diffing a before/after pair of captured handoff examples for schema drift is a separable one-shot analysis task.
- **Data Sources**: CONNECTED (project) — captures real handoff payloads from the team's own staging or production traces (via the same OTel GenAI spans / framework hooks other handoff-tooling ideas in this ledger read) to build a golden-trace corpus automatically; this capture substrate already exists maturely, this project adds the schema-inference-and-regression-check layer on top. MANUAL (skill) — user pastes two sets of example handoff payloads (a "before" set and an "after" set from a recent pipeline/prompt change) to get a schema-drift diff.

## The Gap
WebSearch (qawerk.com, getmaxim.ai) independently recommend "capturing input and output schemas at each boundary" and "automated regression testing that catches context loss at specific agent transitions" as mitigations — implying this isn't standard practice yet, only a recommended-but-unbuilt pattern. The MAST study's 41.8% handoff/specification failure share shows the underlying risk is the single largest cluster of multi-agent failures, yet every mitigation found in this search is a bespoke, hand-rolled recipe (a `handoff.json` contract one team wrote for their own Playwright pipeline) rather than a reusable tool any team can drop into CI.

## The Project
A regression-testing harness that captures representative handoff payloads automatically from real pipeline runs (staging or production traffic, sampled), infers an implicit schema per boundary (field presence, types, size/truncation envelope) from that captured traffic rather than requiring anyone to hand-author a spec up front, and re-runs a held-out sample on every pull request. If a code or prompt change causes a boundary's actual output to violate the schema it has historically satisfied — a dropped field, a truncated payload, a type change — the build fails with the specific boundary and violation named, the same role a snapshot/contract test plays for an API, applied to agent-to-agent handoffs instead.

Components: a traffic sampler that captures handoff payloads from recent runs into a golden corpus; a schema-inference engine (field/type/size envelope per boundary, tolerant of reasonable LLM-output variance); a CI-runnable regression check that replays the held-out corpus against the current build; a PR reporter naming the specific boundary and violation.

## Tangible Impact
**Population**: Engineering teams shipping frequent prompt or pipeline-code changes to production multi-agent systems (support triage, document-processing, coding-review chains) who currently have end-to-end task-success tests but no coverage specifically for the handoff/specification failure class MAST identifies as the largest single cluster of multi-agent failures.
**Mechanism**: Today a handoff-schema regression (a field silently dropped, a payload newly truncated after a prompt edit) is caught, if at all, by an end-to-end test noticing the final task failed — which doesn't localize to the boundary responsible and can miss subtler quality degradation entirely. Auto-capturing a golden corpus and regression-testing against it moves detection to PR time, with the specific boundary and violation named, instead of a vague end-to-end failure discovered later.
**Measure**: (1) percentage of handoff-schema-drift-causing changes caught at PR time vs. discovered only in production or via an end-to-end test failure, on a pilot team's repo; (2) reduction in the MAST-style handoff/specification failure share measured against the team's own incident log, before vs. after adoption; (3) time to add test coverage for a new boundary (near-zero, since schemas are inferred from captured traffic rather than hand-authored).

## Why Now
The MAST study's handoff/specification failure-rate finding was published and widely cited through 2026, giving teams a credible reason to prioritize this specific failure class, at the same time frameworks' maturing OTel GenAI instrumentation makes automatic payload capture at each boundary feasible without bespoke per-team logging.

## Skill Angle
Given two pasted sets of example handoff payloads — a "before" set from the current production behavior and an "after" set from a staged change — infer the implicit schema each set satisfies and flag any field dropped, type changed, or truncation introduced in the "after" set that the "before" set never exhibited. Useful as a quick pre-merge sanity check before any continuous capture pipeline is wired up.

## MVP Sketch
Instrument one framework's handoffs (LangGraph) to capture payloads from 50–100 real or synthetic runs into a golden corpus; infer a lightweight per-boundary schema tolerant of normal LLM variance; build a CI check replaying a held-out sample against a new build. Experiment: deliberately introduce a truncation bug via a prompt edit on a test branch and confirm the check flags the specific boundary, versus a control relying only on end-to-end task-success tests. 2–3 weeks for 1–2 people.

## Risks & Open Questions
- Overlaps conceptually with this repo's existing "Contract Layer" idea (a hand-authored declarative spec checked statically at build time) — this project is the deliberate complement, not a competing implementation: Contract Layer validates a spec the team writes down explicitly, this project auto-derives and continuously regression-tests against what the pipeline actually does in practice, for teams who haven't (or won't) hand-author a spec. The two could later share a schema representation, but the authoring source and detection trigger (declared vs. observed) are distinct.
- Schemas inferred purely from captured traffic risk overfitting to the sample — a legitimate new-but-rare field shape could be flagged as a false-positive regression unless the tolerance model is designed carefully.
- Flaky, naturally-variable LLM outputs could produce noisy drift alerts unless the schema check tolerates reasonable variance rather than exact matching.
- PromptSentry's maintainers could extend its existing minor handoff-testing feature into a dedicated competing tool before this gains adoption.
