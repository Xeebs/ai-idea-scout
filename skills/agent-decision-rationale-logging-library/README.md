# Why Not What: Decision-Span Patch Drafter

A prompt template for drafting a code patch that adds structured "decision-span" logging at one specific branch point in an agent's code — the exact place where an LLM is already asked to choose between options (use tool A vs. tool B, escalate vs. continue, answer from memory vs. retrieve). Paste the block below into any AI chat tool (ChatGPT, Claude, Gemini, etc.), then supply your branch-point code as instructed.

This does not require installing anything, and it is not an always-on logging library itself — it drafts the minimal patch for one named branch point, using one consistent schema, so you don't have to invent the schema or guess the wiring to your trace backend yourself. Today, most agent logging captures the action an agent took at a branch (which tool it called, which path it went down) but discards the reason the model gave for choosing it — this turns that reason into a queryable field sitting right next to the action, the next time something goes wrong three steps downstream of a bad branch decision.

## When to use this

- You have a specific agent codebase with a known decision point — a LangGraph conditional edge, a CrewAI task router, or a plain if/else that calls an LLM to decide — and a debugging session has made clear that the failures are wrong strategic choices, not crashed tool calls.
- You want "why did it branch this way" available in your trace store (Langfuse, Phoenix, Datadog, or any OpenTelemetry-compatible backend) without re-running the agent with extra logging enabled after the fact every time something looks wrong.
- You don't want to design the span schema yourself or guess how to wire it into whichever backend your team already uses.

This is a one-time patch-drafting pass on the branch point you describe. It is not a live monitoring tool, does not touch a running system, and the patch it drafts needs to actually be reviewed and pasted in by you — it's the instrumentation draft, not the maintained SDK.

## What to provide

