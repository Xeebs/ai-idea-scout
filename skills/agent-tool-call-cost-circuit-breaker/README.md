# Breaker Audit: Repeated-Failure Waste Finder for Agent Tool-Call Logs

A portable prompt that reads a batch of agent tool-call logs you already have and tells you (1) whether any runs are burning cost on doomed repeated-failure loops, (2) how much that's actually costing you, and (3) what starting threshold/window to use if you deploy a circuit-breaker to stop it going forward.

This is for anyone running agentic CI pipelines (PR-review bots, coding-agent GitHub Actions), scheduled batch agent jobs, or any metered agent workflow who either suspects wasted spend from retry loops or is about to size a circuit-breaker and doesn't want to guess the numbers. It works in any chat tool — paste your logs, no install required. It is a one-time, after-the-fact analysis of logs you paste in; it does not watch a live agent or stop anything by itself.

## How to use it

Paste the prompt below into any AI chat tool, then paste a batch of your agent run logs. For each tool call, make sure the logs include (or you add) at minimum: which run it belongs to, the tool name, the arguments (or a real summary, not just "called tool X"), whether it succeeded or failed, the error code/message on failures, and the call order. Cost per call (dollars, tokens, API credits, whatever unit you track) is optional but makes the dollar-waste number real instead of just a call count — if you don't have it, say so and the analysis will still run on call counts alone.

If your batch is very small (under ~10 calls total) or missing status on most lines, a good response will tell you the input is too thin and ask for a fuller export rather than guessing.

---

### The prompt

> You are auditing a batch of agent tool-call logs for repeated-failure loops that burn API/compute cost without making progress. This is a one-shot retrospective analysis of the logs provided — you are not watching a live agent and cannot stop anything in real time.
>
> For the logs I give you, do the following:
>
> 1. **Parse and normalize** each tool call into: run/session id, tool name, arguments, success/fail status, error code/message (if failed), and call order within its run. If a line is missing status or tool name, flag it instead of guessing.
>
> 2. **Run three detection passes per run:**
>    - **Strategy A — Identical-argument retry**: the same tool called again with the same arguments after a prior call to that exact (tool, arguments) pair already failed in that run.
>    - **Strategy B — Repeated error code**: the same tool producing the same error code/class two or more times in a run, regardless of whether arguments changed.
>    - **Strategy C — Semantically-similar-argument retry**: the same tool called with different arguments that share a stable identifying token already seen in a prior failure in that run — a PR number, file path, URL, ticket ID, or entity name re-targeted under reworded phrasing. Only report a Strategy C match if you can quote the actual matching token as evidence, and mark it confidence MEDIUM, never HIGH — this is text pattern-matching, not a guaranteed semantic judgment.
>
> 3. **Find the trip point per run**: the earliest call where any one strategy's match count reaches 2 repeats (never use a threshold of 1 — a single retry is normal, not a loop). Every call after that point in that run is "wasted" — it would not have run had a breaker already been in place.
>
> 4. **Tally**: per run, the wasted call count, which strategy triggered, and wasted cost (sum the cost field across wasted calls, if provided). Across the whole batch, total wasted calls, total wasted cost, and % of runs affected. If cost data is missing for any wasted call, report an explicit "cost unknown for N calls" — never substitute $0 or an invented average.
>
> 5. **Recommend starting breaker parameters** for each strategy that actually fired: a threshold (repeats before trip) and window (how many recent calls to track), set to one less than the earliest genuine repeat count observed for that strategy, floored at 2. If any run shows a 2nd or 3rd attempt on the same target *succeeding*, call that out explicitly as the floor — never recommend a threshold that would have blocked a call that actually worked.
>
> Output in exactly this format:
>
> ```
> ## Breaker Audit Summary
> <N> of <M> runs show a repeated-failure waste pattern — <X> wasted calls, <$Y or "cost data not provided"> wasted.
>
> ## Per-Run Breakdown
> | Run | Strategy triggered | Trip point (call #) | Wasted calls after trip | Wasted cost |
> |-----|--------------------|----------------------|--------------------------|-------------|
> | ... | A/B/C | # | # | $ or "unknown" |
>
> ## Strategy Breakdown
> - Strategy A (identical-argument retry): <count> runs
> - Strategy B (repeated error code): <count> runs
> - Strategy C (semantic-similar-argument retry): <count> runs — matched token(s): "<token>" in run <id>, ...
>
> ## Recommended Starting Breaker Parameters
> - Strategy A: threshold=<T>, window=<W> — <one-line rationale>
> - Strategy B: threshold=<T>, window=<W> — <one-line rationale>
> - Strategy C: threshold=<T>, window=<W> — <one-line rationale>, confidence MEDIUM
> (If a legitimate multi-attempt success exists in the batch, state it here as the floor.)
>
> ## Caveats
> - <data gaps found>
> - <confidence note on Strategy C matches>
> - This is a retrospective diagnostic on the logs provided, not a live monitor.
> ```
>
> Never invent a cost-per-call figure or fill in $0 when cost data wasn't given. Never report a Strategy C match without quoting the actual matching token as evidence. Never recommend a threshold of 1. If the batch shows a successful repeat attempt on the same target, treat it as a hard floor on your recommended threshold. If the batch is too thin (under ~10 calls, or missing status/tool throughout), say so and ask for a fuller export instead of producing a report.
>
> Here are the logs:
> [paste your batch of agent tool-call logs here]

## Why this exists

Agentic CI and batch-automation runs can get stuck re-trying something that will never succeed — the same already-failed PR refresh, the same 404'd page under a reworded query — and keep spending API/compute cost until an unrelated timeout or budget ceiling finally stops it, because nothing inspects the *shape* of the repeated failure mid-run. Deploying a live circuit-breaker to stop that requires picking a threshold and window, and guessing those numbers either over-trips on normal retries or misses the loop entirely. This prompt runs that sizing exercise against logs you already have, before you write or buy the live version.

Full project context and evidence: see [`ideas/agent-tool-call-cost-circuit-breaker.md`](../../ideas/agent-tool-call-cost-circuit-breaker.md) in the [ai-idea-scout](https://github.com/Xeebs/ai-idea-scout) repo.
