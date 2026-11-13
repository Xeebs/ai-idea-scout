# Ternary/1-Bit GGUF Quant Verification

Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your actual inputs, and it will walk you through checking whether a downloaded ultra-low-bit GGUF model file (ternary/1-bit/1.58-bit/Q2_0-class) actually matches what its maintainer claims.

## Why this exists

Ultra-low-bit GGUF quants (ternary/BitNet-style, 1-bit, 1.58-bit) are often published by a single maintainer with no independent second source. If that maintainer goes inactive, ships a flawed build, or the file gets corrupted in transit, there is often no way to tell — and no fallback. This is a one-shot check you run on a file you already have, before you trust it.

This does not prove a file is malware-free. It checks whether the file's metadata and measured quality are consistent with what the maintainer published. Treat a clean result as "consistent with the claim," not "certified safe" — see the Guardrails at the bottom.

## Data source

**Connected** — the model card text and any published hash/benchmark numbers are pulled directly from the model's public HuggingFace repo page (no account needed for public repos). The actual quality measurement runs on your own machine against your own downloaded file using your own local `llama.cpp` build — nothing about your file or hardware is uploaded anywhere. You only need to tell the assistant the repo link/ID and your local file path; you don't need to paste the model card text yourself (though you can, if you'd rather not have the assistant fetch it).

## What to hand over

1. **The HuggingFace repo ID or URL** for the quant you downloaded (e.g., `PrismML/Ternary-Bonsai-8B-gguf`).
2. **The local path** to your downloaded `.gguf` file.
3. Confirmation you have (or are willing to build) **`llama.cpp`** with the `llama-perplexity` binary (or equivalent eval tool) available on your machine — the assistant will give you the exact command to run; it cannot run it for you.
4. *Optional:* a path to the original full-precision weights or a known-good reference quant, if you want a stronger KL-divergence comparison instead of perplexity alone.
5. *Optional:* a SHA256 hash you already have for the file, if the model card itself doesn't list one.

## What the assistant will do

1. **Pull the claims.** Read the model card for the repo you named. Quote, verbatim, every published benchmark number (perplexity + dataset + context length, or task-accuracy score), the stated quantization method/llama.cpp version, and any published file hash.
2. **Flag missing methodology.** If the card doesn't say what dataset/context length produced its number, it will say so explicitly — perplexity depends heavily on what text it's measured against, so an unstated methodology means any reproduction is not an apples-to-apples comparison, and the report will label it that way.
3. **Check file identity first.** Compare your file's SHA256 against any published hash, and compare the GGUF file's own internal metadata (architecture, parameter count, context length, quant type) against what the card claims. A mismatch here is treated as more serious than a quality drift — it means the file may not even be what it claims to be.
4. **Give you the exact command to run.** Something like:
   ```
   llama-perplexity -m /path/to/model.gguf -f wikitext-2-raw/wiki.test.raw -c 2048
   ```
   using the dataset/context length from the model card if stated, or the closest standard substitute (commonly wikitext-2) if not — labeled as a substitute either way. If you supplied a reference baseline, it will also give you a KL-divergence comparison command, which is a stronger check than perplexity alone.
5. **Compare your reported result against the claim** and classify it:
   - **MATCH** — within 5% of the claimed number (or within the maintainer's own stated margin, if wider).
   - **DRIFT** — 5–20% worse than claimed.
   - **MISMATCH** — more than 20% worse, or any hash/metadata mismatch.
6. **Always restate the caveat**, regardless of result: a clean match does not prove the file is unmodified or malware-free. Published research has shown GGUF files that stay byte-identical to a known-good version while still being altered to behave differently in specific contexts. This check is about quality-consistency with the published claim, not security.

## Output you'll get

A short report with these sections, in order:
- **File identity** — your file's hash and metadata vs. what's published.
- **Published claim** — the exact quoted text from the model card, with methodology noted as stated or flagged as missing.
- **Reproduction run** — the exact command used, and whether the dataset/context matches the card or is a labeled substitute.
- **Result** — your measured value, percent drift from claimed, and a MATCH/DRIFT/MISMATCH classification with one line of reasoning.
- **Caveat** — the standard "consistent with claim, not confirmed safe" note, every time.
- **Recommendation** — trust it for your use case, retest with closer settings, or hold off until an independent second source exists.

## Guardrails (what this will never do)

- It will never invent a benchmark number the maintainer didn't actually publish — if the card is silent on methodology or hash, it says "not published."
- It will never pretend to run the perplexity command itself — it gives you the command and uses the number you report back, because it cannot execute binaries against files on your machine.
- It will never call a passing result "safe" or "verified clean" — only "quality-consistent with the published claim," with the security caveat restated every single time, not just when something looks off.
- It will never silently substitute a default dataset when the card doesn't specify one without telling you it did so.
- It will never skip the hash/metadata check even if you only asked about perplexity — that check always runs first because it's the cheapest and most decisive one.
