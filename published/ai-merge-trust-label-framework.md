# Merge Trust: A Reusable Label-Gated Autonomy Framework for AI Coding Agents

Vercel says 58% of pull requests in their largest monorepo now merge without a human ever looking at them. That number alone should stop you — it means graduated autonomy for AI coding agents isn't a future-roadmap item, it's already load-bearing infrastructure at scale, and almost nobody is building it as a product. Every team doing it is quietly welding together their own version of the same seatbelt.

## The Gap

The clearest evidence is a single pull request: `alehar9320/agentic-odi` PR #872 adds a deterministic, AND-gated `ai-merge-safe` label to mark pull requests as safe enough for an AI agent to eventually merge. The PR's own description is refreshingly honest about where things stand — it calls itself "Phase 1: labelling only, humans still merge," with the actual autonomous-merge step, Phase 2, explicitly logged as future work. That's one team, mid-build, showing their work in public.

They are not alone, and that's the real signal. A search for the same pattern turns up a Gitea `agents` repo that gives a QA agent narrow merge authority behind an "autopilot" label (where removing the label is the kill switch), a "mergeshield" writeup on dev.to, and a blog post from "timetobuildbob" about agents literally "earning merge authority." GitHub's own Agentic Workflows preview, which shipped in June 2026, offers generic approval-skip controls — but not a dedicated, opinionated trust-label standard. Every one of these is a bespoke, team-internal build. `gh search code "ai-merge-safe"` and repo search turned up nothing shared, nothing packaged, nothing you could install. The appetite is real and the demand is dated this month; the tooling to meet it doesn't exist yet.

## The Project

Merge Trust is an open-source GitHub Action plus a small policy library that implements the trust-label-gated autonomous-merge pattern generically, instead of leaving every team to re-derive it. Teams declare rules — file-path scope, diff size, test-coverage delta, change type — that qualify a PR for an `ai-merge-safe` label. Once labeled, an optional Phase 2 step actually executes the auto-merge, with a hard kill switch: removing the label halts any pending merge, no exceptions. Every qualifying decision writes to a full audit ledger recording what rule fired, the diff hash, and the timestamp, so "why did this merge itself" always has a real answer.

The point isn't to invent a new idea — the idea is already proven by five independent teams building it badly in isolation. The point is to ship the one version that's packaged, documented, auditable, and maintained, so the next team doesn't have to write their own kill switch from scratch and hope they got the edge cases right.

## Tangible Impact

**Population**: engineering teams integrating AI coding agents into CI/CD who want graduated autonomy rather than all-or-nothing human review — concretely, teams at companies already running large monorepos with AI-agent-authored PRs, for whom Vercel's reported 58% of PRs merging without human review in their largest monorepo (April 2026) is a proxy for how many teams are already doing this informally, without a shared, auditable framework.
**Mechanism**: today each team hand-rolls the trust-label and auto-merge logic (per PR #872, Gitea's autopilot label, mergeshield), re-solving the same scoping, audit, and kill-switch problem and risking inconsistent safety bars across teams and even across repos within the same company. A shared, reusable framework lowers the engineering cost of adopting graduated autonomy safely and gives every adopting team the same auditable trust ledger instead of an unreviewed internal script.
**Measure**: time for a new team to adopt graduated-autonomy merging via the Action versus building a custom script (target: hours, not weeks); rate of incorrect auto-merges (merges later reverted or hotfixed) on labeled PRs compared against the team's prior baseline; adoption count across repos as a proxy for closing the "bespoke, unshared" gap the gap-analyst identified.

## Try It

There's no companion `skills/` build for this idea yet — the project side (the installable Action plus audit ledger) is the primary artifact. The idea file does sketch a lighter-weight skill angle worth noting if you're exploring the design before committing to infrastructure: a human pastes a PR diff plus their current review policy, and gets back a recommended trust-label decision with reasoning — a one-shot sanity check you could run in any AI chat tool before standing up the always-on Action.

Worth saying plainly, because the idea file does: GitHub's own Agentic Workflows feature could absorb this into a first-party control within a cycle or two, which would undercut a third-party Action overnight. Liability concerns may also make teams reluctant to hand merge-gating to an outside tool regardless of quality, preferring an in-house script they fully control — and the evidence behind this gap is still mostly single-team internal builds and low-engagement write-ups, not large-scale adoption data. A build here is a bet that "nobody's shipped the shared version yet" stays true for a while longer.

Surfaced from `research/2026-11-12-ai-safety-and-guardrails-in-production.md`, pattern `P7`.
