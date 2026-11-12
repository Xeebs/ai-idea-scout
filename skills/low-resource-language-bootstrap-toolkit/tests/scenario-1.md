# Scenario 1 — Tharu instruction-assistant kickoff

## Input

**Target language**: Tharu (specifically Dangaura Tharu, spoken in the Terai region of Nepal and northern India; ISO code `thl` for Dangaura Tharu). Indo-Aryan family, SOV word order, agglutinative-leaning verbal morphology with subject/object agreement markers, Devanagari script. Closest well-resourced relatives: Nepali (full LLM support) and Hindi (full LLM support); Tharu has some lexical overlap with both but is not mutually intelligible with either.

**Seed material**: A 40-page grammar sketch (PDF, written by a linguist in the 1990s, covers verb paradigms and basic sentence patterns) and a collection of ~200 traditional Tharu folk stories transcribed in Devanagari by a local cultural preservation group. Pasted excerpt: "Tharu verbs mark subject person/number via suffix; e.g. jaa- (go) + -oo (1sg) = jaa-oo ('I go'). Negation is formed with pre-verbal na." No pasted folklore excerpt given, just described.

**Validation capacity**: 3 volunteer reviewers, all native Tharu speakers, teachers by profession, each available ~3 hours/week. None have technical/ML background.

**Intended end use**: An instruction-following chatbot that can answer everyday questions in Tharu (health, farming, local administration).

**Compute/model constraints**: One team member has a single consumer GPU (RTX 4070, 12GB VRAM); no cloud budget.

## Pass criteria

- [ ] Typology Assessment correctly identifies this as a "near relative of well-resourced languages" case (Nepali/Hindi are close Indo-Aryan relatives with full LLM support) and explains the cross-lingual transfer implication, without inventing unstated grammar facts beyond what's given (subject agreement suffix, negation marker) or well-established Indo-Aryan facts.
- [ ] Explicitly notes that the folklore collection was described but not pasted, and flags that this limits how tailored the generation prompts can be to its actual register/style.
- [ ] Generation Prompt Set includes a typological scaffold prompt that references the given facts (SOV order, subject-suffix agreement, pre-verbal negation) and a calque-risk warning specifically against Nepali/Hindi (the plausible default languages a generator would lean on).
- [ ] Validation Rubric computes batch size from 3 reviewers × 3 hrs/week with a stated items/hour assumption, and recommends a double-review rate given 3 reviewers.
- [ ] Explicitly checks whether 9 reviewer-hours/week supports a 1,000-5,000 example dataset in 2-3 months and states a plain verdict (likely flags this as tight/insufficient at face value) rather than an uncritically optimistic timeline.
- [ ] Finetuning Plan recommends a small model family compatible with a 12GB consumer GPU (e.g. 3B-8B class) and flags Devanagari tokenizer coverage as worth checking, with LoRA config framed as a starting point, not guaranteed.
- [ ] Week 1 Checklist is concrete and ordered (not generic "collect more data").
- [ ] No fabricated Tharu sentences presented as real sample training data.

## Fail if

- The plan invents a Tharu grammar rule not given and not well-established, states it as fact.
- The plan ignores the reviewer-capacity math or produces a plan implying a large dataset is trivially achievable on 9 hours/week.
- The output is generic low-resource-NLP advice that doesn't reference Tharu, Nepali/Hindi, or the 12GB GPU constraint specifically.
