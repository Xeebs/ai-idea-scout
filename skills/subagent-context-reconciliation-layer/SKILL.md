---
name: subagent-context-reconciliation-layer
description: Audits two or more sub-agent outputs returned to the same lead-agent step for hidden contradictions, classifies each conflict, and recommends a resolution policy. Use when a multi-sub-agent pipeline (Claude Code Task tool, Cursor parallel worktrees, LangGraph/CrewAI fan-out) returned results that might disagree and you need to know before the lead agent acts on them.
---

# Sub-Agent Context Reconciliation Audit

## When to use this
Reach for this the moment two or more isolated sub-agents (or parallel Task-tool calls, parallel worktree agents, or fan-out graph nodes) have returned digested results for the *same* lead-agent decision, and you're not sure whether those results actually agree. Typical triggers:

- You're reviewing a multi-agent run's transcript and the lead agent's next action depends on sub-agent conclusions you haven't personally cross-checked.
- You're designing a new sub-agent fan-out step and want to pressure-test whether your planned merge logic ("take the most recent," "concatenate both," "no explicit policy yet") would actually catch a real disagreement.
- A pipeline produced a wrong downstream action and you suspect two sub-agents silently disagreed and one got picked arbitrarily.

Do not reach for this when there is only one sub-agent return (nothing to reconcile) or when the sub-agent outputs cover genuinely disjoint tasks with no shared claim to compare (there's no conflict possible, just report that).

## Inputs
**Data source**: Manual — paste (a) a short description of the pipeline shape and how it currently merges sub-agent results today, and (b) the actual text of two or more sub-agent outputs returned for one single lead-agent step. (The parent idea classifies the full middleware version of this as Connected — a runtime adapter reading transcripts directly from the host orchestration framework such as Claude Agent SDK's Task tool or LangGraph node outputs, no such adapter exists today. This skill is the manual, one-shot audit variant of that same job: it needs no integration, just pasted text, so it's usable before anyone builds the adapter.)

Specifically hand over:
1. **Pipeline shape** (1–3 sentences): what each sub-agent was asked to explore/do, and what it was told to return to the lead (a full transcript, or a digested summary under some length).
2. **Current merge behavior** (1–2 sentences): how the lead agent handles multiple returns today — picks the most recent, concatenates all, asks a human, or "no explicit policy."
3. **The sub-agent outputs themselves**, verbatim, labeled by which sub-agent produced each (Sub-agent A, B, C...). Two is the minimum; more is fine.
4. Optional: any ground-truth fact or success criterion you already know, if you have one, to check the outputs against.

## Procedure
1. **Extract claims per output.** For each sub-agent output, list the discrete factual/actionable claims it makes, the scope of what it actually covered (what question it was answering), and any hedging language or caveats it included.
2. **Pairwise compare every pair of outputs** that address the same lead-agent step. For each pair, check three things in order:
   - **Scope check first**: do the two outputs actually answer the same question? If they cover different sub-questions that only *look* related, this is a scope mismatch, not a conflict — both are likely valid and should be merged, not arbitrated.
   - **Factual contradiction**: do the two outputs assert mutually exclusive facts about the same referent (same file, same API, same number, same recommendation)? Quote the exact conflicting spans from each.
   - **Stale assumption**: does one output rely on a state of the world (a file's contents, an API's behavior, a prior decision) that the other output implies has since changed? Quote the span that reveals the staleness.
3. **Classify every detected conflict** as exactly one of: `factual contradiction`, `scope mismatch` (not a true conflict — flag and merge), or `stale assumption`. If a pair triggers more than one of these, report all that apply with separate quotes.
4. **Rate severity** of each true conflict (factual contradiction or stale assumption only) as `high` if the lead agent's next action is irreversible or costly if wrong (e.g., a deploy, a delete, a recommendation a human will act on without re-checking), otherwise `low`.
5. **Check the stated merge policy against each conflict.** State explicitly whether the user's described current behavior (step 2 of Inputs) would catch this specific conflict or silently paper over it.
6. **Recommend a resolution policy per conflict**, chosen from exactly three options:
   - `block-and-ask-lead` — for high-severity factual contradictions; the lead must not proceed without resolving it.
   - `spin-up-tie-breaker-subagent` — for stale assumptions, where a fresh, targeted re-check (not a vote) resolves it; state what that tie-breaker should be asked to verify.
   - `merge-with-flag` — for scope mismatches and low-severity factual contradictions; both outputs get kept, visibly flagged as disagreeing, for the lead or a human to weigh.
7. **Call out false positives explicitly.** If a pair looked like it might conflict but on inspection is only a wording/phrasing difference with no substantive disagreement, say so — do not let a surface-level difference get classified as a conflict.
8. **State your confidence limit.** With only the pasted outputs and no access to ground truth, say plainly which conflicts you're confident are real versus which are plausible but unverifiable from the text alone.

## Output format
A single markdown report with:

1. **Conflict Summary table** — columns: Pair (e.g. A↔B), Type (factual contradiction / scope mismatch / stale assumption / none found), Severity (high/low/n-a), Caught by current policy? (yes/no/unclear).
2. **Per-pair detail** — for every pair with a detected conflict: the exact quoted spans from each side, the classification reasoning, the severity reasoning, and the recommended resolution policy with a one-line justification tied to a concrete downstream consequence.
3. **False positives noted** — any pair that looked suspicious but was ruled out, and why.
4. **Pipeline-level recommendation** — one paragraph: given what was found, should this pipeline's default merge behavior change, and to what, before the next run.

## Guardrails
- Never report a conflict without a direct quote from each side backing it — no "these seem to disagree" without the actual text.
- Never classify a scope mismatch as a factual contradiction — these are the single most common false alarm and conflating them makes the audit useless.
- Never silently decide which of two contradicting sub-agents is "right" — that is the exact failure mode this skill exists to expose, not replicate. Always recommend a policy, never a verdict on the facts themselves, unless the user supplied explicit ground truth to check against.
- Never recommend a resolution policy without naming the concrete downstream consequence if the conflict goes unresolved — "flag it" with no reasoning is not useful.
- If only one sub-agent output is provided, say there is nothing to reconcile — do not invent a second perspective to compare against.
- If the pasted outputs are full raw transcripts rather than digested summaries, note that detection here is still text-based pattern matching, not guaranteed to catch conflicts that only emerge from reasoning not stated in the text.
