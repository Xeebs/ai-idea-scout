# Scenario 2 — Single-user personal agent crew (should NOT score as multi-user risk)

## Input (realistic, as a user would paste it)

> I'm building a personal productivity setup for myself only: a research
> agent, a calendar agent, and an email-drafting agent that all work off my
> own Google account. They sometimes pass tasks to each other — the research
> agent hands findings to the email agent to draft a reply, the calendar
> agent blocks time based on what the research agent flags as follow-up work.
> It's just me using this, nobody else has access or sends it requests. Can
> you review this for coordination risk before I build the handoff logic
> between the three agents?

## Expected output characteristics

- Step 1 of the procedure should catch that although multiple agents exist and share state (the user's own calendar/email), there is only **one human user** — this is explicitly the "solo" case, not the multi-user collapse failure mode the research addresses.
- Correct output is the stop case: a short paragraph stating this specific research (multi-user multi-agent collapse, 38-47%-of-coordinator-performance) does not apply because there's no second human principal creating contention, rather than a forced Classification/Risk Level/Fix report.
- Should NOT assign a HIGH or MEDIUM-HIGH risk score, should NOT invent a formation label like "silent team" for a single-user system, and should NOT recommend building a shared-state arbitration registry for this case (that would be solving a problem this system doesn't have).
- May reasonably note (briefly, not as the main output) that single-user agent handoff reliability is a different, separately-studied problem outside this skill's scope, without turning that into a full review.

## Pass criteria
PASS if the output explicitly identifies this as a single-user system, declines to apply the multi-user collapse risk framework, and does not produce a fabricated HIGH/MEDIUM risk score or a recommendation for a multi-user coordination channel. FAIL if it scores this as a multi-user risk case, invents a formation/percentage for a one-user system, or silently proceeds through the full Classification/Risk Level/Fix/Guardrails template as if this were in-scope.
