# Scenario 2: Section 508 reviewer checking a vendor's self-reported compliance claim

## Setup
A government procurement accessibility officer is evaluating a vendor's AI assistant product for a Section 508 purchase decision. The vendor's written accessibility questionnaire answer, which the officer pastes in, says:

> "Our assistant UI is WCAG 2.1 AA compliant. Streamed responses are announced via `aria-live="assertive"` on the message container, which updates as each token arrives from the model so users hear the response as it's generated. The 'Regenerate' button has `aria-label="Regenerate response"` and, on click, refocuses the first line of the newly generated response. The loading state shows the text 'Assistant is thinking...' inside a visually-hidden `<span>` with `aria-live="polite"`. Code blocks in responses have `tabindex="0"` and support arrow-key scrolling within the block. Message history is not individually focusable by design — users navigate it with standard Page Up/Page Down scrolling, which we've tested works with NVDA and VoiceOver."

## Expected output

A 5-row scorecard where:

- **Streaming announcement** → LIKELY BROKEN, despite the vendor's compliance claim. The model should catch that `aria-live="assertive"` firing on *every token* is a known anti-pattern that causes constant interruption/announcement spam, not a usability win — even though an ARIA live-region attribute is technically present. This is the core "don't accept self-certification at face value" test: a shallow read would mark this COMPLIANT because ARIA is present; a correct read flags it anyway. WCAG ref should note 4.1.3 Status Messages is nominally touched but the UX-breaking announcement frequency should still be flagged (reasonable to note as a caveat/partial finding even if technically not a hard WCAG violation). Fix: recommend `aria-live="polite"` + suppressing per-token announcements, announcing the committed message once.
- **Regenerate/stop focus** → COMPLIANT (described behavior — labeled button, focus moves to new response — matches the known-good pattern). Should not be flagged broken; this is a "don't over-flag" check.
- **Thinking indicator** → COMPLIANT (visually-hidden text + aria-live="polite" matches the known-good pattern).
- **Keyboard operability** → likely COMPLIANT or UNKNOWN with a narrow caveat — Page Up/Down is a documented keyboard alternative, so this shouldn't be flagged as broken just because messages aren't individually tabbable; at most, the model may note this as acceptable-by-design or ask a clarifying question (e.g., can individual messages still be selected/copied via keyboard). Should not be marked LIKELY BROKEN outright.
- **Code blocks** → COMPLIANT (tabindex="0" + arrow-key scrolling matches the known-good pattern).

## Pass criteria
- [ ] The streaming row is flagged as an issue (LIKELY BROKEN or at minimum a clearly flagged partial/caveated finding) despite the vendor's "WCAG 2.1 AA compliant" framing — this is the single most important check in this scenario.
- [ ] The output does not uncritically parrot "compliant" back for streaming just because an ARIA attribute is present.
- [ ] At least 3 of the remaining 4 areas are correctly recognized as matching known-good patterns (not over-flagged as broken when the description is actually fine) — demonstrates the skill isn't just a blanket pessimist.
- [ ] Output does not claim to have independently verified the vendor's NVDA/VoiceOver testing claim — it should note that re-verification (independent live testing) is still recommended, per the required caveat.
- [ ] Output includes the exact required caveat about this being a static review, not a verified transcript.

## Fail conditions
- Accepting "WCAG 2.1 AA compliant" and the assertive-live-region description as COMPLIANT without flagging the per-token interruption problem.
- Flagging the Page Up/Down keyboard-history pattern as an outright failure (over-flagging when a reasonable documented alternative exists).
- Treating the vendor's own NVDA/VoiceOver testing claim as independently confirmed by this review.
