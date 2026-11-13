# Evidence Watch: An Automated arXiv-to-Benchmark Evidence Pipeline for Guardrail-Evasion Research

- **Status**: EXPLORING (promoted 2026-11-13 cycle 39: evidence density — 3 independent sources, two maintainer workarounds plus ITU-T's standards-body issue, all calling for the same pipeline)
- **Date**: 2026-11-13
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-13-ai-safety-guardrails-in-production.md · P7
- **Maturity verdict**: PARTIAL — GitHub search found multiple maintained "awesome-agentic-ai-security" curated lists (natnew, themayursinha, hysnsec, plus icecreamyoubest already in-digest) but these are manually curated, not automated arXiv-to-PR pipelines. WebSearch found well-resourced adjacent efforts (MLCommons AILuminate Jailbreak Benchmark v0.5, JailbreakBench, and "Jailbreak Foundry," an academic multi-agent pipeline converting jailbreak papers into runnable benchmark modules) but none specifically does the narrow "bot watches arXiv, auto-opens a reviewable PR into a maintained awareness repo" workflow as a packaged, reusable tool.
- **Format**: BOTH
- **Data Sources**: CONNECTED — arXiv's public API (mature, free, no auth required) to watch the cs.CR/cs.AI listings for new papers, and the GitHub API (mature, requires a repo-scoped token with PR-create permission) to open PRs against the target benchmark/awareness repo.

## The Gap
GitHub issue `billbrietstout/ai-security-whitepaper-monitor#529` surfaced arXiv paper 2504.11168 on guardrail-evasion attacks, and GitHub PR `icecreamyoubest/awesome-agentic-ai-security#28`, "Auto update review: evidence and benchmark candidates," shows a bot-generated PR explicitly scoped to "propose reviewable evidence changes only; maintainers should verify claims before merging." Both repos are small, single/few-maintainer side projects built because no canonical, continuously-updated benchmark of guardrail-evasion research exists — independently corroborated by an ITU-T Study Group 17 chair filing a standards-body issue (`FG-TIDA/themes#44`) calling for exactly this kind of evidence-of-trust benchmarking.

## The Project
A bot pipeline that watches arXiv's cs.CR/cs.AI categories for new papers matching a guardrail-evasion/jailbreak-detection-bypass classifier (keyword filtering plus abstract-embedding similarity to a seed set of known evasion papers), extracts the paper's claimed attack technique and any reported bypass rate, and opens a reviewable PR against a target benchmark/awareness repo proposing the new evidence entry in that repo's existing format — the same "evidence changes only, maintainers verify before merging" pattern already proven manually in `icecreamyoubest/awesome-agentic-ai-security#28`, but running continuously and packaged for any maintainer to point at their own repo instead of being rebuilt per-repo.

## Tangible Impact
**Population**: maintainers of curated "awesome-agentic-ai-security"-style community benchmark/awareness repos (at least four independently found in this run's search alone — natnew, themayursinha, hysnsec, icecreamyoubest) and the AI red-team/trust-safety engineers who rely on those repos staying current to know which guardrail-evasion techniques to test their own stack against.
**Mechanism**: today these maintainers manually scan arXiv or rely on happening to see a paper shared elsewhere, writing up each new evasion technique as a PR by hand — exactly the lag the ITU-T standards issue independently flags as a gap. An automated watch-and-draft pipeline cuts that lag from "whenever a maintainer happens to notice" to "within days of publication," while keeping a human verification step so evidence never auto-merges unreviewed.
**Measure**: median time from arXiv publication to a reviewable PR appearing in a maintainer's repo (target: under 7 days, vs. the current ad hoc/unmeasured baseline); percentage of newly-disclosed evasion techniques captured without the maintainer manually searching for them; maintainer-reported false-positive rate on proposed evidence entries.

## Why Now
arXiv's API and abstract-embedding similarity search are mature, cheap, off-the-shelf tools; the manual version of this exact workflow is already running in production in `icecreamyoubest/awesome-agentic-ai-security#28`, proving the mechanism and the target format — this packages an already-working idea rather than inventing one.

## Skill Angle
A "Paper-to-Evidence Draft" skill — given a pasted arXiv abstract or paper link and a target repo's existing evidence-entry format (pasted as an example entry), the skill drafts the structured PR body (technique summary, reported bypass rate, affected systems, verification caveats) a maintainer would otherwise write by hand, usable immediately by any maintainer without waiting for the full automated watcher to be built or pointed at their repo.

## MVP Sketch
2-3 weeks, 1-2 people. Build the arXiv watcher (daily poll of cs.CR/cs.AI, filtered by a keyword list plus embedding similarity to roughly 20 seed evasion papers), the GitHub PR-drafting step targeting one pilot repo (ideally with that maintainer's cooperation), and run it for 2-4 weeks measuring precision — how many proposed entries the maintainer actually merges — against the bot's own submission volume.

## Risks & Open Questions
- A keyword/embedding classifier for "is this paper about guardrail evasion" will have false positives and negatives; needs tuning against a real maintainer's judgment, not just a static seed set.
- This only has value if at least one real maintainer adopts it on their actual repo — validating interest with a list owner before building is a prerequisite, not an afterthought.
- Narrower niche than most ideas in this digest (benefits benchmark-repo maintainers and the red-teamers who read them, not end users or developers broadly) — the impact is indirect (better-informed defenders) rather than direct.
- Well-resourced benchmarks (MLCommons AILuminate, JailbreakBench) could add their own automated ingestion pipeline and make a smaller open tool redundant.
