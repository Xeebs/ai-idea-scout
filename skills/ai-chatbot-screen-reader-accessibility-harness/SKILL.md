---
name: ai-chatbot-screen-reader-accessibility-harness
description: Reviews a described (or pasted-code) chat/assistant UI interaction pattern — streaming responses, regenerate/stop buttons, "thinking" indicators, keyboard flow, code blocks — against the five known screen-reader failure modes specific to AI chatbot UIs, and drafts the exact ARIA/focus-management fix for each gap. Use when someone is building or reviewing a chatbot UI's accessibility before (or instead of) running a live screen-reader test harness.
---

# Chatbot UI Screen-Reader Design Review

## When to use this
Reach for this skill the moment someone is building, reviewing, or procuring an AI chatbot/assistant web UI and asks something like "is our chat interface accessible?", "will a screen reader handle our streaming responses okay?", "review this vendor's accessibility questionnaire answer", or "what ARIA do I need for a regenerate button?" — before a full live screen-reader test rig (Playwright + a real screen-reader driver) exists or has been run. This is a static design/code review, not a live test: it catches foreseeable breakage from a description or snippet, fast, with no browser or screen reader required.

## Inputs
**Data source**: Manual — the user pastes a plain-English description of the UI behavior, relevant HTML/JSX/ARIA markup, or a vendor's written accessibility claim/questionnaire answer. Nothing is fetched or driven automatically. (Note: this repo's companion idea also describes a Connected automated harness — Playwright driving the live UI paired with Guidepup driving a real screen reader like NVDA/VoiceOver — but that is the separate full-automation *Project* half of this idea, not this skill. This skill is deliberately the manual, no-setup design-review companion, usable long before anyone stands up that harness, exactly as scoped in the idea's Skill Angle.)

What to hand over, as much as is known:
1. How new assistant text appears on screen while streaming (what DOM element, any ARIA attributes, how often it updates).
2. How "regenerate" / "stop generating" behaves, including what happens to keyboard focus afterward.
3. How the "thinking" / "typing" / loading state is shown (visual-only animation? text? ARIA-live region?).
4. Whether the input box, send control, and message history can be reached and operated by keyboard alone.
5. How code blocks, tables, or other structured content inside responses are rendered and whether they're reachable/navigable by keyboard.

If one of these isn't described, say so — don't guess.

## Procedure
1. Parse the input into the five pattern areas above. For each area, extract exactly what was stated; do not infer behavior that wasn't described.
2. For each area, classify a verdict:
   - **COMPLIANT** — the described implementation matches a known-good pattern for that area.
   - **LIKELY BROKEN** — the description matches a known chatbot-UI failure mode (e.g., a live region with no attribute, token-by-token `aria-live="assertive"` spam, no focus management after regenerate, a purely visual loading animation, keyboard-untestable message history, unlabeled or non-focusable code blocks).
   - **UNKNOWN** — not enough information was given to judge; state exactly what's missing.
3. Map every LIKELY BROKEN or UNKNOWN verdict to the specific WCAG success criterion it threatens (e.g., 4.1.3 Status Messages for live-region issues, 2.4.3 Focus Order / 2.4.11 Focus Not Obscured for regenerate-focus issues, 4.1.2 Name Role Value for unlabeled loading states, 2.1.1 Keyboard for history/code-block navigation).
4. For every LIKELY BROKEN item, draft the concrete fix: the exact ARIA attribute(s)/role, or the focus-management call, or the markup change — not a vague "add ARIA labels" suggestion. Known good patterns to draw on:
   - Streaming text: keep a persistent, pre-rendered `role="log" aria-live="polite" aria-relevant="additions"` container; suppress interim per-token announcements and announce the committed message once streaming ends (e.g., `aria-busy="true"` during streaming, flipped to `false` on completion), rather than firing `aria-live` on every token.
   - Regenerate/stop: on click, programmatically move focus to the start of the new/regenerated response container (or back to the input if no new content yet), never leave focus on a now-hidden button.
   - Thinking indicator: pair any visual animation with a visually-hidden text node (e.g., `<span class="sr-only" aria-live="polite">Assistant is thinking…</span>`) so a screen reader announces the state change, not silence.
   - Keyboard flow: every interactive control (send, stop, regenerate, individual messages if they carry actions like copy/edit) must be in the natural tab order or explicitly given `tabindex="0"` with a documented key handler; pure mouse-only history scrolling is acceptable only if an equivalent Page Up/Down or arrow-key path is documented.
   - Code blocks/tables: ensure the rendered element is reachable by keyboard (`tabindex="0"` on scrollable `<pre>`/table wrappers) and has an accessible name or surrounding context (e.g., "Python code block" landmark) so a screen reader user knows what they've tabbed into.
5. If the input is a vendor's self-reported compliance claim rather than a build-in-progress description, do not accept the claim at face value — apply the same five-area check to what they actually described doing, and flag any claim that sounds compliant but describes a known anti-pattern (e.g., claiming WCAG AA while describing `aria-live="assertive"` firing on every streamed token).
6. Compile the scorecard and action list (see Output format). End with an explicit note that this is a predicted, static review, not verified screen-reader output, and recommend running an automated live harness (Playwright + a real screen-reader driver) for empirical confirmation before shipping or signing off.

## Output format
```
# Chatbot UI Accessibility Design Review

| Pattern Area | What Was Described | Verdict | WCAG Ref | Issue / Fix |
|---|---|---|---|---|
| Streaming announcement | ... | COMPLIANT / LIKELY BROKEN / UNKNOWN | ... | ... |
| Regenerate/stop focus | ... | ... | ... | ... |
| Thinking indicator | ... | ... | ... | ... |
| Keyboard-only operability | ... | ... | ... | ... |
| Code block / structured content navigability | ... | ... | ... | ... |

## Prioritized fixes
1. <highest-impact fix, with exact markup/attribute change>
2. ...

## Caveat
This is a static design review based on the description/code provided, not a verified screen-reader test transcript. Confirm with a live automated pass (e.g., Playwright + Guidepup driving NVDA/VoiceOver) or real assistive-tech users before relying on this as a compliance sign-off.
```

## Guardrails
- Never state or imply that an actual screen reader was run or that output was "captured" — every verdict is a prediction from the description given, and the output must say so.
- Never mark an area COMPLIANT or LIKELY BROKEN when the input didn't describe it — use UNKNOWN and name exactly what's missing instead of assuming the best or worst case.
- Never accept a vendor's or team's self-declared "WCAG compliant" / "accessible" claim without independently re-checking the five pattern areas against what they actually described — self-certification is exactly the gap this skill exists to catch.
- Never give a generic "improve ARIA labels" fix — every LIKELY BROKEN verdict needs the specific attribute, role, or focus-management behavior to add or change.
- Never present this review as a substitute for testing with real screen-reader users or for the live automated harness; always include the caveat.
