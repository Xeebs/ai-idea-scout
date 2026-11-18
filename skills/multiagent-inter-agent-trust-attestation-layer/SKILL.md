---
name: multiagent-inter-agent-trust-attestation-layer
description: Drafts a tailored inter-agent trust policy (which claim types need signed attestation, what evidence backs each, and what trust-score threshold escalates to a human) for a described multi-agent pipeline, before anyone builds or buys actual signing/ledger infrastructure.
---

# Inter-Agent Trust Policy Drafter

## When to use this
Use this when someone is designing, reviewing, or hardening a multi-agent system — built on A2A, LangGraph, CrewAI, OpenAI Agents SDK, or a custom orchestrator — where one agent routinely acts on another agent's unverified claim ("I checked inventory," "tests passed," "the payment cleared," "I verified the customer's identity") and they want to decide, concretely, which of those claims are risky enough to need proof before anyone acts on them. This is a design/review step, not a runtime control: it produces a policy document, not working signing code. Reach for it when someone says things like "do we actually need to verify what our agents tell each other," "which of these handoffs should require proof," "help me design a trust policy for our agent pipeline," or "we got burned by an agent that lied about having done something."

## Inputs
**Data source**: Manual — the user describes their pipeline in their own words or pastes a code/config excerpt (agent definitions, message schemas, tool-call payloads, or orchestration graph edges) showing which agent asserts what to which other agent, and what the receiving agent does in response. There is no connector: this skill never reads a live message bus, A2A session, or LangGraph run state on its own — if the user wants that, they paste the relevant trace or payload as text.

Ask for, if not already given:
1. **The agents and their roles** — who talks to whom.
2. **The claims exchanged** — in prose or as code/log excerpts, every "I did X" / "X is true" statement one agent sends another (tool-call results count as claims too).
3. **The downstream action** each claim gates — what the receiving agent does because it believed the claim (approves a payment, skips a redundant check, escalates, releases an artifact, etc.) and whether that action is reversible.
4. *(If known)* Whether a ground-truth check exists for each claim type (e.g., a payment claim can be checked against the payment processor's own record; a "code review passed" claim often cannot be checked except by re-reviewing).
5. *(If known)* Whether the claiming and receiving agents cross an organizational, vendor, or trust boundary (same team vs. third-party/marketplace agent).

If the user has no claims list yet, ask them to sketch 3–6 real claims from their own pipeline rather than inventing generic examples for them — a policy built on invented claims is worthless to them.

## Procedure
1. **Inventory the claims.** Build one row per distinct claim type (not per message instance) — "inventory checked," "tests passed," "payment cleared," "customer identity verified," etc. Merge claims that are functionally the same even if phrased differently.
2. **Classify stakes.** For each claim, classify the downstream action it gates as:
   - **Informational** — no action changes, it's logged or displayed only.
   - **Reversible** — an action is taken but can be undone cheaply if the claim was false (e.g., a draft gets regenerated).
   - **Irreversible/high-stakes** — money moves, an artifact ships externally, a safety-relevant step is skipped, or a human-facing decision is made.
3. **Classify verifiability.** For each claim, mark:
   - **Checkable** — a ground-truth source exists (a tool-call result, an external API, a hash the receiving agent can independently recompute).
   - **Checkable with effort** — verifiable in principle but costly (re-running the work, a human audit).
   - **Unverifiable judgment** — a pure opinion/assessment with no ground truth to check against (flag this explicitly; it cannot be scored the same way as a checkable claim, per the idea's own risk note that reputation-only scores can be gamed).
4. **Decide attestation requirements**, cross-referencing stakes × verifiability. Treat "checkable with effort" as "checkable" for which bucket applies below, but call out explicitly that verification is costly (someone has to actually re-run the check, not just look up a record):
   - Irreversible/high-stakes + checkable (or checkable with effort) → require signed attestation referencing the actual evidence (tool-call result hash, artifact hash, external record ID) — if only checkable with effort, also recommend spot-checking a sample rather than every instance, since verifying every claim may be too costly to be practical.
   - Irreversible/high-stakes + unverifiable → require attestation anyway (so the claim is at least falsifiable after the fact and attributable) plus a mandatory corroboration or human sign-off before the action proceeds — never let an irreversible action ride on an unscoreable claim alone.
   - Reversible + checkable → attestation recommended but not blocking; log for trust scoring.
   - Reversible/Informational + unverifiable → attestation optional; note that skipping it means that claim type can never contribute to a meaningful trust score.
5. **Set a trust-score threshold and action per claim type** — state it as a concrete rule: "if this agent's trust score for claim type X drops below [threshold], require [corroboration from a second agent / human sign-off] before acting on that claim type again." Tie the threshold tightness to the stakes tier from step 2 (tighter threshold for higher stakes).
6. **Flag cross-boundary risk.** If the claiming agent is third-party/vendor/marketplace (crosses an org boundary), raise every attestation recommendation by one stakes tier — the receiving agent cannot inspect that agent's internals at all, which is the exact scenario the parent idea names as the core gap.
7. **Write the policy table and summary** (see Output format). Call out the 2–3 highest-priority claim types by name and explain in one sentence each why they're the priority.

## Output format
A single markdown document with two parts:

1. **Policy table**, one row per claim type:
   `Claim Type | Asserting Agent → Receiving Agent | Downstream Action | Stakes Tier | Verifiability | Attestation Required? | Evidence to Attach | Trust-Score Threshold & Action`
2. **Priority narrative** — 2–3 short paragraphs naming the highest-priority claim types, why they ranked there, and the single biggest policy gap in the current pipeline as described (usually: an irreversible action gated on an unverifiable or unattested claim).

End with one explicit line: "This is a draft policy for human review — it does not sign, ledger, or score anything on its own. Pressure-test it against a pipeline log before wiring it into an orchestrator's policy hook."

## Guardrails
- Never invent claims, agents, or downstream actions the user didn't describe — ask for real examples instead of filling gaps with generic placeholders.
- Never present this output as working signing/ledger/trust-scoring infrastructure — it is a policy design document only; the actual Ed25519 signing SDK, hash-chained ledger, and scoring service are separate build work this skill does not do.
- Never recommend blanket "attest everything" — that adds latency and storage cost without targeting risk; gate attestation requirements by stakes and verifiability, not by reflex.
- Never score an unverifiable judgment claim as if it had ground truth — always flag reputation-only scoring as gameable, per step 3.
- Never silently skip the cross-organizational-boundary check in step 6 — it's the scenario the gap is actually about.
