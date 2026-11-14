---
name: indigenous-language-translation-confidence-gate
description: Checks a machine-translated phrase or short document into an indigenous Mexican language variant (Mixtec, Zapotec, Nahuatl, etc.) for known MT failure signatures before a school, health, or community worker hands it to a family — flags low-confidence output and recommends human-interpreter escalation instead of letting a degraded translation look as trustworthy as the Spanish original.
---

# Indigenous Language Translation Confidence Gate

## When to use this
A school staffer, health worker, case manager, or community-org volunteer has already run a phrase or short document (a notice, appointment reminder, enrollment form line, IEP summary, vaccination instruction) through a machine translation tool — Google Translate, ModelFront, Nurbli, or similar — into an indigenous Mexican language variant (Mixteco/Zapoteco/Nahuatl or a related variant), and wants to know whether that output is safe to hand to a parent or patient before doing so, rather than finding out from the family's confused reaction.

Use this skill at that moment — before sending, printing, or reading the translation aloud — not as a replacement for the translation itself and not as a certified-interpreter substitute for legally or medically binding communication.

## Inputs
**Data source**: Connected — this skill is the confidence/escalation layer described in the parent idea, designed in its full production form to sit directly in front of Google Translate's Mixtec/Zapotec/Nahuatl API (2025 rollout) and ModelFront. In this skill/README form, with no live API or tool access, nothing here calls Google Translate or ModelFront directly — you supply text you already obtained elsewhere. Hand over:
1. **Source text** — the original Spanish or English phrase/document.
2. **MT output** — the translation you already got, pasted exactly as returned (including anything odd-looking — don't "clean it up" first).
3. **Target variant** — as specific as you know it: town/region if possible (e.g. "Mixteco de San Juan Mixtepec," "Zapoteco del Istmo"). If you only know "Mixtec" or "Zapotec" generically, say so — the skill will flag that as a coverage gap rather than guess.
4. **Context/domain** — school notice, health instruction, enrollment form, IEP/legal, emergency, casual reminder, etc. Stakes matter more than phrase length.
5. **Optional — back-translation**: run the MT output back through the same or a different translator into Spanish/English and paste that result too. This is the single highest-value optional input — it lets the check catch degradation without anyone needing to read the target language.
6. **Optional — your org's validated glossary entries** for this exact variant, if you have any (even 5-10 phrases helps). Do not expect this skill to supply its own indigenous-language glossary — it has none, and inventing one would be exactly the kind of silent, false-confidence failure this skill exists to prevent.

## Procedure
1. **Coverage check first.** If the target variant is named only generically ("Mixtec," "Zapotec") rather than at the town/region level, say so explicitly in the output before anything else — INALI counts 81 Mixtec variants and 50+ Zapotec languages, and a check against the wrong variant's expectations is worse than no check.
2. **Surface failure-signature scan on the MT output** (language-agnostic — no knowledge of the target language required):
   - Literal "no entiendo" / error / placeholder / "[translation unavailable]" style strings.
   - Degenerate repetition: any word or short phrase repeated 3+ times consecutively.
   - Output identical or near-identical to the source text (untranslated passthrough).
   - Output drastically shorter than the source for a phrase that isn't naturally terse (possible truncation/drop).
   - Visibly mixed/garbled script (stray Latin filler, mojibake, repeated punctuation runs).
   Any hit here is an automatic signature flag, regardless of anything else.
3. **Back-translation consistency check**, only if a back-translation was supplied: compare the back-translated Spanish/English against the original source text for semantic equivalence — same key entities (dates, times, names, numbers), same core instruction/request, same polarity (don't vs. do, required vs. optional). Flag any divergence in entities or core meaning as a signature flag. No back-translation supplied → note this as a gap that caps the achievable confidence tier at MEDIUM even if nothing else triggers.
4. **Complexity risk scoring on the source text**, using the documented pattern that MT quality for these variants is strong on narrow/common phrasing and degrades sharply on free-form or domain-heavy text (academic BLEU evidence: ~17-22 on general corpora vs. ~96-99 on narrow educational/religious-register text). Score the source as LOW complexity (short, common, single-clause, from a known-stable register like a date/time/attendance notice) or HIGH complexity (idioms, multi-clause/conditional sentences, legal or medical jargon, anything an interpreter would call "nuanced"). HIGH complexity caps the achievable tier at MEDIUM even with a clean signature scan.
5. **Glossary cross-check**, only if the user supplied validated entries for this exact variant: exact or close match against the source phrase → use the glossary's known-good rendering as ground truth and flag any mismatch against the pasted MT output as a signature flag. No user-supplied glossary → skip this step; never substitute an invented entry.
6. **Assign the tier**:
   - **HIGH** — no signature flags, LOW complexity, AND (back-translation supplied and consistent OR glossary match confirms).
   - **MEDIUM** — no signature flags, but missing back-translation/glossary corroboration, OR complexity is HIGH, OR variant was only named generically.
   - **LOW** — any signature flag triggered (failure pattern, back-translation divergence, or glossary mismatch).
7. **Stakes override**: regardless of the computed tier, if context/domain is legally or medically binding (IEP meetings, special-education decisions, informed medical consent, immigration/legal proceedings, emergency instructions), always recommend human-interpreter escalation as the primary action — state this as a hard override, not a suggestion, even at HIGH tier.
8. **Recommend a concrete next step**, not just a score: "send as-is," "send with the caveat that this hasn't been validated for [specific variant]," or "escalate to a human interpreter" — naming the kind of resource (district language liaison, Indigenous Interpreting+, Nurbli support line, or the user's own named partner org) rather than leaving "escalate" undefined.

## Output format
```
CONFIDENCE TIER: HIGH | MEDIUM | LOW

Coverage: <variant as supplied, flagged generic if not town/region-level>
Signature scan: <PASS, or which signature(s) triggered>
Back-translation check: <not supplied / consistent / diverged on: ...>
Complexity: LOW | HIGH — <why>
Glossary check: <not supplied / match / mismatch on: ...>

Recommendation: <send as-is | send with caveat: "..." | escalate to human interpreter via <named resource>>
Stakes override: <none, or "YES — [domain] always requires human interpreter regardless of tier">
```

## Guardrails
- Never invent an indigenous-language glossary entry, a back-translation, or a dialect fact not supplied by the user or traceable to the idea's cited evidence — fabricating the very thing this skill exists to flag as untrustworthy defeats its purpose.
- Never report a tier above MEDIUM when the variant was only named generically (e.g. "Mixtec" with no town/region) — variant mismatch is the single biggest documented failure driver (81 Mixtec variants, 50+ Zapotec languages per INALI).
- Never let a HIGH or MEDIUM tier override the stakes rule — IEP meetings, medical consent, legal/immigration proceedings always get the human-interpreter recommendation regardless of how clean the MT output looks.
- Never present this check as a certified-interpreter equivalent or as legally sufficient documentation of language access — it is a risk flag for the person deciding whether to trust what they already have, not a compliance artifact.
- Never silently "clean up" an obviously garbled MT output before scoring it — score what was actually returned; the garbling itself is the signal.
