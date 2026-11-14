---
name: multiagent-declarative-orchestration-spec
description: Drafts a declarative contract spec (per-node input/output schemas plus per-edge failure-handling policy) for an existing multi-agent pipeline described in prose or code, and flags every handoff the description leaves ambiguous. Use when someone describes a LangGraph/CrewAI/AutoGen/hand-coded multi-agent pipeline and wants its implicit contracts made explicit and checkable.
---

# Contract Spec Drafter for Multi-Agent Pipelines

## When to use this
Someone describes (in prose, a diagram description, or pasted code) an existing multi-agent pipeline — two or more agents that hand work to each other — and wants to know, before wiring up a validator or just to understand the system, exactly what each agent is supposed to consume, what it's supposed to produce (including when something goes wrong), and where the handoffs between agents are unchecked assumptions rather than guarantees. Typical trigger phrases: "here's my agent pipeline, what could break between these two", "draft a contract for this LangGraph graph", "what's undefined in how agent A hands off to agent B".

Do not use this for a single agent with no handoff to another agent — the entire value of this skill is the inter-agent edge, not any one agent's internal logic.

## Inputs
**Data source**: Manual — the user pastes a description of their existing pipeline: which agents exist, what each one consumes and produces in the happy path, any failure/error/timeout handling they already have, and (optionally) a code excerpt from their orchestration framework showing node definitions, prompts, or retry logic. Nothing is fetched from a connector or API; this skill only works from what is pasted into the conversation.

## Procedure
1. **Extract nodes and edges.** From the pasted material, list every agent as a node with a short id (use the user's own naming), and list every edge — which node's output feeds which node's input, in what order. If the description implies branching (e.g., "if confidence is low, escalate to a human instead of the next agent"), capture each branch as its own edge.
2. **Extract each node's input schema.** What fields/types does this node need to do its job, per the description? If the description doesn't give field names, infer the minimal structure from what it says the node "reads" or "needs" — but mark inferred (not stated) fields as such rather than presenting them as confirmed.
3. **Extract each node's output schema, per path.** Separately capture: (a) the happy-path output schema, and (b) the output schema (or explicit "none" / "pipeline halts") under every failure mode the description or code actually mentions (timeout, validation failure, low-confidence, exception, empty result, etc.). Do not invent a failure path the source material never mentions — leave it absent and flag it in step 5.
4. **Extract each edge's failure-handling policy.** For every edge, classify the stated or code-visible handling as one of: `retry-with-backoff`, `escalate-to-human`, `abort-pipeline`, `fall-back-to-default`, or `unspecified`. Capture concrete detail where given (retry count, backoff shape, who gets escalated to, what the default fallback value is).
5. **Check compatibility across every edge, both paths.** For each edge, compare the upstream node's declared output schema (happy path, and separately each failure path that still passes data downstream) against the downstream node's declared input schema. Mark each edge/path pair `compatible`, `incompatible` (name the specific field/type mismatch), or `undetermined` (the description doesn't give enough detail to check either way — this is common and not a failure of the draft).
6. **Build the ambiguity list.** Anything from steps 2–5 that required guessing, that the source material left unstated, or that produced `undetermined` goes into a separate ambiguities list as a specific, answerable question (e.g., "Writer agent's retry logic is shown for validation failure — what happens if the LLM call itself times out?"), not a vague "needs more detail" note.
7. **Emit the spec** in the exact YAML shape under Output format, plus the ambiguity list, plus one line restating that this is a drafted starting point, not a validated or enforced contract until a human or a static validator checks it against the real pipeline.

## Output format
A single YAML document followed by a numbered ambiguities list:

```yaml
version: 1
pipeline: <short name the user gave, or "unnamed pipeline">
nodes:
  - id: <node-id>
    description: <one line, from source material>
    input:
      schema: { <field>: <type>, ... }   # mark any inferred (not stated) field with "# inferred"
    output:
      happy_path:
        schema: { <field>: <type>, ... }
      failure_paths:
        - trigger: <condition name, e.g. timeout, low-confidence, validation-failure>
          schema: { <field>: <type>, ... }   # or `null` if the pipeline halts / produces nothing
          policy: retry-with-backoff | escalate-to-human | abort-pipeline | fall-back-to-default | unspecified
          policy_detail: <concrete detail if given, else omit>
edges:
  - from: <node-id>
    to: <node-id>
    path: happy | failure:<trigger>
    compatible: true | false | undetermined
    note: <field/type mismatch if false; what's missing if undetermined>
ambiguities:
  - node_or_edge: <id or "A -> B">
    issue: <what the source material left unstated>
    question: <the specific question to ask the pipeline owner>
```

Close with: "This is a drafted starting point from the description given — treat every `undetermined` and every ambiguity entry as open until confirmed against the real pipeline (code, logs, or the owner)."

## Guardrails
- Never invent a failure-handling policy, a schema field, or a failure path that the pasted material didn't state or clearly imply — route anything uncertain to the ambiguities list instead of guessing silently.
- Never mark an edge `compatible` when the description doesn't give enough detail to actually check it — use `undetermined`, not an optimistic guess.
- Never claim this spec has been validated against the running pipeline — this skill only drafts from what was described; it does not execute code, call the orchestration framework, or inspect a live system.
- Don't produce a spec for a single-agent setup with no handoff — say so and stop rather than padding output with a trivial one-node "pipeline."
- Keep the output in the exact YAML shape given — don't freelance a different structure, since the point is that this draft is usable as a starting point for an actual static validator later.
