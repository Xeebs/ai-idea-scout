# Sub-Agent Context Reconciliation Audit

A paste-in prompt for auditing whether two or more AI sub-agents (parallel Task-tool calls, Cursor parallel-worktree agents, LangGraph/CrewAI fan-out nodes, or any custom multi-agent fan-out) actually agreed before a lead agent acted on their combined results. If you've ever had a multi-agent pipeline silently pick one sub-agent's answer over another's — or merge two conclusions that quietly contradicted each other — this finds that failure before it becomes a wrong action.

This is a one-shot diagnostic you run manually by pasting text into any AI chat tool. It does not require installing anything, connecting to any API, or instrumenting your pipeline. It is the "audit a specific run" sibling of a (not-yet-built) runtime middleware version of the same idea — this README is the part you can use today.

## When to use this

Use this the moment two or more isolated sub-agents have returned digested results for the *same* lead-agent decision and you're not fully sure they agree. Concretely:

- You're reviewing a multi-agent run's transcript and the next action depends on sub-agent conclusions nobody has personally cross-checked.
- You're designing a new fan-out step and want to pressure-test your planned merge logic before you ship it.
- A pipeline took a wrong action and you suspect two sub-agents disagreed and one got picked arbitrarily, with no trace of the disagreement.

Skip this if there's only one sub-agent return (nothing to reconcile against), or if the outputs cover clearly disjoint tasks with no overlapping claim (no possible conflict — just note that).

## What to hand over

This works entirely from text you paste — **Data source: Manual**. There is no connector or API involved; you paste everything yourself. Give the assistant:

1. **Pipeline shape** (1–3 sentences) — what each sub-agent was asked to explore or do, and what it was told to return to the lead (a full transcript, or a digested summary under some length limit).
2. **Current merge behavior** (1–2 sentences) — how the lead agent handles multiple returns today: picks the most recent, concatenates everything, asks a human, or has no explicit policy at all.
3. **The actual sub-agent outputs, verbatim**, each clearly labeled (Sub-agent A, Sub-agent B, Sub-agent C...). You need at least two.
4. Optional: any ground-truth fact or success criterion you already know, to check the outputs against directly.

## The procedure (what the assistant should do with this)

1. **Extract claims per output.** For each sub-agent output, list its discrete factual or actionable claims, the scope of the question it actually addressed, and any hedging or caveats it stated.
2. **Compare every pair of outputs** addressing the same lead-agent step, in this order:
   - **Scope check first.** Do the two outputs actually answer the same question? If they answer different sub-questions that only look related, that's a scope mismatch, not a conflict — both are probably valid and should simply be merged.
   - **Factual contradiction.** Do they assert mutually exclusive facts about the same thing (same file, same number, same recommendation)? Quote the exact conflicting text from each side.
   - **Stale assumption.** Does one output rely on a state of the world that the other implies has since changed? Quote the revealing span.
3. **Classify each detected conflict** as exactly one of: factual contradiction, scope mismatch (flag-and-merge, not a true conflict), or stale assumption. A pair can trigger more than one — report each with its own quote.
4. **Rate severity** of true conflicts (factual contradiction or stale assumption) as high if the lead agent's next move is costly or irreversible if wrong, otherwise low.
5. **Check the user's described current merge policy against each conflict** — would it actually catch this one, or silently paper over it?
6. **Recommend exactly one policy per conflict**, from these three:
   - **Block-and-ask-lead** — high-severity factual contradictions; don't let the lead proceed unresolved.
   - **Spin-up-a-tie-breaker-subagent** — stale assumptions; a fresh, targeted re-check resolves it. State precisely what that re-check should verify.
   - **Merge-with-flag** — scope mismatches and low-severity contradictions; keep both outputs, visibly marked as disagreeing, for a human or the lead to weigh.
7. **Call out false positives.** If a pair looked suspicious but turns out to be only a wording difference with no real disagreement, say so explicitly rather than inflating the conflict count.
8. **State the confidence limit.** Flag which conflicts are clearly real from the text alone versus merely plausible but unverifiable without more context.

## Output format

Produce one markdown report with:

1. **Conflict Summary table** — Pair | Type | Severity | Caught by current policy? (yes/no/unclear)
2. **Per-pair detail** — quoted spans from both sides, classification reasoning, severity reasoning, recommended policy with a one-line concrete consequence if left unresolved.
3. **False positives noted** — any ruled-out pair and why.
4. **Pipeline-level recommendation** — one paragraph on whether the default merge behavior should change before the next run.

## Guardrails

- Never report a conflict without quoting the exact text from each side — no "these seem to disagree."
- Never call a scope mismatch a factual contradiction; that's the most common false alarm and conflating them defeats the point.
- Never silently decide which sub-agent is "right." The whole point is to surface the disagreement for a policy decision, not to replicate the silent-pick failure this exists to catch — unless the user gave explicit ground truth to check against.
- Never recommend a policy without naming the concrete downstream consequence of leaving the conflict unresolved.
- If only one sub-agent output is given, say plainly there's nothing to reconcile rather than inventing a second viewpoint.
- If the pasted outputs are full raw transcripts, note that this is still text-based pattern matching — it won't catch a conflict that exists only in reasoning the sub-agents never wrote down.

## How this differs from existing "agent output reconciler" skills

A few public Claude Code skill collections already ship something adjacent — notably a community "agent-output-reconciler" skill that checks per-task result files against acceptance criteria inside a specific task-splitter/acceptance-gate workflow convention, and a bundled "merge-reconciler" skill in Nous Research's Hermes Agent that arbitrates git merge conflicts between two agents' code branches. Both require adopting a specific framework's file layout or working at the git-diff level.

This skill is deliberately framework-agnostic and conflict-type-agnostic: it works from any two pasted sub-agent *outputs* (not file-layout conventions, not git diffs), classifies the disagreement by type (factual contradiction / scope mismatch / stale assumption) rather than just flagging "mismatch," and recommends a policy tied to severity and a named downstream consequence — so it's usable as a one-off audit on any pipeline, in any chat tool, with zero setup.
