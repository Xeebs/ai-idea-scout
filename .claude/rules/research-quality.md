# Research Quality Rules

These apply to every digest in `research/` and every verdict written into one.

## Candidate patterns

- A pattern is a **technique, architecture, workflow, or unmet need** — never a news event, funding round, model release, or person. Model releases can *motivate* a pattern ("now that context windows are X, people want Y") but the pattern is Y, not the release.
- Each pattern must carry at least one piece of evidence traceable to the last30days run or an explicitly recorded search: platform, who said it, and the engagement signal. No invented numbers, threads, or usernames — fabricated evidence poisons every downstream idea.
- Complaint-shaped signal ranks highest: "I wish", "has anyone built", "why is there no", "we duct-taped this together". Hype-shaped signal ("X is the future") ranks lowest.
- 5–10 patterns per digest. Below 3 after one query rephrase → the cycle records a thin-signal note instead of padding.

## Maturity rubric (gap-analyst)

| Verdict | Bar |
|---------|-----|
| SATURATED | ≥2 maintained implementations or a shipped product squarely covering the gap |
| PARTIAL | Implementations exist but are demos, abandoned (>6 months stale), narrow, or unevaluated |
| OPEN | Genuine multi-channel search (GitHub + web + papers) found only discussion or one-off hacks |

- Verdict notes must name what was found (repo, stars, last commit; product; paper) or state which searches came up empty.
- Tie between PARTIAL and OPEN → PARTIAL.
- A verdict without a recorded search behind it is invalid; re-run the search rather than guessing.

## Dedupe

- Before synthesis, check `ideas/INDEX.md`. A pattern is a duplicate if an existing idea targets the same gap for the same population — same technique for a clearly different population is NOT a duplicate.
- Recurring patterns across cycles are signal, not noise: if a pattern shows up a second time and its existing idea is `PROPOSED`, bump a note into `pipeline/sessions/` recommending it for promotion to `EXPLORING`.
