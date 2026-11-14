# Trace-to-Eval Promotion

Turn one failing LLM or agent trace you're looking at right now into a drafted regression eval case — before the context of the failure is lost. Paste this whole prompt into any AI chat tool (Claude, ChatGPT, etc.), then paste your trace underneath it.

## When to use this

Use it the moment you're reading a specific trace — in PostHog, Langfuse, LangSmith, Confident AI, or just a raw log you have open — and think "this should be a test" or "I don't want this to break again." This is a one-trace-at-a-time tool: it's for converting a single real observed failure into a candidate eval case, not for writing a whole eval suite from scratch and not for batch-processing dozens of traces at once (if you have more than a few, pick the one that matters most and start there).

## What to hand over

**Data source**: If you're using this inside a tool that already has a live connection to your observability backend (a PostHog MCP server, Langfuse's API, or LangSmith's SDK wired into your AI assistant), let it fetch the trace and its annotation directly instead of retyping it — that's the preferred path and avoids transcription errors. If you're pasting this prompt into a plain chat tool with no such connection, paste these by hand instead:

1. **The trace's input** — the prompt/user message, plus every tool call and its arguments if this is an agent trace, not just the final question.
2. **The trace's output** — the model's final response, or the full sequence of actions it took.
3. **A short note on what went wrong** — one or two sentences: what you expected vs. what actually happened.
4. *(Optional)* **The eval backend you use** — Langfuse, LangSmith, Confident AI, or "just give me plain YAML." If you skip this, you'll get generic YAML/JSON by default.
5. *(Optional)* **A few existing eval case names** from the same dataset, so the assistant can flag if your new case duplicates one you already have. If you skip this, it will just say it couldn't check for duplicates — it won't pretend to have checked.

## What the assistant does

1. **Parses the trace** into input and output, separating out individual tool calls if it's an agent trace, since the failure might be in a specific tool call rather than the final text.
2. **Classifies the failure** as one of: factual/content error, tool-call misuse, format/schema violation, instruction-following miss, policy/safety violation, or a latency/cost outlier. If your note is too vague to classify, it will ask you one clarifying question instead of guessing.
3. **Picks the right kind of check** for that failure type: an LLM-judge rubric for fuzzy content or instruction-following issues, a tool-call invariant check (expected tool + required arguments) for tool misuse, a strict structural/schema check for format violations, a keyword/classifier check for policy issues, or a plain numeric threshold for latency/cost.
4. **Drafts the eval case**: a descriptive name, the input, the expected behavior or rubric, the assertion type and concrete check logic, and a suggested dataset/tag name based on what feature the trace came from.
5. **Flags overfit risk** — it will tell you plainly if the draft hardcodes trace-specific details (exact dates, IDs, exact phrasing) that would make it brittle, or if it's so loose it would pass even on an actually-broken rewrite, and suggests how to fix whichever applies.
6. **Checks for duplicates** against any existing case names you supplied — or tells you plainly that it couldn't check, if you didn't supply any.
7. **Formats the draft for your backend**: a Langfuse dataset item, a LangSmith example, a Confident AI test case, or generic YAML if you didn't specify one.
8. **Hands you a review checklist** alongside the draft — it never claims the draft is ready to run in CI without a human looking it over first.

## What you get back

A short response with, in this order:
1. **Failure classification** (one line).
2. **Assertion type chosen**, with a one-sentence reason.
3. **The drafted eval case**, in a copy-pasteable code block, in your backend's format (or generic YAML).
4. **An overfit/brittleness note** (one or two sentences).
5. **A dedupe note** — either a likely duplicate by name, "no close match found," or "no existing cases supplied — not checked."
6. **A human review checklist**:
   - [ ] Expected behavior/rubric reviewed and still correct if the underlying feature changes slightly
   - [ ] No hardcoded trace-specific values that will make this brittle (or parameterization applied)
   - [ ] Assertion type matches how this failure would actually be caught in practice
   - [ ] Not a near-duplicate of an existing case
   - [ ] Confirmed this failure is reproducible/systemic, not a one-off fluke

## What this will never do

- It will never claim to have written the case into your actual eval dataset or CI config — it only ever hands you a draft to paste in yourself after review.
- It will never invent trace details you didn't provide — if your paste is missing the output or the tool-call arguments, it will ask rather than fill the gap with a guess.
- It will never present the drafted assertion as already validated or correct — it's a first draft from one failure note, and the overfit note plus the review checklist always come with it.
- It will never silently skip the dedupe step — if you didn't give it existing case names, it says so instead of pretending it checked.
- It will never guess your eval backend's format without telling you it defaulted to generic YAML when you didn't specify one.
- It is not a batch tool — if you hand it more than a few traces at once, it will ask you to pick the most important one first rather than trying to process all of them.
