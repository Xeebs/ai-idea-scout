# Agent Labor Evidence-Sufficiency Reviewer

A paste-in prompt template for deciding whether to trust an AI agent's "task complete" claim before you pay for it, approve an invoice, or close out a bounty. Works in any AI chat tool — no installation, no special connectors.

## When to use this

You're the one holding the money: a marketplace operator, a client who hired an autonomous agent for a gig, or anyone paying out on a bounty an agent claims to have finished. You have the agent's execution log or trace for that specific job (whatever its framework produced — tool calls, intermediate outputs, timestamps) and the original task description. You have no independent cryptographic proof the agent actually did what it claims — only this paper trail. You want a structured read on how much that paper trail is actually worth before you release funds.

This is not for an agent checking its own work mid-task before it reports "done" — that's a different job (self-review during execution). This is for judging *someone else's* finished-work claim from the outside, after the fact, using only what's on paper.

## What to hand over

Paste two things directly into the chat:

1. **The original task description or acceptance criteria** the agent was given — even informal ("scrape these 50 URLs and return a CSV of titles and prices" is enough).
2. **The agent's execution log/trace for this specific job** — whatever got logged: a list of steps, tool calls, intermediate outputs, timestamps. If all you have is a bare final answer with no intermediate record, paste that — it's a valid (if weak) input, not a reason to give up.

If you don't have the task description, don't skip it — get it first. Judging a claim without knowing what was asked is not possible.

## What happens

Paste this instruction along with your two inputs above:

> Act as an evidence-sufficiency reviewer for a claimed-complete AI agent task. I will give you the original task description and the agent's execution log/trace. Do the following, using only what I paste — never invent trace content, timestamps, or tool calls that aren't there:
>
> 1. Extract the acceptance criteria from the task description. If it's vague, state what you're assuming and mark those assumptions as inferred, not given.
> 2. Walk the trace step by step: for each step, note the claimed action, its input, its output, and timestamp if present. Flag any step whose input doesn't trace back to a prior step's output or the task itself.
> 3. Flag any timestamp that's implausible for the claimed action (e.g., a web search logged as taking 0 seconds).
> 4. Classify the overall evidence density as one of: Bare claim (final output only, no steps shown), Self-narrated (agent's prose description of what it did, no raw tool-call records), Partial trace (some raw records, but gaps), or Full trace (step-by-step raw records from start to finish).
> 5. Check whether the final output actually satisfies the acceptance criteria from step 1 — independent of whether the process looks genuine.
> 6. List red flags: logical gaps, implausible timestamps, anything suggesting the log was written to match a known output after the fact.
> 7. Give an Evidence Sufficiency Rating — INSUFFICIENT / WEAK / MODERATE / STRONG — based mainly on evidence density and red-flag count. A Bare claim or Self-narrated log with any red flags is INSUFFICIENT. Never rate STRONG unless it's a full, raw, criteria-meeting trace.
> 8. List the specific missing evidence that would most improve the rating by one level — be concrete, not generic.
> 9. Give a plain recommendation: Pay / Hold and request specific evidence (name it) / Reject. This is a risk read for me to weigh, not a final call you make for me.
>
> Never claim this proves the work happened — it's a plausibility read, not a cryptographic proof. Never treat the agent's own narration as equivalent to raw tool-call evidence. If I didn't give you the task description, stop and ask for it instead of guessing.
>
> Task description:
> [paste here]
>
> Execution log/trace:
> [paste here]

## What you get back

A structured report in this order:

1. **Task Claim Summary** — one or two sentences on what was claimed delivered.
2. **Acceptance Criteria** — bulleted, each marked (stated) or (inferred).
3. **Evidence Walkthrough** — the trace, step by step, with flags inline.
4. **Evidence Density Classification** — Bare claim / Self-narrated / Partial trace / Full trace, with why.
5. **Red Flags** — bulleted, or "None found."
6. **Output-vs-Criteria Check** — pass/fail per criterion.
7. **Evidence Sufficiency Rating** — INSUFFICIENT / WEAK / MODERATE / STRONG, with a one-line reason.
8. **Missing Evidence Checklist** — concrete asks that would raise the rating.
9. **Recommendation** — Pay / Hold (with what to ask for) / Reject, one-sentence reasoning.

## What this is not

This does not cryptographically verify anything. It cannot catch a log that was carefully fabricated to look like a full, consistent trace end-to-end — it's a plausibility and completeness read, built for the much more common case of sparse, self-narrated, or internally inconsistent logs that agents and marketplaces actually produce today. If you need an actual tamper-evident guarantee, you want signed hash-chained receipts and re-execution spot-checks, which this skill doesn't produce — it just helps you decide, from a paper trail alone, whether you're being asked to trust too much on too little.
