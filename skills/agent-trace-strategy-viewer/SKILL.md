---
name: agent-trace-strategy-viewer
description: Segments a long agent execution trace (dozens to hundreds of steps) into labeled strategy phases instead of a flat pass/fail span list, and diffs a failing run against a known-good run to find where their strategies diverged. Use when someone pastes or points at a long agent trace and asks "what was it actually doing" or "why did this one fail when the other one passed."
---

# Agent Trace Strategy Viewer

## When to use this
Someone hands you one long agent execution trace — a coding agent, a research agent, a customer-support agent, anything with dozens to hundreds of steps (tool calls, LLM calls, retries) — and asks something like "what was this agent actually trying to do," "where did this go off the rails," or "why did run A fail when run B passed on the same task." A flat linear read of 300 spans is too slow for this; this skill produces a short, phase-level strategy summary instead, and — if given a second trace of the same task — a diff that names the first point the two runs' strategies diverged.

Do not use this for a single-call failure or a trace that is obviously one undifferentiated phase from end to end — say so and just read it directly; manufacturing phase boundaries on a trace that has none adds noise, not clarity. This is a judgment about whether the trace actually contains multiple distinct strategies, not a fixed step count — a short trace (even 6–10 steps) that visibly shifts strategy partway through, or that's being compared against a second trace in diff mode, is still worth segmenting; a 40-step trace that's just one long tool call with verbose output is not.

## Inputs
**Data source**: Connected — this skill consumes a trace export already produced by the user's agent framework or observability backend (LangGraph callback/checkpoint JSON, or an OTel-based export from Phoenix, Langfuse, or LangSmith). Those export/connector mechanisms already exist and are mature today; nothing here asks the user to hand-retype or reconstruct trace data that a connector could supply directly. Concretely, provide one of:
1. A raw trace export (paste the JSON/text, or attach the export file) — the primary, always-working path in a plain chat tool with no live connector.
2. If you're in an environment with a live MCP connector to LangSmith, Langfuse, or Phoenix already active, a run ID or URL — fetch the trace through that connector instead of asking for a paste.
3. Optionally, a second trace export of the *same task* that succeeded, for diff mode.
4. Optionally, a one-line description of the task/goal, if it isn't obvious from the trace content — this gives the phase labeler a target to judge "on strategy" vs. "off strategy" against.

Never ask the user to manually describe what the agent did step by step — that defeats the point. If given only a trace ID and no connector is actually available, say so plainly and ask for the exported file instead of guessing at its content.

## Procedure
1. **Ingest.** If a live connector tool for the named backend is available in this session, fetch the trace by ID. Otherwise parse the pasted/attached export. Normalize into an ordered list of steps, each with: index, actor (tool name, LLM call, or system event), a one-line input/output summary, and status (ok / error / retried).
2. **Segment into phases.** Walk the step list and open a new phase boundary wherever one of these occurs: a sustained tool-type switch (e.g., three straight `read` calls followed by a run of `write`/`edit` calls), the start or end of a retry loop (same action repeated with no new information), an explicit plan/replan or "let me try a different approach" moment, or a hard context reset. Each phase gets a step-index range (e.g., steps 1–14).
3. **Label each phase.** For each phase, write one short strategy description (one line, plain language — e.g., "searched docs for the API signature, found nothing, switched to reading the installed package source directly") derived only from that phase's steps. Every label must cite the step indices it's grounded in. Never write a label you can't point back to specific steps for.
4. **Flag anomalies per phase.** Note, per phase: retry loops that repeat without new information (likely wasted steps), tool errors that were never recovered from, and whichever phase directly precedes or contains the run's terminal failure.
5. **Diff mode (only if a second trace was given).** Run steps 1–4 on the second trace. Align the two phase sequences by similarity of phase type/label (not by raw step count, since a passing run and failing run rarely have equal step counts). Walk the aligned sequence and report the *first* phase pair where the two runs' strategies meaningfully differ — name both phases' step ranges and the specific action that differed (e.g., "run A's phase 3 retried the same failing call four times; run B's phase 3 abandoned that call after one failure and read the config file instead").
6. **Write the bottom line.** In 2–3 plain-language sentences, state the most likely point of failure or divergence and what to check first — grounded in the evidence just produced, not speculation beyond it.

## Output format
A markdown report with these sections, in order:
1. **Trace summary** — total step count, time span if timestamps are present (otherwise state "no timestamps in export"), and the recorded outcome (pass/fail/unknown).
2. **Phase table** — columns: Phase # | Step range | Strategy label | Status (ok / flagged) | Evidence (cited step indices).
3. **Flags** — a bullet per anomaly found in step 4, each with its cited step range.
4. **Divergence** (diff mode only) — the first diverging phase pair, both step ranges, and the specific differing action.
5. **Bottom line** — the 2–3 sentence plain-language diagnosis from step 6.

If the trace was too short or single-phase to meaningfully segment, skip the phase table and say so directly in the trace summary instead.

## Guardrails
- Never produce a phase label that isn't grounded in cited step indices from the actual export — an uncited, narrative-sounding label that merely sounds plausible is the exact failure mode this skill exists to avoid (LLM-hallucinated coherence over real evidence).
- Never invent trace content absent from the export (costs, timestamps, model names, retry counts) — state "not present in trace" rather than filling gaps with a plausible-sounding guess.
- Never fabricate phase boundaries on a trace that genuinely has none (one undifferentiated action, or verbose output from a single call) just to look thorough — say the trace doesn't warrant segmentation and summarize it directly instead. A trace's step count alone is not the test; whether it contains more than one distinct strategy is.
- Never ask the user to manually retype trace content that a named connector (LangSmith/Langfuse/Phoenix) could supply directly if one is active in the session — prefer the connector fetch over a paste when both are available, but accept and use a paste without complaint if that's what's given.
- Never claim a root cause beyond what step-level evidence shows; phrase anything not directly evidenced as "possible" and say what additional data would confirm it.
