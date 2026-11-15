# Evidence Watch: An Automated arXiv-to-Benchmark Evidence Pipeline for Guardrail-Evasion Research

Every curated "known jailbreak techniques" list that security teams lean on is really a volunteer's spare-time habit of reading arXiv — which means the list is only ever as current as that one person's last free evening. Nobody has packaged the fix that a couple of small projects have already proven works by hand.

## The Gap

The signal here didn't come from a single loud complaint — it came from watching the workaround already happening in public. A GitHub issue on `billbrietstout/ai-security-whitepaper-monitor` (#529) surfaced a fresh arXiv paper on guardrail-evasion attacks the moment it landed, and a PR on `icecreamyoubest/awesome-agentic-ai-security` (#28), titled "Auto update review: evidence and benchmark candidates," shows a bot already drafting entries for a curated awareness repo — explicitly scoped to "propose reviewable evidence changes only; maintainers should verify claims before merging." Both are small, single- or few-maintainer side projects, built because no canonical, continuously-updated benchmark of guardrail-evasion research exists. An ITU-T Study Group 17 chair independently filed a standards-body issue (`FG-TIDA/themes#44`) calling for exactly this kind of continuous evidence-of-trust benchmarking — a third, unrelated voice arriving at the same missing piece from the standards side rather than the maintainer side.

Put plainly: the pattern maintainers want already exists as a one-off script bolted onto one repo. It has never been packaged so any maintainer of any curated list can point it at their own repo without rebuilding it from scratch.

## The Project

Evidence Watch is a bot pipeline that watches arXiv's cs.CR and cs.AI categories for new papers, classifies which ones describe a guardrail-evasion or jailbreak-detection-bypass technique (keyword filtering plus abstract-embedding similarity against a seed set of known evasion papers), and extracts the paper's claimed attack technique and any reported bypass rate. It then opens a reviewable PR against a target benchmark or awareness repo, formatted to match that repo's existing entry style — the same "evidence changes only, maintainer verifies before merging" pattern already proven manually in `icecreamyoubest/awesome-agentic-ai-security#28`, but running continuously and packaged so it isn't rebuilt per repo.

The centerpiece is the classifier-plus-draft loop, not a generic scraper: it has to tell a genuine evasion/bypass paper apart from a defense paper, and it has to produce a PR a human maintainer can actually review in under a minute rather than a wall of unverified claims.

## Tangible Impact

**Population**: maintainers of curated "awesome-agentic-ai-security"-style community benchmark/awareness repos (at least four independently found in this run's search alone — natnew, themayursinha, hysnsec, icecreamyoubest) and the AI red-team/trust-safety engineers who rely on those repos staying current to know which guardrail-evasion techniques to test their own stack against.
**Mechanism**: today these maintainers manually scan arXiv or rely on happening to see a paper shared elsewhere, writing up each new evasion technique as a PR by hand — exactly the lag the ITU-T standards issue independently flags as a gap. An automated watch-and-draft pipeline cuts that lag from "whenever a maintainer happens to notice" to "within days of publication," while keeping a human verification step so evidence never auto-merges unreviewed.
**Measure**: median time from arXiv publication to a reviewable PR appearing in a maintainer's repo (target: under 7 days, vs. the current ad hoc/unmeasured baseline); percentage of newly-disclosed evasion techniques captured without the maintainer manually searching for them; maintainer-reported false-positive rate on proposed evidence entries.

## Try It

A companion Claude Code skill, [`skills/arxiv-guardrail-evasion-evidence-pipeline/`](../skills/arxiv-guardrail-evasion-evidence-pipeline/), already exists — it's the lightweight, manual-paste companion to the fully automated watcher described above, usable today without waiting for anyone to build the bot. Its one-line description: "Drafts a reviewable PR/issue entry for a curated guardrail-evasion or jailbreak benchmark/awareness repo from a pasted arXiv paper and the repo's existing entry format. Use when a maintainer or red-teamer has found a new evasion paper and needs it reformatted into their repo's style without inventing any data the paper doesn't support."

To use it: paste the arXiv paper's abstract (plus the specific results paragraph if it reports a bypass rate) and one example entry copied verbatim from your target repo, and the skill drafts a structured, maintainer-ready PR body — flagging anything the paper doesn't support rather than guessing at it. Drop the README into any AI chat tool as a prompt template, or drop the whole `skills/arxiv-guardrail-evasion-evidence-pipeline/` folder into `~/.claude/skills/` if you're running Claude Code.

Worth being clear-eyed about the limits: this only pays off if a real maintainer adopts it on an actual repo, and a well-resourced benchmark like MLCommons AILuminate or JailbreakBench could ship its own ingestion pipeline and make a smaller open tool redundant. The classifier also needs real tuning against a maintainer's judgment, not a static seed set — false positives and negatives are the expected failure mode, not an edge case.

---

Surfaced from `research/2026-11-13-ai-safety-guardrails-in-production.md`, pattern `P7`.
