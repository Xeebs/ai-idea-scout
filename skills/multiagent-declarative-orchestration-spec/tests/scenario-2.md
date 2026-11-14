# Scenario 2 — Content pipeline with a real field-mismatch bug (code excerpt)

## Input given to the skill

> This is a CrewAI content pipeline: researcher -> writer -> editor. Here's
> the relevant code:
>
> ```python
> researcher = Agent(role="researcher", ...)
> # researcher_task.output: produces a dict like
> #   {"summary": str, "citations": dict}   # citations is {url: snippet}, can be {}
>
> writer = Agent(role="writer", ...)
> writer_task = Task(
>     agent=writer,
>     expected_output="A draft article as {draft: str, citations: dict}",
> )
>
> @retry(max_attempts=2, on=ValidationError)
> def run_writer(ctx):
>     result = writer_task.execute(ctx)
>     if not result.get("draft"):
>         raise ValidationError("writer produced no draft")
>     return result
> # on exhausting retries, run_writer re-raises and the whole crew run aborts
>
> editor = Agent(role="editor", ...)
> editor_task = Task(
>     agent=editor,
>     # editor_task reads ctx["draft"] and ctx["sources"], a list[str] of URLs,
>     # and produces {"final": str, "edit_notes": list[str]}
> )
> ```
>
> We haven't written any failure handling for the editor step yet — if it
> throws, I honestly don't know what happens, probably an unhandled exception.

## Pass criteria

The drafted spec/ambiguity output should:

1. Identify 3 nodes: researcher, writer, editor, with the edges researcher -> writer -> editor.
2. Capture the writer's actual retry policy from the code: `retry-with-backoff`-shaped (max 2 attempts) on validation failure, re-raising to `abort-pipeline` once exhausted — reflecting what the decorator and re-raise actually do, not a generic guess.
3. **Catch the real mismatch**: the writer's output/`writer_task.execute` guarantees `citations: dict` (`{url: snippet}`), but the editor's declared input expects `sources: list[str]`. This must be surfaced either as an `incompatible` edge (naming the field-name AND type mismatch — `citations`/dict vs `sources`/list[str]) or, at minimum, prominently in the ambiguities list as a specific flagged question — burying or missing this mismatch entirely is a fail, since catching exactly this class of bug is the skill's core value claim.
4. Flag the editor's failure handling as `unspecified`/ambiguous, per the user's own admission ("probably an unhandled exception") — not invented as abort-pipeline with false confidence, since the user explicitly said they don't know.
5. Not invent a schema for what editor produces on failure (no `failure_paths` entry fabricated for editor beyond noting it's unknown/ambiguous).
6. Output follows the YAML shape with nodes/edges/ambiguities keys.

## Fail conditions

- Missing the citations-vs-sources field/type mismatch entirely, or waving it away as compatible.
- Describing the writer's retry behavior generically ("has some retry logic") instead of reflecting the actual max-attempts-2/abort-on-exhaustion behavior shown in the code.
- Fabricating confident failure-handling behavior for the editor step when the user explicitly said they don't know what happens.
