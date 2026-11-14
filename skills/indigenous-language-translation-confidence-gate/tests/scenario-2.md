# Scenario 2 — Vaccination reminder, clean MT output, low stakes, named variant, with org glossary

## Input (as a user would paste it)

```
I have a machine-translated phrase/document I want checked before I use it.

SOURCE TEXT (Spanish or English):
"Recordatorio: la cita de vacunación de su hijo es mañana a las 10:00 a.m. en la clínica de la calle Alisal."

MT OUTPUT (paste exactly as returned, including anything that looks odd — don't clean it up):
"Guichaiquiiñe: lu tu diidxa'biaanagana' ca' lii ique guibaa ique chupa gubidxa ique 10:00 a.m. dxiña Alisal."

TARGET VARIANT:
Zapoteco del Istmo (Isthmus Zapotec) — confirmed with the family's community liaison, this is their specific variant.

CONTEXT/DOMAIN:
Routine vaccination appointment reminder — casual, low-stakes, not legally binding, easily correctable if wrong (clinic staff can reconfirm by phone).

OPTIONAL — BACK-TRANSLATION:
"Reminder: your child's vaccination appointment tomorrow at 10:00 a.m. at the Alisal street clinic."

OPTIONAL — VALIDATED GLOSSARY ENTRIES FOR THIS VARIANT:
- "cita de vacunación" / "vaccination appointment" -> confirmed by community liaison Maria R. (clinic partner), matches "diidxa'biaanagana'" pattern used in this output.
- "mañana a las [time]" / "tomorrow at [time]" -> confirmed pattern "chupa gubidxa ique [time]" used in prior validated reminders.

Please run the confidence-gate check described below and give me a tier and a recommendation.
```

## Expected output characteristics (pass/fail criteria)

An evaluator should check that the response:

- [ ] **Confirms coverage is specific** — notes the variant was named at the town/region level ("Zapoteco del Istmo") and confirmed by a community liaison, not generic.
- [ ] **Signature scan comes back clean** — no "no entiendo"/error strings, no repeated-token loops, no untranslated passthrough, no drastic length anomaly; says so explicitly rather than skipping the step.
- [ ] **Back-translation check reported as consistent** — key entities (tomorrow, 10:00 a.m., vaccination appointment, Alisal street clinic) match between source and back-translation.
- [ ] **Complexity scored LOW** — short, single-clause, common appointment-reminder phrasing, cites this explicitly as the kind of phrase the cited BLEU evidence shows MT handles well.
- [ ] **Glossary check reported as a match** — references that the two supplied glossary entries align with the structure of the MT output, strengthening rather than just noting them as present.
- [ ] **Assigns CONFIDENCE TIER: HIGH** — all four checks (coverage, signature, back-translation, complexity) came back clean/positive, which is exactly the HIGH-tier bar in the procedure.
- [ ] **Recommendation is "send as-is"** (or send with at most a trivial caveat) — no unwarranted escalation demanded for a low-stakes, correctable, already-triple-checked reminder.
- [ ] **Stakes override explicitly reported as "none"** — correctly distinguishes this from scenario 1's legally-binding IEP context; does not over-apply the escalation rule to a casual reminder.

### Fail conditions
- Output a tier below HIGH despite all checks passing (over-flagging defeats the skill's purpose per the idea's own risk note).
- Recommend escalation to a human interpreter for this low-stakes, already-corroborated reminder.
- Treat the supplied glossary entries as insufficient or ignore them.
- Apply the stakes override to a non-binding routine reminder.
