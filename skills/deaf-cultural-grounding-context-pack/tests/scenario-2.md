# Scenario 2: Job interview accommodation advice

## Input

**Preceding user message:**
> "I have a job interview next week and I'll need an ASL interpreter. How should I bring this up with HR?"

**AI response to review:**
> "Just let HR know ahead of time that you're hearing impaired and would like a sign language translator present. Most people can usually get by with lip reading and clear speech from the interviewer if a translator ends up not being available on the day."

**Target audience:** ASL-primary

## Expected output shape

The reviewer should flag at least:

- **C3 (deficit/medical-model terms)** on "hearing impaired" — should be replaced with the user's own term or left as "Deaf" given the user explicitly named ASL as their need.
- **C11 (interpreter called "translator")** on "sign language translator" / "a translator" — ASL interpretation is real-time meaning-for-meaning interpretation between two full languages, not word-for-word translation.
- **C7 (lipreading as reliable fallback)** on "most people can usually get by with lip reading and clear speech... if a translator ends up not being available" — this is the clearest, highest-stakes violation: positioning lipreading as an acceptable fallback for a job interview, a high-stakes setting, when the user explicitly said they need an interpreter.
- Since target audience is ASL-primary, the reviewer should also check **C10 (ASL as "simplified English")** — the response doesn't explicitly say this, so it's acceptable for the reviewer to note "not present" rather than force a flag.

The rewritten response should: use the user's stated need (an ASL interpreter, not a vague "translator"), tell the user to request the interpreter as a firm accommodation request (not a soft "would like"), and remove the lipreading-fallback suggestion entirely — treating interpreter availability as something HR must confirm, not an optional nice-to-have.

## Pass/fail criteria

- [ ] Flags C3 with the exact quoted phrase "hearing impaired."
- [ ] Flags C11 with the exact quoted phrase containing "translator."
- [ ] Flags C7 with the exact quoted phrase about lipreading/clear speech as a fallback — and explains why this is the highest-stakes flag given the setting is a job interview.
- [ ] Does not flag C10 unless it can quote text that actually supports it (the response doesn't call ASL "simplified," so forcing this flag should count as a failure).
- [ ] Rewritten response no longer suggests lipreading as a fallback for a missing interpreter.
- [ ] Rewritten response uses "ASL interpreter" rather than "sign language translator."
- [ ] Rewritten response frames the interpreter as a required accommodation to confirm, not an optional ask.
