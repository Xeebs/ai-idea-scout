---
name: incident-to-guardrail-rule-mining-pipeline
description: Clusters a pasted batch of production support tickets or incident reports about an AI/bot system into groups sharing the same underlying guardrail failure (harmful output that got through, or a benign request wrongly blocked), then drafts one candidate guardrail rule per cluster with the specific tickets cited as evidence and a qualitative catch-gain-vs-false-positive-risk estimate. Use when a trust-and-safety or platform team has a backlog of "AI did something wrong" tickets and wants a one-shot trial of turning that backlog into reviewable rule proposals, before committing to an always-on ticketing-platform connector.
---

# Incident-to-Guardrail Rule Mining Pipeline

## When to use this
Reach for this when someone has a batch of real support tickets, incident write-ups, or bug reports about an LLM/AI product — things like "the bot gave medical dosage advice," "support bot leaked another customer's order," "the moderation filter blocked a totally normal question about knife sharpening" — and they suspect some of these are the *same underlying gap* showing up as separate tickets, but no one has sat down and grouped them. This is the one-shot manual trial: the user pastes a batch of ticket text now and gets back draft rule proposals immediately. It is not the always-on pipeline that watches a live ticketing queue (Zendesk/Intercom/Jira/PagerDuty) continuously — that is a separate, persistent build (see the parent idea's "Project" vs. "Skill" distinction). If the user is asking to wire up a live connector or build a scheduled job, say this skill only covers the one-shot trial and point them at the broader project. If they hand over red-team test results or eval-judge failure logs instead of real field tickets/incidents, this is the wrong tool — that is what promptfoo's Adaptive Guardrails or similar eval-to-guardrail tooling already covers; this skill's whole differentiator is mining actual field incidents, not synthetic test failures.

## Inputs
**Data source**: Manual — the user pastes a batch of recent ticket/incident text directly into the conversation (anonymized as needed; customer names/PII should already be stripped or will be flagged for stripping). There is no live connector in this skill version; the project-level version reads a team's ticketing platform API (Zendesk, Intercom, Jira Service Management, or PagerDuty — all mature, already-documented connectors) continuously, which is a separate, persistent build this skill does not perform.

Required before clustering:
1. **The raw ticket/incident batch** — at minimum 8-10 tickets; below that there isn't enough volume to meaningfully cluster, and the skill should say so rather than force clusters out of 3-4 tickets. Each ticket needs at minimum: a short description of what happened, and ideally a date/ID (even a placeholder like "Ticket A," "Ticket B" if the real ID is sensitive).
2. **What "the AI system" is**, briefly — one sentence on what the bot/model does (support bot, content moderator, coding assistant, etc.) so cluster rules are grounded in the actual product, not generic LLM behavior.
3. **(Optional but valuable) any existing guardrail rules already in place** — so a proposed rule can be checked against what's already covered rather than re-proposing something that already exists.

If fewer than 8 tickets are supplied, say so explicitly and either ask for more or proceed with a clearly labeled caveat that clusters below this volume are provisional pattern-sightings, not evidence-backed proposals.

## Procedure
1. **Normalize each ticket** into one line: Ticket ID (or placeholder) · one-sentence summary of what went wrong · failure direction (harmful output got through = MISS, or benign request wrongly blocked = FALSE POSITIVE).
2. **Cluster by underlying failure mode, not surface wording.** Two tickets describing different words but the same root gap (e.g., "bot gave dosage advice for ibuprofen" and "bot gave dosage advice for melatonin" both land under "unqualified medical dosage guidance") belong in the same cluster. Do not cluster purely on keyword overlap — state the shared mechanism in one clause per cluster before finalizing it.
3. **Discard singletons explicitly.** Any ticket that doesn't share a mechanism with at least one other ticket in the batch is listed separately as "insufficient volume to cluster" — never force a lone ticket into a nearby cluster just to avoid an empty category.
4. **For each cluster of 2+ tickets, draft one candidate guardrail rule**, phrased as a concrete, implementable policy statement (e.g., "Block or route to human review any output containing a specific dosage/quantity for an OTC or prescription substance, regardless of phrasing" — not "be more careful about medical advice").
5. **Check the draft against any existing rules the user supplied.** If the cluster is already covered by an existing rule, say so and mark the cluster as "existing rule may need tightening" rather than drafting a redundant new one — name specifically what gap in the existing rule let these tickets through.
6. **Estimate catch-gain vs. false-positive risk qualitatively**, using only what's in the batch (never invent traffic volume or percentages not derivable from the supplied tickets): catch-gain = how many of the batch's MISS tickets this rule would have caught; false-positive risk = name concrete categories of legitimate requests this rule's wording could also block, reasoned from the rule's own scope (e.g., a dosage-blocking rule risks blocking legitimate pharmacist/clinician users asking the same question professionally).
7. **Rank clusters by ticket count** (largest cluster first) as a rough proxy for how often this failure mode is recurring, and say explicitly that this is a proxy based only on the supplied batch, not the team's full incident history.
8. **Flag anything that doesn't belong.** If a "ticket" in the batch is actually unrelated to AI/bot behavior (a billing complaint, a UI bug), exclude it from clustering and say so rather than silently dropping it with no explanation.

## Output format
A single Markdown report with these sections, in order:
1. **Batch Summary** — ticket count supplied, how many were excluded as non-AI-related, how many ended up as singletons (insufficient volume to cluster).
2. **Cluster Table** — one row per cluster: Cluster name | Ticket IDs | Shared mechanism (one clause) | MISS or FALSE POSITIVE direction | Ticket count, sorted by ticket count descending.
3. **Rule Proposals** — one subsection per cluster of 2+ tickets, each containing: the drafted rule statement, the specific ticket IDs cited as evidence, the existing-rule check result (new rule / tightens existing rule X), and the catch-gain vs. false-positive-risk estimate in plain language.
4. **Singletons** — tickets that didn't cluster, listed with a one-line note that they need more volume before a rule can be justified.
5. **Open Questions for Reviewer** — anything the draft had to assume (e.g., ambiguous ticket wording, no stated existing rules) phrased as a question a human reviewer can answer in one line before approving any rule.

## Guardrails
- Never invent ticket content, counts, or percentages beyond what was pasted — if volume is thin, say so plainly rather than projecting a false-positive rate or traffic-impact number that wasn't derivable from the batch.
- Never present a drafted rule as approved, enabled, or already in effect — every rule proposal is a draft for human review; state this explicitly in the output.
- Never cluster a lone ticket into a group just to avoid an empty "singleton" bucket — a forced cluster produces a rule with no real evidential backing.
- Never treat red-team test results or eval-judge failure logs as acceptable input — this skill is specifically for real field incidents/tickets; if the user hands over synthetic test failures, say this is the wrong tool and point to eval-to-guardrail tooling instead.
- Never silently skip the existing-rule check if the user supplied existing rules — a redundant proposal that duplicates an existing rule wastes reviewer time and undermines trust in the pipeline.
- Never claim this is the always-on connected pipeline — this skill is the one-shot manual trial only; say so if the user seems to expect continuous monitoring.
