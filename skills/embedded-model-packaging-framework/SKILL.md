---
name: embedded-model-packaging-framework
description: Generates the integration scaffold (model loading shim, first-run download-into-userdata logic, update-check stub, packaging checklist) for embedding one small local model as an invisible feature inside a narrow Tauri, Electron, or Chrome-extension app. Use when a developer says they want to add one offline/local-AI feature to an existing non-AI app and needs the plumbing, not a general chat UI.
---

# Pocket Model Scaffold: Embed One Small Local Model Into a Narrow App

## When to use this
A developer is adding exactly one small local model (a classifier, extractor, renamer, categorizer — not a chat interface) as a background feature of an app that is not itself an AI product, and says something like "I want to embed Gemma/Phi/a small GGUF model into my Tauri/Electron/Chrome extension app to do [narrow task] offline." They need the download/packaging/update plumbing around the model, not model selection advice or inference-quality tuning.

## Inputs
**Data source**: Manual — the user states the target stack, platform(s), chosen model identifier/format, and the narrow task directly in the conversation; they may optionally paste an existing `package.json`, `Cargo.toml`, or extension `manifest.json` for the app being modified, but nothing is read from a live connector.

Required, ask for whichever is missing before generating anything:
1. **Target stack**: Tauri, Electron, or Chrome extension (WebGPU/Transformers.js). If undecided, ask which and don't guess.
2. **Target platform(s)**: macOS/Windows/Linux for desktop stacks, or "browser only" for the extension.
3. **Chosen model**: name, parameter count, and format (GGUF quant, MLX, or a WebGPU-compatible safetensors/ONNX export). If the user hasn't picked a format yet, ask — the scaffold differs by format.
4. **The narrow task**: what the model does (classify, extract, rename, summarize, detect). This only affects naming/comments in the generated stub, not the plumbing, but confirms this is genuinely a single-task embed and not a general chat feature (if it's the latter, say this skill isn't the right fit and stop).

Optional: an existing manifest/config file pasted in, so generated snippets match the real project structure instead of a bare-bones example.

## Procedure
1. **Confirm scope.** If any required input (1–3) is missing, ask for it. Do not generate a scaffold on assumed stack/model/format — a wrong runtime choice (e.g. WebGPU for a non-browser target) wastes the developer's time.
2. **Pick the inference approach by stack** — this is the load-bearing decision, not a detail:
   - **Electron**: never load GGUF/model inference in the main process (the `@electron/llm` maintainers themselves warn this ballons memory and can crash the UI process). Scaffold inference in a separate `utilityProcess`/worker, communicating with the renderer over IPC.
   - **Tauri**: run inference in a Rust async task or a sidecar binary (not blocking the webview thread); use `tauri::async_runtime` or a sidecar process for the actual `llama.cpp`/MLX call.
   - **Chrome extension**: run inference in a service worker or offscreen document via WebGPU/Transformers.js; never bundle the model file inside the `.crx`/Web Store package — Chrome Web Store has hard item-size limits and model files routinely exceed them.
3. **Generate the first-run download logic**: the model is fetched into user/app-data (`app.getPath('userData')` for Electron, `tauri::path::BaseDirectory::AppLocalData` for Tauri, `IndexedDB`/Cache API for the extension) on first run or first use — never bundled into the installer/package. Include resumable/retry download with a visible progress callback, and a graceful offline-first-run message (don't crash if the network is unavailable; tell the user what's missing and let them retry).
4. **Generate the integrity + update-check stub**: pin a SHA-256 checksum for the expected model file, verify it after download before marking the model "ready," and write a small manifest (`{version, sha256, url}`) the app checks on startup against the locally cached one — flag (don't silently auto-replace) when a new version is available, to avoid a background multi-GB re-download surprising the user.
5. **Generate the packaging checklist**, as an explicit markdown checklist (not prose), covering at minimum:
   - Model file excluded from the installer/package manifest (build config, not just gitignore).
   - GPU path has a verified CPU fallback (don't assume WebGPU/Metal/CUDA is present).
   - No duplicate runtime bundling (check the app isn't already shipping a second LLM runtime, e.g. both `node-llama-cpp` and a bundled Ollama binary).
   - Model license terms checked for redistribution/offline-use compatibility (many small-model licenses restrict commercial redistribution — this is a legal check, not a technical one, and the skill cannot verify it for the user).
   - Extension/installer size budget confirmed against the target store's limits, if applicable.
6. **Self-review before handing back**: check that every snippet actually matches the stack chosen in step 1 (e.g. no Electron `ipcMain` code leaking into a Tauri answer) and that the checklist in step 5 is present even if the user only asked for "the download code."

## Output format
A single markdown response with four labeled sections, in this order:
1. `### Model loading / runtime shim` — a code block in the stack's native language, with inline comments marking the process/thread boundary from step 2.
2. `### First-run download logic` — a code block implementing step 3, including the progress callback and offline-failure handling.
3. `### Update-check stub` — a code block implementing step 4's manifest comparison, plus the one-line manifest JSON shape it expects.
4. `### Packaging checklist` — a markdown checklist (`- [ ] ...`) from step 5, every item phrased as a concrete, checkable action, not a general reminder.

If scope was ambiguous and the user answered clarifying questions, restate the confirmed stack/model/task in one line at the top before the four sections.

## Guardrails
- Never generate Electron code that loads or calls the model inference directly from the main process — always a separate process/worker, per the known production-stability warning.
- Never bundle the model binary inside the installer, `.crx`, or Web Store package in generated code — always a first-run/first-use download into user/app data.
- Never skip the checksum-verification step even if the user only asked for "the simple version" — an unverified model download is a silent corruption/supply-chain risk, not an optional nicety.
- Never claim the skill checked model license compatibility for redistribution — flag it as a required human/legal check, since this skill has no way to verify license terms itself.
- Never produce a scaffold for a stack the user didn't confirm; ask rather than defaulting to the most common stack (Electron) when it wasn't stated.
