# A2A Policy Draft

A prompt template for drafting a least-privilege RBAC/ABAC policy for the agent-to-agent handoffs in a multi-agent system (triage agent -> specialist agent -> action agent, or any similar delegation chain), and for flagging today's handoffs that hand a downstream agent more access than its own declared task needs.

This is a **design/review task, not a runtime system**. It produces a document you (or your team) review and then implement in whatever policy engine you use — it does not enforce anything by itself, and it is not the same thing as access control for which *humans* may invoke which agents (that's a different, already-served problem).

## When to use this

Use this when you have a multi-agent system with one or more hand-off points between agents and you want to know: what should each agent be allowed to ask the next agent to do, and is any current handoff already over-privileged. Typical triggers:

- You're about to ship a delegation-heavy agent system and want a least-privilege policy drafted before launch.
- You inherited or built a multi-agent chain and suspect some agents are passing full context/tool access downstream instead of a narrow, task-scoped subset.
- A security review asked "what's your agent-to-agent authorization model" and the honest answer today is "there isn't one."

Not the right tool if your question is about which human users may trigger which agents — that's multi-user access control, not agent-to-agent delegation, and this template doesn't cover it.

## What to hand over (data source: Manual)

Paste, for every agent in your delegation chain:

1. **Role name** and **declared task** — what that agent is actually supposed to do.
2. **Every handoff it makes today** — which other agent it calls, what triggers the handoff, and exactly what gets passed at that moment (its full conversation history? a summary? its own tool allowlist? a specific credential or API key? just a task description?).

The more concrete you can be about what's passed at each handoff, the better the audit — "the triage agent calls the specialist agent with its entire message history and the same tool permissions it has itself" is far more useful than "they talk to each other." If you have the actual code or config that wires the handoff (a subagent-spawn call, a LangGraph edge definition, a config file listing allowed tools per agent), paste that directly — it's the strongest possible input.

Everything here is something you type or paste yourself. This template doesn't read your codebase, call any API, or connect to anything — if you want it to look at an actual repo, open it in a coding assistant that can read files and ask it to follow this same procedure against those files directly.

## The procedure to follow

Once you have the agent list and handoff descriptions, work through these steps in order:

1. **List every agent** with its declared task and — based only on that task — what tools/data it needs to do its *own* job (not what it currently has, what it actually needs).
2. **List every handoff**: from-agent, to-agent, what triggers it, and what's granted today. If you don't know what's granted for a given handoff, write "unstated" — don't guess.
3. **For each handoff, work out the minimum necessary scope** the downstream agent needs, based strictly on its declared task from step 1. Be concrete: name specific tools, specific data categories, specific allowed actions — not "relevant context."
4. **Compare what's granted today against that minimum** for every handoff and label it:
   - **OK** — granted scope is at or below the minimum necessary.
   - **OVER-PRIVILEGED** — granted scope is broader than necessary (say exactly what's excessive — e.g., "specialist agent receives the triage agent's full tool allowlist, but its declared task only requires two of those tools").
   - **UNCLEAR** — you can't tell from the input what's granted, or can't pin down the minimum necessary scope. Don't resolve this by guessing in either direction — name what's missing.
5. **Draft an RBAC/ABAC policy**: one entry per existing handoff pair, stating which role may hand off to which role, with what allowed actions/tools/data, and any conditions (e.g., "only when the task is billing-related"). Base every entry on the *minimum necessary* scope from step 3, not on what's currently granted — the draft policy is the fix, not a rubber stamp of the status quo.
6. **Add an explicit default-deny line**: any handoff pair not listed in the policy is denied by default. State this as its own line, don't leave it implied.
7. **Recommend an audit log schema** (fields only, no implementation): timestamp, delegator role, delegate role, declared purpose of the handoff, scope requested, scope granted, decision, rationale.
8. **Write a one-line summary**: how many agents, how many handoffs, and the count of OK / OVER-PRIVILEGED / UNCLEAR. If anything is over-privileged, say so plainly in that summary line — don't bury it.

## Output format to produce

Structure the result as:

1. A one-line verdict: `N agents, H handoffs reviewed — X OK, Y OVER-PRIVILEGED, Z UNCLEAR`.
2. **Agent inventory table**: Role | Declared Task | Scope Needed for Own Task.
3. **Handoff audit table**: From -> To | Trigger | Scope Granted Today | Minimum Necessary Scope | Verdict | Why. Put OVER-PRIVILEGED rows first, then UNCLEAR, then OK.
4. **Draft RBAC/ABAC policy**, one block per handoff pair plus the default-deny clause as the final entry.
5. **Recommended audit log schema** — the field list from step 7.
6. A closing note stating plainly: this is a one-time draft based only on what was described, it enforces nothing on its own, it can't see handoffs that weren't described, and it should be re-run after any change to the agent roster or the handoff code. If you want this policy actually enforced at runtime (scoped identities minted per hop, out-of-policy handoffs actually blocked), that requires a separate runtime enforcement system wired into your agent framework's own handoff hook — this template only produces the design document for that system or for manual policy-engine configuration (OPA, Cedar, or similar).

## Rules to follow while doing this

- Never invent an agent, a handoff, or a declared task that wasn't given to you. If the chain described is incomplete, say what's missing and ask for it.
- Never mark a handoff "OK" just because nothing excessive was mentioned — if the granted scope wasn't stated, it's unclear, not fine.
- Never widen a draft policy entry beyond the minimum necessary scope "to be safe" — when genuinely unsure, draft narrower and flag it for the human to deliberately widen if needed, don't widen it yourself.
- Never skip the default-deny clause — without it, a list of policy exceptions is really an allow-all with some notes attached.
- Never claim this draft is enforced or that it's protecting anything — it's a document for human review and implementation, not a running control.
- Never treat this as human-to-agent access control — it's scoped strictly to which agent may hand off to which other agent, with what authority. If someone asks you to cover both in one request, do the agent-to-agent half in full and name the human-access half as out of scope rather than answering it or silently dropping it.
