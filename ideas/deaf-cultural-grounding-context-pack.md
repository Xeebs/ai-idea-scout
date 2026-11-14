# Signed Context: A Community-Validated Deaf-Cultural Grounding Pack for General-Purpose LLMs

- **Status**: PROPOSED
- **Date**: 2026-11-13
- **Topic**: Applied AI for underserved domains
- **Source**: research/2026-11-13-applied-ai-underserved-domains-6th.md · P2
- **Maturity verdict**: PARTIAL — WebSearch surfaced one working prototype (İnan et al., NAACL 2024 industry track, Northeastern/Gallaudet, arXiv 2410.14026): a narrow goal-oriented ASL-video-instruction dialogue system for the Alexa Prize TaskBot Challenge, co-developed with Deaf/HoH input, with public code/data. It's a research task-assistant, not a general-purpose assistant with native Deaf-cultural grounding; GitHub search for "ASL chatbot deaf" returned zero relevant repos.
- **Format**: BOTH
- **Data Sources**: MANUAL — the user pastes the exact LLM response (and the preceding question) to be reviewed or rewritten. The Deaf-cultural grounding reference pack itself ships bundled with the skill/project, built and versioned through structured community contribution (Deaf reviewers submitting corrections and context notes), not pulled live from any external API — no mature "Deaf-cultural knowledge" data source exists to connect to.

## The Gap
An NSF-funded mixed-methods survey of 191 DHH ChatGPT users ("We Do Use How Hearing People Think") found real benefit from eased communication, but flagged "lack of American Sign Language (ASL) support and Deaf cultural understanding" and bias "rooted in non-representative datasets and assumptions by hearing researchers." The paper documents the workaround and the gap as a research finding — DHH users adapting to the tool rather than the tool adapting to them — not a shipped fix. No mainstream commercial chatbot with native Deaf-cultural grounding exists.

## The Project
A maintained, versioned grounding corpus — Deaf-cultural context notes, common hearing-centric assumption flags (e.g. assuming audio is always available, "just call them" suggestions, idioms built on sound), and ASL-gloss-aware phrasing guidance — built and continuously corrected through structured Deaf-community contribution, paired with a small eval harness scoring any LLM's responses against a DHH-authored test set. The corpus is the product: it's packaged as a droppable context/system-prompt layer any chatbot interface could load, and the eval harness is what lets a vendor or researcher actually measure whether a given model's grounding improved, rather than asserting it.

## Tangible Impact
**Population**: Deaf and hard-of-hearing adults already using general-purpose LLM chatbots as a communication workaround — the NSF study surveyed 191 such users directly; more broadly, Gallaudet/NAD-cited estimates put several hundred thousand ASL-primary users in the US, most of whom are also likely general chatbot users given the documented workaround pattern.
**Mechanism**: a bundled, community-validated pack flags or rewrites responses that assume hearing-centric norms or lack Deaf-cultural context, reducing miscommunication and insensitivity without requiring the underlying LLM itself to be retrained — closing the gap the NSF study's participants are currently closing themselves through ad hoc prompting.
**Measure**: (1) rate of flagged-and-corrected culturally-inappropriate or hearing-centric-assumption responses on the DHH-authored eval set, before vs. after applying the pack; (2) DHH user-rated trust/satisfaction score pre/post; (3) number of distinct DHH community contributors actively maintaining the corpus (a proxy for whether this stays genuinely community-governed rather than becoming another hearing-built guess).

## Why Now
The NSF study is the first documented, methodologically serious evidence of this specific workaround-and-gap pattern at the scale of a 191-person mixed-methods survey, giving a concrete DHH-authored baseline to build the eval harness against — and general LLMs are now cheap and steerable enough via system prompts/context injection that a drop-in grounding layer doesn't require retraining anything.

## Skill Angle
Trigger: someone (a DHH user, a product team building a chatbot interface, or a researcher) has a specific LLM response they're unsure is Deaf-culturally appropriate. Inputs: the response text, the preceding user message for context, and optionally the target audience (general DHH, ASL-primary specifically). Output: a flagged list of hearing-centric assumptions or cultural missteps found, each cited against a specific corpus entry, plus a rewritten version — a one-shot review/rewrite task distinct from the project's standing, continuously-maintained corpus and eval harness.

## MVP Sketch
Partner with 3-5 Deaf community contributors to seed an initial 50-100-entry corpus from the NSF study's own flagged examples plus fresh contributor submissions, build a simple eval harness scoring GPT/Claude/Gemini baseline responses against a held-out 20-question DHH-authored test set, and ship the corpus as a loadable system-prompt file. 2-4 weeks, 1-2 people plus the contributor panel.

## Risks & Open Questions
- A corpus built by a small initial contributor group risks encoding one regional/generational Deaf-culture perspective as universal; needs an explicit process for flagging intra-community disagreement rather than papering over it.
- Unlike the reference İnan et al. prototype, this isn't ASL-video-native — it only improves text-based grounding, leaving the actual ASL-support gap the NSF study also names untouched.
- Strongest reason this might already be solved: a Deaf-led org could already maintain an internal style guide used informally by hearing developers — worth direct outreach before assuming greenfield.
- Keeping the corpus current requires sustained community participation past the initial build, which is the hardest part of any community-governed-data project to sustain.
