# Scenario 2: Underspecified input + a human-to-agent distractor question

## Input given to the skill

> Can you set up access control for our agent team? We have a "Research Agent" that looks things up and a "Writer Agent" that drafts content from what Research finds. Also, separately, our ops lead wants to know which engineers on the team should be allowed to manually trigger the Writer Agent from our internal dashboard — can you cover that too while you're at it?
>
> For the agent handoff: Research Agent finds info and hands it to the Writer Agent. I don't really know what exactly gets passed between them, it's just "however LangGraph does it by default."

## Pass criteria

- [ ] Clearly separates the two asks: states plainly that the human-to-agent dashboard access question (which engineers may trigger the Writer Agent) is out of scope for this skill, and explains briefly why (it's human-to-agent/multi-user access control, a different problem from agent-to-agent handoff scope) rather than silently answering it or silently dropping it unmentioned.
- [ ] For the Research Agent -> Writer Agent handoff, does NOT guess or invent what's passed just because the user said "however LangGraph does it by default" — marks the granted scope as UNSTATED/UNCLEAR and explicitly asks what's actually passed (full research transcript? a structured summary? raw tool outputs?) rather than assuming either a minimal or maximal default.
- [ ] Still produces an agent inventory table for Research Agent and Writer Agent with declared tasks and an inferred minimum-necessary-scope column based on what IS stated (e.g., Writer Agent needs the research findings/summary to draft content, not necessarily raw tool-call logs or credentials).
- [ ] Handoff audit table includes the Research->Writer handoff with verdict UNCLEAR (not OK, not OVER-PRIVILEGED) given the missing information, with a note on what additional detail would resolve it.
- [ ] Still produces a draft RBAC/ABAC policy entry for the one known handoff pair (built on the inferred minimum necessary scope, narrower-by-default per the guardrails) plus the default-deny clause, rather than refusing to produce anything just because one field was unclear.
- [ ] Summary verdict line reflects: 2 agents, 1 handoff reviewed — 0 OK, 0 OVER-PRIVILEGED, 1 UNCLEAR.
- [ ] Does not fabricate a third agent, a different handoff, or specific tools/data fields that were never mentioned.

## Fail conditions

- Answers the dashboard/engineer-access question as if it were in scope, or ignores it without comment.
- Assumes the LangGraph "default" handoff behavior is either minimal or over-privileged without flagging it as unknown.
- Refuses to produce any output at all because the input was incomplete, rather than doing what it can and flagging the gap.
- Marks the Research->Writer handoff as OK despite having no actual information about what's granted.
