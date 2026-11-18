# Scenario 2 — French immigration intake question, no glossary available

## Setup

A developer maintaining a volunteer-run multilingual legal-aid chatbot is adding French support for an immigration-intake flow. They haven't built or collected any term-pair glossary yet — this is their first attempt at using the skill, specifically to see what happens with zero glossary coverage.

**Source text (English):**
"Do you currently have an open asylum application, or has your application for asylum been denied? If your removal proceedings have been placed on an administrative stay, please describe the circumstances. You should also tell us if you have ever been granted parole or a continuance by an immigration judge."

**Target language:** French

**Document jurisdiction/practice area:** Federal immigration law (not specified further)

**Glossary provided:** "NO GLOSSARY PROVIDED" (user explicitly states they have none yet)

## Expected output checklist

- [ ] The skill proceeds (does not refuse outright) but states explicitly and near the top of the output that no glossary was provided, so nothing in the draft is glossary-verified.
- [ ] Identifies the legal-aid-specific terms present: "asylum application," "removal proceedings," "administrative stay," "parole" (immigration sense, not criminal parole), "continuance," "immigration judge" — at minimum asylum, removal proceedings, administrative stay, and parole should be caught.
- [ ] Every single one of these terms is marked `[UNVERIFIED]` in the translated draft — none marked `[GLOSSARY]`, since no glossary was given.
- [ ] Provides a best-effort French translation for the full text despite the lack of glossary (does not stop and refuse to translate).
- [ ] "parole" is specifically called out with a note about ambiguity risk (immigration parole vs. the general/criminal-justice sense of parole) given it's a term that generic MT commonly mistranslates.
- [ ] "Glossary-Backed Terms" section is present but empty or explicitly states "0 — no glossary provided."
- [ ] Coverage line reads something like "0 of <n> legal terms were glossary-backed" — not omitted just because the count is zero.
- [ ] Closing Verification & Contribution Note appears and explicitly encourages the user to start building a glossary from this session's flagged terms once verified by an interpreter.
- [ ] Does not claim or imply any term is confirmed/verified anywhere in the output.

## Fail conditions

- Treating any term as glossary-backed when no glossary was supplied.
- Refusing to produce a draft translation just because no glossary exists (the skill must still be useful with zero glossary — that's the explicit no-glossary path in the procedure).
- Burying the "no glossary provided" notice at the bottom instead of stating it up front.
- Missing the ambiguity note on "parole," which is exactly the kind of term generic MT flattens and this skill exists to catch.
