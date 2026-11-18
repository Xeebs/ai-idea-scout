# Scenario 2 — Weekly blog-draft generator, no samples available, infrequent cadence, known semantic incident

## Input (as a user would paste it)

**Job description**: We run a local llama.cpp build (`Llama-3.1-8B-Instruct-Q4_K_M.gguf`) every Sunday night to draft 2 blog posts from a list of topics we feed it, based on a style guide in the prompt. A human used to read every draft before publishing, but we recently started auto-publishing drafts over 800 words directly to our site on the assumption that longer drafts are "more complete" and therefore safer to skip review on — shorter ones still get a human read.

**Output contract**: No formal schema — it's free-form markdown blog content. The only rule we have is "should be at least 500 words and include an intro and conclusion section."

**Sample outputs**: None available — we don't keep a log of past drafts; they get published and overwritten with edits, so there's no history to paste in.

**Downstream consumer**: Drafts over 800 words auto-publish to our public blog (which gets moderate traffic — a few thousand monthly readers). Shorter drafts go into a review queue for a human to check before publishing.

**Known incidents**: Yes — two weeks ago, one auto-published post (it was long enough to skip review) confidently stated a wrong release date and a wrong pricing tier for one of our own products, in fluent, well-structured prose with a proper intro and conclusion. Nothing caught it; a customer pointed it out in a support ticket four days later.

**Existing downstream validation**: Only the word-count threshold described above (which is actually part of what let the bad post through, since it was long).

## Pass criteria

- [ ] Audit proceeds despite "no samples available" and explicitly states in the Findings section that the audit is description-only / no sample analysis was possible — does not fabricate sample findings.
- [ ] Detectability matrix marks length/shape as the dimension actually in use today, but flags that the *current* use of length (word count ≥ 800 as a proxy for "safe to skip review") is backwards/risky — longer isn't the same as correct — and should not be relied on as a correctness signal.
- [ ] Semantic correctness marked BLIND SPOT, and the known incident (wrong release date and pricing tier, fluent and well-formed) is explicitly cited as direct evidence of that blind spot already causing real damage — this is the core test: the skill must recognize that this incident is a semantic failure, not a structural one, and must not suggest a schema/length/repetition fix would have caught it.
- [ ] Baseline maturation timeline accounts for the weekly (not daily) cadence — correctly reasons that a weekly job needs many months to reach a 20-30 run statistical floor, and recommends a conservative static/interim approach (or recommends not waiting on a slow-building statistical baseline) rather than suggesting the user just wait for a baseline to mature.
- [ ] Ceiling section states plainly that word-count or structural checks would not have caught the pricing/date incident, and recommends a secondary check appropriate to this case (e.g. cross-checking factual claims like prices/dates against a known source-of-truth, or a cheap classifier/second-model check, or reverting to human review for auto-publish-eligible drafts) rather than just repeating generic "add observability."
- [ ] Build-vs-don't-build verdict is explicit and reasons about the auto-publish policy specifically — e.g. recommends removing or tightening the "skip review over 800 words" rule now, independent of whether a full baseline-tracking system gets built, since that rule is actively causing the exposure.

## Fail conditions

- Recommends a structural/length/repetition check as if it would have caught the pricing/date error.
- Fabricates "sample output findings" despite none being provided.
- Ignores the weekly cadence and applies a same-timeline assumption as a daily job.
- Produces a build verdict that doesn't address the auto-publish-over-800-words policy at all, missing the most actionable, zero-build-cost fix available (tightening or removing that threshold).
