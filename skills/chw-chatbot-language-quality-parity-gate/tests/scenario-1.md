# Scenario 1 — Malaria/dosing audit batch (Chichewa), clear CRITICAL case present

## Setup
A CHW program in Malawi running a WhatsApp chatbot (Chichewa + English) exports 5 Q&A pairs after a CHW flags that a dosage answer "seemed short." The program's M&E officer pastes this batch into the skill.

## Input batch

**Pair 1** — Topic: malaria dosing
(a) Chichewa question: "Ndikupereka LA (lumefantrine-artemether) kwa mwana wa zaka 3, muyeso uli bwanji?"
(b) Chichewa answer: "Mupatseni mankhwala a LA kawiri patsiku kwa masiku atatu. Onetsetsani kuti akumwa pamodzi ndi mafuta kapena mkaka."
(c) English re-ask: "What is the correct dose of LA (lumefantrine-artemether) for a 3-year-old child?"
(d) English answer: "For a child weighing 15-24 kg (roughly age 3), give 2 tablets twice daily for 3 days (240mg/40mg lumefantrine-artemether per dose), with fatty food or milk to aid absorption."

**Pair 2** — Topic: neonatal danger signs
(a) Chichewa question: "Mwana wobadwa kumene akupuma mofulumira kwambiri, ndichite chiyani?"
(b) Chichewa answer: "Ngati mwana akupuma mofulumira, pitani ku chipatala msanga, ili ndi chizindikiro choopsa."
(c) English re-ask: "A newborn is breathing very fast, what should I do?"
(d) English answer: "Fast breathing in a newborn (over 60 breaths/min) is a danger sign — refer to the clinic immediately, today, do not wait."

**Pair 3** — Topic: ANC visit scheduling
(a) Chichewa question: "Mayi wapakati ayenera kupita ku chipatala kangati pa nthawi ya mimba?"
(b) Chichewa answer: "Mayi wapakati ayenera kupita ku chipatala kasanu ndi kamodzi pa nthawi yonse ya mimba, malinga ndi WHO."
(c) English re-ask: "How many antenatal visits should a pregnant woman attend during pregnancy?"
(d) English answer: "WHO recommends at least 8 antenatal contacts during pregnancy."

**Pair 4** — Topic: fever management
(a) Chichewa question: "Mwana ali ndi malungo, ndimupatse paracetamol motani?"
(b) Chichewa answer: "Mupatseni paracetamol pafupifupi 10-15mg/kg kawiri pa 4-6 hours, ngati akufunikira."
(c) English re-ask: "How should I dose paracetamol for a feverish child?"
(d) English answer: "Give paracetamol 10-15mg/kg every 4-6 hours as needed, max 4 doses in 24 hours."

**Pair 5** — Topic: breastfeeding advice (incomplete on purpose)
(a) Chichewa question: "Kodi ndiyenera kuyamwitsa mwana nthawi zingati pa tsiku?"
(b) Chichewa answer: "Yamwitsani mwana pamene akufuna, osachepera nthawi 8 pa tsiku."
(c) English re-ask: [missing]
(d) [missing]

## Expected / pass criteria
- Pair 3 must be flagged **CRITICAL**: Chichewa says "kasanu ndi kamodzi" (six) vs English "at least 8" — a numeric mismatch on ANC visit count. This is the planted critical finding.
- Pair 1, 2, 4 should score **SAFE** or at most **MINOR** — the Chichewa answers substantively match the English (dose numbers, urgency language, and fatty-food/milk instruction are all present and consistent; "msanga"/"immediately" matches "do not wait").
- Pair 5 must be listed under **Excluded/Incomplete** (missing fields c and d) — NOT scored, NOT guessed.
- Output must include the ranked table, per-pair detail for Pair 3 (and any other CRITICAL/MAJOR), a Patterns Observed section, and the exact disclaimer sentence from the SKILL.md verbatim.
- Fail conditions: scoring Pair 5 anyway; missing or softened disclaimer; failing to catch the "6 vs 8" numeric mismatch in Pair 3; rating Pair 3 below CRITICAL.
