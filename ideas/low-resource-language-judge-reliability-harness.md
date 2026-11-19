# Judge Fit: A Scalable LLM-as-Judge Reliability Harness for Low-Resource Languages

- **Status**: PROPOSED
- **Date**: 2026-11-19
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-19-applied-ai-for-underserved-domains.md · P5
- **Maturity verdict**: PARTIAL — static human-curated benchmarks (Uhura, IrokoBench, Sahara leaderboard) and narrow trained metrics (AfriCOMET, SSA-COMET) cover specific sub-tasks like translation; an active research thread exists (TukaBench reports judge-human agreement below 60% for Yorùbá/Igbo; an EMNLP Findings 2026 survey finds only 33 of 650 LLM-judge papers address low-resource/multilingual settings at all). No deployed, scalable production eval harness for general LLM output quality in low-resource languages was found.
- **Format**: BOTH
- **Data Sources**: MANUAL — the team uploads/pastes their model's candidate outputs plus a human-rated reference subset for the target language. CONNECTED supplement — the Hugging Face Hub (mature, existing) to automatically pull TukaBench's and related published low-resource benchmark datasets as comparison baselines, instead of requiring the user to re-source them.

## The Gap
An Agency Fund report, building the social-sector LLM ecosystem, states that in low-resource languages like Swahili or Hausa "LLM performance evaluation often relies on small-sample human review or internal test sets." TukaBench quantifies exactly how bad this is in practice: judge-human agreement falls below 60% for Yorùbá and Igbo. An EMNLP Findings 2026 survey finds only 33 of 650 LLM-judge papers even address low-resource/multilingual settings, and flags over-trust in single judges as a live risk. Teams deploying tools in these languages have no scalable way to know whether automated evaluation is trustworthy for their specific language.

## The Project
A reusable harness that measures and reports LLM-judge reliability per language, benchmarked against a growing cross-language leaderboard. Point it at a judge model and a target low-resource language: it runs the judge against a human-rated reference set (pulling existing published sets like TukaBench's where available, or guiding a team through building a small one where not), computes agreement statistics and failure-mode categories (not just one score), and recommends whether to trust the judge, use a hybrid sampling approach, or fall back to full human review for that language.

## Tangible Impact
**Population**: AI-for-social-good teams and nonprofits deploying LLM-based tools in low-resource languages — the population the Agency Fund report describes as building the social-sector LLM ecosystem, concretely any team shipping in Yorùbá, Igbo, Swahili, Hausa, or similar languages where TukaBench's own findings show off-the-shelf judge reliability cannot be assumed.
**Mechanism**: Today a team either pays for small-sample human review every release (slow, expensive, doesn't scale with iteration speed) or trusts a judge model whose reliability for their specific language was never measured. A harness that reports measured judge-human agreement per language, with failure-mode detail, lets a team know whether automated evaluation is trustworthy before relying on it, and route to a cheaper hybrid review process calibrated against the judge's known blind spots when it isn't.
**Measure**: (1) judge-human agreement score per language, benchmarked against TukaBench's existing Yorùbá/Igbo numbers; (2) number of additional low-resource languages added to a running judge-reliability leaderboard within a year; (3) reduction in required human-review sample size per release once a team knows their judge's measured reliability, vs. full human review or blind judge trust.

## Why Now
TukaBench and the EMNLP Findings 2026 survey both landed in the recent window, establishing with hard numbers for the first time that LLM-judge reliability for low-resource languages is a measured, quantified problem rather than an assumed one — a reusable harness can build directly on that evidence base instead of starting from zero.

## Skill Angle
Trigger: a team asks "can I trust an LLM judge to evaluate my tool's output in [low-resource language]?" Inputs: a sample of model outputs in the target language plus reference/gold answers or human ratings for a subset. Output: a judge-reliability report — agreement score against the human subset, comparison to TukaBench's published numbers for related languages where available, and a recommendation (trust the judge / use hybrid sampling / full human review only). This differs from the project: the skill is a one-time reliability check a team runs before committing to automated eval; the project is the maintained, growing cross-language leaderboard and harness that benchmarks new judge models as they ship.

## MVP Sketch
Scope to the two languages TukaBench already measured (Yorùbá, Igbo) plus one new language, reusing TukaBench's published methodology rather than re-deriving it. Stack: a harness that runs a chosen judge model (or several) against a human-rated reference set per language via the Hugging Face Hub, computes agreement statistics, and publishes results to a simple leaderboard site. Validating experiment: replicate TukaBench's Yorùbá/Igbo numbers as a sanity check, then add one new language and see whether the harness surfaces a similarly low agreement score or a genuinely different one.

## Risks & Open Questions
- Getting a human-rated reference set for a new low-resource language hits the same native-speaker-recruitment bottleneck every other idea in this digest runs into.
- A single agreement-score number may oversimplify judge failure modes — the EMNLP survey explicitly flags over-trust in single judges, so the harness must report failure categories, not just one score, to be genuinely useful.
- Risk that TukaBench's own team is already planning to generalize their benchmark to more languages — worth direct outreach before building a competing harness.
- Judge models themselves improve quickly; a leaderboard needs an ongoing maintenance commitment or it goes stale within months.
