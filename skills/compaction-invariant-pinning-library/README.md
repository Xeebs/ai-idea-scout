# Compaction Invariant Pinning Design

A self-contained prompt template for designing what a long-running AI agent should permanently protect from context compaction — the "already tried and failed," the hard constraints, and the key decisions that must survive every summarization pass — versus what's safe to let a compaction summary compress away. Paste the block below into any AI chat tool (Claude, ChatGPT, etc.) along with your inputs.

## When to use this

You're running, or about to run, a long-horizon autonomous agent — a coding agent, a research agent, or any multi-hour task runner — that hits automatic context compaction more than once per session (Claude Code's auto-compact, a LangGraph checkpointer summarization step, or a custom summarizer you built into an agent loop). Either you've noticed the agent re-attempt a fix it already tried and failed a few compactions ago, or you want to design around that failure before it happens. This gives you a one-time design pass: a concrete policy for what to pin, a token budget for the pinned content, and reusable classification rules — not a live implementation.

Don't use this to debug one transcript where something unrelated clearly broke (a tool outage, a bad prompt). It's for designing a repeatable policy for a recurring compaction pattern.

## What you need to provide

**Data source: Manual.** Everything this skill works from is text you paste into the conversation — there is no API, connector, or live session this skill reads on its own.

1. **Workflow description** — what the agent does, which framework it runs on (Claude Code, LangGraph, a custom loop), roughly how long sessions run, and roughly how many compactions a session hits.
2. **Compaction config, if you know it** — the trigger threshold and summarization prompt you're using, or just say "default/unknown."
3. **A transcript excerpt or a handful of representative turns** (strongly recommended) — real lines showing attempted fixes and their outcomes, constraints that got stated, or decisions that got made, ideally spanning a point where compaction actually fired. If you don't have one, say so — the output will be clearly marked provisional instead of silently guessing.

## The prompt to paste

```
You are designing a context-compaction "invariant pinning" policy for my agent workflow. Do not write code or build the live middleware — produce only the design document described below.

My workflow:
[paste: what the agent does, framework, session length, how often it compacts]

My compaction config:
[paste: trigger/threshold + summarization prompt, or write "default/unknown"]

Sample transcript / representative turns (if available):
[paste real lines showing attempted fixes + outcomes, constraints, decisions — or write "none available"]

Do the following:
1. Classify my workflow's domain and session shape from the description.
2. If I gave you a transcript, extract three lists VERBATIM from it, never inventing content: (a) tried-and-outcome items — approaches attempted and whether each succeeded/failed/was inconclusive, (b) hard constraints stated to hold the whole session, (c) key decisions other steps depend on, with their stated or inferable reason. If I gave you no transcript, generate illustrative examples instead and label that whole section "hypothetical (no transcript provided)."
3. Classify every item into exactly one bucket: PIN (must survive every future compaction untouched), SUMMARIZE (fine to compress, gist survives), or DROP (adds no value even summarized). Tag any PIN item whose failure reason could become invalid later (e.g. a transient error) as REVIEW-ON-RETRY instead of treating it as permanent.
4. Check every failed attempt for a later superseding success on the same approach. If the transcript shows the same approach retried later and that retry succeeded, tag the original failure SUPERSEDED (keep it as historical context) instead of leaving it as a standing "already tried, don't retry" block that would wrongly discourage the now-working approach.
5. Draft a pinned-slot schema: a short structured template with field names and one real example row per field, drawn from the actual PIN items.
6. Recommend a token budget for the pinned slot: an absolute ceiling based on expected PIN volume over the stated session length, plus an eviction rule for what gets dropped first if the ceiling is hit (state which priority order you recommend and why for this workflow).
7. Write plain-language classification rules, one per bucket, that someone could apply consistently on every future compaction for this same workflow — not just for this one sample.
8. State plainly whether this output is "validated against sample" or "provisional (no transcript)," and name the single most important thing to check once this runs against a real compaction event.

Output as a markdown report with these exact sections in order: Workflow Summary, Extracted Candidates (with PIN/SUMMARIZE/DROP/REVIEW-ON-RETRY tags), Pinned-Slot Schema, Token Budget, Classification Rules, Validation Status and Next Step.

Guardrails: never mark everything PIN "to be safe" — every PIN needs a specific reason it would cause a repeated failure or lost constraint if dropped. Never invent transcript content — label generated examples as hypothetical. Never pin content that changes moment-to-moment (file contents, timestamps, live variable values) — only pin stable facts: outcomes, constraints, decisions. Never claim this has been measured — it's a design and a hypothesis, not a validated result. This is a design document, not the live hook/middleware itself.
```

## What you get back

A markdown report with six sections, in this order:

1. **Workflow Summary** — one paragraph on domain, framework, and session shape.
2. **Extracted Candidates** — three labeled lists (tried-and-outcome, hard constraints, key decisions), each item tagged PIN / SUMMARIZE / DROP (and REVIEW-ON-RETRY where relevant). Marked "hypothetical" if you didn't supply a transcript.
3. **Pinned-Slot Schema** — the structured template you'd actually store, with a real example row per field.
4. **Token Budget** — a specific number, the reasoning behind it, and the eviction-priority rule for when it's exceeded.
5. **Classification Rules** — a short, reusable rule per bucket you (or a later automated classifier) can apply next time compaction fires on this workflow.
6. **Validation Status and Next Step** — whether the design is provisional or validated against your sample, and the one thing to check once it runs for real.

## Guardrails (built into the prompt above)

- Never pins everything "to be safe" — every recommendation traces to a specific reason.
- Never invents transcript content — hypothetical examples are always labeled as such.
- Never recommends pinning volatile, moment-specific content — only stable facts.
- Never claims a measured result — this is a design pass, not an eval.
- Never pretends to be the live middleware — it's the design step before you build or install that.

## What this is not

This does not implement the actual compaction hook, write code, or run against a live agent session. It produces the policy document a human (or a later automated classifier) would use to configure that hook. If you need the always-on enforcement — a library that actually intercepts Claude Code's PreCompact hook or a LangGraph checkpointer and applies this policy live — that's a separate build, not something this skill does.
