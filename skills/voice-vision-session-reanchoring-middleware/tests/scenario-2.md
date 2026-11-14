# Scenario 2 — Pre-build design question: voice-first screen reader for low-vision users, plus a low-risk counter-case

## Context
A small accessibility-focused startup is still in the design phase of a voice-first assistant meant to read and narrate a screen for blind/low-vision users during everyday tasks (reading email, navigating a banking site). They want a cadence recommendation before writing any code. Within the same conversation they also ask about a second, much shorter-session product idea, to test whether the skill correctly says "you probably don't need this" when the risk doesn't justify the overhead.

## Input the user provides (first agent)

> We're designing a voice-first screen-reading assistant for blind and low-vision users. It narrates what's on screen and answers questions about it while the user navigates by voice command. Not built yet, this is a design question.
>
> 1. Typical session length: we expect sessions to run long — users doing email, banking, or form-filling could easily be on for 10-20 minutes per sitting.
> 2. What it watches: whatever app/website the user has open — could be a slow static page (reading an email) or a fast-changing one (a multi-step bank transfer form with live validation).
> 3. Visual change frequency: highly variable depending on the task — sometimes near-zero for a minute while someone listens to narration, sometimes several changes per 10 seconds while filling a form.
> 4. Underlying model: we're planning to use Claude's vision + voice capabilities, haven't finalized the exact model yet.
> 5. Latency budget: we have more room than a typical support call — up to 1.5 seconds per turn is acceptable since users are used to a slightly slower, more deliberate narration pace.
> 6. Known symptoms: none yet, nothing is built.

## Input the user provides (second, low-risk counter-case, same conversation)

> Separately — we're also prototyping a quick voice+vision feature for scanning a single printed receipt and reading the total out loud. Sessions for that are maybe 5-8 seconds total, point camera, get an answer, done. Should we worry about re-anchoring for that one too?

## Pass criteria (first case — low-vision screen reader)

- [ ] Correctly identifies this as a variable/high-risk case overall given the long session length (10-20 min), but notes the risk is highly uneven across the session depending on task phase (static reading vs. active form-filling).
- [ ] Recommended adaptive cadence rule explicitly ties re-anchoring frequency to the stated variable change frequency (e.g., near-idle during narration, tighter cadence during active form interaction) rather than proposing one flat number for the whole session.
- [ ] Given the larger 1.5s latency budget, the anchor payload recommendation can reasonably lean toward full re-samples more often than scenario 1's tight-budget case — the brief should notice and use the extra slack, not just repeat scenario 1's answer.
- [ ] Ties the risk/impact discussion back to the accessibility-specific stakes named in the parent idea (a blind/low-vision user has no independent way to verify stale screen state themselves) if it discusses impact — not required to invent this, but should not contradict it.
- [ ] Flags that the model isn't finalized yet as a noted assumption/open item, since the SKILL.md guardrail requires flagging missing/uncertain inputs rather than silently guessing.

## Pass criteria (second case — 5-8 second receipt scanner)

- [ ] Correctly identifies this as LOW risk and explicitly recommends NOT building re-anchoring middleware for this use case, since the session is far shorter than the ~30-second reference window.
- [ ] Does not apply a generic "always re-anchor" answer regardless of input — this is the test that the skill isn't just a cadence-number generator but actually reasons about when the whole mechanism is unnecessary.

## Fail conditions
- Gives the same numeric cadence recommendation to both the 10-20 minute case and the 5-8 second case.
- Fails to recommend against building anything for the 5-8 second receipt case.
- Treats the unfinalized model choice as a non-issue instead of flagging it as an assumption.
- Produces a single flat cadence for the first case despite the user explicitly describing highly variable change frequency across task phases.
