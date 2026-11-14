# Stack Math: A Compounding-Failure Simulator for Layered Guardrail Pipelines

- **Status**: PUBLISHED
- **Date**: 2026-11-12
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-12-ai-safety-guardrails-production.md · P7
- **Maturity verdict**: PARTIAL — WebSearch found an existing interactive Monte Carlo simulator (annie2000.github.io/consistency-tax) and a layer-redundancy Python snippet (agentpatterns.ai), but both are one-off academic/blog artifacts, not a maintained product integrated into any guardrail framework (Guardrails AI's "Guard" primitive stacks validators but doesn't model compounding reliability). Real but thin and unintegrated coverage.
- **Format**: BOTH
- **Data Sources**: MANUAL — the team types or pastes each guardrail layer's measured accuracy/false-positive/false-negative rate, the declared pipeline order, and each layer's fail-open-vs-fail-closed policy. A CONNECTED upgrade — pulling live per-layer pass/fail rates automatically from an observability backend (Langfuse, Arize, Datadog) that already captures OTel GenAI guardrail spans — is a plausible v2, but no mature connector purpose-built for "per-layer guardrail accuracy over time" exists today, so MANUAL is the honest classification for the MVP.

## The Gap
A Tian Pan production-guardrails write-up warns that "stacking five guardrails at 90% accuracy each yields overall system correctness of about 59%," and a Galileo guide describes a fail-open/fail-closed policy choice per severity tier — both presented as prose cautionary rules of thumb, not computed by any tool. No maintained product lets a team plug in its actual stacked guardrail layers and see the real compounded reliability number before shipping; the one interactive simulator and one code snippet found are unmaintained one-off artifacts, not something a team adopts and keeps using.

## The Project
A small simulation library and CLI/web tool that takes a team's declared guardrail pipeline — an ordered list of layers, each with a measured (not assumed) true-positive/false-positive/false-negative rate and a fail-open-or-closed policy — and runs a Monte Carlo simulation across representative traffic mixes (adversarial-heavy, benign-heavy, mixed) to output the system-level missed-hazard rate, false-block rate, and expected latency, with a sensitivity chart showing which single layer's accuracy swing moves the end-to-end number most. Unlike the existing one-off simulators, this ships as an installable library with a schema for describing a pipeline (so it can be checked into a repo and re-run in CI whenever a layer's measured accuracy changes) rather than a static interactive demo.

## Tangible Impact
**Population**: engineering teams running three or more chained guardrail checks in production (content filter → topic classifier → tool-call guard → output validator is a typical stack) on top of toolkits like NeMo Guardrails, Guardrails AI, or custom gateway middleware — a proxy for scale is the combined ~18k GitHub stars across those toolkits, implying thousands of teams stacking checks without doing the compounding math.
**Mechanism**: teams today pick a guardrail stack depth and per-layer policy by intuition or a blog post's rule of thumb, not by computing what their specific layers' actual measured accuracy compounds to; a team that believes its 5-layer, 90%-accurate-per-layer stack is safe may actually be shipping a 59%-correct system without knowing it. A simulator that ingests real measured per-layer rates turns a guessed architecture into a computed one, surfacing both over-engineered stacks (adding a redundant layer that barely moves the number) and under-protected ones (a weak layer dominating the failure rate) before an incident forces the discovery.
**Measure**: delta between a team's assumed end-to-end accuracy (naive multiplication or no estimate at all) and the simulator's Monte Carlo output on their real traffic mix; number of pipeline changes (layer removed/reordered/re-tuned) made as a direct result of a simulation run; post-adoption incident rate attributable to guardrail-stack miscalibration, compared to the prior period.

## Why Now
The compounding-error framing is now a live talking point in 2026 production-guardrails write-ups (Tian Pan, Galileo), meaning teams are already primed to want the number; Monte Carlo simulation over a handful of probability parameters is trivial compute, and the only missing piece is packaging it as a reusable, pipeline-schema-driven tool instead of a one-off demo page.

## Skill Angle
Trigger: a team hands over their guardrail pipeline's layer order, each layer's measured accuracy/FP/FN numbers (from their own eval set or production logs), and declared fail-open/closed policy per layer. The skill runs the same compounding-failure math as a one-shot judgment, returning the computed end-to-end missed-hazard and false-block rates plus a plain-language flag of the weakest link, without the team installing or maintaining anything. The project differs by being the always-available library/CI check that re-runs this automatically every time a layer's measured accuracy is updated, rather than a single point-in-time estimate.

## MVP Sketch
A Python library (`pip install stackmath`) taking a YAML pipeline description (layer name, TP/FP/FN rate, fail-open/closed flag, order) and running a configurable-iteration Monte Carlo simulation across 2–3 traffic-mix presets, outputting a JSON report plus a simple matplotlib sensitivity chart. Single experiment: feed it the Tian Pan "five guardrails at 90% each" scenario and confirm it reproduces the ~59% figure, then vary one layer's accuracy to show the sensitivity chart correctly identifies it as the dominant factor.

## Risks & Open Questions
- Getting honest per-layer accuracy numbers from a team in the first place may be the harder problem — most teams don't currently measure individual layer accuracy at all, which this tool assumes as an input rather than solving.
- A guardrail gateway vendor (TrueFoundry, agentgateway.dev) could bundle a native reliability-estimation feature, absorbing this as a point feature rather than leaving it a standalone gap.
- Monte Carlo output is only as good as the assumed traffic-mix presets; a team's real traffic distribution may not match any preset, requiring a custom-mix input path from day one, not as a v2 feature.
- Community-demand signal here is thin (two blog posts, not a discussion thread), so validating real pull means checking whether teams run the tool against their own numbers, not just read about the math.
