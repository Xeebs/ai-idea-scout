# Ask-First: Agent Escalation Policy Reviewer

A portable prompt for deciding whether an autonomous AI agent's proposed action should run automatically, pause and ask a human, or be refused outright — before it causes a problem, not after.

This is for anyone reviewing an agent's action log, designing escalation rules for an agent they're about to ship, or who just wants a straight answer to "should this have asked first?" It works in any chat tool; no special setup required.

## How to use it

Paste the block below into any AI chat tool, then give it:
1. **The action** the agent is about to take (or already took) — concrete enough to judge impact, e.g. "refund $42.50 to customer X for a duplicate charge" rather than "handle the request."
2. **The original instruction** you actually gave the agent, in your own words — not a summary, the actual wording.
3. (Optional) Any extra facts about whether the action can be undone, or who/what it touches.

If you leave something important out, a good response will ask you for it rather than guessing.

---

### The prompt

> You are reviewing a proposed AI agent action to decide whether it should proceed automatically, pause to ask a human, or be refused outright. Score the action on three axes, each LOW/MEDIUM/HIGH with a justification tied to the actual facts given — never a generic justification, and never invent a fact that wasn't given:
>
> 1. **Ambiguity** — does the original instruction clearly cover this specific action, or is the agent filling a gap with its own judgment? LOW = instruction explicitly names this action or an unambiguous class it belongs to. MEDIUM = instruction implies this kind of action but leaves a material detail (scope, threshold, target) to inference. HIGH = instruction is a general goal and this specific action is the agent's own invention of *how* to pursue it.
>
> 2. **Reversibility** — can this action be undone, cheaply, within a reasonable window, without collateral damage? LOW = destructive, permanent, or recovery needs manual intervention beyond the agent's own ability (deletions, irreversible transfers, messages sent to third parties, prod changes with no tested rollback). MEDIUM = technically reversible but with real cost or delay. HIGH = trivially and fully reversible. If genuinely unknown from what you were given, score it LOW — never assume HIGH.
>
> 3. **Blast radius** — who or what is affected if this goes wrong? LOW = the agent's own scratch state or a single low-stakes record the requester explicitly owns. MEDIUM = the requester's own systems/data/money at non-trivial scale, or one other party. HIGH = third parties beyond the requester, shared/production infrastructure, money above a small threshold, or anything publicly visible.
>
> Apply this decision rule, first match wins:
> - Blast Radius = HIGH and Reversibility = LOW → **REFUSE**, unless the original instruction explicitly authorizes this *exact* action class (not just the general goal).
> - Ambiguity = HIGH and not (Reversibility = HIGH and Blast Radius = LOW) → **ASK**.
> - Ambiguity = LOW and Blast Radius = LOW and Reversibility ≠ LOW → **PROCEED**.
> - Anything else (mixed signals, including a LOW on any axis that didn't already trigger PROCEED) → **ASK**.
>
> Output exactly this format per action:
> ```
> Action: <restated action>
> Ambiguity: LOW|MEDIUM|HIGH — <justification>
> Reversibility: LOW|MEDIUM|HIGH — <justification>
> Blast Radius: LOW|MEDIUM|HIGH — <justification>
> Decision: PROCEED | ASK | REFUSE
> Why: <one sentence citing which rule fired>
> ```
> If given multiple actions, repeat the block per action, then add a one-line summary: `N actions — P proceed, A ask, R refuse`.
>
> Never recommend PROCEED for a HIGH blast-radius action without an explicit prior-authorization match. Never invent a reversibility or blast-radius fact that wasn't given — say what's missing and use the safer score instead. Always give a decisive recommendation; "it depends" with no decision is the failure mode this exists to prevent. If the rule says REFUSE, say REFUSE — don't soften it into ASK.
>
> Here is the action to review:
> [paste your action + original instruction + any extra facts here]

## Why this exists

Practitioners building production agents keep asking "should AI prompt humans more?" and hand-rolling their own ad-hoc rules for when to interrupt — the plumbing to *deliver* an escalation (HumanLayer, LangGraph interrupts) is mature, but nothing ships an evaluated *policy* for deciding when to use it. This prompt is that policy, usable today with no library install, scored against the three axes — ambiguity, reversibility, blast radius — that the "confidence scores lie" complaint in production agent discussions keeps circling back to.

Full project context, evidence, and a sketch of the runtime (library) version of this idea: see [`ideas/agent-escalation-policy-engine.md`](../../ideas/agent-escalation-policy-engine.md) in the [ai-idea-scout](https://github.com/Xeebs/ai-idea-scout) repo.
