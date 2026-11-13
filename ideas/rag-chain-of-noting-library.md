# Note First: A Maintained Chain-of-Noting Library for Noisy RAG Retrieval

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: RAG techniques
- **Source**: research/2026-11-13-rag-techniques.md · P5
- **Maturity verdict**: PARTIAL — Chain-of-Note is a published, peer-reviewed technique (Yu et al., arXiv 2311.09210, EMNLP 2024, Tencent AI Lab), and a prior LangChain "chain-of-note-wiki" template implemented it, but that template now only survives as an archived git mirror, is not in LangChain's current maintained templates, and is prompt-only/Wikipedia-scoped. The new GitHub PR `arakoodev/EdgeChains#844` (2026-11-10) is a second, independent, equally early-stage attempt (CLA just signed, 4 comments at capture). Two abandoned-or-nascent implementations, no adopted or benchmarked general-purpose production version — the maintained, corpus-agnostic implementation is the real gap.
- **Format**: BOTH
- **Data Sources**: CONNECTED (for the Project) — operates on whatever retrieved passages the host RAG pipeline already fetched from its own vector store/search index (no new external data source is introduced; the library is a drop-in post-retrieval, pre-generation step that consumes the host app's existing retrieval output). The Skill Angle variant is MANUAL — the user pastes the question plus the retrieved passages directly, no pipeline integration needed for a one-off check.

## The Gap

GitHub PR `arakoodev/EdgeChains#844`, "feat(ai): implement Chain of Noting (CoN) for robust RAG retrieval" (2026-11-10, surfaced directly by the last30days engine), shows an active developer re-implementing this exact technique from scratch today — strong evidence it isn't available as a reusable dependency. The original EMNLP 2024 paper and LangChain's own past "chain-of-note-wiki" template prove the technique works and was once adopted, but the LangChain template is now archived, unmaintained, and scoped only to Wikipedia-style corpora — leaving every team that wants this robustness property on their own corpus to build it themselves, which is exactly what the EdgeChains PR is doing in real time.

## The Project

A maintained, corpus-agnostic Chain-of-Noting library: given a query and a set of retrieved passages, the library has the model write a short intermediate "note" per passage — summarizing what's relevant, flagging what's irrelevant or contradictory, and explicitly marking passages with no useful information — before those notes (not the raw noisy passages) are composed into the final answer. Unlike the original paper's Wikipedia-only scope and the archived LangChain template, this version is corpus-agnostic (works over any retrieved-passage format), includes a robustness eval harness that measures answer quality specifically on queries with noisy/partially-irrelevant/contradictory retrieved context (the exact failure mode CoN targets), and ships as a drop-in post-retrieval step compatible with any RAG pipeline rather than a bespoke wiki-scoped template.

## Tangible Impact

**Population**: Engineering teams building RAG systems over corpora with inherently noisy or redundant retrieval results — multi-source knowledge bases, customer support ticket histories, long internal wikis with outdated and current versions of the same policy coexisting — where naive "just concatenate the top-k passages" composition regularly hands the generator contradictory or irrelevant context. This is the direct audience the EdgeChains PR and the original paper's "robust RAG under noisy context" framing target.
**Mechanism**: Today, teams either accept degraded answers when retrieval returns partially-irrelevant or contradictory passages, or hand-roll their own filtering step (as the EdgeChains contributor is doing right now) with no shared, tested implementation to start from. A maintained library with a built-in noisy-context eval harness turns "build your own noise-filtering step and hope it works" into "adopt a tested component and measure the specific improvement on your own noisy-query subset."
**Measure**: answer accuracy on a held-out noisy-retrieval eval set (queries deliberately constructed so top-k includes irrelevant/contradictory passages), before vs. after adopting the library, compared against naive passage-concatenation; rate of answers that incorporate information from an irrelevant/contradictory passage, with vs. without the noting step; adoption/reuse signal (stars, downstream forks) versus the archived predecessor's trajectory.

## Why Now

The underlying technique is a validated, EMNLP-published result from two years ago, and a developer is independently re-implementing it from scratch this month (the EdgeChains PR) — a clear, current, real-time signal that the gap (no maintained, corpus-agnostic version to depend on instead of rebuilding) is live right now, not hypothetical.

## Skill Angle

A "Note and Filter" skill: given a pasted question and a set of retrieved passages, it writes the per-passage notes, flags which passages are irrelevant or contradictory, and composes a final answer grounded only in the notes that actually support it — useful as a one-off noisy-retrieval check on a single query/answer pair without integrating the full pipeline library.

## MVP Sketch

2–4 weeks, 1–2 people: implement the per-passage noting step and note-based composition as a corpus-agnostic function (query + passages in, notes + grounded answer out), build a constructed noisy-retrieval eval set (queries paired with deliberately mixed relevant/irrelevant/contradictory passages) across 2-3 different corpus types to prove corpus-agnosticism, and benchmark answer accuracy against both naive concatenation and the original paper's reported numbers.

## Risks & Open Questions

- The EdgeChains PR, once it lands and matures, may itself become the maintained general-purpose implementation this idea calls for — worth checking its progress before committing significant build time to a competing version.
- Per-passage noting adds a model call per passage per query, which increases latency and cost; needs to prove the robustness gain is worth that overhead versus a cheaper noise-filtering heuristic.
- The original paper's gains were demonstrated specifically on noisy-context benchmarks; the project's value depends on real-world retrieval noise looking similar enough to those benchmarks, which needs validating on actual production traces, not just constructed eval sets.
- LangChain's prior template existed and was eventually archived rather than maintained — worth understanding why adoption stalled before assuming a second attempt will fare differently.
