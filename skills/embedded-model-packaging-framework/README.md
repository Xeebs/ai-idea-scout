# Pocket Model Scaffold — Embed One Small Local Model Into a Narrow App

A paste-anywhere prompt for generating the download/packaging/update plumbing around embedding exactly **one** small local model (a classifier, extractor, renamer, detector — not a chat UI) as an invisible feature inside an existing Tauri, Electron, or Chrome-extension app.

This is for the "I just want this one offline feature to work and be packaged correctly" moment — not for choosing which model to use, tuning inference quality, or building a general local-chat product.

## When to use this

Use this when you are adding a single small local model to a narrow, non-AI-first app and need the integration glue: how the model gets downloaded on first run, how it's kept out of the installer, how updates are checked safely, and what to double-check before shipping. If you're building a general AI chat app or haven't picked a model/stack yet, this isn't the right prompt — pick those first.

## Data source

**Manual.** You type in the target stack, platform(s), chosen model (name, size, format), and the task it performs. Nothing is read automatically from any connected service. You may optionally paste an existing `package.json`, `Cargo.toml`, or extension `manifest.json` so the generated code matches your real project, but this is optional.

## What to give the AI

Before pasting the prompt below, have these ready (the AI will ask if anything is missing — don't let it guess):

1. **Target stack**: Tauri, Electron, or Chrome extension (WebGPU/Transformers.js).
2. **Target platform(s)**: macOS/Windows/Linux, or "browser only" for an extension.
3. **Chosen model**: name, parameter count, and format (GGUF quant, MLX, or a WebGPU-compatible safetensors/ONNX export).
4. **The narrow task**: what the model does (classify / extract / rename / summarize / detect, etc.).
5. *(Optional)* an existing manifest/config file for the app you're modifying.

## The prompt

Paste this into any AI chat tool, filling in the bracketed details:

```
I'm embedding one small local model as an invisible feature inside a [Tauri / Electron / Chrome extension] app, targeting [macOS/Windows/Linux, or "browser only"]. The model is [model name, size, format — e.g. "Gemma 2B, GGUF Q4_K_M" or "a WebGPU-compatible ONNX export"]. It performs this one narrow task: [describe the task, e.g. "classifying screenshots to suggest a filename"].

Do not generate anything until you've confirmed you have all of: stack, platform(s), model name/size/format, and the task. Ask me first if anything is missing or ambiguous.

Once confirmed, produce exactly these four sections, in this order:

1. "Model loading / runtime shim" — code in the stack's native language. For Electron, the inference must run in a separate process/worker, never the main process (the @electron/llm maintainers warn that in-main-process GGUF loading balloons memory and can crash the UI process). For Tauri, use an async task or sidecar process, not the webview thread. For a Chrome extension, use a service worker or offscreen document with WebGPU/Transformers.js, never bundling the model file inside the extension package.

2. "First-run download logic" — code that downloads the model into app/user data (not the installer) on first run or first use, with a resumable/retry mechanism, a visible progress callback, and a graceful message if the network is unavailable at first run (no crash).

3. "Update-check stub" — code that pins a SHA-256 checksum for the model, verifies it after download before marking the model ready, and compares a small remote manifest ({version, sha256, url}) against the locally cached one on startup — flagging an available update rather than silently re-downloading a multi-GB file in the background.

4. "Packaging checklist" — a markdown checklist covering at minimum: model excluded from the installer/package build config (not just .gitignore); a verified CPU fallback if a GPU path is used; no duplicate LLM runtime bundled elsewhere in the app; a note that model license terms for redistribution/offline use must be checked by me, since you can't verify that; and, if this targets an extension/app store, a check that the final package size stays under that store's limits.

If I gave you an existing package.json / Cargo.toml / manifest.json, match the generated snippets to that project's actual structure instead of a generic example.
```

## What you get back

A single response with the four labeled sections above, in order — runnable-shaped code for the shim, download logic, and update stub, plus a checkbox-style packaging checklist. If you didn't give a required detail up front, the AI should ask before generating anything, not guess a stack or model format for you.

## Guardrails (what a good answer never does)

- Never puts model inference in an Electron main process — always a separate process/worker.
- Never bundles the model binary into the installer, `.crx`, or Web Store package — always a first-run/first-use download into app/user data.
- Never skips the checksum-verification step, even for "just the simple version."
- Never claims it checked your model's license terms for redistribution — that's flagged as your job, not something it can verify.
- Never produces a scaffold for a stack you didn't actually confirm.

## Example trigger phrases

- "I want to embed a small Gemma model into my Tauri screenshot-renamer app, offline."
- "How do I add a local Phi classifier to my Chrome extension without blowing past the Web Store size limit?"
- "I built an Electron budgeting app and want to add one local model for categorizing transactions — what's the right way to package and update it?"
