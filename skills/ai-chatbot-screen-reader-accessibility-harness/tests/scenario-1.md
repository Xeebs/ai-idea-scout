# Scenario 1: New internal chat UI, pre-launch review

## Setup
A frontend engineer building an internal company AI assistant pastes this description before launch:

> "Here's how our chat UI works. Assistant responses stream in token by token into a `<div id="response">` — we just do `responseDiv.textContent += nextToken` as tokens arrive, no special attributes on the div. There's a 'Stop generating' button that appears while streaming and disappears when the response finishes; clicking it just hides the button, focus stays wherever the user last clicked (usually still on the button, which is now gone). While waiting for the first token, we show an animated three-dot `<div class="typing-dots">` with a CSS keyframe animation — no text anywhere, just moving dots. The message input is a `<textarea>`, Enter sends the message, Shift+Enter adds a newline. Message history is a scrollable `<div>` full of plain `<div>` bubbles — you can scroll with the mouse wheel but there's no way to tab into individual messages. Code blocks in responses go through a markdown-it + highlight.js pipeline into `<pre><code class="hljs">`, with normal syntax highlighting colors, no extra attributes added."

## Expected output

A 5-row scorecard (streaming, regenerate/stop, thinking indicator, keyboard operability, code blocks) where:

- **Streaming announcement** → LIKELY BROKEN (plain `textContent` updates with no `role="log"`/`aria-live` at all means a screen reader hears nothing as the response streams in). WCAG ref should cite 4.1.3 Status Messages. Fix should specify adding `role="log" aria-live="polite"` (pre-rendered, empty, before content is injected) and recommend suppressing per-token churn / announcing once complete.
- **Regenerate/stop focus** → LIKELY BROKEN (focus is left on a now-hidden button). WCAG ref should cite 2.4.3 Focus Order (or 2.4.11/4.1.2 depending on framing). Fix must specify programmatically moving focus (e.g., to the input or the new response start) on click.
- **Thinking indicator** → LIKELY BROKEN (purely visual animation, no text/ARIA). WCAG ref should cite 4.1.2 Name Role Value or 4.1.3. Fix must specify a visually-hidden `aria-live="polite"` text node like "Assistant is thinking…".
- **Keyboard operability** → LIKELY BROKEN specifically for message history navigation (mouse-wheel-only scrolling, no tab stops, no documented keyboard alternative) even though input/send (Enter/Shift+Enter) is fine. WCAG ref should cite 2.1.1 Keyboard. Fix should specify adding a keyboard scroll path (Page Up/Down handling or tabindex on the history container).
- **Code blocks** → either COMPLIANT or LIKELY BROKEN/UNKNOWN depending on whether the model notices `<pre><code>` is natively focusable/scrollable by default in most browsers only if given `tabindex="0"` — acceptable either way as long as the reasoning is explicit, not a blanket accept.

## Pass criteria
- [ ] All 5 areas addressed with a verdict, not skipped.
- [ ] At least 4 of 5 areas correctly identified as LIKELY BROKEN given the described anti-patterns (streaming, regenerate focus, thinking indicator, keyboard history nav).
- [ ] Each LIKELY BROKEN item cites a specific WCAG success criterion (not "accessibility issue" generically).
- [ ] Each LIKELY BROKEN item includes a concrete fix (specific attribute/role/focus call), not vague advice.
- [ ] Output includes the exact caveat language that this is a static review, not a verified screen-reader test.
- [ ] Nowhere does the output claim a screen reader was actually run.

## Fail conditions
- Any area silently skipped or merged into another.
- A fix that says only "add ARIA" or "improve accessibility" without a specific attribute/behavior.
- Claiming or implying actual screen-reader output was captured.
