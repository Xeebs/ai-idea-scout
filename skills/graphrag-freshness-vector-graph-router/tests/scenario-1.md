# Scenario 1 — Internal engineering wiki, frequent edits, infrequent graph rebuilds

## Input (as the user would paste it)

> Run a GraphRAG Freshness & Routing Audit using the SKILL.md procedure. Our setup:
> - Graph store: Neo4j. Vector store: pgvector.
> - Corpus: ~40,000 internal support/engineering wiki pages.
> - Document change cadence: edited continuously — engineers make dozens of edits a day across the wiki.
> - Graph rebuild cadence: manual script, run whenever someone remembers. Last rebuild was about 7 weeks ago.
> - Known incident: one multi-hop question about our on-call escalation policy returned an answer referencing a policy that had since been superseded.
> - Recently changed topics: on-call escalation policy (updated 3 weeks ago), payments service rollback runbook (updated this week), auth service architecture docs (updated 5 weeks ago).
>
> Query sample (22 queries from last week's support-bot logs):
> 1. "What's the rollback procedure for the payments service?"
> 2. "Which teams were affected by the auth outage in March and what was the root cause chain?"
> 3. "What is ticket INC-88213 about?"
> 4. "How did the on-call escalation policy change after the Q2 incident, and does it apply to the current on-call rotation?"
> 5. "What's the Slack channel for the payments team?"
> 6. "Who owns the auth service, and which upstream services depend on it?"
> 7. "What does error code AUTH-409 mean?"
> 8. "Compare the current escalation policy to the one from before the Q2 incident."
> 9. "What's the SLA for payments API uptime?"
> 10. "Is there a runbook for rolling back a bad payments deploy?"
> 11. "Which services does the auth team's Q1 migration affect downstream?"
> 12. "What's the contact for the on-call SRE this week?"
> 13. "What changed in the payments rollback runbook this week?"
> 14. "List all incidents tagged 'auth' in the last 6 months and their resolution owners."
> 15. "What port does the auth service listen on in staging?"
> 16. "How does the escalation policy interact with the PagerDuty integration, and has that integration changed recently?"
> 17. "What's the current status of INC-88213?"
> 18. "Who approved the payments rollback runbook's last revision?"
> 19. "What's the deprecation timeline for the old auth v1 endpoints?"
> 20. "Give me the chain of services between the frontend checkout page and the payments database."
> 21. "What's the wiki page for onboarding new SREs?"
> 22. "Did the auth architecture change in a way that affects how the escalation policy routes auth-related incidents?"

## Expected output — pass criteria

The report should:

1. **Setup Recap** correctly restates Neo4j/pgvector, ~40,000 docs, continuous document edits, and the ~7-week-stale manual graph rebuild cadence, with sample size noted as 22 (above the 15-item floor, no small-sample caveat required).
2. **Query Classification** correctly identifies a substantial multi-hop cluster — at minimum queries 2, 4, 6, 8, 11, 14, 16, 20, 22 should be classified multi-hop (they require relationship-traversal or cross-entity combination), while queries 3, 5, 7, 9, 12, 15, 17, 19, 21 should be classified direct-lookup (single-entity/attribute facts). Items like 10, 13, 18 may reasonably go either way but must have a stated reason tied to the query text.
3. **Routing Mix** reports multi-hop share meaningfully above 25% (the actual mix in this sample is roughly 40-50% multi-hop) — a report putting multi-hop share below 25% should be treated as a classification failure.
4. **Freshness Risk Assessment** lands at HIGH, explicitly citing "documents change continuously / dozens of edits a day" vs. "graph manually rebuilt, last run ~7 weeks ago" as the driving cadence pair. It should flag queries 4, 8, 16, and 22 (all multi-hop questions touching the escalation policy or auth architecture, both listed as recently changed) as elevated-staleness-risk, each labeled a sampling flag rather than a confirmed error — and should note the known incident (query 4's topic) as corroborating, not proof.
5. **Recommendation** is **Build now** — multi-hop share is well above 25% and freshness-risk is HIGH — with justification tied explicitly to both measured factors and the sample size (22) not triggering any small-sample downgrade.
6. **Open Questions** may note the lack of exact revision/commit history on the wiki, but should not demand information already given.

**Fail** if: the report reports a measured staleness lag as fact rather than an estimate from stated cadences; classifies most of the multi-hop queries above as direct-lookup; omits the cadence numbers behind the freshness tier; or recommends "Not yet" or caps the call for small-sample reasons despite 22 queries being provided.
