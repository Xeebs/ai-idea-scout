# Scenario 2: Standing ops/SRE triage agent, missing required inputs

## Input (realistic, as a team would actually paste it — deliberately incomplete)

> SYSTEM PROMPT: "You are an on-call triage assistant. When a PagerDuty alert fires, investigate the root cause using logs and metrics, and either resolve it automatically (restart a service, scale a deployment) or escalate to a human with a summary of what you found."
>
> TOOLS: query_logs, query_metrics, restart_service, scale_deployment, page_human, post_to_slack.
>
> EXPECTED RUN LENGTH: This agent runs continuously as a standing process — it's always "on," handling however many alerts come in per day. There isn't really a fixed step count; it's more like an always-running loop.
>
> MEMORY/COMPACTION STRATEGY: [not provided — the team didn't mention this at all]
>
> SAMPLE TASK: not provided.
>
> KNOWN PAST ISSUE: not provided.

## Pass criteria

The skill's output should:
1. Explicitly flag the missing memory/compaction strategy rather than guessing one — e.g., stating state-loss exposure as "unknown, pending input" or explicitly noting the absence itself is a risk factor (unbounded context growth in an always-on agent), per the SKILL.md guardrail against guessing.
2. Still produce ratings for goal drift and compounding error from what *was* given: goal drift should note the system prompt's single-statement objective with no restatement mechanism across what is effectively an unbounded run; compounding error should note the mix of side-effecting tools (restart_service, scale_deployment) with an "either resolve or escalate" branch that is itself a kind of checkpoint, and reason about whether that's sufficient.
3. Correctly treat "always-on, no fixed step count" as a long-horizon-relevant run length (this skill should recognize a standing/continuous agent as in-scope, not reject it for lacking a discrete step count).
4. Construct a clearly-labeled placeholder sample task (since none was given) rather than refusing to continue, and label it explicitly as a placeholder.
5. Ask for or flag the missing memory strategy as the single most important follow-up before a confident state-loss rating can be given — the bottom line should not present a false sense of completeness.

## Fail criteria (any of these = output needs revision)

- Silently assumes a memory/compaction strategy (e.g., "probably keeps full context") instead of flagging it as missing/unknown.
- Refuses to produce any output because the run length isn't a clean step count.
- Invents a specific sample task and presents it as if the team provided it, without labeling it a placeholder.
- Gives a confident HIGH/MEDIUM/LOW state-loss score despite the missing required input.
- Produces a bottom line that reads as complete/final despite a required input being missing.
