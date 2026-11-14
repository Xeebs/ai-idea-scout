# Contract Spec Drafter for Multi-Agent Pipelines

A self-contained prompt template for drafting a declarative contract spec — per-agent input/output schemas plus per-handoff failure-handling policy — from a description of an existing multi-agent pipeline (LangGraph, CrewAI, AutoGen, or anything hand-coded). It also produces an explicit list of everything the description left ambiguous, instead of silently guessing. Paste the block below into any AI chat tool, then paste your pipeline description after it.

**Data source**: Manual. You paste a description of your pipeline — which agents exist, what each consumes and produces, and any failure/retry/escalation handling you already have — plus, optionally, a code excerpt (LangGraph node definitions, CrewAI task/agent definitions, prompt templates, retry logic). Nothing is fetched automatically from any API or connector; the draft is only as good as what you paste in.

**When to use it**: You have two or more agents that hand work to each other, and you want to know exactly what each one is supposed to produce — including when something fails — and where the handoffs between them are unchecked assumptions rather than actual guarantees. Not useful for a single agent with no handoff to describe.

---

## Prompt template

```
You are drafting a declarative contract spec for an existing multi-agent
pipeline I'm about to describe. Follow this procedure exactly:

1. List every agent in my pipeline as a node, and every handoff between
   them as an edge (including any conditional branches, e.g. "if
   confidence is low, go to a human instead of the next agent").

2. For each node, extract its input schema (what fields/types it needs)
   from what I said it reads or needs. If I didn't give field names,
   infer the minimal structure but mark inferred fields "# inferred" —
   don't present a guess as something I stated.

3. For each node, extract its output schema separately for: (a) the
   happy path, and (b) each failure mode I actually mentioned or that's
   visible in any code I pasted (timeout, validation failure, low
   confidence, exception, empty result, etc.). Do not invent a failure
   path I never mentioned — leave it out and flag it in step 5 instead.

4. For each edge, classify its failure-handling policy as one of:
   retry-with-backoff, escalate-to-human, abort-pipeline,
   fall-back-to-default, or unspecified. Capture concrete detail where
   I gave it (retry count, backoff shape, who gets escalated to, what
   the fallback value is).

5. For each edge, compare the upstream node's output schema (happy path,
   and each failure path that still passes data downstream) against the
   downstream node's input schema. Mark it compatible, incompatible
   (name the exact field/type mismatch), or undetermined (not enough
   detail in what I gave you to check either way).

6. Build an ambiguities list: every place steps 2-5 required guessing or
   produced "undetermined," written as a specific, answerable question
   — not a vague "needs more detail."

7. Output the result as the YAML spec below, followed by the numbered
   ambiguities list. Do not claim anything is validated against my real,
   running pipeline — you only have what I described.

Output format (follow this exact shape):

version: 1
pipeline: <short name I gave, or "unnamed pipeline">
nodes:
  - id: <node-id>
    description: <one line>
    input:
      schema: { <field>: <type>, ... }
    output:
      happy_path:
        schema: { <field>: <type>, ... }
      failure_paths:
        - trigger: <condition name>
          schema: { <field>: <type>, ... }   # or null if nothing is produced
          policy: retry-with-backoff | escalate-to-human | abort-pipeline | fall-back-to-default | unspecified
          policy_detail: <concrete detail if given>
edges:
  - from: <node-id>
    to: <node-id>
    path: happy | failure:<trigger>
    compatible: true | false | undetermined
    note: <mismatch or missing detail>
ambiguities:
  - node_or_edge: <id or "A -> B">
    issue: <what I left unstated>
    question: <specific question to ask me>

Here is my pipeline:

[PASTE YOUR PIPELINE DESCRIPTION AND/OR CODE EXCERPT HERE]
```

## What you get back

A YAML contract spec covering every agent node (input schema, happy-path output schema, failure-path output schemas) and every handoff between them (with a failure-handling policy and a compatibility verdict of `true`/`false`/`undetermined`), followed by a numbered list of specific, answerable questions about anything your description left unclear. This is a drafted starting point for a real contract — not a validated one. Treat every `undetermined` edge and every ambiguity entry as open until you confirm it against your actual code, logs, or the pipeline's owner.

## Guardrails

- The draft will never invent a failure policy, schema field, or failure path you didn't mention — anything uncertain goes into the ambiguities list, never silently guessed.
- An edge is only ever marked `compatible` when there's enough stated detail to actually check it; otherwise it's `undetermined`.
- This is a description-only draft. It does not run your code, call your orchestration framework, or inspect a live system — it only reflects what you pasted.
- If you only describe one agent with no handoff to another, this skill isn't the right tool — there's no edge to draft a contract for.
