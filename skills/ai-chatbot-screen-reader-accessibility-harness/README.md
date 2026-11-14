# Chatbot UI Screen-Reader Design Review

A paste-in prompt template for reviewing an AI chatbot/assistant web UI's screen-reader accessibility — before you have a live testing rig, and before you trust a vendor's self-reported compliance claim. Works in any chat-based AI tool: paste the prompt block below, then paste your UI description, markup, or vendor's answer underneath it.

## When to use this
Use this the moment you're building or reviewing an AI chatbot/assistant UI and need to know whether its specific interaction patterns — streamed responses, regenerate/stop buttons, "thinking" indicators, keyboard flow, code blocks in responses — will work for screen-reader users. General WCAG scanners don't check these chatbot-specific dynamic patterns well; this does. It's a static design review from a description or code snippet, not a live screen-reader test — use it early, often, and before committing engineering time to a full automated test harness (Playwright + a real screen-reader driver like NVDA or VoiceOver).

## What you need to provide
This is a **manual** skill — you paste in what you know, nothing is fetched automatically. Describe (in plain English, code, or both) as many of these five things as you can:

1. **Streaming announcement** — how new assistant text appears while it's streaming in: what DOM element, any ARIA attributes used, how often it updates.
2. **Regenerate/stop behavior** — what happens when the user clicks "regenerate" or "stop generating," especially where keyboard focus goes afterward.
3. **Thinking/loading indicator** — how the "assistant is thinking" state is shown (purely visual animation, or something a screen reader would also announce).
4. **Keyboard-only operability** — whether the input box, send button, and message history can all be reached and used without a mouse.
5. **Code blocks / tables in responses** — whether structured content inside a response is reachable and navigable by keyboard.

If you don't know one of these yet, say so — don't guess, and the review won't guess either.

## The prompt
Paste this, followed by your description/markup/claim:

```
You are reviewing an AI chatbot UI's screen-reader accessibility. I will describe (or paste code for) how its interaction patterns work. For each of the five areas below, do the following:

1. Extract exactly what I described — do not infer behavior I didn't mention.
2. Classify it as COMPLIANT, LIKELY BROKEN, or UNKNOWN (not enough info — state what's missing).
3. For LIKELY BROKEN or UNKNOWN, name the specific WCAG success criterion at risk (e.g. 4.1.3 Status Messages, 2.4.3 Focus Order, 4.1.2 Name Role Value, 2.1.1 Keyboard).
4. For every LIKELY BROKEN item, give the exact fix — specific ARIA attribute/role, or specific focus-management behavior, or specific markup change. No vague "improve ARIA labels" advice.

The five areas:
A. Streaming announcement — does new streamed-in text get announced to a screen reader sensibly (not token-spammed, not silent)?
B. Regenerate/stop focus handling — does keyboard focus land somewhere sensible after clicking regenerate/stop?
C. Thinking/loading indicator — is the "assistant is thinking" state exposed to assistive tech, not just shown visually?
D. Keyboard-only operability — can the input, send control, and message history all be used without a mouse?
E. Code blocks/tables in responses — are they reachable and navigable by keyboard, with an accessible name/context?

If what I'm pasting is a vendor's or team's self-reported "WCAG compliant" claim rather than a build description, do NOT take the claim at face value — apply the same five checks to what they actually described doing, and flag anything that sounds compliant but describes a known anti-pattern (for example: claiming compliance while describing aria-live="assertive" firing on every streamed token, which causes constant interruption even though a live-region attribute is technically present).

Known good patterns to check against:
- Streaming: a persistent, pre-rendered role="log" aria-live="polite" container; suppress per-token announcements, announce the committed message once (e.g. via aria-busy toggling), rather than firing aria-live on every token.
- Regenerate/stop: focus moves to the start of the new response (or back to input) — never left stranded on a now-hidden button.
- Thinking indicator: pair any visual animation with a visually-hidden aria-live="polite" text node announcing the state.
- Keyboard flow: every interactive control is in tab order or has tabindex="0" with a documented key handler; mouse-only history scrolling is only okay if an equivalent keyboard path (Page Up/Down, arrows) is documented.
- Code blocks/tables: tabindex="0" on scrollable containers, plus an accessible name/context so a screen-reader user knows what they tabbed into.

Output a markdown table with columns: Pattern Area | What Was Described | Verdict | WCAG Ref | Issue/Fix — one row per area (A–E). Follow it with a short "Prioritized fixes" numbered list (highest-impact first), and end with this exact caveat: "This is a static design review based on the description/code provided, not a verified screen-reader test transcript. Confirm with a live automated pass (e.g. Playwright + a real screen-reader driver such as NVDA/VoiceOver) or real assistive-tech users before relying on this as a compliance sign-off."

Here is what I'm reviewing:
<paste your UI description, markup, or vendor claim here>
```

## What you get back
A five-row scorecard (one row per pattern area) showing exactly what was described, a COMPLIANT/LIKELY BROKEN/UNKNOWN verdict, the specific WCAG criterion at risk, and — for anything broken or unclear — the exact fix or missing information needed. Followed by a short prioritized fix list and a caveat reminding you this is a design review, not a verified live screen-reader test.

## Guardrails
- This tool never claims to have run a real screen reader — it reviews a description, not a live capture. Always run a real automated or manual screen-reader pass before shipping or signing off on compliance.
- It won't guess at behavior you didn't describe — unmentioned areas come back UNKNOWN with a note on what's missing, not an assumed pass or fail.
- It won't accept "we're WCAG compliant" at face value from a vendor — it re-derives the verdict from what they actually described.
- Every "LIKELY BROKEN" fix is a specific, concrete change (an exact ARIA attribute, role, or focus call) — if you get back a vague "add more labels" answer, push back and ask for the specific fix.
