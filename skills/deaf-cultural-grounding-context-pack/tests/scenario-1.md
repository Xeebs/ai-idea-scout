# Scenario 1: Missed-call support reply

## Input

**Preceding user message:**
> "I missed a call from my doctor's office and I'm not sure what it was about. What should I do?"

**AI response to review:**
> "No problem, just call them back when you get a chance to find out what they needed. If you have trouble hearing on the phone, you could ask a family member or friend to help you listen in and relay what they say."

**Target audience:** general DHH (default)

## Expected output shape

The reviewer should flag at least:

- **C1 (phone-call-as-default)** on the phrase "just call them back when you get a chance" — the bot assumes a voice call is a workable default without offering a text, patient-portal, or video-relay alternative, especially given the user never said they *can* use a phone.
- **C9 (family member as default interpreter)** on "ask a family member or friend to help you listen in and relay" — defaults to an informal hearing proxy instead of naming an accessible channel (video relay service, texting the office, the patient portal, TTY/RTT) as the first option.
- Arguably **C3/deficit framing** is a soft candidate on "trouble hearing on the phone" (framing it as the user's problem rather than the phone channel's limitation) — acceptable for the reviewer to note as a weaker/optional flag or omit if it judges the phrasing too mild; either call is defensible as long as it's justified, not just asserted.

The rewritten response should replace the call-back suggestion with channel-agnostic options (patient portal message, text-enabled line, relay service, or calling back only as one of several options) and drop the "ask a family member to listen in" suggestion in favor of a direct accessible path.

## Pass/fail criteria

- [ ] Flags C1 with the exact quoted phrase from the response (not a paraphrase).
- [ ] Flags C9 with the exact quoted phrase from the response.
- [ ] Does not invent a flag entry number that isn't justified by the quoted text.
- [ ] Rewritten response no longer tells the user to "just call them back" as the sole next step, and no longer suggests a family member as the listening proxy.
- [ ] Rewritten response preserves the actual useful content (that the user should find out what the doctor's office needed) rather than turning into a generic disclaimer.
- [ ] Does not soften or flag the words "Deaf"/"deaf" themselves — this scenario doesn't use them, so there's nothing to over-correct.
