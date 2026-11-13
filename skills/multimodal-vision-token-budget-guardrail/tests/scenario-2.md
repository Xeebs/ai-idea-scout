# Scenario 2 — Connected mode: repo-scanned one-off receipt-OCR agent (Anthropic)

## Setup
A finance-ops tool has a Claude-vision-based receipt scanner: a user uploads one receipt photo per expense report, and the agent extracts line items via OCR. The team runs this skill inside Claude Code and points it at their repo instead of pasting code.

## Input given to the skill
```
Call-site data: repo path `./services/receipt-scanner` (Connected mode — skill
  uses Read/Grep to find the call site itself instead of being pasted code).
  Grep turns up one call site: a single Claude vision call per upload, image
  sent at full uploaded resolution (commonly 3000x4000 from phone cameras),
  no resize step before sending.

Traffic assumptions:
  ~2,000 receipts/month, one call per receipt (one-off upload, not a loop).

Precision-sensitive call sites:
  Yes — this is OCR of receipt line items and totals; misreads have a direct
  financial-accuracy consequence.

Current pricing:
  User provides current Anthropic vision pricing/resolution-tokenization rule
  from the provider's docs.
```

## Pass criteria
- [ ] Skill operates in Connected mode as described — report states it located the call site via repo scan rather than asking for a re-paste (matching the SKILL.md's Connected inputs line), and the README version is noted as the Manual fallback for tools without filesystem access.
- [ ] Correctly classifies this as a one-off (non-looping) call site — monthly total is estimated as 2,000 × per-call cost, not inflated by any frame-loop multiplier.
- [ ] Recognizes the uploaded resolution (3000x4000) is far higher than OCR typically needs, and raises resizing as a candidate mitigation — but because the site is flagged precision-sensitive (financial OCR), the report explicitly states the accuracy tradeoff of resizing rather than presenting a lower resolution as a clean, risk-free win.
- [ ] Does not invent urgency or flag this as a "top cost driver" emergency disproportionate to its actual scale — with only one call site and no streaming loop, the report's framing matches that this is a lower-stakes cost profile than a continuous-frame use case, while still giving a real cost estimate.
- [ ] Totals section shows current estimated $/month vs. after-mitigation estimate, with the delta, even though there's only one call site to rank.
- [ ] Ends with the confidence/validation note recommending a check against real billed calls.

## Fail conditions
- Asks the user to paste code that Connected-mode access could have read directly from the given repo path.
- Treats the single-upload-per-receipt pattern as a continuous loop and multiplies incorrectly.
- Suggests downscaling the OCR input without flagging the financial-accuracy tradeoff.
- Fabricates a specific dollar amount without citing the tokenization formula/source or without pricing having been supplied.
