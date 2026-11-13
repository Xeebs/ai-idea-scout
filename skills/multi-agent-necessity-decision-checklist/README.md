# Multi-Agent Necessity Decision Checklist

A scored, weighted checklist that answers "should this be multi-agent, or single-agent with good tools?" — with a per-criterion breakdown and a quantified estimate of the "multi-agent tax" (extra tokens, latency, failure surface), instead of a gut call or whatever a tutorial happened to scaffold.

Paste this entire file into any AI chat tool (ChatGPT, Claude, Gemini, Copilot Chat, etc.) along with your task description, then follow the prompt at the bottom.

## When to use this

Use it when you're at a design decision point for an agent system and either:
- you're asking yourself (or a tutorial just assumed) "should this be multiple agents?",
- you already have a planned or existing split into roles (planner, workers, critic, etc.) and want a sanity check on whether that split is earning its cost, or
- you're reviewing someone else's agent architecture sketch and want a structured second opinion instead of an intuition call.

It is a one-time scoring exercise, not a monitoring tool — it doesn't watch your system over time or re-score itself; run it again when the task or constraints materially change.

## What to hand it

Give the assistant:
1. **Task description** — what the system needs to accomplish, in your own words.
2. **Planned or existing agent roles**, if you have them (e.g. "planner agent + 3 worker agents + critic agent"). If you haven't decided yet, say so — it'll score from the task alone.
3. **Constraints** — your latency budget (does this need to answer in under a second, or is minutes fine), your cost/token budget if you know it, your team size, and whether your team can currently trace a failure across multiple agent handoffs (debugging capacity).

Everything here is information you type or paste — this skill doesn't read any file, repo, or API on its own. If you don't know a constraint, say "unstated" rather than guessing; the assistant will mark it neutral and tell you what answer would change the result.

## What it does

The assistant scores your task against six criteria, each 0-5, each weighted by how much it actually drives the single-vs-multi decision in practice:

| Criterion | Weight | What pushes the score up (toward multi-agent) |
|---|---|---|
| Decomposability | 2 | Task splits into genuinely independent subtasks with little shared state |
| Specialization need | 2 | Subtasks need materially different tools/personas/domain context |
| Verification/critique need | 1.5 | An independent second-opinion check would materially change outcomes |
| Parallelism value | 1.5 | Subtasks can run concurrently with real wall-clock savings |
| Cost/latency budget | 2 | You have budget to absorb multiple agent calls (batch, not sub-second) |
| Debugging capacity | 2 | Your team can already trace failures across agent-to-agent handoffs |

It multiplies each score by its weight, sums them (max 55), and maps the total to:
- **Under 22** → single-agent-with-tools.
- **22-38** → hybrid — prototype both, but default to trying single-agent-with-tools first; the reply will name the specific criteria pulling the score toward multi-agent so you know what to re-test if single-agent hits a wall.
- **Over 38** → multi-agent is justified by the stated criteria.

Alongside the verdict, it estimates the "multi-agent tax" for your specific proposed (or minimally viable) number of agent roles: a token-multiplier range (roughly 4x baseline for one agent with tools, up to 3x-15x baseline for a naive multi-agent split, scaling with how many agents and handoffs you'd add), a latency multiplier (each sequential handoff is roughly another full round trip; parallel subtasks cost far less), and a failure-surface count (how many new handoff points your design adds where context can get dropped or mis-passed). These are labeled explicitly as estimates from published benchmark ranges, not a measurement of your actual system — if the decision is high-stakes, it will suggest running your own quick before/after test on one representative task.

If you mention non-performance reasons for splitting — compliance/data-separation requirements, team ownership boundaries, org-chart reasons — those are called out separately, never folded into the numeric score, because a low score shouldn't be read as overriding a real compliance requirement.

## Output you'll get

1. **Verdict line**: `Recommendation: <single-agent-with-tools | hybrid | multi-agent justified>` with the weighted total out of 55.
2. **Criteria table**: each criterion, its score, weight, weighted subtotal, and a one-line reason tied to what you actually described (not generic boilerplate).
3. **Multi-agent tax estimate**: token multiplier range, latency multiplier, and failure-surface count, each clearly labeled as an estimate.
4. **Non-performance factors**, if you mentioned any, listed separately with a note that they can override the score.
5. **One summary paragraph** naming the 1-2 criteria that actually drove the result, and what new evidence would flip it.

## The prompt to paste

```
You are scoring whether my system below should be single-agent-with-tools or multi-agent, using a weighted rubric, not a gut call.

My task: <describe what the system needs to do>
My planned/existing agent roles (or "undecided"): <list roles, or say undecided>
My constraints: latency budget = <sub-second / seconds / minutes / batch>, cost/token budget = <known figure or "unstated">, team size = <N>, debugging capacity = <can you trace a failure across agent handoffs today? yes/no/unstated>
Any non-performance reasons for splitting (compliance, team ownership, etc.), if any: <describe or "none">

Score these six criteria 0-5 (higher = more multi-agent-favoring), weighted as shown, and give me the weighted total out of 55:
- Decomposability (weight 2): does the task split into genuinely independent subtasks with little shared state?
- Specialization need (weight 2): do subtasks need materially different tools/personas/domain context?
- Verification/critique need (weight 1.5): would an independent second-opinion check materially change outcomes?
- Parallelism value (weight 1.5): can subtasks run concurrently with real wall-clock savings?
- Cost/latency budget (weight 2): how much budget exists to absorb multiple agent calls?
- Debugging capacity (weight 2): can my team trace failures across agent-to-agent handoffs today?

For any constraint I marked "unstated," score it neutral (3/5) and tell me what answer would change the result.

Map the weighted total to a recommendation: under 22 = single-agent-with-tools, 22-38 = hybrid (prototype both, default to single-agent-with-tools first, name what's pulling it toward multi-agent), over 38 = multi-agent justified.

Then estimate the "multi-agent tax" for my proposed (or a minimally viable) number of agent roles: a token multiplier range, a latency multiplier based on sequential vs. parallel handoffs, and a count of new failure-surface points my design adds versus single-agent. Label these explicitly as estimates from published benchmark ranges, not measurements of my system, and tell me if a quick before/after test on one representative task would be worth running given how high-stakes this decision is.

List any non-performance reasons I gave separately from the score, and note they can override a low score.

Give me: (1) the verdict line, (2) the criteria table, (3) the tax estimate, (4) non-performance factors if any, (5) one paragraph naming what's actually driving the result.
```

## Guardrails this skill follows

- It never presents the token/latency multipliers as measured facts about your specific system — only as ranges from public reports, with a suggestion to run your own small benchmark if the stakes justify it.
- It never gives a bare yes/no without the per-criterion breakdown — the breakdown is the entire point; a verdict without it is just another unvalidated blog checklist.
- It never folds compliance or team-ownership reasons into the numeric score — those are listed separately and can override the score.
- It never guesses a specific number for a constraint you left unstated and presents it as given — it marks it neutral and tells you what would change the outcome.
- It never treats "the starter kit/tutorial defaulted to multi-agent" as evidence for any criterion — only the task and your stated constraints are scored.
