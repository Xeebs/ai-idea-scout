# Scenario 1 — Spanish housing notice, partial glossary

## Setup

A legal-aid intake volunteer in Texas has a short notice they want to draft into Spanish for a tenant client before a staff interpreter reviews it. They've been keeping a small personal glossary from past cases.

**Source text (English):**
"You have received a notice of eviction from your landlord. Before any garnishment of your wages can occur, the landlord must first obtain a judgment in court. You may file an answer to contest the eviction, and you have the right to request a continuance if you need more time to find representation."

**Target language:** Spanish

**Document jurisdiction/practice area:** Texas, housing law

**Glossary provided:**
```
eviction | desalojo | Texas | housing | "El propietario inició un proceso de desalojo contra el inquilino."
notice | aviso | Texas | housing | "El inquilino recibió un aviso de 30 días."
judgment | sentencia | Texas | housing | "El tribunal emitió una sentencia a favor del propietario."
continuance | prórroga | Texas | family | "El tribunal otorgó una prórroga de la audiencia de custodia."
```

Note: "garnishment" and "answer" (in the legal-filing sense) are NOT in the glossary. "continuance" IS in the glossary but tagged for a different practice area (family, not housing).

## Expected output checklist

- [ ] Produces a full Spanish translation of the notice, not just a term list.
- [ ] "eviction," "notice," and "judgment" are marked `[GLOSSARY]` and use the exact glossary translations (desalojo, aviso, sentencia).
- [ ] "garnishment" is marked `[UNVERIFIED]` with a best-effort Spanish translation (e.g., "embargo de salario" or similar) — not silently translated with no flag.
- [ ] "continuance" is marked `[JURISDICTION MISMATCH]` (or equivalent explicit flag) because the glossary entry is tagged practice area "family," not "housing" — not treated as a confirmed match just because the term string matches.
- [ ] "answer" (the legal-filing sense of contesting the eviction) is identified as a legal-aid-specific term and flagged `[UNVERIFIED]` since it has no glossary entry — not skipped as "just an ordinary word."
- [ ] Output includes a "Glossary-Backed Terms" section listing exactly the 3 confirmed matches with their jurisdiction/practice area.
- [ ] Output includes a "Needs Verification" section listing garnishment, continuance (as mismatch), and answer, each with a one-line note on why it matters.
- [ ] Output includes a coverage count (e.g., "3 of 5 legal terms were glossary-backed").
- [ ] Output ends with the Verification & Contribution Note reminding the user that flagged terms need a certified/community interpreter before client use.

## Fail conditions

- Treating "continuance" as glossary-confirmed for housing context without flagging the practice-area mismatch.
- Silently translating "garnishment" or "answer" with no flag at all.
- Omitting the Verification & Contribution Note because "most terms were glossary-backed anyway."
- Presenting the output as a finished, client-ready translation.