- **Required**: the actual branch-point code — the function, conditional edge, or if/else block where the LLM's output decides which path runs next — pasted verbatim. Redact anything unrelated to the branch first.
- **Required**: which framework it's written in — LangGraph (conditional edge), CrewAI (task router), or "raw" (plain if/else calling an LLM). If you're not sure, say so and the draft will try to infer it from the code's shape, then confirm with you before proceeding.
- **Required**: which trace backend you want the span to land in — Langfuse, Phoenix, Datadog, a raw OpenTelemetry SDK/collector, or "none yet" (in which case the patch targets the raw OTel SDK so it's portable to any of those later).
- **Optional**: whether your LLM call already produces an explicit rationale (a chain-of-thought field, or a `reasoning`/`rationale` key in structured output). If you don't know, the draft will check the snippet itself.

## The prompt

```
You are drafting a code patch that adds a structured "decision span" at one
specific branch point in my agent code — the place where an LLM's output
determines which of several paths runs next.

Here is the decision-span schema to populate, using exactly these fields,
no more and no fewer unless I explicitly ask for additional ones:
- decision_point_id: derived from the function/edge/router name
- branch_options_considered: the options the branch could choose between,
  as evidenced in my code — never invent options not present in the snippet
- chosen_option: which one was selected, read from my existing branching variable
- stated_rationale: the model's own text explaining its choice, read verbatim
  from wherever it already exists in my code, or newly added if it doesn't
- confidence: if my LLM output already includes one, otherwise null
- timestamp: captured at the moment the decision is made, not after the
  downstream action runs

My framework is: <LANGGRAPH CONDITIONAL EDGE / CREWAI TASK ROUTER / RAW IF-ELSE
— name it, or say "not sure" and I'll describe what I see first>

My trace backend is: <LANGFUSE / PHOENIX / DATADOG / RAW OPENTELEMETRY SDK /
NONE YET>

Here is my branch-point code (redacted of anything unrelated to the branch):

<PASTE YOUR BRANCH-POINT CODE HERE — the function, conditional edge, or
if/else block, including the LLM call that produces the decision>

[Optional — tell me if this code already elicits an explicit rationale from
the model, e.g. a chain-of-thought field or a reasoning/rationale key in
structured output. If you don't know, check the snippet yourself.]

Now do the following:

1. Locate the exact branch point in my snippet. If more than one plausible
   branch point exists, or none does, stop and ask me which one before
   drafting anything.
2. Check whether my snippet already captures an explicit rationale from the
   model. If yes, note exactly which field holds it — read from there, don't
   re-elicit it. If no, add the smallest possible addition to my existing
   prompt or structured-output schema to elicit one, and call this out
   explicitly as a BEHAVIOR-ADJACENT CHANGE, separate from pure logging —
   never silently fold it into the logging diff.
3. Populate the decision-span schema above for this branch point, reading
   values only from what's actually evidenced in my code.
4. Draft the patch as a clear BEFORE / AFTER code block, touching nothing in
   my snippet except the span emission (and, only if step 2 required it, the
   one small rationale-eliciting addition, marked as a separate change).
   - If my framework is LangGraph: wrap the conditional-edge function so the
     span emits before the chosen edge is returned.
   - If CrewAI: wrap the task-router call so the span emits before the
     selected task is dispatched.
   - If raw if/else: insert the span emission right after the LLM call
     returns, before the branching logic executes.
5. Wire the span to my named backend: draft the minimal OTel-compatible span/
   attribute call for Langfuse, Phoenix, or Datadog if I named one. If I said
   "none yet," draft against the raw OpenTelemetry SDK
   (tracer.start_as_current_span) instead, so it's portable to any backend
   later without rewriting the branch-point code again.
6. Write it up using this structure:

## Branch Point Identified
## Rationale Capture
## Decision-Span Schema (populated for this branch point)
## Code Patch (<framework>)
### Before
### After
## Wiring Notes
## Caveats

Rules you must follow:
- Never invent branch_options_considered entries not evidenced in my code.
- Always state, every single time, that stated_rationale is the model's
  self-reported reason, not a verified causal account of its actual decision
  process — this caveat must appear in every output, no exceptions.
- Never change my branch point's actual decision logic or outcome — you are
  adding observability, not changing which path gets taken.
- Never claim the patch "implements" or is "compatible with" Galileo's
  decision spans or Datadog's execution flow features by name — this is an
  independent, portable schema, not a reimplementation of either vendor's
  proprietary feature.
- Never add schema fields beyond the six listed above unless I explicitly ask.
- If you can't tell my framework or backend from what I gave you, ask me
  before drafting — don't guess an API shape and hand me code that won't run.
- Don't touch more of my snippet than the branch point itself — no unrelated
  refactors, renames, or style changes riding along with the instrumentation.
```

## What you get back

A markdown write-up with the exact branch point identified, how the rationale is being captured (an existing field, or a small newly-added one — flagged as behavior-adjacent if so), the decision-span schema populated with values traced to your actual code, a before/after code patch scoped only to that branch point, notes on wiring the span to your named trace backend, and a caveat block (always present) stating that the captured rationale is self-reported by the model, not a verified account of why it actually chose what it chose.

## Limits

- One-shot patch drafting for the single branch point you describe — not an always-on SDK, and it does not install, run, or monitor anything itself.
- If your branch point doesn't already have the model state a rationale, the patch has to add a small prompt or schema change to elicit one — that's a real (if minimal) behavior-adjacent change to your agent, not pure logging, and it's always called out separately so you can review it before shipping.
- The captured rationale is whatever the model says its reason was, not a verified causal account — a model's stated rationale can be a post-hoc confabulation rather than the real cause of its choice. Treat it as diagnostic signal, not ground truth.
- Wiring notes assume your trace backend connector (Langfuse/Phoenix/Datadog API key, exporter endpoint) is already configured on your side — this draft can't fill that part in for you.
- Framework APIs change between versions; re-check the drafted patch against your installed version's conditional-edge/task-router signature before merging.
