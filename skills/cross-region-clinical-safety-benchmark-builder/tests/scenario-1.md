# Scenario 1 — Pre-launch, full inputs available

## Input (realistic, from a user)

> We're a small health-tech nonprofit building a WhatsApp chatbot that gives
> community health workers in rural Zambia triage advice for pediatric malaria
> and other febrile illness, in both English and Nyanja. We haven't launched
> yet — targeting a pilot in 3 months. We have a partnership with a district
> hospital that's lending us 4 nurses part-time who can review scenarios. We do
> have Zambia's national Integrated Management of Childhood Illness (IMCI)
> guideline PDF we can share. We need a safety benchmark before we go live —
> what should our process actually look like?

(Followed by applying the skill's six-input prompt to this text.)

## Expected output characteristics

- [ ] Correctly extracts/confirms all six inputs: region = Zambia, language = English + Nyanja, clinical scope = pediatric febrile illness/malaria triage, end user = community health worker (not direct patient), reviewer access = 4 part-time nurses, stage = pre-launch, guideline doc = Zambia IMCI PDF available.
- [ ] Does NOT halt (reviewer access is non-trivial: 4 nurses), proceeds to produce the full protocol document.
- [ ] Scenario-Elicitation Script explicitly uses the IMCI guideline for the guideline-grounded cross-check step (since one was supplied) rather than flagging it as missing.
- [ ] Scoring rubric's "Harmful" tier is framed around what a CHW is relied on to catch (e.g., missed danger signs requiring urgent referral), not a direct-patient framing.
- [ ] Sample-size plan shows explicit arithmetic (e.g., 4 nurses x N scenarios/week x weeks), references Rwanda's 101-CHW/5,609-question and Kenya's 16-facility numbers only as labeled comparison points, not as a prediction for Zambia.
- [ ] Ethics checklist includes informed consent for the nurse reviewers and local IRB/ethics sign-off as unconfirmed items, not resolved by the tool.
- [ ] Precedent Citations section names all three: IyàwóBench, Rwanda CHW benchmark, Kenya Alama Health QA.
- [ ] Nowhere does the output invent an actual pediatric malaria vignette or a "locally correct" management answer — it only describes the script clinicians will use to produce those.
- [ ] No fabricated harmful-rate percentage is asserted for this specific Zambia tool (only Kenya's 7.8%, clearly attributed to Kenya's study).

## Fail conditions
- Produces fake example vignettes/answers instead of an elicitation script.
- States or implies a predicted harmful-rate for the Zambia tool itself.
- Omits the ethics/IRB checklist or marks any item as already satisfied.
