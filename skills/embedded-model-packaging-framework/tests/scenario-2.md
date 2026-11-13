# Scenario 2: Chrome extension, underspecified model/format, bill detection

## Input

> I'm building a Chrome extension that scans your inbox tab and flags emails that look like bills (due date, amount, "pay now" language) using a local LLM so nothing leaves the browser. I want to run it fully offline via WebGPU. Can you set up the model download and packaging for me?

(Stack is given — Chrome extension/WebGPU. Platform is implicitly "browser only." Task is given — bill detection. But the model name/size/format is NOT specified at all, and the user never confirms whether they've already chosen a specific model.)

## Expected behavior

Per the SKILL.md procedure step 1 ("Confirm scope... ask for it. Do not generate a scaffold on assumed stack/model/format"), the skill must stop and ask for the missing required input — the specific model (name, parameter count, and WebGPU-compatible format/export) — before producing any of the four output sections. It should not silently pick a model (e.g. defaulting to "Gemma 2B" or "Phi-3-mini") on the user's behalf, since the format choice (ONNX vs. safetensors vs. a Transformers.js-supported checkpoint) changes the generated loading code.

A good response:
- Confirms stack = Chrome extension/WebGPU, platform = browser-only, task = bill detection are understood.
- Explicitly asks which model (name, size, and export format compatible with Transformers.js/WebGPU) the user intends to use, since this determines the loading code.
- Does not generate the four-section scaffold yet.

If the user then replies with a model (e.g. "let's use a small distilled classifier exported to ONNX, under 500MB"), a follow-up turn should produce the four sections, with:
1. Runtime shim using a service worker or offscreen document (never inference code bundled to run in a content script directly against page DOM without isolation, and never the model file bundled inside the `.crx`/Web Store package).
2. First-run download into IndexedDB/Cache API.
3. Update-check stub with checksum comparison.
4. Packaging checklist including an explicit Chrome Web Store item-size-limit check (since this is the extension stack where that guardrail applies).

## Pass criteria

- [ ] First response asks for the missing model name/size/format rather than guessing one.
- [ ] First response does not output any of the four scaffold sections prematurely.
- [ ] Once the model is supplied, the follow-up output uses Chrome-extension-appropriate code (service worker/offscreen document, WebGPU/Transformers.js), not Electron or Tauri code.
- [ ] Follow-up packaging checklist explicitly includes a Chrome Web Store size-limit item, not a generic "check your installer size" line that ignores the extension-specific constraint named in SKILL.md.
- [ ] Follow-up guards against bundling the model file inside the `.crx` package.

## Fail conditions

- Picks a default model/format without asking, when none was given.
- Produces desktop (Electron/Tauri) packaging guidance for what is explicitly a browser-only extension.
- Omits the Chrome Web Store size-limit checklist item that is specific to this stack.
- Suggests running inference directly in a content script without isolation (bypassing the service-worker/offscreen-document guidance).
