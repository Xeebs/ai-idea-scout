# From Tickets to Rules: Mining Production Incidents Into Guardrail Policy Proposals

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-13-ai-safety-and-guardrails-in-production.md · P10
- **Maturity verdict**: PARTIAL — promptfoo's maintained, widely-used "Adaptive Guardrails" feature analyzes failed red-team tests to auto-generate guardrail policies; SPLX's "Policy Generator" does the same for Bedrock-style guardrail providers; Splunk describes an "evals-to-guardrails" loop sampling live production traffic into failure clusters that become new eval criteria. None of these specifically mines raw production incident reports or support tickets — they all operate on red-team or eval-judge failures. No tool mining literal incident/ticket text into guardrail rules was found.
- **Format**: BOTH
- **Data Sources**: CONNECTED (project) — reads the team's existing ticketing/incident platform (Zendesk, Intercom, Jira Service Management, or PagerDuty) via its standard REST API; all are mature, widely-used connectors already. No new protocol needs to be built, just an ingestion adapter per platform. MANUAL (skill) — user pastes a batch of recent ticket/incident text (anonymized as needed) for a one-shot clustering-and-draft trial.

## The Gap
WebSearch follow-up content advises teams to "add guardrails based on incidents you encounter in production logs, since guarding against unobserved threats raises false positives without necessarily improving safety" — framed purely as manual judgment. The closest existing automation, promptfoo's Adaptive Guardrails and SPLX's Policy Generator, both work from red-team-test or eval-judge *failures*, and Splunk's evals-to-guardrails loop samples live traffic into failure clusters for new *eval criteria* — none of these close the loop from an actual support ticket or incident report to a proposed new guardrail *rule*, which is specifically the framing this pattern names and which no source closes.

## The Project
A pipeline that ingests a team's production incident/support-ticket stream, uses an LLM to cluster tickets describing the same underlying guardrail failure mode (a harmful output that got through, or a benign request wrongly blocked), drafts a proposed new or adjusted guardrail rule for each cluster with the specific tickets cited as supporting evidence, and routes the proposal to a human reviewer with a clear diff of what historical traffic the new rule would have affected (estimated catch gain vs. estimated new false-positive risk) before it is ever enabled. The centerpiece is turning unstructured field complaints — not synthetic red-team misses — directly into reviewable, evidence-backed policy proposals.

## Tangible Impact
**Population**: trust-and-safety and platform teams operating a production LLM guardrail stack who currently rely on an engineer manually noticing a pattern across support tickets or incident write-ups before deciding to add a new rule — specifically teams without red-team/eval-based tooling (promptfoo, SPLX) already in place, or who want their actual field incidents, not synthetic red-team misses, driving new rules.
**Mechanism**: spotting a recurring pattern across dozens of unrelated-looking support tickets is today a manual task that depends entirely on one engineer connecting the dots, often weeks after the pattern started. An automated clustering-and-proposal pipeline surfaces the pattern as soon as enough tickets accumulate, drafts the candidate fix, and quantifies the catch-gain/false-positive-risk trade-off before a human has to decide — shortening the loop from "we kept seeing complaints about X" to a specific, evidence-backed rule proposal.
**Measure**: (1) time from the Nth similar incident/ticket to a drafted rule proposal reaching a human reviewer (target: days, not however long informal pattern-noticing takes); (2) reviewer acceptance rate of proposed rules, as a proxy for proposal quality; (3) reduction in repeat incidents of the same cluster type after an accepted rule ships, compared to the team's prior ad hoc reactive cadence.

## Why Now
Ticketing and incident-management platforms (Zendesk, Intercom, Jira, PagerDuty) all expose mature, well-documented APIs for pulling ticket/incident text today, and the LLM-based clustering-and-drafting step this pipeline needs is now cheap and reliable enough to run continuously on that stream — the missing piece the digest names (mining raw incidents rather than red-team/eval failures) is a wiring problem, not a missing capability.

## Skill Angle
Trigger: a team pastes a batch of recent incident/support-ticket text (anonymized as needed). The skill clusters similar complaints, drafts a candidate guardrail rule for the largest cluster with the supporting tickets cited, and estimates its likely trade-off qualitatively — a one-shot trial run before committing to the always-on ticketing-platform connector. The project is the continuously-running ingestion-clustering-proposal-review pipeline; the skill is the one-time test that validates the approach on a team's own tickets first.

## MVP Sketch
A script that pulls the last N days of tickets tagged with an "AI/bot" category from one ticketing platform's API (starting with Zendesk), runs an LLM clustering pass to group similar complaints, and drafts a candidate guardrail rule plus a historical-impact estimate (replayed against a sample of past traffic) for the largest cluster. Single experiment: run it against a real or realistic ticket sample with a known recurring issue seeded in, and check whether the pipeline surfaces that exact cluster and drafts a sensible rule without being told the answer in advance. 2-3 weeks for 1-2 people.

## Risks & Open Questions
- Support tickets are noisy and often mis-categorized; clustering quality depends heavily on how cleanly "AI/bot" complaints are tagged in the source system, which varies a lot team to team.
- A drafted rule's historical-impact estimate is only as good as the sample of past traffic available to replay against — thin traffic history weakens the trade-off estimate.
- Risk of the pipeline over-fitting to a handful of complaints and proposing an overly narrow rule that doesn't generalize past the exact tickets that triggered it.
- Could be seen as adjacent to promptfoo's Adaptive Guardrails or Splunk's evals-to-guardrails loop; the differentiator — real production incidents, not red-team/eval failures — needs to stay the headline or it reads as a redundant wrapper.
