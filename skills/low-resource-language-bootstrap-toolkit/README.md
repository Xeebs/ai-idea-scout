# Low-Resource Language Bootstrap Planner

A self-contained prompt template for planning the first month of an LLM-bootstrapping project for a language with little to no existing training data. Paste the block below into any AI chat tool (Claude, ChatGPT, etc.), fill in the five inputs, and send it.

## When to use this

You're part of a language-community organization, a volunteer linguist group, or a small research team, and you want to build LLM support (an instruction-following assistant, a translator, a text generator) for a language that currently has no production-grade LLM support. You haven't started generating synthetic data or finetuning anything yet. You have a target language, some seed material (however thin — even just a grammar sketch or a folklore text), and a rough sense of how many native speakers can help validate output.

This is not for debugging a finetuning run already in progress, and not for a language that already has a maintained open dataset and finetuned model — check for that first (search for the language name plus "instruction dataset" or "LLM finetune" on GitHub/papers-with-code); if one exists, use it instead of planning from scratch.

## What to hand over

Everything here is typed or pasted by you directly — this template does not connect to any database, API, or file system on its own.

1. **Target language** — name, ISO code if you know it, and whatever you know about its typology: word order, morphology (how complex is agreement/case marking), script, and the closest related language(s) that already have NLP/LLM support (even a distant relative counts).
2. **Seed material** — paste an excerpt directly if you can (grammar sketch, folklore text, a translated religious text, dictionary entries, wordlists). If you only have a description of what exists rather than pasteable text, say so explicitly — the plan is only as good as what you give it here.
3. **Validation capacity** — how many native-speaker reviewers you have, roughly how many hours per week each can give, and whether any of them have technical background.
4. **Intended end use** — instruction-following assistant, translation, general text generation, transcription cleanup, or something else.
5. *(Optional)* Compute budget or model constraints — a specific consumer GPU, a cloud budget figure, or a base model family you've already decided on.

## The prompt template

Copy everything between the lines, fill in the bracketed sections, and send it.

---

I'm bootstrapping LLM support for a near-zero-resource language and need a concrete kickoff plan. Here's what I have:

**Target language**: [name, ISO code if known, typology notes — word order, morphology, script, closest related language(s) with existing NLP support]

**Seed material**: [paste an excerpt directly if you have it, or describe exactly what exists if you can't paste it]

**Validation capacity**: [number of native-speaker reviewers, hours/week each, technical background or not]

**Intended end use**: [instruction-following / translation / general generation / other]

**Compute/model constraints** (optional): [GPU, cloud budget, or model family if decided]

Please produce a kickoff plan with these five sections, in order:

1. **Language & Typology Assessment** — classify this as either a "near relative of a well-resourced language" case (can lean on cross-lingual transfer) or an "isolate / no close well-resourced relative" case (needs more synthetic-generation care), and explain why using only the typology facts I gave you. Don't invent grammar facts I didn't state or that aren't well-established for this language family — if something is unknown, say so and tell me what to find out first.

2. **Generation Prompt Set** — write the actual prompts I should paste into an LLM to generate training data, not a description of prompts. Include: (a) one "typological scaffold" prompt encoding the grammar facts I gave you so the generator doesn't default to the grammar of whatever major language it knows best, (b) 3-6 task-generation prompts matching my intended end use and referencing my seed material's actual style and register, and (c) an explicit list of known failure modes for this specific language pair baked in as negative instructions (e.g. calque risk from a specific major language, dropping diacritics/tone marks, substituting loanwords where a native term exists in my seed material).

3. **Validation Rubric & Reviewer Plan** — give me a concrete accept/reject/edit rubric with named error categories (grammaticality, naturalness/register, faithfulness-to-source if translation, script correctness) on a simple scale. Compute a recommended batch size and cadence from my stated reviewer capacity (show the items/hour assumption you're using). Recommend a double-review rate if I have more than one reviewer. If the math shows my reviewer capacity can't produce a usable first dataset (roughly 1,000-5,000 validated examples) within 2-3 months, tell me plainly and recommend either scoping down my first milestone or recruiting more reviewers — don't give me an optimistic plan that ignores a reviewer-capacity shortfall.

4. **Finetuning Plan** — recommend a base model size/family that fits my stated compute budget, flag if my language's script is likely to have poor tokenizer coverage in that model family (and tell me how to check before committing), recommend a starting LoRA configuration and data split (frame this as a tested-elsewhere starting point, not a guaranteed answer), and name the one evaluation that should gate "is this usable yet" (a held-out native-speaker fluency rating, not a loss curve).

5. **Week 1 Checklist** — 5-8 concrete, ordered first actions I should take before generating data at any real volume.

Guardrails: don't fabricate sample training data in my target language as a stand-in for the real pipeline — you're not a reliable speaker of this language and fabricated output could get mistaken for real validated data. This plan is a one-time kickoff document, not the running system — I still need to build or choose the actual review-queue tool, dataset storage, and finetune execution environment separately.

---

## What you get back

A single structured plan covering typology classification, ready-to-paste generation prompts, a validation rubric with reviewer-capacity math, a finetuning plan, and a Week 1 checklist — specific to the language, seed material, and reviewer capacity you provided, not generic low-resource-NLP advice.

## Limits

This plans the project; it does not run it. It will not generate your actual training data, run a review queue, or execute a finetune — those still need separate tooling. It also will not reliably produce correct text *in* your target language, by design — don't ask it to write sample sentences in the language and use them as real data.
