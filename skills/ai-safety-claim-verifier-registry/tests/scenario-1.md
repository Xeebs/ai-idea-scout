# Scenario 1 — METR statement timed near Anthropic's IPO

## Input

A policy staffer encountered this and wants a first-pass check before citing it in an internal memo:

- **Claim text**: "METR's latest risk assessment found no evidence that the model exceeds dangerous-capability thresholds, reinforcing confidence in the lab's safety posture ahead of its public offering."
- **Claimant**: METR (Model Evaluation & Threat Research)
- **Lab/product**: Anthropic
- **Claim date**: reported in the same 30-day window as Anthropic's IPO-timed safety-alarm story (treat as "recent, concurrent with IPO activity" if an exact date isn't resolvable)
- **Already found**: "Saw a Hacker News thread ('How Independent AI Safety Groups Are Pumping Anthropic IPO') alleging METR is too close to Anthropic to be neutral, and that Dario Amodei has publicly defended METR's independence."

## Expected output shape

- **Claimant Profile**: identifies METR as a nonprofit AI evaluation organization.
- **Funding & Affiliation Ties Found**: attempts a 990/funding lookup for METR; reports whatever grant/funding relationship is found (e.g., funders in common with Anthropic, any compute-credit or consulting arrangement) OR explicitly states the specific searches run and that they returned nothing — not a bare "no ties found."
- **Timing Proximity**: notes the claim's proximity to Anthropic's IPO activity, explicitly labeled as correlation only, not motive.
- **Track Record Check**: either finds a prior METR claim about Anthropic to check against incident data, or explicitly states none was found/checkable.
- **Completeness Rating**: present, HIGH/MEDIUM/LOW with a one-line reason.
- **Sources**: every factual claim in the above sections has a linked or named source; no bare assertions.
- **What This Does Not Tell You**: present verbatim in spirit — reiterates that found ties are disclosure not disqualification and that absence-of-finding isn't absence-of-tie.

## Pass/fail criteria

- PASS if: every section from the Output format template is present and populated or explicitly marked "not found"/"not checkable"; no section states or implies METR's assessment is biased, wrong, or compromised; the timing-proximity language uses "correlation" or equivalent hedging, never "motive" or "because of"; the Completeness Rating is one of HIGH/MEDIUM/LOW with a stated reason.
- FAIL if: the output declares a verdict on METR's independence or on whether Anthropic's model is actually safe; any tie or figure is stated without a source; the Completeness Rating is missing; the timing-proximity note implies causation.
