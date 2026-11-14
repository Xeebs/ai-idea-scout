# Agent Trace Strategy Viewer

A self-contained prompt template for turning one long, hard-to-read agent execution trace into a short, phase-by-phase strategy summary — and, if you have a second trace of the same task that succeeded, a diff showing exactly where the two runs' strategies diverged.

This is for the moment you have a trace with dozens or hundreds of steps (a coding agent, a research agent, a support bot) and reading it span-by-span top to bottom is too slow. Instead of "step 1: called search_docs, step 2: called search_docs again, step 3: called search_docs again..." you get "Phase 1 (steps 1–12): searched docs repeatedly for the API signature, found nothing."

## When to use this

- You have one long failing agent trace and want to know what the agent was actually doing, not just where it stopped.
- You have two traces of the same task — one that passed, one that failed — and want to know the first point where their strategies diverged.
- A flat linear trace viewer is giving you a wall of spans with no higher-level structure.

Skip this for a single-call failure or a trace that's obviously one undifferentiated phase end to end — just read it directly. This is about whether the trace actually contains more than one distinct strategy, not a fixed step count: a short 6–10 step trace that shifts strategy partway through (or that you're comparing against a second trace) is still worth segmenting; a 40-step trace that's really just one long call is not.

## What you need to hand over

**Data source note**: this works off a trace export your framework or observability tool already produces — you are not being asked to retype or reconstruct what the agent did. Provide:

1. **The primary trace** (required) — paste the raw JSON or text export of the failing run. This can come from LangGraph's callback/checkpoint output, or an export from Phoenix, Langfuse, LangSmith, or any similar trace store. If your AI tool has a live connector to one of these platforms already configured, you can instead give a run ID/URL and ask it to fetch the trace through that connector — but a pasted export always works and is the default path.
2. **A second "known-good" trace of the same task** (optional) — only needed if you want the diff/divergence analysis. Same format as above.
3. **A one-line description of the task/goal** (optional) — helpful if it's not obvious from the trace content itself, so the strategy labels can be judged against what the agent was actually supposed to accomplish.

## The prompt

Paste this along with your trace(s) into any AI chat tool:

> I'm giving you a long agent execution trace (and optionally a second, successful trace of the same task). Instead of summarizing it as a flat list of steps, do the following:
>
> 1. Normalize the trace into an ordered list of steps: index, actor (tool/LLM/system), one-line input/output summary, status (ok/error/retried).
> 2. Segment the steps into phases. Open a new phase wherever there's a sustained tool-type switch, the start or end of a retry loop (same action repeated with no new information), an explicit "trying a different approach" moment, or a hard context reset. Give each phase a step-index range.
> 3. Label each phase with one short, plain-language strategy description, and cite the specific step indices that label is based on. Never give me a label you can't point to steps for.
> 4. Flag anomalies per phase: wasted retry loops, unrecovered tool errors, and whichever phase contains or directly precedes the run's failure.
> 5. If I gave you a second "known-good" trace: run steps 1–4 on it too, align the two phase sequences by similarity (not by raw step count), and tell me the *first* phase pair where the two strategies meaningfully diverge, naming both step ranges and the specific differing action.
> 6. End with a 2–3 sentence plain-language bottom line: the most likely point of failure or divergence, grounded only in what you just cited — not speculation beyond it.
>
> If the trace is too short or already a single phase, say so and just summarize it directly instead of inventing phase boundaries.
>
> Never invent trace content that isn't in what I gave you (timestamps, costs, retry counts, model names) — say "not present in trace" instead of guessing.

## What you get back

A short report with:
- **Trace summary** — step count, time span if available, recorded outcome.
- **Phase table** — phase number, step range, one-line strategy label, status flag, cited evidence steps.
- **Flags** — any anomalies found, each with its step range.
- **Divergence** (only if you gave two traces) — the first diverging phase pair and what specifically differed.
- **Bottom line** — 2–3 sentences on where to look first.

## Guardrails this depends on

- Every phase label must cite specific step indices — an uncited, narrative-sounding label is exactly the failure mode this exists to prevent.
- No invented trace content — missing fields get called out as missing, not filled in with a guess.
- No manufactured phases on a trace that's genuinely short or single-phase.
- If a live connector could fetch the trace directly, that's preferred over asking you to paste a possibly stale copy — but a pasted trace is always accepted and used as given.
