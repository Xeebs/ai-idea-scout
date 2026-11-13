# Canary Set: Catching Golden Eval-Set Drift Before It Silently Breaks CI Gates

Your CI eval gate has been green for months. Your users are not happy. Those two facts are not a contradiction — they're the default state of a team that froze a "golden" eval set at launch and never asked whether it still looks anything like what people actually do with the product today. Nobody deletes a passing check. Nobody notices a eval set quietly going stale, either — until a regression ships straight through a gate that was testing last year's traffic.

## The Gap

A practitioner writing at tianpan.co spent three posts in April 2026 working through exactly this failure mode — "golden dataset decay / eval liability," "The Eval-Set-as-Simulator Drift," and "Your Gold Eval Set Has Drifted" — and landed on a blunt framing: "Eval dataset drift is the silent killer... the nightly job runs against a sample of yesterday's production traces so you catch drift the fixed set will not." The fixes the author describes — embedding-divergence monitoring, versioning the dataset and judge prompt together, nightly re-scoring against fresh traffic — are sound, well-reasoned, and entirely personal practice. There's no shared repo, no named product, nothing another team could just adopt. A multi-channel search for "golden eval set drift detection" and "eval dataset drift" turns up zero GitHub implementations and zero products addressing it. The knowledge exists; the tool doesn't.

That's worth sitting with for a second, because the underlying techniques here aren't exotic — embedding divergence and dataset versioning are both well-understood. The gap isn't capability, it's packaging: one sharp practitioner figured this out the hard way and wrote it down, and nobody has turned it into something a second team can install instead of rediscovering.

## The Project

Canary Set is a scheduled service that treats your golden eval set the way you'd treat any other production asset that can go stale: it watches it. Every night, it embeds the golden set and a rolling sample of recent production traces, then computes a divergence metric between the two — Jensen-Shannon divergence over embedding clusters, or straightforward new-intent-cluster detection — to answer one question: has production drifted away from what the golden set actually tests?

When a production intent cluster has grown without a matching golden-set example, the system flags it. It also version-stamps the golden set and the judge prompt together, so when a CI score moves, you can tell whether that's a real model regression or just someone quietly editing an eval asset without anyone noticing. And rather than leaving the fix as homework, it proposes specific, real production traces as candidate additions to the golden set, ready for a human to review and accept.

The pieces: an embedding-plus-clustering pipeline running on a daily sample; a divergence scorer with tunable alert thresholds; a version ledger tying golden-set state to judge-prompt state; and a weekly report surfacing uncovered production clusters with concrete example traces attached, not just a number.

## Tangible Impact

**Population**: Teams running LLM/agent products with a fixed golden-eval-set CI gate who ship weekly or faster — the same population the tianpan.co posts are written for (a practitioner who personally hit this), realistically any team past the prototype stage with more than one eval-gated release per week and a live user base generating traffic distinct from launch-day traffic.
**Mechanism**: Today a golden set quietly stops representing live traffic as new user intents emerge, so a CI gate keeps reporting a passing score while the product's real, current failure modes go untested. The drift monitor turns that invisible decay into a weekly "here are N new intent clusters in production not covered by your golden set" report, so the eval set gets refreshed before a real regression ships unnoticed.
**Measure**: (1) number of genuinely new production intent clusters surfaced per month and added to the golden set, versus zero today; (2) time between a new usage pattern appearing in production and being represented in the eval gate, dropping from "never, until a user complains" to under two weeks; (3) at least one real regression caught by the refreshed golden set that the stale set would have missed, demonstrated by backtesting on a pilot team's historical traffic.

## Try It

There's a companion skill at [`skills/golden-eval-set-drift-monitor/`](../skills/golden-eval-set-drift-monitor/) for the one-time version of this question — no nightly infrastructure required. Its `SKILL.md` describes it as a tool that "audits whether an LLM/agent product's golden eval set still represents current production traffic, by comparing a pasted golden-set export against a pasted production-query sample and surfacing uncovered intent clusters plus candidate new golden-set examples." Reach for it when CI keeps passing but users are still complaining, ahead of a quarterly eval review, or after a pivot.

To use it: either paste the contents of the skill's `README.md` into any AI chat tool along with your golden-set export and a sample of recent production queries, or drop the whole `golden-eval-set-drift-monitor/` folder into `~/.claude/skills/` if you're running Claude Code. Worth being clear about what it isn't: it does qualitative LLM-driven clustering from pasted data, not an embedding-space statistical divergence score, and it's a point-in-time audit, not the always-on nightly service described above — it will tell you, honestly, if you ask it to "just monitor this ongoing."

Two honest caveats carried straight from the project's own risk list: the individual techniques here (embedding divergence, canary re-scoring) are already known to sophisticated eval teams, so the real bet is that nobody has packaged them — which a well-resourced vendor like Braintrust or Langfuse could still beat this to market on. And getting representative production traces, not just error logs, into the pipeline is itself an adoption blocker for any team that's cautious about where real user data flows.

Surfaced from `research/2026-11-11-llm-evaluation-observability.md`, pattern `P6`.
