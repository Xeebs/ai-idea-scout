---
name: low-resource-language-bootstrap-toolkit
description: Drafts a kickoff plan (generation prompt set, validation rubric, finetuning plan) for a team trying to bootstrap LLM support for a near-zero-resource language. Use when someone describes a target language with little/no existing training data, some seed material, and a native-speaker review pool, and needs a concrete first-month plan before writing any code.
---

# Low-Resource Language Bootstrap Planner

## When to use this
A language-community organization, volunteer linguist group, or small research team is about to start building instruction-following, translation, or general text-generation capability for a language that has no production-grade LLM support today, and they have not yet started generating synthetic data or finetuning anything. They have: a target language, some seed material (however thin), and a rough idea of how many native speakers can help validate output. They need a concrete, language-specific plan — not generic advice about "collect more data" — before spending generation budget or reviewer time.

Do not use this mid-project to debug a specific finetuning run, or for languages that already have a maintained open dataset and finetuned model (check first — if one exists, point the user to it instead of planning from scratch).

## Inputs
**Data source**: Manual — the user types or pastes everything; there is no connector or API this skill reaches into. Specifically:
1. **Target language** — name, ISO code if known, and whatever is known about its typology (word order, morphology, script, closest related language(s) with existing NLP/LLM support).
2. **Seed material** — paste an excerpt directly if possible (grammar sketch, folklore text, religious-text translation, dictionary entries, wordlists). If only a description of what exists is available (not pasted text), say so explicitly — the plan quality depends heavily on this.
3. **Validation capacity** — number of native-speaker reviewers available, their rough hours/week, and whether any have technical background.
4. **Intended end use** — instruction-following assistant, translation, general text generation, transcription cleanup, etc.
5. *(Optional)* Compute budget or base-model constraints (consumer GPU, cloud budget, specific model family already chosen).

If (1), (2), or (3) is missing, ask for it before drafting — a plan built on a guessed typology or an unstated reviewer count is the exact kind of generic wrapper this skill exists to avoid.

## Procedure
1. **Classify typology risk.** State explicitly whether this language is a "near relative of a well-resourced language" case (can lean on cross-lingual transfer from a sibling language's tokenizer/data) or an "isolate / no close well-resourced relative" case (needs more synthetic-generation care, higher risk of calque errors from whichever major language the generator model defaults to). Say which case applies and why, using only the typology facts given — never invent grammar facts not stated or well-established for that language family.

2. **Draft the generation prompt set** — write the actual prompts, ready to paste into an LLM, not a description of prompts:
   - One "typological scaffold" prompt encoding the known grammar facts (word order, case/agreement system, script/diacritics) so the generator doesn't silently default to the grammar of the nearest major language.
   - 3-6 task-generation prompts matching the stated end use (instruction/response pairs, translation pairs, dialogue turns, etc.), each referencing the actual seed material style and register.
   - An explicit "known failure mode" list baked into the prompts as negative instructions specific to this language pair (e.g. "do not calque [major language]'s word order," "preserve [diacritic/tone marking] — do not drop it," "avoid [major language] loanwords where a native term exists in the seed material").

3. **Draft the validation rubric and reviewer plan:**
   - A concrete accept/reject/edit rubric with named error categories (grammaticality, naturalness/register, faithfulness-to-source if translation, script correctness) each on a simple 1-5 or binary scale.
   - A recommended batch size and cadence computed from the stated reviewer capacity (reviewers × hours/week ÷ realistic items/hour, state the items/hour assumption explicitly, e.g. 15-30 short items/hour for careful review).
   - A double-review rate recommendation (10-20% of items reviewed by a second person) if more than one reviewer exists, for inter-rater reliability.
   - **If the computed weekly reviewable volume can't support a usable first dataset (roughly 1,000-5,000 validated examples) within 2-3 months, say so plainly** and recommend either scoping the first milestone down or recruiting more reviewers before generating at full volume — never produce an optimistic plan that papers over a reviewer-capacity shortfall.

4. **Draft the finetuning plan:**
   - Recommend a base model size/family appropriate to the stated compute budget, and flag if the target language's script is likely to have poor tokenizer coverage in that model family (if the script is non-Latin or has combining marks, say to check tokenizer fertility on a seed-text sample before committing).
   - Recommend a LoRA starting configuration (rank, target modules, roughly what data split) as a tested-elsewhere starting point to adjust, never as a guaranteed-correct answer.
   - Name the single gating evaluation: a held-out native-speaker fluency/accuracy rating on examples the model has never seen — not a loss curve — as the thing that decides "is this usable yet."

5. **Assemble the output** as one structured kickoff document (see Output format) and end with a "Week 1 Checklist" of the first concrete, sequenced actions.

## Output format
A single markdown document with these sections, in order:
1. **Language & Typology Assessment** — the classification from step 1 and its implications.
2. **Generation Prompt Set** — the actual ready-to-paste prompts from step 2, each labeled by purpose.
3. **Validation Rubric & Reviewer Plan** — the rubric table, batch-size math, and double-review recommendation from step 3, including the capacity-shortfall warning if applicable.
4. **Finetuning Plan** — base model recommendation, tokenizer-coverage flag, LoRA starting config, data split, and gating evaluation from step 4.
5. **Week 1 Checklist** — 5-8 concrete, ordered first actions (e.g. "run a 50-sentence tokenizer-fertility test on [model] with the pasted seed excerpt before generating anything at volume").

## Guardrails
- Never invent seed material, example sentences, or typological/grammar facts in the target language that weren't given or aren't well-established for that language family — if typology is unknown, say so and recommend finding it out first rather than guessing.
- Never generate actual sample training data in the target language as a stand-in for the real generation pipeline — this skill is not a reliable speaker of an unfamiliar low-resource language, and fabricated "sample output" could be mistaken for real validated data if it leaks into the project.
- Never present the LoRA config or model recommendation as guaranteed to work — it is a documented starting point, always framed as "adjust based on your first validation round."
- Never soften or omit a reviewer-capacity shortfall to make the plan look more achievable than the stated numbers support.
- This produces a one-time kickoff plan, not the running pipeline — never imply it replaces an actual review-queue tool, dataset store, or finetune execution environment; point out that those still need to be built or chosen separately.
