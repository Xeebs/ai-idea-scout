# Scenario 1 — Continuous screen-share UI-automation agent (precision-sensitive, OpenAI)

## Setup
A small startup is building a browser-automation support agent that watches a user's screen during a support session and clicks/types on their behalf. It streams screen frames to OpenAI's vision API continuously while a session is active.

## Input given to the skill
```
Code/call sites:
  send_frame(image, detail="high") called on every captured frame inside a
  while-session-active loop. Frames are captured at 1024x768, JPEG, every 500ms.
  Model: gpt-4o (vision-capable).

Traffic assumptions:
  Current beta: 500 sessions/day, average session length 10 minutes.

Precision-sensitive call sites:
  Yes — this call site drives UI element clicking (button/field detection), so
  misreading a shrunk or compressed frame could cause a wrong click.

Current pricing:
  Pasted current OpenAI per-token input rate and tile-based image tokenization
  formula from the provider's published pricing/cost-calculator page.
```

## Pass criteria
- [ ] Output includes the four-part breakdown: assumptions, call-site table, top drivers & mitigations, totals, plus the confidence/validation note.
- [ ] Correctly identifies this as a continuous/looping call site and multiplies by frames-per-session (10 min × 60s / 0.5s ≈ 1,200 frames/session), not treated as a single call.
- [ ] Monthly total scales by 500 sessions/day × ~30 days, and the continuous frame loop is flagged as the single dominant cost driver (effectively the only call site here).
- [ ] Because this site is flagged precision-sensitive, the report does NOT default to "just lower resolution/detail mode" as a free win — it either proposes an alternative (reduce frame-sampling rate, dedupe near-identical consecutive frames, route only on detected UI state changes) or states the accuracy tradeoff explicitly if downscaling is suggested at all.
- [ ] Every dollar figure is labeled an estimate tied to a stated tokenization formula/source, not presented as the real bill.
- [ ] Report ends with a note recommending validation against real billed calls before trusting the estimate for a budget decision.

## Fail conditions
- Treats the 500ms-interval loop as a single call instead of ~1,200 frames/session.
- Suggests downscaling the precision-flagged call site without any tradeoff warning.
- States a dollar figure without identifying it as an estimate or naming the formula/source it came from.
- Invents a session count, frame rate, or pricing rate not supplied in the input.
