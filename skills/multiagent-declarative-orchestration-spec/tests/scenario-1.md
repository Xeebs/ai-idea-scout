# Scenario 1 — Support-ticket triage pipeline (prose description, no code)

## Input given to the skill

> Here's my pipeline. It's built in LangGraph for our support desk.
>
> 1. **Triage agent** — reads the raw incoming ticket text and classifies it,
>    producing `{category: "bug"|"feature"|"question", confidence: float}`.
> 2. **Router agent** — takes the triage agent's output. If `confidence >= 0.6`,
>    it picks a specialist team and produces `{assigned_team: string}`, which
>    goes to the specialist agent. If `confidence < 0.6`, it skips the
>    specialist agent entirely and escalates the ticket to a human reviewer
>    queue instead — I haven't built out what happens after that beyond
>    "shows up in a queue."
> 3. **Specialist agent** — takes `{assigned_team}` plus the original ticket
>    text, and produces `{draft_response: string}`.
>
> We don't have any timeout or retry handling built yet — if any agent's LLM
> call fails outright, the whole LangGraph run just errors out right now.

## Pass criteria

The drafted spec/ambiguity output should:

1. Identify exactly 3 nodes (triage, router, specialist) with ids derived from the user's own names.
2. Capture the router's branch as two distinct edges: `triage -> router` (happy) and two downstream paths from router — one to specialist (`confidence >= 0.6`) and one representing the human-escalation branch (`confidence < 0.6`) — rather than collapsing the branch into a single edge.
3. Correctly extract `router`'s stated condition (confidence threshold 0.6) as real content, not as an ambiguity — this was explicitly given.
4. NOT invent a retry-with-backoff or any other failure policy for LLM-call failures, since the user explicitly said there's no handling yet (current behavior is "whole run errors out" — this should map to `abort-pipeline` with that noted as the stated current behavior, not a flagged gap for that specific point).
5. Flag as an ambiguity that the human-escalation branch's downstream behavior is undefined past "shows up in a queue" (no schema or policy for what happens to that ticket afterward) — this is a real gap the user admitted, so it must appear in the ambiguities list, not be silently glossed over.
6. Mark the `router -> specialist` edge's output schema fields reasonably (e.g. `{assigned_team: string}` plus the carried-forward ticket text) and mark the specialist's input as needing both fields — if the user's description doesn't explicitly confirm the original ticket text is passed through to the specialist, that should be flagged as an ambiguity (inferred, not stated) rather than assumed.
7. Output must follow the YAML shape from SKILL.md (nodes/edges/ambiguities keys present) — not freeform prose only.

## Fail conditions

- Treating "no timeout/retry handling yet" as license to invent a plausible-sounding retry policy anyway.
- Collapsing the confidence branch into a single straight-line pipeline, losing the human-escalation path entirely.
- Marking the human-escalation branch's downstream handling as `compatible` or otherwise resolved instead of flagging it.
