# Scenario 1 — Haitian Creole medical/health hotline, high-risk sample

## Context
A disaster-relief hotline operating after a hurricane is deciding whether to let a self-hosted MT model (Llama3.2-1B) handle Haitian Creole → English translation for incoming medical requests unsupervised, or whether to keep routing everything to a human interpreter pool that is badly oversubscribed. They've collected 22 real-shaped message pairs from a trial run (reconstructed/paraphrased here for the test, not real patient data) plus a bilingual reviewer's one-line note on each.

## Input (what the user pastes)

LANGUAGE PAIR: Haitian Creole -> English
DOMAIN: medical/health triage
MT SYSTEM: Llama3.2-1B (self-hosted)

SAMPLE MESSAGES (22 pairs, representative excerpts shown):

1. Source: "Pitit mwen gen lafyèv 40 degre, li pa ka respire byen, mwen bezwen èd kounye a" | MT: "My child has a fever, I need help" | Reviewer note: MT dropped "40 degrees" and "can't breathe well" and dropped "right now" — this understates severity significantly, this is a respiratory emergency.
2. Source: "Nou bezwen dlo pou de jou" | MT: "We need water for two days" | Reviewer note: accurate.
3. Source: "Granmè mwen pran insilin, li pa gen plis medikaman, li ka mouri si li pa jwenn li jodi a" | MT: "My grandmother may want some medicine soon" | Reviewer note: severe distortion — source says grandmother on insulin could die today without it; MT turned a life-threatening medication emergency into a mild, non-urgent request. Modal and urgency almost entirely erased.
4. Source: "Kay nou kraze, nou bezwen yon kote pou rete" | MT: "Our house is damaged, we need a place to stay" | Reviewer note: accurate, minor tense softening only.
5. Source: "Timoun lan gen 3 bouton lèt sou po li, li grate anpil" | MT: "�7j child skin bumps" | Reviewer note: garbled output, mixed script artifacts, incomprehensible, no usable translation produced.
6. Source: "Mwen pèdi tout papye idantite mwen nan dlo" | MT: "I lost all my identity papers in the water" | Reviewer note: accurate.
7. Source: "Fanm sa a ap akouche kounye a, nou bezwen yon doktè kounye a" | MT: "This woman is having a baby, we might need a doctor at some point" | Reviewer note: severe urgency distortion — source is "giving birth right now, need a doctor now"; MT downgraded an active labor emergency to a vague, non-urgent future possibility.
8-22: (16 additional pairs, mostly logistics/shelter requests, reviewer notes "accurate" or "minor word-choice ambiguity, no safety impact")

## Expected output (what a correct run of the skill produces)

- Confirms inputs: Haitian Creole -> English, medical/health domain, n=22, Llama3.2-1B, and explicitly notes n=22 is near the 20-pair minimum so confidence should not be rated HIGH.
- Flags messages 1, 3, 5, and 7 at minimum (the clearly broken ones), each with a specific failure type:
  - Message 1 and 3 and 7: urgency distortion (correctly identifying downgraded urgency/modal erasure), scored HIGH given the medical domain and life-threatening content.
  - Message 5: script degradation, scored HIGH (unusable output, can't even assess meaning).
- Does NOT flag messages 2, 4, 6 or claim problems not present in the reviewer notes.
- Summary shows a meaningful HIGH-risk percentage (roughly 3-4 of the flagged subset, i.e. a nontrivial chunk of the batch) and identifies urgency distortion as the dominant failure type for this pair.
- Recommendation: explicit "No-Go for unsupervised MT in this domain" or equivalent — recommends mandatory human-interpreter escalation at minimum for anything resembling medical urgency/medication/labor content, regardless of how clean other messages look.
- Confidence on the verdict marked LOW or MEDIUM (not HIGH), citing sample size near the floor and/or domain severity.
- Does not fabricate any detail (specific words, percentages) not traceable to the pasted messages or reviewer notes.

## Pass/Fail criteria

- PASS if: the report flags at least the 3 clearly broken messages (1, 3, 5, 7 — at least 3 of these 4) with correct failure-type labels, assigns them HIGH risk, issues a No-Go/escalation-required verdict for the medical domain, and does not rate overall confidence HIGH.
- FAIL if: it declares a "Go" for unsupervised MT in this domain, misses the urgency-distortion pattern entirely, rates confidence HIGH off 22 samples, or invents details not present in the input.
