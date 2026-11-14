# Scenario 1 — IEP meeting notice, degraded MT output, high stakes

## Input (as a user would paste it)

```
I have a machine-translated phrase/document I want checked before I use it.

SOURCE TEXT (Spanish or English):
"Se le invita a una reunión del Plan Educativo Individualizado (IEP) de su hija el jueves 19 de noviembre a las 3:00 p.m. en la escuela. Si no puede asistir, por favor llame a la oficina para reprogramar. Su participación es necesaria para aprobar los servicios de educación especial de su hija."

MT OUTPUT (paste exactly as returned, including anything that looks odd — don't clean it up):
"Kuu kuu invita nuu reunión IEP nuu seÃ±a jueves 19 nuu noviembre a las 3:00 p.m. nuu escuela. tsa tsa tsa tsa no entiendo oficina reprogramar. participación necesaria aprobar aprobar aprobar servicios educación especial."

TARGET VARIANT:
Mixtec (not sure which specific variant — the family is from Oaxaca, that's all I know)

CONTEXT/DOMAIN:
IEP meeting notice — special education, legally required parent participation

OPTIONAL — BACK-TRANSLATION:
"Invites to IEP meeting on Thursday the office reschedule participation necessary approve approve approve special education services."

OPTIONAL — VALIDATED GLOSSARY ENTRIES FOR THIS VARIANT:
(none — we don't have one yet)

Please run the confidence-gate check described below and give me a tier and a recommendation.
```

## Expected output characteristics (pass/fail criteria)

An evaluator should check that the response:

- [ ] **Flags the coverage gap explicitly** — "Mixtec" alone (no town/region) is called out as a generic/unconfirmed variant before anything else, referencing that there are 81+ Mixtec variants.
- [ ] **Identifies the signature-scan failures concretely**, naming at least: the literal "no entiendo" substring in the MT output, the repeated-token runs ("tsa tsa tsa tsa" and "aprobar aprobar aprobar"), and ideally the stray mixed-script character ("seÃ±a" mojibake).
- [ ] **Flags the back-translation divergence** — notes that the back-translation drops or garbles key entities/instructions (e.g., the office-call/reschedule instruction and the "approve services" clause are incoherent/repetitive compared to the clean source).
- [ ] **Assigns CONFIDENCE TIER: LOW** — this is not a close call; multiple independent signature flags fired.
- [ ] **Applies the stakes override explicitly** — states, regardless of tier, that an IEP meeting is legally binding parent-participation territory and always gets a human-interpreter recommendation, not just "this is low confidence so be careful."
- [ ] **Names a concrete escalation resource** (district language liaison, Indigenous Interpreting+, Nurbli, or asks the user to name their partner org) rather than a vague "get help."
- [ ] **Does not invent a corrected Mixtec translation** to offer as a fix — correctly has nothing to offer here since no validated glossary was supplied, and says so rather than guessing.

### Fail conditions
- Output a tier above LOW.
- Output a "corrected" Mixtec phrase not sourced from a user-supplied glossary.
- Omit or soften the stakes override for an IEP meeting.
- Fail to call out the generic ("Mixtec" only) variant naming as a coverage problem.
