# Inter-Agent Trust Policy Drafter

A self-contained prompt template for drafting a trust policy for a multi-agent system — deciding which claims one agent makes to another need proof before being acted on. Paste the block below into any AI chat tool (Claude, ChatGPT, Copilot Chat, etc.) along with your pipeline description.

## When to use this

Use this when you're designing, reviewing, or hardening a multi-agent system — built on A2A, LangGraph, CrewAI, OpenAI Agents SDK, or a custom orchestrator — where one agent routinely acts on another agent's unverified claim ("I checked inventory," "tests passed," "the payment cleared," "I verified the customer's identity") and you want to decide, concretely, which of those claims are risky enough to require proof before anyone acts on them.

This produces a **policy document**, not working code. It's the step you take before building or buying an actual signing/ledger/trust-scoring system — so you know what that system actually needs to enforce instead of guessing.

## What to hand over

**Data source: Manual.** You paste a description of your pipeline — in your own words or as a code/config excerpt — showing which agent asserts what to which other agent, and what happens because of it. Nothing is read automatically from a live message bus, A2A session, or orchestration graph; if you want that context included, paste the relevant trace or payload as text yourself.

Specifically, have ready:

1. **The agents and their roles** — who talks to whom.
2. **The claims exchanged** — every "I did X" / "X is true" statement one agent sends another, in prose or as real code/log excerpts. Tool-call results count as claims too (e.g., a tool reporting "inventory: 40 units" is itself a claim the next agent trusts).
3. **The downstream action each claim gates** — what the receiving agent does because it believed the claim, and whether that action is reversible (can be undone cheaply) or not (money moves, something ships, a safety check gets skipped).
4. *(If known)* Whether a ground-truth check exists for each claim type — can you ever independently verify it was true?
5. *(If known)* Whether the claiming and receiving agents cross an organizational or vendor boundary (your own agent vs. a third-party/marketplace agent).

Use 3–6 real claims from your own system. Invented generic examples produce a worthless policy — the whole point is tailoring thresholds to your actual stakes.

## The prompt

```
You are drafting an inter-agent trust policy for my multi-agent pipeline.
I will describe the agents, the claims they make to each other, and what
happens as a result. Do NOT invent claims or agents I haven't described —
ask me for real examples if I've given you too little to work with.

For each distinct claim type I describe:

1. Classify the downstream action's stakes:
   - Informational (nothing changes, it's just logged/displayed)
   - Reversible (an action happens but can be cheaply undone if the claim
     was false)
   - Irreversible/high-stakes (money moves, something ships externally,
     a safety-relevant check gets skipped, or a human-facing decision
     is made)

2. Classify verifiability:
   - Checkable (a ground-truth source exists — a tool result, an
     external API, an independently recomputable hash)
   - Checkable with effort (verifiable in principle, costly to check —
     re-doing the work, a human audit)
   - Unverifiable judgment (pure opinion/assessment, no ground truth
     exists — flag this explicitly; it can never be scored the same
     way as a checkable claim and is gameable if used alone)

3. Decide whether signed attestation is required, cross-referencing
   stakes x verifiability. Treat "checkable with effort" as "checkable"
   for which rule below applies, but call out that verification is
   costly (someone has to actually redo the check, not just look up
   a record):
   - Irreversible + checkable (or checkable with effort) -> require
     attestation referencing the actual evidence (tool-call result,
     artifact hash, external record ID). If only checkable with
     effort, also recommend spot-checking a sample rather than every
     instance, since verifying every claim may be too costly.
   - Irreversible + unverifiable -> require attestation anyway (for
     attribution/audit) PLUS mandatory corroboration or human sign-off
     before the action proceeds. Never let an irreversible action ride
     on an unscoreable claim alone.
   - Reversible + checkable -> attestation recommended, not blocking;
     log it for trust scoring.
   - Reversible/Informational + unverifiable -> attestation optional,
     but note that skipping it means this claim type can never feed a
     meaningful trust score.

4. Set a concrete trust-score threshold and action per claim type:
   "if this agent's trust score for claim type X drops below
   [threshold], require [corroboration from a second agent / human
   sign-off] before acting on that claim type from that agent again."
   Make thresholds tighter for higher-stakes claim types.

5. If the claiming agent is third-party, vendor, or otherwise outside my
   own organization, raise every attestation recommendation for that
   agent by one stakes tier -- I cannot inspect that agent's internals
   at all, which is the whole reason this policy matters.

Output:
- A markdown table, one row per claim type:
  Claim Type | Asserting Agent -> Receiving Agent | Downstream Action |
  Stakes Tier | Verifiability | Attestation Required? | Evidence to
  Attach | Trust-Score Threshold & Action
- A short priority narrative (2-3 paragraphs) naming the 2-3
  highest-priority claim types and the single biggest policy gap in
  my pipeline as described -- usually an irreversible action currently
  gated on an unverifiable or unattested claim.
- End with: "This is a draft policy for human review -- it does not
  sign, ledger, or score anything on its own. Pressure-test it against
  a pipeline log before wiring it into an orchestrator's policy hook."

Here is my pipeline:
[describe your agents, the claims they exchange, and what happens
downstream]
```

## What you get back

A markdown policy table plus a short written summary, as specified above. It names your highest-risk claim types, tells you exactly which ones need cryptographic attestation versus which are fine to leave as-is, and gives you a concrete trust-score threshold rule per claim type — in a form you can hand directly to whoever builds or configures the actual signing/ledger/scoring infrastructure.

## What this does not do

It does not sign anything, does not run a ledger, does not compute a live trust score, and does not connect to your actual message bus, A2A session, LangGraph state, or CrewAI task context. It is a one-time design pass you run before building or adopting that infrastructure — treat its output as a draft for a human (you, or your team) to review and pressure-test against a real pipeline log, not as a production control.
