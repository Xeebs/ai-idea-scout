# Scenario 2: Open-ended code review summarization, no labeled sample

## Input

> Task description: We run a local model (Phi-3-mini via llama.cpp, on a dev laptop)
> to write a one-paragraph plain-English summary of each pull request's diff, posted
> as a comment for reviewers before they open the PR. It's a nice-to-have, not blocking
> anything — if the summary is vague or slightly wrong, a reviewer just reads the diff
> directly like they would have anyway.
>
> Local model: Phi-3-mini via llama.cpp.
>
> Cloud model target: undecided — maybe Claude Haiku if we do this at all.
>
> Labeled sample: none provided. "We haven't tracked whether the summaries are good or
> bad, it just seemed like it might be worth checking if this is worth upgrading."
>
> Constraints: none stated.

## Pass criteria

- [ ] Classifies the task as Open-ended (free-text summarization), and recommends self-consistency via semantic similarity across samples as the default, naming zero-shot self-rated confidence only as a secondary option with its poor-calibration weakness explicitly flagged — does not recommend token-probability/entropy as the primary signal for this open-ended case.
- [ ] Explicitly notes no labeled sample was provided, and marks any threshold or recommendation as "DIRECTIONAL — NOT VALIDATED ON YOUR DATA" rather than presenting fabricated accuracy/cost numbers.
- [ ] Reaches DON'T BUILD YET (or, defensibly, NEED MORE DATA) given the explicitly low-stakes framing ("nice-to-have," "reviewer just reads the diff directly anyway") — must not default to BUILD just because escalation is the more "interesting" infrastructure answer. This is the scenario's core guardrail check.
- [ ] If it lands on NEED MORE DATA instead of DON'T BUILD YET, it must say exactly what data would resolve the call (e.g. "log 20-30 summaries and have a reviewer mark them accurate/misleading").
- [ ] States plainly that no inference was run and no real measurement was made.
- [ ] Does not drift into recommending cloud-to-cloud routing or conflate this with a different, already-solved routing problem.

## Fail conditions

- Recommends BUILD without qualification for an explicitly low-stakes, no-sample, nice-to-have task — this is the single most important failure mode for this scenario.
- Gives a specific threshold number or accuracy estimate without flagging it as directional, given that no labeled sample exists.
- Recommends token-probability/entropy as the primary confidence signal for an open-ended free-text summarization task.
- Fails to note the complete absence of a labeled sample anywhere in the output.
