# Track Record: A Historical-Risk-Conditioned Autonomy Gate for Coding Agents

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-13-ai-safety-and-guardrails-in-production.md · P7
- **Maturity verdict**: PARTIAL — `gh search repos` for "risk conditioned autonomy agent approval" returned zero matches. WebSearch found plenty of static risk-*tier* approval-gating guidance (AWS Well-Architected agentic-AI lens, Gravitee, FeatBit, getmaxim) classifying actions into fixed AUTO/LOW/HIGH/CRITICAL categories, but none dynamically conditions autonomy on a learned model of historical outcome data per action/code area — specifically what `kodustech/kodus-ai` PR #2193 does. kodus-ai remains the only implementation found, and it's an internal vendor PR with self-reported eval numbers, not externally validated.
- **Format**: BOTH
- **Data Sources**: CONNECTED — reads PR history, revert commits, and hotfix labels directly from the GitHub/GitLab API, a mature, already-available connector; the outcome ledger is built and kept current entirely from data the platform already holds, requiring no manual data entry beyond initial policy configuration (which paths to track, how "revert/hotfix" is defined for the repo).

## The Gap
`kodustech/kodus-ai` PR #2193 ("feat: conditional PR approval with historical code-area risk") reports a concrete eval shift: moving from a blanket clean-review policy to one conditioned on historical risk per code area changed the approval outcome on 147 of 156 previously-approved PRs (156/156 → 9/156 under the new model) on a frozen 200-PR eval set. This is a single vendor's internal PR with its own numbers — no second, externally-validated implementation of historical-outcome-conditioned autonomy for agents surfaced anywhere else in the digest's search.

## The Project
A drop-in gate for AI-coding-agent PR auto-approval/auto-merge pipelines that replaces a fixed AUTO/LOW/HIGH/CRITICAL rule with a per-code-area (and per-change-type) historical outcome ledger: which past agent-authored changes to this file or module were later reverted, hotfixed, or flagged in review. The gate starts conservative everywhere, earns autonomy area-by-area as the ledger accumulates clean outcomes, and tightens immediately after a revert in that area — rather than waiting for a scheduled policy review. It ships as a GitHub Action/bot plus the outcome ledger as a queryable store, independently evaluated against a frozen historical PR set the way kodus-ai measured its own, to confirm the approach generalizes beyond one vendor's internal numbers.

## Tangible Impact
**Population**: engineering teams running AI coding agents with partial autonomy over PR approval/merge, specifically teams who've found a static trust-label scheme too coarse because it treats a historically safe, well-trodden module identically to a volatile one on day one. Proxy for scale: Vercel's reported 58% of PRs in its largest monorepo already merging without human review (April 2026), implying teams are granting autonomy today without a principled, outcome-based basis for where.
**Mechanism**: a static rule (file-path scope, diff size) can't distinguish a code area that has reliably survived 50 past agent changes from one that's reverted every third time. A historical-risk ledger tracks actual track record per area instead of a one-size-fits-all threshold, and tightens immediately after a revert rather than on the next scheduled policy audit.
**Measure**: (1) revert/hotfix rate on auto-approved PRs under the historical-risk gate vs. a static-rule baseline, replayed against the same kind of frozen historical PR set kodus-ai used; (2) % of previously-blanket-approved PRs the gate correctly re-flags for human review, as an external reproduction of kodus-ai's own 156→9 shift; (3) time-to-autonomy-recovery after a revert event — how quickly a tightened area loosens again once new clean outcomes accumulate.

## Why Now
kodus-ai's PR this month is the first concrete evidence the historical-conditioning approach works in practice (a 96% outcome shift from flat to risk-conditioned policy on its own eval set), and the GitHub/CI platform metadata needed to build the outcome ledger — revert commits, hotfix labels, review comments — is already fully queryable via mature, existing APIs. No new infrastructure primitive is missing, only the ledger-and-gate logic on top of data platforms already hold.

## Skill Angle
Trigger: a team hands over a PR diff plus the repo's commit/revert history for the touched files. The skill produces a one-shot risk-conditioned recommendation (approve autonomously / flag for human review) with its reasoning, as a pre-adoption sanity check before committing to the always-on ledger-and-gate infrastructure. The project is the continuously-updated ledger and live merge-pipeline gate; the skill is the one-time judgment that tests the approach on a single PR first.

## MVP Sketch
A GitHub Action that, on each merged PR, tags it with an outcome label (clean / reverted / hotfixed within N days), building a per-path ledger over time; a second Action that, on new PR open, queries the ledger for the touched paths and outputs an approve/flag recommendation. Single experiment: replay against a public repo's historical PR set (a mix of dependabot-style low-risk changes and larger changes) and compare the gate's recommendations against which PRs actually needed a later revert. 3-4 weeks for 1-2 people.

## Risks & Open Questions
- Code-area-level historical risk may not generalize to novel changes in that area — a historically safe module could still break on genuinely new logic; the ledger is a prior, not a guarantee.
- Cold-start problem: brand-new repos or newly agent-managed areas have no history to condition on and need a conservative default.
- kodus-ai's own numbers are self-reported and internal; the MVP experiment is explicitly designed to independently re-derive a similar result before trusting the approach more broadly.
- Could read as redundant with a static trust-label framework (declarative scope/size rules); the differentiator — a continuously learned, outcome-conditioned model vs. a fixed rule set — needs to stay the clear headline.
