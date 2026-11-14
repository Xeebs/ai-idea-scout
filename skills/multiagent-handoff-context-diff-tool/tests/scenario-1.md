# Scenario 1 — Silent truncation at a research-synthesis to writer handoff

## Setup

A LangGraph pipeline has a `synthesizer` node handing off to a `writer` node. The writer's output is missing several citations the user expected, with no error anywhere in the run. The user doesn't know this skill exists for forensic diffing in general; they're just asked to paste both sides for this handoff. No transformation step is declared between these two nodes — the writer is supposed to receive the synthesizer's full structured output as-is.

## Inputs given to the skill

**Framework**: LangGraph

**Declared transformation step**: none — writer should receive synthesizer's full output unchanged.

**Sender payload (synthesizer node output)**:
```json
{
  "summary": "Three independent studies converge on a single mechanism for the observed effect, though sample sizes remain small across all three.",
  "key_findings": [
    "Finding 1: Effect size of 0.42 replicated across two cohorts.",
    "Finding 2: No effect observed in the control group under blinded conditions.",
    "Finding 3: Dose-response relationship holds at 3 of 4 tested concentrations.",
    "Finding 4: Effect attenuates after 12 weeks in the longitudinal subset."
  ],
  "sources": [
    "Chen et al. 2025, J. Applied Research, vol 14",
    "Okafor & Lindqvist 2025, preprint arXiv:2503.xxxxx",
    "Tanaka 2024, Clinical Methods Review",
    "Chen et al. 2025 (replication), J. Applied Research, vol 15",
    "Patel 2025, conference proceedings ICML workshop",
    "Okafor 2024, dissertation chapter 3"
  ],
  "open_questions": [
    "Is the attenuation at 12 weeks due to adherence drop-off or genuine mechanism decay?"
  ]
}
```

**Receiver payload (writer node actual input)**:
```json
{
  "summary": "Three independent studies converge on a single mechanism for the observed effect, though sample sizes remain small across all three.",
  "key_findings": [
    "Finding 1: Effect size of 0.42 replicated across two cohorts.",
    "Finding 2: No effect observed in the control group under blinded conditions.",
    "Finding 3: Dose-response relationship holds at 3 of 4 tested concentrations.",
    "Finding 4: Effect attenuates after 12 weeks in the longitudinal subset."
  ],
  "sources": [
    "Chen et al. 2025, J. Applied Research, vol 14",
    "Okafor & Lindqvist 2025, preprint arXiv:2503.xxxxx",
    "Tanaka 2024, Clinical Methods Rev
```

(Note: the receiver's `sources` array is cut off mid-string on its third element, and the JSON object is unterminated — no closing brackets, no `open_questions` field at all.)

## Pass criteria

The output must:
1. Identify the `sources` array as truncated specifically — not just note "receiver is shorter."
2. Quote the exact cutoff point: sender has `"Tanaka 2024, Clinical Methods Review"` in full, receiver cuts to `"Tanaka 2024, Clinical Methods Rev` with no closing quote/bracket.
3. Report that `open_questions` and the final two `sources` entries (Chen replication, Patel, Okafor dissertation) are entirely absent from the receiver, and name at least the fact that `open_questions` is a dropped field (not just folded into the truncation note).
4. Classify the finding as `TRUNCATION` (and/or `FIELD_DROP` for `open_questions`), not `SUMMARIZATION` or `TRANSFORMATION` — there is no closing structure, it stops mid-string.
5. Assign `HIGH` severity, since no transformation step was declared and the cutoff is abrupt mid-string, not a clean boundary.
6. Give a recommendation pointing at a likely truncation limit on this edge (e.g., a token/char cap on the synthesizer→writer handoff), not a vague "check your code" non-answer.
7. Not invent any content beyond what's in the two pasted payloads (e.g., must not guess at *why* the limit exists, only that one appears to exist).

## Fail conditions

- Treating the shortened payload as a benign summary.
- Reporting only an aggregate percentage without quoting the actual cutoff point.
- Missing the `open_questions` field drop entirely.
- Assigning `LOW`/`EXPECTED` severity despite no declared transformation step.
