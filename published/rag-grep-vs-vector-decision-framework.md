# Grep or Vector: A Decision Framework for Code-Retrieval Strategy in Coding Agents

Every team building a coding agent eventually hits the same fork in the road: should it search a codebase with plain old grep, a vector index, or some hybrid of the two? Right now almost everyone answers that question by copying whatever a louder team did, not by measuring their own repo. That's a strange place for the field to be, given how much else about agent design has gotten rigorous.

## The Gap

The signal here is less "nobody has an opinion" and more "nobody has evidence anyone can reuse." A WebSearch sweep of the conversation around this turned up an ITNEXT benchmark showing the exact same grep hits scoring anywhere from 10 to 34 out of 40 depending purely on which ranking method was applied to them — a strong hint that retrieval quality is less about grep-versus-vector in the abstract and more about how the results get ranked afterward. A dev.to piece from harrisonsec frames the whole choice as "a cost-curve problem" rather than a philosophical one. And there's a widely repeated, if only secondhand-confirmed, account that an Anthropic engineer described Claude Code dropping a local vector-DB RAG approach in favor of live ripgrep in production.

That last data point is the most interesting one, because it's real: multiple independent sources — dev.to/harrisonsec, Towards AI, even a rebuttal post from vector-database vendor Zilliz, plus several Chinese-language technical breakdowns — converge on confirming that Claude Code genuinely does run grep rather than a persistent vector index at scale. So the underlying technique is proven, by a maintained, well-resourced, shipped product. What isn't proven, or even written down anywhere reusable, is *why* that's the right call for a given codebase, or when it stops being the right call. Reports on what Cursor and Aider do are contradictory — some call their retrieval hybrid, others dispute that framing entirely. The one academic attempt to settle this, an arXiv paper literally titled "Is Grep All You Need?", is only months old and lives as a benchmark, not a tool. The search's own synthesis put it bluntly: this is "anecdotes and one small benchmark," not a decision framework.

## The Project

The idea is a harness, not another opinion piece: point it at a target repository and a labeled sample of realistic queries — a mix of exact-identifier lookups ("where is `parseRetryConfig` defined") and vaguer conceptual ones ("where do we handle request retries") — and it runs both grep and a basic vector index against that same repo and query set, scoring hit-rate, precision, and latency for each. Layered on top of that is a routing rule derived from the repo's own characteristics: churn rate, size, and identifier density, all pulled straight from `git log` and a filesystem scan. The output is a recommendation grounded in that specific codebase's measured behavior, not a borrowed anecdote about what Claude Code happened to choose or a from-scratch rerun of the ITNEXT benchmark's methodology.

Three components do the work: a git-metadata extractor, a dual-strategy query runner, and a scored recommendation report that ties the two together.

## Tangible Impact

**Population**: Maintainers of coding-agent frameworks and in-house AI dev-tool teams (e.g., teams building on OpenHands/SWE-agent/Aider-style agents, or an internal coding assistant at a mid-size engineering org) who must choose a code-retrieval strategy for their agent but currently guess rather than measure — distinct from Claude Code's own team, which settled on grep for its specific product without publishing a general decision rule others can reuse.
**Mechanism**: Running a team's own repo and query sample through grep, vector, and hybrid strategies and reporting hit-rate/precision/latency per strategy lets them pick based on their repo's actual churn rate and identifier density instead of copying an anecdote or re-running the one academic benchmark from scratch — directly closing the "anecdotes and one small benchmark" gap the digest's own search confirmed.
**Measure**: hit-rate/precision@k delta between the harness's recommended strategy and whatever the team was defaulting to; % of teams whose own numbers contradict an "always grep" default (showing the right answer genuinely varies by repo); time-to-decision (target: under a day via the harness vs. the weeks of ad hoc trial the digest's sources describe).

## Try It

There's no companion skill for this one yet — the idea is currently tagged `Format: BOTH` in the backlog, so a lighter judgment-only version ("reason through grep vs. vector vs. hybrid for my repo, given its size/churn/query shape, without running a full benchmark") is planned but not yet written. Check `skills/rag-grep-vs-vector-decision-framework/` in the repo for whether that's landed by the time you're reading this.

Worth being honest about the risk here too: the academic benchmark this leans on (arXiv 2605.15184, "Is Grep All You Need?") could itself get wrapped into a tool by someone else mid-build, and Cursor/Aider's disputed hybrid approaches hint the field may already be drifting toward hybrid-by-default — which would narrow this project's real value down to tuning a split rather than deciding a binary. And the "Claude Code dropped vector RAG for grep" story, while corroborated by several independent sources, is still secondhand in parts; any framework built on it has to validate per-repo empirically rather than assume the anecdote generalizes.

---

Surfaced from `research/2026-11-20-rag-techniques.md`, pattern `P7`.
