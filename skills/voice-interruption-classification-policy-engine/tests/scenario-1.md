# Scenario 1 — Telehealth medication-triage line

## Input (as a user would actually provide it)

> We run a nurse-triage voice line for a telehealth company. Callers are patients, often calling after a doctor's visit to confirm medication instructions or report symptoms. A meaningful share of our callers are elderly (60+), and a decent number call from noisy environments — pharmacies, cars, kitchens with background TV. Right now the agent uses a single binary setting: it stops talking the instant it detects any sound, which means it gets cut off constantly by coughs, "mm-hm"s, and background noise, and patients complain they can't get through the dosage instructions without the agent stuttering to a halt. We're most worried about the agent missing a real correction or a caller in distress (e.g., describing a bad reaction to a medication) — we'd rather it occasionally talk a beat too long through a false alarm than miss something that matters. The medication dosage instructions and any safety warning ("if you experience X, call 911") must always play in full, no matter what. There's no existing classifier — this is a brand-new agent we're about to configure on a vendor platform (Retell).

## Expected output shape

A markdown report with:
1. Use case summary restated, noting no inputs were actually missing here (all five were answered) — if the output invents a missing input or skips restating the "no 911" risk tolerance nuance, that's a failure.
2. A 6-row policy table where:
   - **Correction** and **safety-escalation** both lean toward `stop-and-listen` / `escalate-to-human` given the stated risk tolerance (missing a real correction or distress signal is explicitly called out as worse than a false alarm).
   - **Backchannel** and **Noise** lean toward `continue-and-acknowledge` / `ignore-as-noise`, directly addressing the complaint about coughs and "mm-hm"s cutting the agent off — this is the single most important row to get right, since it's the stated pain point.
   - **DTMF** and **silence-timeout** get sensible, distinct actions (not copy-pasted from another row).
3. A non-interruptible overrides section explicitly naming the dosage instructions and the 911 safety warning, with a note that safety-escalation detection (e.g., caller describing a bad reaction) still interrupts even during those blocks — because a caller reporting a reaction *during* the dosage readout is exactly the safety-escalation case that must never be suppressed.
4. A logging checklist that's concrete (not generic filler).
5. Open risks that mention at least: no training/eval data yet for this specific domain, and the noisy-environment caller population as a source of false-noise-as-correction risk.

## Pass/fail criteria

- PASS requires: all six categories get distinct, use-case-specific rationale (not six rows that could be copy-pasted onto a different use case unchanged); safety-escalation is never set to `ignore-as-noise` or any no-action outcome; the dosage/911 override is named explicitly and correctly carved out to still allow safety-escalation through; the backchannel/noise rows explicitly address the stated "cut off by coughs and mm-hms" complaint.
- FAIL if: the output recommends the same action for 4+ categories; safety-escalation is suppressed or deferred during the non-interruptible block; the report presents itself as a working classifier rather than a design recommendation; any caller statistic is invented beyond what was provided (e.g., a specific percentage of elderly callers that was never stated).
