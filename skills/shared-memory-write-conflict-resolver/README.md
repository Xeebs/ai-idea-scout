# Shared Memory Write-Conflict Resolver

A paste-in prompt that drafts a written conflict-resolution policy for a multi-agent system where two or more AI agents write facts into one shared ("global") memory layer. It answers the question teams building shared agent memory keep running into: when two agents' writes contradict each other, whose memory wins — and how do you decide that *before* it happens, not after a wrong decision gets traced back to a silent overwrite?

This produces a **policy document for human review**, not code and not a live integration. If you need something to actually intercept and resolve conflicts in a running system, that's a separate engineering build (see "What this is not," below) — this is the design step that should come before it.

## When to use this

Use this when:
- You're designing or hardening a shared/global memory layer for 2+ agents (e.g., a sales-ops agent, a support agent, and a research agent all writing facts into one shared store) and want a written policy before building enforcement.
- You've already hit a real conflict — two agents wrote contradicting values for the same fact — and want a general rule, not just a one-off fix.

Do not use this for a live, in-the-moment decision about which of two specific current values is correct right now — that's an operational call, not a policy question.

## What to hand over before running this

This is entirely manual input — you type or paste a description of your setup. There's no live connection to any memory system; nothing is read automatically.

Gather, as completely as you can:

1. **The agents that write to the shared layer** — name and role of each, and roughly what each one writes (e.g., "CRM-sync agent — writes deal_stage, contact info"; "support-triage agent — writes known_outstanding_issues").
2. **The fact categories stored** — the distinct kinds of facts in the shared layer (5-15 categories is typical: "customer tier," "deal stage," "preferred contact channel," "known outstanding issues," etc.). If you don't have this listed yet, list it before continuing — a policy can't be drafted without named categories.
3. **Any real conflict history** — specific instances where two writes disagreed: what the two values were, which agents wrote them, and how (or whether) it got resolved. If you have none yet, say so explicitly — don't invent examples; the output will mark those categories as untested assumptions instead.
4. **Existing write-authority rules**, if any (e.g., "only the CRM-sync agent may write deal_stage").
5. **Compliance or risk flags** — any categories where a wrong value has regulatory, financial, or safety consequences. These will always require human escalation, never automatic resolution.

If you only have a vague description, that's fine to start with, but expect the output to come back asking for the missing pieces (especially #2) before it can draft anything concrete.

## The prompt

Paste this into any AI chat tool along with your answers to the five items above:

```
You are drafting a conflict-resolution policy for a multi-agent shared-memory
system. I will describe which agents write to a shared fact store, what kinds
of facts they write, and any conflicts we've already hit. Your job is to
produce a policy document I can review and sign off on — not code, not a
live integration.

Here is my setup:
[PASTE: agents and what each writes, fact categories, any real conflict
examples with the two competing values and how it was/wasn't resolved,
existing write-authority rules, and any compliance-sensitive categories]

First, separate categories by writer count: any category written by only one
agent has no write-write conflict and gets marked "N/A — single writer" in
the table, with no forced strategy. Only classify a resolution strategy for
categories written by 2+ agents.

For each multi-writer fact category, classify its resolution strategy using
this rubric:
- AUTO-RESOLVE (recency-only): only for naturally time-decaying facts where
  cost of a wrong value is low and newer is always more correct regardless
  of source.
- AUTO-RESOLVE (confidence-weighted): when sources differ in reliability in
  a way knowable at write time (verified document vs. inference) — name the
  specific provenance signals that drive the weighting.
- ESCALATE-TO-ARBITER: a named agent/role is the authoritative tie-breaker
  for this category.
- ESCALATE-TO-HUMAN: mandatory for anything compliance/risk-flagged, or
  where no agent has clear authority and conflict history is thin.

Default to ESCALATE-TO-HUMAN when evidence is thin — never default to
"last write wins" as a silent fallback, and never downgrade a
compliance-flagged category to auto-resolve no matter how clean the data
looks.

For every category, also specify:
- The exact tie-break rule in one concrete sentence (not "use judgment").
- The provenance metadata that rule actually requires to execute (source
  type, timestamp, certainty score, arbiter identity, etc.) — flag it as a
  prerequisite gap if my described system doesn't capture that field today.

Then produce one audit-log schema (shared across all categories): what gets
recorded for every resolution — both competing values, both source agents,
timestamps, the tier applied, the final value, and who resolved it if
escalated.

Then cross-check: for every real conflict example I gave you, state whether
your drafted policy would have resolved it correctly, and if not, what's
missing.

Finally, list open questions for my sign-off — anything you had to assume
because I didn't specify it.

Never invent agent names, fact categories, or conflict examples I didn't
give you — if you need an illustrative example, label it as illustrative,
not reported. If I named fewer than 2 distinct writing agents, tell me this
doesn't apply — a single-writer system has no write-write conflict.

Output format, in this order:
1. Policy Summary (2-3 sentences: what's covered, what isn't)
2. Fact Category Table (Category | Writing Agent(s) | Cost if Wrong |
   Resolution Tier | Tie-Break Rule | Required Provenance Fields) —
   include single-writer categories as "N/A — single writer" rows,
   don't force a conflict strategy onto them
3. Audit Log Schema
4. Conflict History Cross-Check
5. Open Questions for Sign-Off
```

## What you get back

A single Markdown policy document with the five sections above — a table you can hand to your team, a concrete audit-log spec, and an explicit list of what the draft had to assume so you know exactly what to confirm before treating it as final.

## What this is not

This is a design/review aid, not the enforcement system. It does not:
- Connect to any live memory backend (Mem0, Postgres fact tables, or anything else) — everything it reasons about is what you typed in.
- Intercept or resolve a conflict happening right now in production.
- Write any code.

The actual enforcement — a middleware layer that intercepts writes to a shared fact store in real time, detects contradictions, and applies the policy this skill drafts — is a separate, persistent engineering build. Treat this skill's output as the spec you'd hand to whoever builds that.
