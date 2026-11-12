# Barge Triage Policy Reviewer

Paste this whole document into any AI chat tool (Claude, ChatGPT, Gemini, etc.), then answer the five questions at the bottom with your own voice-agent use case. No installation, API key, or prior context about any other project is required — this is fully self-contained.

## What this is for

Most voice AI agents today handle interruptions with one binary switch: either the agent stops talking the instant it detects *any* sound from the caller, or it never stops until it's done. Both are wrong most of the time. A caller saying "mm-hm, go on" is not the same event as a caller saying "no, I meant Tuesday," a cough, a keypad press, dead silence, or someone saying "I need to talk to a person right now." Treating all five the same way causes two different failure modes: the agent cuts itself off mid-sentence constantly (annoying, erodes trust), or it talks over a real correction or a caller in distress (worse — can cause real harm in high-stakes settings like telehealth or crisis lines).

This prompt produces a differentiated policy — one recommended action per interruption category, tailored to your specific use case — instead of a single blanket setting. It does not build or train anything; it is a design document to hand to whoever is configuring your voice platform or building your classifier.

## What you need to provide

Answer these five questions about your own use case. If you don't know the answer to one, say "unknown" — don't guess, and the output will flag it as an assumption rather than silently filling it in.

1. **Domain/use case** — What is this voice agent for? (e.g., telehealth triage line, insurance intake, debt collections, outbound sales, crisis/non-emergency support, IVR for a utility company)
2. **Caller population** — Anything notable about who calls? (e.g., skews older, many non-native speakers, often calling from noisy environments like cars or call-center floors, often distressed)
3. **Risk tolerance** — Which is worse for your use case: the agent cutting itself off on a false alarm (over-sensitive), or the agent talking over a real correction or a caller in distress (under-sensitive)?
4. **Non-interruptible content** — Are there specific things the agent says that must play in full no matter what? (e.g., legal disclaimers, payment/consent confirmations, medication dosage instructions, required opt-out notices)
5. **Current behavior** (optional) — What does the agent do today, if anything already exists?

## What the AI should do with your answers

Instruct the AI tool to follow this procedure exactly:

1. Restate the use case in 1-2 sentences, and explicitly list which of the five inputs above were missing, noting the assumption made for each instead of silently guessing.
2. For each of these six interruption categories, pick exactly one recommended action from this list: `stop-and-listen`, `continue-and-acknowledge`, `ignore-as-noise`, `route-to-DTMF-handler`, `treat-as-timeout`, `escalate-to-human`:
   - **Correction** — caller actively contradicts or changes what was just said ("no, I meant Tuesday")
   - **Backchannel** — caller signals they're listening ("mm-hm", "okay", "right")
   - **Noise** — non-speech audio: cough, background TV, line static
   - **DTMF** — keypad tone during a menu or form-fill step
   - **Silence-timeout** — caller has gone quiet past an expected response window
   - **Safety-escalation** — caller expresses distress, a medical/crisis signal, or explicitly asks for a human
3. Weight each recommendation in this priority order: (a) does this moment fall inside a non-interruptible content block? If so, override to DTMF-only/non-interruptible for every category except safety-escalation, which always escalates even mid-disclaimer. (b) the stated risk tolerance. (c) caller population notes — e.g., noisy environments should bias noise-handling toward `ignore-as-noise` with a confidence floor rather than stopping on every cough.
4. Apply this guardrail no matter what: safety-escalation never maps to `ignore-as-noise` or any no-action outcome. It always escalates, biased toward over-triggering rather than under-triggering — a false escalation costs a few seconds, a missed one leaves a distressed caller unheard. If the stated risk tolerance conflicts with this (e.g., "never stop, even for distress"), the output must flag that conflict instead of silently complying.
5. Write a one-line, use-case-specific rationale for each of the six rows — if the same justification would apply to any team regardless of their answers, it's too generic and should be rewritten.
6. If the reasoning ends up recommending the same action for all six categories, stop and reconsider — a uniform answer across all categories just recreates the binary-toggle problem this exercise exists to avoid.
7. Add a logging/QA checklist: concrete fields to capture per interruption event for later retraining or audit (timestamp offset into the agent's utterance, which content block was playing, detected category, action taken, caller's next utterance, call outcome — escalated/completed/hung up).
8. List 2-4 open risks specific to this use case (e.g., no distress-keyword list defined yet for this domain, or no non-English callers considered).

## Output format

Produce a single markdown report, in this exact order:

1. **Use case summary** — restated use case plus flagged missing inputs/assumptions.
2. **Policy table** — six rows, columns: Category | Example trigger | Recommended action | Rationale.
3. **Non-interruptible overrides** — bullet list of content blocks that override the table, and what applies during them.
4. **Logging checklist** — bullet list of fields to capture per interruption event.
5. **Open risks** — 2-4 bullets.

## Hard rules the AI must follow

- Safety-escalation is never ignored or deferred — always `escalate-to-human`, biased toward over-triggering. This is non-negotiable, even if your stated risk tolerance points the other way (the output will flag that conflict instead).
- The output is a design recommendation, not working code or a trained model — it must say explicitly that it needs validation against real call recordings before going live.
- No invented statistics. If you said "unknown" for caller population, the output should say "unknown," not fill in a plausible-sounding guess.
- Legal, compliance, consent, or safety-instruction content defaults to non-interruptible or DTMF-only unless you explicitly say otherwise.
- If every category ends up with the same recommended action, that's a sign the analysis didn't actually differentiate — it should be redone with more specific reasoning per category.
