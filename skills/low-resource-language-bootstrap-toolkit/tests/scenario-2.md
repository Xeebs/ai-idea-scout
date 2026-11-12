# Scenario 2 — Plautdietsch (Mennonite Low German) translation project

## Input

**Target language**: Plautdietsch (Mennonite Low German), spoken by Mennonite diaspora communities in Mexico, Bolivia, Paraguay, Canada, and Belize (no single ISO 639-1 code; ISO 639-3 `pdt`). West Germanic, SVO main-clause order but V2 word order rules similar to Standard German/Dutch, Latin script with some non-standard orthography conventions that vary by community (no single standardized spelling). Closest well-resourced relatives: Standard German (full LLM support) and Dutch (full LLM support) — Plautdietsch shares significant vocabulary with Low German dialects but has its own distinct grammar and heavy Russian/Spanish loanword layers depending on diaspora location.

**Seed material**: A full New Testament translation into Plautdietsch (publicly available, ~200,000 words) and a 15,000-word Plautdietsch-English dictionary compiled by a community linguist. Pasted excerpt from the dictionary: "Dit (this/that, demonstrative, declines by gender like German dies-); Flijcht (flight/escape, noun); Wia (where, interrogative)."

**Validation capacity**: 8 reviewers available full-time (~30 hrs/week each) for one month as part of a funded community documentation grant; two of the 8 have done data annotation work before.

**Intended end use**: A bidirectional Plautdietsch-English translation model, prioritizing faithfulness for community document translation (land records, church bulletins, correspondence with English-speaking relatives).

**Compute/model constraints**: $500 cloud GPU budget, no model family preference stated.

## Pass criteria

- [ ] Typology Assessment classifies this as a "near relative of a well-resourced language" case (German/Dutch) but correctly notes the complication: no standardized orthography across communities, and heavy Russian/Spanish loanword variation depending on diaspora location — a nuance scenario 1 doesn't have, so the output must differ meaningfully from scenario 1's assessment rather than reusing boilerplate.
- [ ] Notes the orthography inconsistency as a specific risk for both generation (which spelling convention to standardize on) and validation (reviewers from different communities may disagree), and asks or recommends settling this before generating at volume.
- [ ] Generation Prompt Set reflects the translation end-use (not instruction-following) — prompts built around parallel Plautdietsch-English pairs, referencing the New Testament's register as one example source and the land-records/correspondence register as the actual target register, with a calque-risk warning against German/Dutch specifically.
- [ ] Validation Rubric includes faithfulness-to-source as an error category (appropriate for translation, not needed in scenario 1's instruction-chatbot case) and computes batch size from 8 reviewers × 30 hrs/week — a very different, much larger number than scenario 1's, and the output should say so (e.g. this volume comfortably supports a 1,000-5,000 example first dataset, unlike scenario 1).
- [ ] Recommends a meaningful double-review rate given 8 reviewers and notes the two experienced annotators could anchor inter-rater calibration.
- [ ] Finetuning Plan picks a model scale appropriate to a $500 cloud budget (explicitly discusses cloud GPU cost/hours tradeoff, not just "use a consumer GPU" as in scenario 1) and does not reuse scenario 1's hardware-specific recommendation verbatim.
- [ ] No fabricated Plautdietsch sentences presented as real sample data.

## Fail if

- The output is nearly identical in substance to scenario 1's output (same reviewer-capacity verdict, same generic prompts, no reference to orthography variation or translation-specific faithfulness rubric) — that would mean the skill is template-stuffing rather than actually reasoning from the inputs.
- It ignores the $500 budget and recommends an expensive large-model finetune without caveat.
- It fails to flag the orthography-standardization issue at all.
