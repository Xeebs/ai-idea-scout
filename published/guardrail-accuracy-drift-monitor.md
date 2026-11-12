Every team running LLM guardrails in production ran an evaluation at some point — scored the classifier against a snapshot of real traffic, confirmed it caught the jailbreaks and content violations they cared about, and shipped it. Nobody reruns that evaluation on a schedule. The guardrail just sits there, quietly assumed to still be working, while the traffic flowing past it keeps changing shape.

## The Gap

Decagon's own glossary entry on guardrail evaluation says it plainly: a guardrail that passed evaluation six months ago may no longer hold against today's input patterns. That's not a hedge in fine print — it's a vendor stating the obvious and then moving on, because nobody has built the thing that would actually catch it happening. The surrounding landscape backs that up. Arize and FutureAGI have published comparison posts on guardrails-versus-evals that describe the same blind spot without closing it. IBM ships runtime-monitoring dashboards and Galileo ships threshold-based drift alerts — but both are generic, pointed at model-output drift or agent-behavior drift, not at the guardrail checks themselves. A DEV Community post even named the problem outright: "Your guardrails are decaying and you aren't measuring it." The building blocks for drift detection are mature and commodity-priced. Nobody has aimed them at the one layer that's supposed to be the safety net.

## The Project

Guard Drift treats guardrail-check accuracy as a metric under continuous surveillance, the same way a model-quality dashboard treats output quality — instead of a one-time evaluation that's assumed to hold forever. It periodically samples recent traffic that each guardrail category has passed or blocked, re-scores a stratified subset with a stronger reference judge (or routes a slice to periodic human spot-check to avoid judging the guardrail with another guardrail-shaped tool), and computes a rolling precision/recall estimate per category. When a category's estimated accuracy crosses a configured threshold, it alerts — naming the specific check that's decaying and what kind of input is breaking it, with enough lead time to recalibrate before an incident or a user complaint forces the issue.

The core loop is simple on purpose: sample, re-judge, trend, alert. The differentiator is where it points. Generic drift tooling watches whether the model's outputs are drifting from expected quality. This watches whether the guardrail's verdicts are still correct — a distinct failure mode that the rest of the market has described but not instrumented.

## Tangible Impact

**Population**: ops and trust-safety teams operating production LLM guardrail stacks whose input traffic shifts over time (customer support platforms, content moderation vendors, agent platforms) — specifically teams built on NeMo Guardrails, Guardrails AI, or LLM Guard (combined ~18k GitHub stars, a proxy for deployment scale) who today re-tune guardrails only reactively, after an incident or complaint.

**Mechanism**: guardrails evaluated once against a traffic snapshot silently lose accuracy as real input patterns shift (new jailbreak phrasing, new product surfaces, new user populations); without a dedicated decay signal, teams discover failures only after a missed-harm incident or an over-blocking complaint. A continuous monitor gives the specific decaying category and lead time to recalibrate proactively.

**Measure**: lead time between a decay alert firing and the next real incident/complaint tied to that category (goal: alert precedes incident); reduction in mean time-to-detect guardrail decay versus the team's prior reactive baseline; number of recalibrations triggered proactively by the monitor vs. reactively by an incident, post-adoption.

## Try It

There's no packaged skill or runnable monitor for this yet — the idea is still at the EXPLORING stage, ahead of a `skills/guardrail-accuracy-drift-monitor/` build. The project's own idea file sketches a one-shot diagnostic version of this (point a session at a sample export of recent guardrail decision logs and get a report on which categories show drift) as the natural first cut of a skill, distinct from the always-on monitoring service described above. Check back on this repo for a companion skill directory once it exists.

Worth saying up front, because the idea file says it too: establishing the "ground truth" to re-judge against is itself close to the guardrail problem. Anchor it with periodic human-labeled gold slices rather than another automated judge, or the comparison risks circularity. And this is a niche that Galileo or IBM could extend into quickly once it's named publicly — the differentiation has to stay guardrail-specific, not another generic drift dashboard with a new label.

Surfaced from `research/2026-11-12-ai-safety-and-guardrails-in-production.md`, pattern `P3`.
