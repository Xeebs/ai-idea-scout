# Scenario 1: Tauri screenshot-renamer, Gemma 2B GGUF, macOS only

## Input

> I'm building a small macOS menu-bar app in Tauri that watches the Desktop for new screenshots and renames them based on what's in the image (e.g. "invoice-acme-corp-nov.png" instead of "Screenshot 2026-11-12 at 3.42.11 PM.png"). I want to run Gemma 4 2B, quantized to GGUF Q4_K_M, fully locally — no cloud calls. I don't have an existing manifest to share, just starting the integration now. Can you help me with the download, packaging, and update handling?

(All four required inputs are present: stack = Tauri, platform = macOS, model = Gemma 4 2B GGUF Q4_K_M, task = screenshot renaming via image classification/description.)

## Expected behavior

The skill should NOT ask clarifying questions here — all four required inputs (stack, platform, model, task) are already present in the message. It should go straight to generating the four-section output:

1. **Model loading / runtime shim** — Rust/Tauri code showing inference running in an async task or sidecar (e.g. a `llama.cpp` binding called from a `tauri::async_runtime::spawn` or a sidecar binary), not blocking the webview/main thread.
2. **First-run download logic** — code that downloads the GGUF file into `BaseDirectory::AppLocalData` (or equivalent), not bundled into the `.app`/installer, with progress reporting and a retry/offline-safe path.
3. **Update-check stub** — SHA-256 checksum pinning, a small manifest comparison ({version, sha256, url}) on startup, flagging rather than silently re-downloading.
4. **Packaging checklist** — markdown checkboxes including: model excluded from `tauri.conf.json` bundle resources, CPU fallback note (macOS Metal path with CPU fallback), no duplicate runtime bundled, model license check flagged as the user's responsibility, and (since this is a installer not a store extension) no app-store size-limit item required — or explicitly noted as not applicable.

## Pass criteria

- [ ] Output is in four labeled sections, in the specified order.
- [ ] Code is Tauri/Rust-shaped (not Electron `ipcMain`/`BrowserWindow`, not Chrome extension `manifest.json`/service-worker code).
- [ ] Inference is explicitly kept off the main/webview thread (async task or sidecar), matching the SKILL.md guardrail.
- [ ] Download logic targets app-local-data, not the install bundle, and includes a progress/retry mechanism.
- [ ] Update-check includes a SHA-256 checksum verification step before marking the model usable.
- [ ] Packaging checklist explicitly flags model license checking as the user's responsibility — does not claim to have verified license terms.
- [ ] No clarifying question was asked (since nothing required was missing) — asking here would be a false negative on scope-confirmation.

## Fail conditions

- Generates Electron-style code for a Tauri target.
- Puts model inference directly on the main thread/webview with no mention of a separate process/task.
- Suggests bundling the GGUF file directly into the `.app`/installer.
- Omits the checksum/update-check section entirely.
- Silently proceeds without noting the license-check caveat.
