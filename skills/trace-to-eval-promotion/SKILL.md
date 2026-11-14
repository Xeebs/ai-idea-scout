---
name: trace-to-eval-promotion
description: Turns one flagged/failing LLM or agent trace plus a short failure note into a backend-formatted draft regression eval case (Langfuse, LangSmith, Confident AI, or generic YAML). Use when an engineer says "this should be a test" about a trace they just read, before the context of the failure is lost.
---

# Trace-to-Eval Promotion

## When to use this
The trigger moment: an engineer (or an agent reading traces via MCP) is looking at one specific failing or surprising LLM/agent trace — in PostHog, Langfuse, LangSmith, Confident AI, or just pasted raw log text — and says something like "this should be a test," "I don't want this to regress," or "turn this into an eval case." Use this skill at that exact moment, not as a batch job over many traces and not as a general "write me some eval cases" request with no concrete trace in hand.

Do not use this for: writing an eval suite from scratch with no real trace, mining hundreds of traces for patterns (that's a batch-harness job, not this skill), or auto-filing a case into CI without human review.

## Inputs
**Data source**: Connected (preferred) — if the environment already has a PostHog MCP, Langfuse REST API, or LangSmith SDK connector wired in, use it to fetch the flagged trace's full input/output and any existing annotation directly, rather than asking the user to retype it. Manual fallback — when no connector is available (e.g., pasted into a plain chat tool, or the trace lives in a tool without a wired connector), the user pastes:
1. The trace's input (the prompt/user message, plus any tool calls and their arguments if it's an agent trace).
2. The trace's output (the model's final response or action sequence).
3. A one-to-two sentence note on what went wrong — expected vs. actual.
4. (Optional) The target eval backend — Langfuse, LangSmith, Confident AI, or "just give me YAML." If omitted, default to generic YAML/JSON and say so.
5. (Optional) A few existing eval case names/titles from the same dataset, for the dedupe check in step 5 below. If omitted, skip dedupe and say so explicitly rather than guessing.

## Procedure
1. **Parse the trace.** Separate input (what went in) from output (what came out). For agent traces, list each tool call with its arguments and the final response separately — the failure may be in a tool call, not just the final text.
2. **Classify the failure** using the note provided, into one of: factual/content error, tool-call misuse (wrong tool, wrong args, missed required call), format/schema violation, instruction-following miss, policy/safety violation, or latency/cost outlier. State the classification explicitly before drafting anything — if the note is too vague to classify, ask one clarifying question rather than guessing.
3. **Pick an assertion type** matched to the classification:
   - Factual/content error → LLM-judge rubric (the "right" answer isn't exact-match-able).
   - Tool-call misuse → tool-call invariant assertion (expected tool name + required argument keys/values, not full output match).
   - Format/schema violation → exact structural/schema validation (deterministic, no judge needed).
   - Instruction-following miss → LLM-judge rubric keyed to the specific instruction that was missed.
   - Policy/safety violation → deterministic keyword/classifier check plus a judge rubric as backup.
   - Latency/cost outlier → a numeric threshold assertion, not a content assertion at all.
4. **Draft the case**: a short id/name (derived from the failure, not a generic counter), the input, the expected behavior (either the exact expected output for structural checks, or the rubric text for judge-based checks), the assertion type and concrete check logic, and a suggested dataset/tag name based on the feature area the trace came from.
5. **Flag overfit risk.** Check whether the draft hardcodes trace-specific values (exact dates, IDs, names, phrasing) that would make the case too brittle, or so loosely worded it would pass on an actually-broken rewrite. Say explicitly which it is and suggest a parameterization if hardcoded values are the problem.
6. **Dedupe check**, only if existing case names/titles were supplied: compare the draft against them for near-duplicates (same input shape, same failure mode) and flag a likely duplicate by name before presenting the draft as new. If no existing cases were supplied, state plainly that no dedupe check was possible — never silently skip this and never claim a dedupe check happened when it didn't.
7. **Format for the target backend**: Langfuse dataset item JSON (`input`, `expectedOutput`, `metadata.tags`), LangSmith example dict (`inputs`, `outputs`, `metadata`), Confident AI test case schema (`input`, `actualOutput`, `expectedOutput`, `context`), or generic YAML (`input`, `expected`, `assertion_type`, `check`, `tags`) if no backend was specified.
8. **Present with a review checklist** — never hand back a case framed as ready-to-run without the checklist from step 9.

## Output format
1. **Failure classification** — one line.
2. **Assertion type chosen** — one line, with a one-sentence reason.
3. **Drafted eval case** — in the requested backend's native format (or generic YAML), as a fenced code block ready to copy-paste.
4. **Overfit/brittleness note** — one or two sentences (step 5 result).
5. **Dedupe note** — one line: either "possible duplicate of: <name>," "no close match found," or "no existing cases supplied — dedupe not checked."
6. **Human review checklist** (always included, exactly these items, checked or unchecked as applicable):
   - [ ] Expected behavior/rubric reviewed and still correct if the underlying feature changes slightly
   - [ ] No hardcoded trace-specific values that will make this brittle (or: parameterization applied)
   - [ ] Assertion type matches how this failure would actually be caught in practice
   - [ ] Not a near-duplicate of an existing case
   - [ ] Confirmed this failure is reproducible/systemic, not a one-off environment fluke (ask the user if unknown)

## Guardrails
- Never write, submit, or commit the drafted case into the team's actual eval dataset or CI config — this skill only produces a draft for a human to paste in after review, even if a connector could technically write it.
- Never invent trace content (inputs, outputs, tool call arguments) that wasn't provided or fetched via a real connector — if the trace is incomplete, say so and ask for the missing piece rather than filling gaps.
- Never present a drafted assertion as validated or "correct" — it is a draft derived from one failure note, not a verified check; the overfit note and review checklist are mandatory, not optional polish.
- Never skip the dedupe note — if no existing cases were supplied, say that plainly instead of omitting the line.
- Never assume a backend format without asking when none was specified — default to generic YAML and say that's what you did.
- Never treat this as a batch-processing tool — if the user hands over more than ~3 traces at once, say this skill is scoped to one trace at a time and ask them to pick the most important one first.
