# Scenario 1: Multi-day coding agent with periodic summarization

## Input (realistic, as a team would actually paste it)

> SYSTEM PROMPT: "You are an autonomous coding agent. Your job is to migrate the billing service from the legacy REST client to the new gRPC client across the entire codebase, keeping all existing tests passing. Work until the migration is complete."
>
> TOOLS: read_file, write_file, run_shell (for running tests and git commands), search_codebase (grep-like search across the repo), create_pr.
>
> EXPECTED RUN LENGTH: This runs as a standing session over roughly 2-3 days of wall-clock time, checking in periodically but mostly autonomous; expect 300-500+ tool calls total.
>
> MEMORY/COMPACTION STRATEGY: We use a sliding window — once the context hits about 80% of the model's limit, we summarize everything older than the last 20 turns into a short paragraph and drop the raw turns. The summary is regenerated each time the window fills again (so old summaries get re-summarized, compounding).
>
> SAMPLE TASK: The actual migration task above — roughly 40 files touched across 6 services, each needing the client swap plus updated tests.
>
> KNOWN PAST ISSUE: On a similar past migration, we noticed the agent re-introduced a bug in a file it had already fixed earlier in the run, as if it forgot it had already handled that file.

## Pass criteria

The skill's output should:
1. Summarize the architecture correctly (autonomous multi-day coding agent, side-effecting tools, sliding-window summarization with re-summarization of summaries).
2. Rate **state loss** as HIGH or at minimum MEDIUM, explicitly citing the repeated-summarization-of-summaries detail (lossy compounding of what gets dropped each time) as the specific mechanism — not a generic "summarization is risky" statement.
3. Rate **compounding error** as MEDIUM or HIGH, citing the side-effecting tools (write_file, run_shell, create_pr) combined with no explicit verification-gate description beyond "keep tests passing" as a self-reported (not externally enforced) check.
4. Connect the known past issue ("re-introduced a bug in an already-fixed file") explicitly to the state-loss rating as corroborating evidence — a good answer should notice this detail is literally an instance of the risk it's rating, not ignore it.
5. Produce at least 2 concrete test scenarios, at least one of which is built from the actual migration task (e.g., "ask the agent at steps 50, 150, 300 which files it has already completed and cross-check against git log/PR diffs").
6. End with a bottom-line sentence naming state loss (or compounding error, if argued well) as the top risk, not a blended or evasive answer.

## Fail criteria (any of these = output needs revision)

- Blends the three failure modes into a single score.
- Rates state loss without mentioning the resummarization-of-summaries detail specifically.
- Ignores the "known past issue" entirely instead of using it as evidence.
- Gives vague test scenarios ("test the agent thoroughly over a long run") instead of concrete, runnable ones.
- Claims this audit proves the agent will or won't fail, rather than framing it as a risk read pending real testing.
