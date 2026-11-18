---
name: assistive-ai-codesign-governance-protocol
description: Scores a disability-focused AI product's community co-design process against a 7-point evidence rubric and produces a gap report naming exactly what's missing, partial, or unclear before the team seeks outside co-design certification or launches publicly. Use when a team building assistive/disability-facing AI wants to check "did we actually co-design this, or just consult after the fact" before a skeptical disability community, funder, or procurement officer asks the same question.
---

# Built-With-Not-For Co-Design Gap Checker

## When to use this
A team is building or about to launch an AI product aimed at a disability community (captioning/sign-language AI, mobility tech, blind/low-vision tools, cognitive-accessibility tools, etc.) and wants an honest pre-submission check of whether their community engagement process would hold up to scrutiny — from the community itself, a funder, a procurement officer, or a future formal co-design certification body — before they publicly claim to be "built with" that community. Use this before launch or before applying for any co-design certification, not after a backlash has already started.

## Inputs
**Data source**: Manual — the user pastes (1) a short description of the product and which disability community/vertical it serves, and (2) a plain-language account of their community engagement process so far: who they worked with, how, when in the project timeline, whether/how participants were compensated, who had final say over launch decisions, and what (if anything) they've published about what changed because of community input. No external API or connector exists for this — "did a team genuinely co-design with a community" is organizational and documentary evidence, not data any system already holds.

If the user provides only a product description with no engagement account at all, do not guess — ask them to describe their engagement process before scoring, or score every category MISSING and say so plainly.

## Procedure

1. **Identify the vertical.** Note the specific disability community served (e.g., Deaf/ASL users, blind/low-vision users, mobility-disabled users, cognitively disabled users). The rubric below applies to any vertical; don't change the bar based on which one it is.

2. **Score against the fixed 7-point rubric.** For each item, classify as **MET**, **PARTIAL**, **MISSING**, or **UNCLEAR — ask**, citing the exact sentence or fact from the user's input that supports the rating. Never infer a rating from something the user didn't say — silence on compensation means MISSING compensation, not an assumed yes.

   | # | Criterion | What counts as MET |
   |---|---|---|
   | 1 | Named community partner(s) | A specific organization or identifiable group is named — "the Deaf community" or "some users" alone is not a name |
   | 2 | Documented compensation | Participants were paid or otherwise compensated for their time, and this is stated, not implied |
   | 3 | Engagement timing | Community involvement happened at problem-definition/design stage, not only as feedback on a finished product |
   | 4 | Decision-making power | Community reviewers had real veto power over launch decisions, not just an advisory/consultative role |
   | 5 | Transparency artifact | A plain-language summary exists (or is planned) distinguishing what changed because of community input vs. what the builder decided unilaterally |
   | 6 | Representation breadth | More than one or two individuals were involved, reflecting some diversity within the vertical (not a single "friendly" contact) |
   | 7 | Continuity | Engagement is ongoing/iterative, not a single one-off consultation early on with no further contact |

3. **Flag the hard-fail condition.** If criterion 3 (timing) is MISSING — i.e., all engagement happened after the product was substantially built — say explicitly that this fails the "process-stage, not post-hoc" bar regardless of how well other criteria score. This is the single most common way teams produce "built with" claims the community doesn't believe (per the CHI-paper backlash this rubric is built to anticipate).

4. **Compute an overall readiness tier**:
   - **Certification-Ready**: 6-7 criteria MET, no hard-fail.
   - **Needs Evidence**: 3-5 MET, or any criteria PARTIAL/UNCLEAR with a plausible path to MET.
   - **Not Ready**: 0-2 MET, or the hard-fail condition triggered, or genuinely no engagement described.

5. **Write a prioritized action list** — the 2-4 highest-impact gaps to close first, phrased as concrete next steps ("name the Deaf organization you worked with and confirm compensation terms in writing," not "improve community engagement").

6. **Always state the limit of this tool**: this gap report is a self-assessment aid, not a certification. Actual certification requires review by rotating disabled community reviewers from the relevant vertical — this skill cannot award certified status and should say so every time.

## Output format

```
## Co-Design Gap Report: <product name>
**Vertical**: <disability community served>

| # | Criterion | Rating | Evidence cited |
|---|---|---|---|
| 1 | Named partner(s) | MET/PARTIAL/MISSING/UNCLEAR | <quote or "not stated"> |
...7 rows...

**Hard-fail check**: <triggered / not triggered, with reason>
**Readiness tier**: Certification-Ready | Needs Evidence | Not Ready

### Priority actions before seeking certification or launching
1. ...
2. ...

### Limits of this report
This is a self-assessment against a published rubric, not a certification. Formal certification requires review by rotating disabled community reviewers from <vertical>, who may weigh evidence differently than this automated pass.
```

## Guardrails
- Never mark a criterion MET on inferred or assumed evidence — if the user didn't state it, it's MISSING or UNCLEAR, never filled in charitably.
- Never fabricate a named partner organization, a compensation figure, or a quote the user didn't provide.
- Never issue or imply an actual certification, badge, or "passed" verdict — this tool produces a gap report for self-correction, not a credential.
- Never soften the hard-fail (post-hoc-only engagement) into a merely "partial" score — it is a named, called-out failure every time it applies, because it's the exact pattern the CHI-paper community backlash was about.
- Never treat a single sympathetic individual contact as equivalent to a named organization or representative group (criteria 1 and 6 are deliberately separate from each other).
