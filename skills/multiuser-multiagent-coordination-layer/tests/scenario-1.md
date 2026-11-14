# Scenario 1 — Shared on-call/scheduling bot crew, no channel

## Input (realistic, as a user would paste it)

> We're rolling out an internal Slack-based "ops assistant" for our 40-person
> infra team. Right now it's three separate agents behind the same bot
> identity: a scheduling agent that reads/writes our shared on-call calendar,
> an incident-triage agent that assigns pages, and a runbook-lookup agent.
> Any of the ~15 engineers who are on an active rotation can DM the bot at
> any time and ask it to swap their on-call shift, request someone cover for
> them, or check who's currently on call. Each request just goes straight to
> whichever agent handles it — there's no central process reconciling two
> people's shift-swap requests that land around the same time, and the
> agents don't message each other about in-flight calendar changes. We
> haven't seen a conflict yet but we're about to expand this from one team to
> four teams sharing the same calendar system, and I want a read before we do.

## Expected output characteristics

- **Classification**: shared resource type = shared schedule/calendar. Formation = silent team (multiple agents touching the calendar independently, explicitly stated "no central process reconciling," "agents don't message each other").
- **Risk level**: HIGH, with justification citing the 38-47%-of-coordinator / complete-collapse research explicitly tied to calendar-type shared resources with a silent-team formation (not a vague "this seems risky").
- **Likely failure behavior**: names double-booking or silent overwrite of another engineer's shift-swap as the concrete failure, in plain language — not a generic "conflicts could occur."
- **Recommended fix**: leads with the lighter option (a shared-state registry tracking in-flight shift-swap requests, surfacing conflicts) before mentioning the heavier coordinator-formation rebuild; does not recommend only the heavy rebuild.
- **Guardrails**: explicitly calls out that any swap/cover action affecting another engineer's already-requested shift should require explicit confirmation before executing.
- Does not invent a precise percentage for anything beyond the cited 38-47% figure.

## Pass criteria
PASS if the output hits all five bullets above in the specified structure (Classification / Risk Level / Likely Failure Behavior / Recommended Minimum Fix / Guardrails). FAIL if it skips classifying the formation as "silent team" explicitly, scores risk as LOW/MEDIUM without citing the collapse research, recommends only the heavyweight rebuild, or fabricates a specific percentage/number not in the cited research.
