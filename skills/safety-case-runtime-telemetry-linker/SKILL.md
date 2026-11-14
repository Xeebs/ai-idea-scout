---
name: safety-case-runtime-telemetry-linker
description: Checks a pasted AI safety case's claims against a fresh incident report or eval/regression result and flags exactly which claims are now contradicted, stale, or unaffected, with ready-to-paste revision language. Use the moment a new incident or eval run lands and someone needs to know if it breaks an existing safety-case claim, without waiting for the next scheduled case review.
---

# Safety Case Runtime Telemetry Linker (Companion Skill)

## When to use this
The moment a team with an existing AI safety case (a structured claims/evidence document — GSN, UL 4600-style, or an internal spreadsheet) gets a new piece of evidence that might affect it: a red-team or production incident report, a failed eval/regression run, or a new audit finding. Instead of waiting for the next scheduled safety-case review (often 6–12 months out), the user pastes the claims and the new evidence in and gets an immediate per-claim verdict.

This is the one-shot, paste-based companion to the full "Living Case" project (a continuously running tool that auto-ingests a team's incident tracker, eval pipeline, and agent trace store via live connectors). This skill does not connect to anything — it is the lightweight version for a single ad hoc check, usable by a team that has no automated pipeline at all yet.

Do not use this for: writing a safety case from scratch (this only reconciles an existing one against new evidence), or for continuous/automatic monitoring (that is the project's job, not this skill's).

## Inputs
**Data source**: Manual — the user pastes (a) the safety case's claims list and (b) one new evidence item (incident report or eval/regression result). The parent idea classifies the full always-on project as CONNECTED (it ingests live from Jira/Linear/GitHub Issues, the team's eval/CI pipeline, and OTel agent traces). This skill is deliberately the manual, point-in-time companion described in the idea's Skill Angle — it never reaches into a connector, by design, so a team can use it before they've wired up any live integration at all.

Specifically needed from the user:
1. **Claims list** — each claim as plain text, ideally with: a claim ID or short name, the claim statement, the risk category it covers, and the evidence type/source it currently cites (and, if known, the date of that evidence). A spreadsheet export, a GSN diagram's text labels, or a bulleted doc all work — ask for risk category per claim if it's missing, don't guess it silently.
2. **New evidence** — one of: an incident/red-team report (what happened, what category of failure, when), or an eval/regression run result (which categories passed/failed, when). Multiple items can be pasted in one pass if the user has them.
3. **Optional**: a staleness window (e.g. "flag anything with no evidence newer than 90 days"). If not given, default to 90 days and say explicitly that this is a working default, not a confirmed team policy.

If the claims list has no risk-category tags and none can be reasonably inferred from the claim text, stop and ask rather than guessing a mapping.

## Procedure
1. **Parse the claims list** into claim objects: ID, statement, risk category, cited evidence type, cited evidence date (if given).
2. **Parse the new evidence item(s)**: classify each as incident report or eval/regression result; extract risk category/tags, severity or pass/fail, and date.
3. **Map evidence to claims** by risk category — only map a claim if the evidence's category plausibly matches the claim's stated category. Name the specific claim ID being matched and quote the matching phrase from both the claim and the evidence; never fuzzy-match silently.
4. **Classify every claim in the list** (not just the ones this round's evidence touches — staleness is checked independently for every claim, every time):
   - **CONTRADICTED** — this round's evidence maps to the claim (per step 3) and shows the exact failure mode the claim says is prevented or mitigated (e.g., claim: "jailbreak attempts are caught pre-execution"; incident: a jailbreak executed and produced the target harmful output).
   - **STALE** — independent of whether this round's evidence maps to the claim, check the claim's own last-cited-evidence date against the staleness window. If that date is older than the window AND nothing in this round's evidence refreshes it (either no evidence was mapped to it, or mapped evidence doesn't actually reconfirm the specific thing the claim asserts), mark it STALE. A claim can be both "no new evidence touched its category this round" and STALE at once — say both explicitly rather than picking one.
   - **UNCHANGED** — the claim's own cited evidence is still within the staleness window AND this round's evidence doesn't touch its risk category. Label it explicitly "no new evidence this round, prior evidence still fresh" rather than implying it was actively re-checked.
   - **RECONFIRMED** — this round's evidence maps to the claim's risk category and actively supports (does not contradict) it — e.g., a relevant eval suite ran and passed. Treat this as a fresh "supported" state, distinct from UNCHANGED's passive carry-forward.
5. **For every CONTRADICTED or STALE claim**, draft:
   - an updated one-line status for the claim,
   - a 1–2 sentence addendum citing the specific evidence by date/ID,
   - for CONTRADICTED only, a suggested immediate follow-up action (e.g., "escalate to red-team for scope review," "add this exact prompt pattern to the regression suite").
6. **Flag ambiguous mappings explicitly** under a separate "Needs Human Judgment" heading — list the claim ID, the evidence item, and the specific reason the mapping is unclear (e.g., category overlap, vague claim wording). Never silently resolve ambiguity by picking the closer-seeming claim.
7. **Close with a scope reminder**: this is a point-in-time check against the evidence pasted in this session, not a continuous monitor, and does not replace the next full scheduled case review.

## Output format
```
## Claim Status Summary
| Claim ID | Status | Evidence cited | Reasoning (1 line) |
|---|---|---|---|
| ... | CONTRADICTED / STALE / UNCHANGED / RECONFIRMED | ... | ... |

## Draft Revisions
### <Claim ID> — <old status> -> <new status>
Addendum: "<1-2 sentence addendum citing evidence by date/ID>"
Follow-up (if CONTRADICTED): <specific suggested action>
(Only written for CONTRADICTED and STALE claims; RECONFIRMED and UNCHANGED claims appear in the summary table only.)

## Needs Human Judgment
- <Claim ID>: <why the mapping is ambiguous>

## Scope Note
This is a point-in-time check against the evidence pasted above (dated <date(s)>), not continuous monitoring. The next full scheduled safety-case review is still required.
```

## Guardrails
- Never mark a claim "supported" or "passed" without a fresh matching piece of evidence actually pasted in this session — distinguish "unchanged, no new evidence" from "actively reconfirmed."
- Never invent incident details, severities, categories, or dates not present in what the user pasted.
- Never evaluate a claim that wasn't in the pasted claims list, and never silently drop a claim that was in the list but had no matching evidence — it must appear as UNCHANGED, not disappear.
- Never apply a staleness window the user didn't confirm without flagging it as a default assumption.
- Never present this one-shot check as equivalent to, or a substitute for, continuous runtime monitoring or the next full scheduled case review — always include the scope note.
- If the claims list lacks risk-category tags and they can't be reasonably inferred, stop and ask before mapping anything.
