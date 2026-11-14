# Stack Math: A Compounding-Failure Simulator for Layered Guardrail Pipelines

Every production AI team eventually ends up with a stack of guardrails — a content filter, then a topic classifier, then a tool-call guard, then an output validator — bolted on one at a time, each added because the last one alone wasn't enough. Nobody ever sits down and computes what the whole stack actually does. A team will tell you their pipeline is "pretty solid" because each individual layer tests at 90% accuracy, and they'll be wrong, because five independent 90%-accurate layers chained together compound down to something much worse than 90% — and nobody runs that math before shipping.

## The Gap

A Tian Pan production-guardrails write-up puts a number on the intuition most engineers never check: "stacking five guardrails at 90% accuracy each yields overall system correctness of about 59%." A Galileo guide on production guardrails adds the other half of the problem — that teams pick fail-open versus fail-closed per layer by severity tier, with high-severity safety/compliance checks typically failing closed and lower-severity tone/formatting checks failing open — but this, too, is prose guidance, not something any tool computes for a team's actual measured numbers.

Both pieces describe the same unsolved problem from different angles: the compounding math and the fail-policy tradeoff are talked about as cautionary rules of thumb, not calculated. A search for existing tooling turns up exactly two artifacts — an interactive Monte Carlo simulator (annie2000.github.io/consistency-tax) that lets you fiddle with per-step accuracy and pipeline length, and a layer-redundancy Python snippet on agentpatterns.ai — and both are one-off academic or blog demos, not something a team installs, checks into a repo, and re-runs when a layer's measured accuracy changes. Guardrails AI's "Guard" primitive, the closest thing to a mainstream framework here, stacks validators together but still doesn't model what that stacking does to end-to-end reliability. The real gap isn't the math (it's trivial) — it's that nobody packaged it as a reusable, re-runnable tool.

## The Project

Stack Math is a small simulation library and CLI/web tool that takes a team's actual declared guardrail pipeline — an ordered list of layers, each with a measured true-positive/false-positive/false-negative rate and a stated fail-open-or-closed policy — and runs it through a Monte Carlo simulation across representative traffic mixes (adversarial-heavy, benign-heavy, mixed) to produce the real system-level missed-hazard rate, the real false-block rate, and expected latency. Alongside those headline numbers it generates a sensitivity chart showing exactly which single layer's accuracy swing moves the end-to-end result the most — the weakest link, in other words, not a guess about which layer "feels" most important.

What separates this from the two existing one-off artifacts is packaging: a pipeline is described in a schema (think a YAML file per guardrail stack), which means it's checked into version control and re-run in CI the moment a layer's measured accuracy is updated from a fresh eval run. A static interactive demo tells you what compounding looks like in the abstract; this tool tells a specific team, with their specific five layers and their specific measured numbers, what their specific stack actually does — and keeps telling them, every time the numbers change.

## Tangible Impact

**Population**: engineering teams running three or more chained guardrail checks in production (content filter → topic classifier → tool-call guard → output validator is a typical stack) on top of toolkits like NeMo Guardrails, Guardrails AI, or custom gateway middleware — a proxy for scale is the combined ~18k GitHub stars across those toolkits, implying thousands of teams stacking checks without doing the compounding math.
**Mechanism**: teams today pick a guardrail stack depth and per-layer policy by intuition or a blog post's rule of thumb, not by computing what their specific layers' actual measured accuracy compounds to; a team that believes its 5-layer, 90%-accurate-per-layer stack is safe may actually be shipping a 59%-correct system without knowing it. A simulator that ingests real measured per-layer rates turns a guessed architecture into a computed one, surfacing both over-engineered stacks (adding a redundant layer that barely moves the number) and under-protected ones (a weak layer dominating the failure rate) before an incident forces the discovery.
**Measure**: delta between a team's assumed end-to-end accuracy (naive multiplication or no estimate at all) and the simulator's Monte Carlo output on their real traffic mix; number of pipeline changes (layer removed/reordered/re-tuned) made as a direct result of a simulation run; post-adoption incident rate attributable to guardrail-stack miscalibration, compared to the prior period.

## Try It

A companion Claude Code skill, [`skills/guardrail-stack-compounding-failure-simulator/`](../skills/guardrail-stack-compounding-failure-simulator/), runs the same compounding math as a one-shot judgment call — no library install required. From its `SKILL.md`:

> Computes the real end-to-end missed-hazard rate and false-block rate of a stacked (multi-layer) guardrail pipeline from each layer's measured accuracy/FP/FN numbers, instead of a naive single-accuracy guess, and ranks which layer dominates the result.

To use it: either paste the contents of [`skills/guardrail-stack-compounding-failure-simulator/README.md`](../skills/guardrail-stack-compounding-failure-simulator/README.md) into any AI chat tool along with your pipeline's layer order and measured TPR/FPR/fail-policy numbers, or drop the whole `guardrail-stack-compounding-failure-simulator/` folder into `~/.claude/skills/` if you're running Claude Code, and invoke it directly on your own stack. It will not invent numbers for layers you haven't measured — it asks for the missing data instead, which is the whole point.

Two honest caveats worth carrying over before you lean on either version: getting honest per-layer accuracy numbers in the first place is likely the harder problem, since most teams don't currently measure individual layer accuracy at all — this tool assumes that input exists rather than solving for it. And a guardrail gateway vendor (TrueFoundry, agentgateway.dev) could ship a native reliability-estimation feature tomorrow and absorb this as a point feature rather than leaving it a standalone gap.

---

Surfaced from `research/2026-11-12-ai-safety-guardrails-production.md`, pattern `P7`.
