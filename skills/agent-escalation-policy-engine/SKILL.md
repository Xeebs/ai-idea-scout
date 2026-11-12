---
name: agent-escalation-policy-engine
description: Scores one proposed AI-agent action on ambiguity, reversibility, and blast radius, and recommends PROCEED, ASK, or REFUSE with justification. Use when reviewing an autonomous agent's planned action (from a log, a trace, or a "should it do this?" question) before it executes, or when designing an escalation policy by hand.
---

# Ask-First: Agent Escalation Policy Reviewer

## When to use this
Someone has a proposed or already-logged autonomous-agent action and wants a principled answer to "should this have run automatically, or should it have asked a human first?" — reviewing an agent trace, designing escalation rules before shipping an agent, or deciding in the moment whether to let an action through.

## Inputs
For each action to review, the user provides:
1. **The action** — what the agent is about to do (or did), concretely enough to assess impact (e.g. "refund $42.50 to customer X", not just "handle request").
2. **The original instruction/authorization** — what the human actually told the agent to do, in their own words, as given (not the agent's summary of it).
3. *(Optional but improves accuracy)* Any domain facts relevant to reversibility or blast radius: can this be undone, what/who does it touch, is there a dollar amount or scope.

If any of these is missing, ask for it rather than guessing — scoring on absent information is the exact "confidence scores lie" failure mode this skill exists to avoid.

## Procedure
Score the action on three axes. Each is LOW / MEDIUM / HIGH with a one-line justification tied to the actual inputs given — never a generic justification.

1. **Ambiguity** — does the original instruction clearly cover this specific action, or is the agent filling a gap with its own judgment?
   - LOW: the instruction explicitly names this action or an unambiguous class it belongs to.
   - MEDIUM: the instruction implies this kind of action but leaves a material detail (scope, threshold, target) to inference.
   - HIGH: the instruction is a general goal and this specific action is the agent's own invention of *how* to pursue it.

2. **Reversibility** — can this action be undone, cheaply, within a reasonable window, without collateral damage?
   - LOW: destructive, permanent, or recovery requires manual intervention beyond the agent's own capability (deletions, irreversible financial transfers, messages sent to third parties, production config changes without a tested rollback).
   - MEDIUM: technically reversible but with real cost or delay (can be undone by another action, but takes real effort or time).
   - HIGH: trivially and fully reversible (a draft, a staged change, a read, a reversible toggle).
   - **If reversibility is genuinely unknown from the inputs given, treat it as LOW** — never default to HIGH on an assumption.

3. **Blast radius** — who or what is affected if this goes wrong?
   - LOW: the agent's own scratch state or a single low-stakes record the requester explicitly owns.
   - MEDIUM: the requester's own systems/data/money at non-trivial scale, or one other party.
   - HIGH: third parties beyond the requester, shared/production infrastructure, money above a small threshold, or anything publicly visible.

Apply the decision rule in order (first match wins):
- Blast Radius = HIGH **and** Reversibility = LOW → **REFUSE**, unless the original instruction gives explicit prior authorization for this *exact* action class (not just the general goal).
- Ambiguity = HIGH **and not** (Reversibility = HIGH **and** Blast Radius = LOW) → **ASK**.
- Ambiguity = LOW **and** Blast Radius = LOW **and** Reversibility ≠ LOW → **PROCEED**.
- Anything else (mixed signals, including a LOW on any axis that didn't already trigger PROCEED) → **ASK** — conflicting or worst-case axes default to caution, not to a tie-break guess.

## Output format
One block per action:

```
Action: <restated action>
Ambiguity: LOW|MEDIUM|HIGH — <justification tied to the actual instruction given>
Reversibility: LOW|MEDIUM|HIGH — <justification tied to the actual facts given>
Blast Radius: LOW|MEDIUM|HIGH — <justification tied to who/what is affected>
Decision: PROCEED | ASK | REFUSE
Why: <one sentence citing which rule fired>
```

If reviewing multiple actions, repeat the block per action, then a one-line summary: `N actions — P proceed, A ask, R refuse`.

## Guardrails
- Never recommend PROCEED for a HIGH blast-radius action without an explicit prior-authorization match — "the agent seemed confident" is not authorization.
- Never invent reversibility or blast-radius facts not given or clearly inferable; say what's missing and score the safer value instead.
- Give a decisive recommendation every time — "it depends" with no decision is the hand-rolled-heuristic failure mode this skill replaces, not an acceptable output.
- Do not soften a REFUSE into an ASK to be agreeable; if the rule fires REFUSE, say REFUSE and name the missing authorization that would change it.
