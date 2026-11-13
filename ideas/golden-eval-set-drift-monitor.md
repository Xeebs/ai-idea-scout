# Canary Set: Catching Golden Eval-Set Drift Before It Silently Breaks CI Gates

- **Status**: PUBLISHED — [writeup](../published/golden-eval-set-drift-monitor.md) (promoted 2026-11-13 cycle 47: recurrence — same golden-dataset-decay/no-drift-triggered-refresh gap (P6 there) surfaced independently again as P2 in the 2026-11-13 digest)
- **Date**: 2026-11-11
- **Topic**: LLM evaluation & observability
- **Source**: research/2026-11-11-llm-evaluation-observability.md · P6
- **Maturity verdict**: OPEN — WebSearch for "golden eval set drift detection" and "eval dataset drift" returned zero GitHub repos and no named product; only practitioner blog posts (tianpan.co, oneuptime.com, futureagi.com) independently recommending techniques as personal practice, not a shared tool anyone else has adopted.
- **Format**: BOTH — a nightly drift-monitoring service is a scheduled runtime job; a one-shot "score my golden set against this traffic sample" audit is a separable, stateless analysis task.

## The Gap
A connected series of posts from one practitioner (tianpan.co — "golden dataset decay / eval liability," 2026-04-20; "The Eval-Set-as-Simulator Drift," 2026-04-27; "Your Gold Eval Set Has Drifted," 2026-04-28) names the exact gap: "Eval dataset drift is the silent killer... the nightly job runs against a sample of yesterday's production traces so you catch drift the fixed set will not." The author frames the fixes — embedding-divergence monitoring, dataset/judge-prompt versioning, nightly re-scoring — as their own practice, not a packaged tool; multi-channel search found zero repos or named products implementing it.

## The Project
A service that embeds the golden eval set and a rolling sample of recent production traces, computes a divergence metric (e.g., Jensen-Shannon divergence over embedding clusters, or new-intent-cluster detection) between the two on a schedule, flags when a production intent cluster has grown without a matching golden-set example, version-stamps the golden set and judge prompt together so a CI score change is attributable to a real regression rather than a silent eval-asset edit, and proposes specific new production traces as candidate golden-set additions for human review.

Components: embedding + clustering pipeline; divergence scorer with alert thresholds; golden-set/judge-prompt version ledger; a weekly report of uncovered production clusters with example traces.

## Tangible Impact
**Population**: Teams running LLM/agent products with a fixed golden-eval-set CI gate who ship weekly or faster — the same population the tianpan.co posts are written for (a practitioner who personally hit this), realistically any team past the prototype stage with more than one eval-gated release per week and a live user base generating traffic distinct from launch-day traffic.
**Mechanism**: Today a golden set quietly stops representing live traffic as new user intents emerge, so a CI gate keeps reporting a passing score while the product's real, current failure modes go untested. The drift monitor turns that invisible decay into a weekly "here are N new intent clusters in production not covered by your golden set" report, so the eval set gets refreshed before a real regression ships unnoticed.
**Measure**: (1) number of genuinely new production intent clusters surfaced per month and added to the golden set, versus zero today; (2) time between a new usage pattern appearing in production and being represented in the eval gate, dropping from "never, until a user complains" to under two weeks; (3) at least one real regression caught by the refreshed golden set that the stale set would have missed, demonstrated by backtesting on a pilot team's historical traffic.

## Why Now
Embedding models cheap and fast enough to cluster a daily production-traffic sample at negligible cost only became a non-issue in 2026. The pattern is freshly documented (April 2026 posts) as one practitioner's hard-won lesson, with no tool yet built to generalize it — the gap here is organizational catch-up, not a capability wait.

## Skill Angle
Trigger: a team maintaining a golden eval set asks "is our eval set still representative of what users are actually doing" ahead of a quarterly review, after a product pivot, or when CI keeps passing despite user complaints. Inputs: the current golden-set file and a sample export of recent production traces/queries — no live infra access needed. Output: a drift report — a divergence score, a list of production-traffic clusters not represented in the golden set with example traces for each, and a short ranked list of concrete candidate examples to add. The skill is the one-time audit; the project is the thing that runs this automatically every night and alerts without being asked.

## MVP Sketch
Embed golden-set examples and a sampled day of production traces with the same embedding model; cluster both (HDBSCAN or similar); flag production clusters with no close golden-set neighbor above a similarity threshold; output a markdown report plus an append-ready JSON of candidate new examples. Experiment: run against one pilot team's real golden set and a week of their production logs, and check whether it surfaces at least one genuinely new intent cluster a human reviewer agrees isn't in the golden set. 2 weeks, 1 person.

## Risks & Open Questions
- The individual techniques (embedding divergence, canary re-scoring) are already known to sophisticated teams — the bet is purely on nobody having packaged them, which a well-resourced eval vendor (Braintrust, Langfuse) could do first.
- Divergence thresholds that avoid flooding teams with false "drift" alerts on normal traffic variance are unproven and need real tuning data.
- Access to representative production traces, not just error logs, is itself an adoption blocker for privacy-conscious teams.
- The evidence base is a single practitioner's three connected blog posts — thin, single-source signal worth watching for recurrence before heavy investment.
