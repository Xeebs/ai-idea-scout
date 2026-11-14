# Safety Case Runtime Telemetry Linker (Companion Check)

A paste-in prompt template for checking whether a fresh incident report or eval/regression result breaks any existing claim in your AI safety case — without waiting for the next scheduled case review.

Use this the moment something happens: a red-team finding, a production incident, or a failed eval/regression run. You hand over your safety case's claims and the new evidence, and get back a verdict per claim, plus ready-to-paste revision language for anything that's now wrong.

This is a one-shot, manual check. It does not connect to Jira, Linear, GitHub Issues, or your eval pipeline — you paste in what you have. If your team eventually builds (or buys) a tool that continuously reconciles your safety case against those live systems, this prompt is the lightweight stand-in for teams that don't have that yet, or for a single quick check even if they do.

## What to hand over

1. **Your safety case's claims list.** For each claim, ideally: an ID or short name, the claim statement, the risk category it covers, and what evidence currently backs it (and when that evidence is from, if you know). A spreadsheet export, bullet list, or the text labels off a GSN diagram all work. If you don't have risk categories tagged per claim, say so — don't make the AI guess them.
2. **The new evidence.** Either:
   - An incident or red-team report: what happened, what kind of failure it was, when it happened.
   - An eval/regression run result: which categories passed or failed, and when the run happened.
   You can hand over more than one evidence item at once.
3. **(Optional) Your staleness window** — how old evidence has to be before a claim counts as stale. If you don't give one, the default used is 90 days, flagged explicitly as a working assumption, not your confirmed policy.

## What you'll get back

A table with one row per claim — every claim gets checked for staleness independently of whether this round's evidence even touches it — each marked:
- **CONTRADICTED** — this round's evidence maps to the claim and shows the exact failure it says is prevented. Example: the claim says jailbreaks are caught before execution; the incident report shows one that wasn't.
- **STALE** — the claim's own last-cited evidence is older than the staleness window, and nothing in this round's evidence refreshes it (either nothing was mapped to it, or what was mapped doesn't actually reconfirm it). This can apply even to a claim this round's evidence never touches, purely because its own evidence is old.
- **UNCHANGED** — the claim's own evidence is still within the staleness window, and this round's evidence doesn't touch its risk category either. Labeled "no new evidence this round, prior evidence still fresh," not silently assumed re-checked.
- **RECONFIRMED** — this round's evidence maps to the claim's category and actively supports it (e.g., a relevant eval suite ran and passed). Kept distinct from UNCHANGED, which is just a passive carry-forward.

For every CONTRADICTED or STALE claim, you get a draft revision: an updated status line, a short addendum citing the specific evidence by date, and — for contradicted claims — a suggested immediate follow-up action.

Any claim where the mapping between evidence and claim is genuinely ambiguous gets listed separately under "Needs Human Judgment" with the specific reason, instead of being guessed at.

The output always ends with a scope note: this was a check against the specific evidence you pasted in, on this date — it is not continuous monitoring, and your next full scheduled safety-case review still needs to happen.

## The prompt template

Paste this into any AI chat tool, filling in the bracketed sections:

```
I need you to check my AI safety case's claims against a new piece of evidence and tell me exactly which claims are now contradicted, stale, or unaffected.

SAFETY CASE CLAIMS:
[paste your claims list here — ID, statement, risk category, and current cited evidence + date for each, if you have them]

NEW EVIDENCE:
[paste the incident report or eval/regression result here, including what happened/what failed, what category it falls under, and the date]

STALENESS WINDOW (optional): [e.g. "90 days" — if you skip this, default to 90 days and say so explicitly]

For EVERY claim in my list (check staleness independently for all of them, not just ones this evidence touches):
1. Only map this round's evidence to a claim if the risk categories plausibly match — name the specific claim and quote the matching text from both sides, don't fuzzy-match silently.
2. Mark it CONTRADICTED if mapped evidence shows the exact failure mode the claim says is prevented/mitigated.
3. Mark it STALE if the claim's own cited evidence date predates the staleness window and nothing in this round's evidence refreshes it — this applies even if this round's evidence never touched that claim's category at all, purely because its own evidence is old.
4. Mark it RECONFIRMED if mapped evidence actively supports (doesn't contradict) the claim.
5. Mark it UNCHANGED only if its own evidence is still within the staleness window AND this round's evidence doesn't touch it — say "no new evidence this round, prior evidence still fresh."
6. For every CONTRADICTED or STALE claim, draft: an updated one-line status, a 1-2 sentence addendum citing this evidence by date, and (for CONTRADICTED only) a suggested immediate follow-up action.
7. List anything ambiguous under "Needs Human Judgment" with the specific reason — never silently resolve ambiguity.
8. If my claims list has no risk categories and you can't reasonably infer them, stop and ask me before mapping anything.
9. End with a scope note: this is a point-in-time check against this evidence only, not continuous monitoring, and doesn't replace my next scheduled full case review.

Output as: a claim status table, then a draft revision block per contradicted/stale claim, then a needs-human-judgment list, then the scope note.
```

## Guardrails to expect from the output

- It will never mark a claim "supported" without fresh matching evidence actually pasted in — "unchanged, no new evidence" and "actively reconfirmed" are kept separate.
- It will never invent incident details, dates, severities, or categories you didn't paste in.
- It will never drop a claim silently — every claim in your list appears in the output, even if untouched this round.
- It will flag the 90-day default as an assumption, not your policy, unless you supplied your own window.
- It will always include the scope note so this one-shot check never gets mistaken for ongoing monitoring.
