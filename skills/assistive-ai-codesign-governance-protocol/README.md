# Built-With-Not-For Co-Design Gap Checker

A self-contained prompt for checking whether a disability-focused AI product's community engagement process would actually hold up to scrutiny — before the team publicly claims to be "built with" that community, before they apply to any formal co-design certification, and before a skeptical community member, funder, or procurement officer asks the same question themselves.

This exists because disability communities have started rejecting outsider-built "helpful" AI wholesale when they discover the "built with" claim was a token gesture rather than genuine process — one documented case is an online Deaf community that banned all posts proposing sign-language AI, viewing it as a threat rather than help. A checkable, honest self-assessment before launch is cheaper than a backlash after.

## When to use this
You're building or about to launch an AI product aimed at a disability community (captioning/sign-language tools, mobility tech, blind/low-vision tools, cognitive-accessibility tools, etc.) and want an honest check of your community engagement process before you call it "co-designed," before you apply for any outside certification, or before launch.

## What to hand the AI (copy this into any chat tool)

Paste the prompt below, then answer the two questions it asks before the model scores anything. This is a manual, paste-in workflow — there is no API or connector involved; the evidence about whether you genuinely co-designed with a community is organizational and documentary, something you have to describe yourself, not something any system already holds.

---

**Prompt to paste:**

> Act as a co-design gap checker for disability-focused AI products. I will describe (1) my product and which disability community it serves, and (2) my community engagement process so far — who I worked with, how, when in the project timeline, whether/how participants were compensated, who had final say over launch decisions, and what I've published (if anything) about what changed because of community input versus what I decided unilaterally.
>
> Score my process against this fixed 7-point rubric. For each item, rate MET, PARTIAL, MISSING, or UNCLEAR, and quote or cite the exact part of my description that supports the rating. Do not infer a "yes" from something I didn't actually say — if I didn't mention compensation, that criterion is MISSING, not assumed met.
>
> 1. Named community partner(s) — a specific organization or identifiable group, not "the community" or "some users" in general.
> 2. Documented compensation — participants were paid or otherwise compensated, and I said so explicitly.
> 3. Engagement timing — involvement happened at the problem-definition/design stage, not only as feedback on an already-built product.
> 4. Decision-making power — community reviewers had real veto power over launch decisions, not just an advisory role.
> 5. Transparency artifact — a plain-language summary exists (or is planned) of what changed because of community input vs. what I decided on my own.
> 6. Representation breadth — more than one or two individuals, reflecting some diversity within the community, not a single friendly contact.
> 7. Continuity — engagement is ongoing/iterative, not a one-off consultation with no further contact.
>
> If criterion 3 (timing) comes back MISSING — meaning all engagement happened after the product was substantially built — call this out explicitly as a hard fail regardless of how the other six score. This is the single most common pattern behind disability communities rejecting "built with" claims they don't believe.
>
> Then give me an overall tier: Certification-Ready (6-7 MET, no hard fail), Needs Evidence (3-5 MET, or partial/unclear items with a plausible path to MET), or Not Ready (0-2 MET, hard fail triggered, or no real engagement described).
>
> Then give me 2-4 prioritized, concrete next actions to close the biggest gaps — not vague advice like "improve community engagement," but specific steps like "name the organization you worked with and confirm compensation terms in writing."
>
> Finally, always remind me that this is a self-assessment, not an actual certification — a real certification requires review by rotating disabled community reviewers from the relevant disability vertical, who may weigh evidence differently than this check does.
>
> My product and community: [describe]
> My engagement process so far: [describe]

---

## Output format you should get back

```
## Co-Design Gap Report: <product name>
**Vertical**: <disability community served>

| # | Criterion | Rating | Evidence cited |
|---|---|---|---|
| 1 | Named partner(s) | ... | ... |
| 2 | Documented compensation | ... | ... |
| 3 | Engagement timing | ... | ... |
| 4 | Decision-making power | ... | ... |
| 5 | Transparency artifact | ... | ... |
| 6 | Representation breadth | ... | ... |
| 7 | Continuity | ... | ... |

**Hard-fail check**: triggered / not triggered, with reason
**Readiness tier**: Certification-Ready | Needs Evidence | Not Ready

### Priority actions
1. ...
2. ...

### Limits of this report
Self-assessment only, not a certification. Real certification needs review by disabled community reviewers from the relevant vertical.
```

## Guardrails to insist on
- No criterion should be marked MET on an assumption — if you didn't say it, it should come back MISSING or UNCLEAR, not filled in charitably.
- The tool should never fabricate a partner organization name, a compensation figure, or a quote you didn't give it.
- The tool should never tell you that you're "certified" or "passed" — only that you're ready (or not) to pursue real certification.
- The hard-fail (post-hoc-only engagement) should never get softened into just a "partial" score.
- A single sympathetic individual contact should never count as either a named organization (criterion 1) or representation breadth (criterion 6) — those are separate bars on purpose.

If the output does any of the above, re-paste your answers and ask it to re-score strictly against the rubric as written.
