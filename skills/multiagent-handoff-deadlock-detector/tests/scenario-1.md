# Scenario 1 — LangGraph research pipeline with a real deadlock risk

## Input (what the user pastes)

> We've built a 4-agent research pipeline in LangGraph and want a design review before we deploy it.
>
> - **Researcher** agent: searches the web, gathers sources, then hands off to **Critic**.
> - **Critic** agent: reviews the sources Researcher gathered. If it judges the sources insufficient, it routes back to **Researcher** asking for more (up to 3 rounds — we have a `revision_count` state field that increments each time and Critic always checks `revision_count >= 3` before deciding to send back; once it hits 3 it routes forward to **Writer** regardless). If the sources look fine, it also routes forward to **Writer**.
> - **Writer** agent: drafts the report from the approved sources, then hands off to **Approver**.
> - **Approver** agent: reviews the draft. This is implemented as a LangGraph edge where the Writer node literally blocks on `approver_result = graph.invoke_and_wait(approver_node, draft)` — Writer cannot return until Approver's node returns a verdict. If Approver rejects, it routes back to Writer for a rewrite, and that edge is also a blocking call: Approver's node does `writer_result = graph.invoke_and_wait(writer_node, feedback)` and waits for Writer's redo before proceeding. There's no counter, timeout, or max-retries on this particular back-and-forth — we just assumed it would eventually converge.
>
> Is any of this a real deadlock risk?

## Expected handling

The reviewer should build a 4-node graph (Researcher, Critic, Writer, Approver) with these edges:
- Researcher → Critic (BLOCKING or ASYNC per LangGraph's normal node transition — reasonable either way, not the crux of the exercise)
- Critic → Researcher (CONDITIONAL, revision_count < 3)
- Critic → Writer (CONDITIONAL, revision_count >= 3 or sources approved)
- Writer → Approver (BLOCKING, explicit `invoke_and_wait`)
- Approver → Writer (BLOCKING, explicit `invoke_and_wait`, no counter/timeout stated)

It must find two cycles:
1. **Researcher ↔ Critic** cycle — should be classified `BENIGN_LOOP`, explicitly citing the `revision_count >= 3` termination mechanism as the reachable exit.
2. **Writer ↔ Approver** cycle — should be classified `DEADLOCK_RISK`: both edges are explicitly `BLOCKING` (`invoke_and_wait` both directions) and the input explicitly says there is no counter or timeout on this pair — "assumed it would eventually converge" is not a stated termination mechanism.

For the Writer↔Approver finding, it must propose at least one concrete breaking rule naming Writer and Approver specifically (e.g., a max-rewrite counter mirroring the Researcher/Critic pattern, or a timeout-plus-human-escalation fallback) — not a generic "add a timeout."

## Pass/fail criteria

- PASS requires: both cycles identified; Researcher↔Critic correctly called BENIGN_LOOP with the revision_count mechanism cited; Writer↔Approver correctly called DEADLOCK_RISK with both edges named as BLOCKING and the absence of a stated exit explicitly noted; at least one named breaking rule given for Writer↔Approver; a closing note that this is a static read, not a live monitor.
- FAIL if: Writer↔Approver is missed entirely or waved through as benign because "it's just a review loop like the first one" (the key difference — one cycle has a stated counter, the other doesn't — must be the stated reason, not vibes); or if Researcher↔Critic is incorrectly flagged as a deadlock despite its explicit counter; or if the output recommends writing the actual auto-break code rather than naming the design rule.
