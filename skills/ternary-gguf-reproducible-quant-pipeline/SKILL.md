---
name: ternary-gguf-reproducible-quant-pipeline
description: Verifies a downloaded ultra-low-bit (ternary/1-bit/1.58-bit) GGUF quant against its maintainer's published benchmark claims and file metadata, flagging drift, corruption, or undisclosed changes. Use when a user has a single-source GGUF quant file and no independent second source to cross-check it against.
---

# Ternary/1-Bit GGUF Quant Verification

## When to use this

The user has downloaded a ternary or ultra-low-bit (1-bit, 1.58-bit, Q2_0-class) GGUF quant — typically from a single maintainer's HuggingFace repo (e.g., a "Ternary Bonsai"-style release) — and wants to know, before relying on it, whether the file actually matches what the maintainer claims. This matters most when:
- No independently-built second source of the same quant exists yet (the single-point-of-failure case this skill exists for).
- The user is about to deploy the quant somewhere they care about correctness (local assistant, agent backend, evaluation baseline).
- The user suspects corruption, a bad download, or wants a sanity check after a model card update/revision.

This is a one-shot verification pass on a file the user already has. It does not build quants and it is not a malware scanner — see Guardrails.

## Inputs

**Data source**: Connected — pulls the target model's card text and any published hash/benchmark claims directly from HuggingFace Hub (mature, freely accessible, no auth needed for public repos); the actual perplexity/eval measurement runs locally against the user's own downloaded GGUF file and local llama.cpp build. No manual paste required beyond naming the HF repo and the local file path.

Required from the user:
1. The HuggingFace repo ID or URL for the quant being verified (e.g., `PrismML/Ternary-Bonsai-8B-gguf`).
2. The local filesystem path to the downloaded `.gguf` file.
3. Confirmation they have (or can build) `llama.cpp` with the `llama-perplexity` (or `llama-imatrix`/eval-harness equivalent) binary available locally — this skill cannot run perplexity for them; it tells them the exact command.

Optional but strengthens the result:
4. A path to the original FP16/BF16 weights or a known-good reference quant of the same model, enabling a KL-divergence-style comparison instead of perplexity alone.
5. A SHA256 hash the user already has for the file (from the download page or a community post), if the model card itself doesn't publish one.

## Procedure

1. **Pull the claims.** Fetch the HuggingFace model card for the named repo. Extract verbatim: every published benchmark number (perplexity value + dataset + context length, or task-accuracy score), any stated quantization method/script, the llama.cpp commit/version used to build it, and any published file hash. Quote the exact text — never paraphrase a number into something more precise-sounding than what was written.
2. **Flag missing methodology.** If the card doesn't state the dataset, context length, or llama.cpp version behind its claimed number, say so explicitly before proceeding. Perplexity is sensitive to calibration/eval data choice, so an unstated methodology means any reproduction attempt is "not a like-for-like comparison" — label it that way in the output, don't silently assume a default.
3. **Check file identity first.** Compare the local file's SHA256 against any hash published on the model card or repo. Independently, read the GGUF file's own metadata header (architecture, parameter count, context length, quantization type field) and compare it against what the model card declares. A metadata or hash mismatch is reported as higher-severity than a perplexity drift — it indicates the file may not be what it claims to be at all, before any quality question even applies.
4. **Reproduce the measurement.** Give the user the exact local command to run (e.g., `llama-perplexity -m <path> -f <dataset> -c <context_length>`), using the dataset/context length identified in step 1 if known, or the closest standard public dataset (commonly wikitext-2-raw test) if the card didn't specify — labeled accordingly. If the user supplied a reference baseline (input 4), also give the command for a KL-divergence comparison, which research indicates is a more direct check than perplexity alone since it compares the quant against the original model rather than only against held-out text.
5. **Compare and classify.** Take the user-reported measured value and compute percent drift from the claimed value. Classify as:
   - **MATCH** — drift within 5% (or within the maintainer's own stated error margin, if larger).
   - **DRIFT** — 5–20% worse than claimed.
   - **MISMATCH** — >20% worse, or any hash/metadata mismatch from step 3.
   State these thresholds as the skill's own heuristic, not an industry standard — the maintainer's claimed numbers themselves may carry real variance.
6. **Write the caveat every time, unmodified by result:** a clean perplexity/hash match does not prove the file is safe or unmodified — adversarial research has demonstrated GGUF quants that stay byte-identical to a known-good baseline while still being altered to produce attacker-chosen output in specific contexts. This skill checks quality-consistency with published claims, not security.

## Output format

A single markdown report:

```
## Verification Report: <model repo>

**File checked**: <local path>
**Claimed source**: <HF repo URL>

### File identity
- SHA256: <computed> vs <published, or "not published">
- GGUF metadata (arch/params/context/quant type): <declared> vs <card claim> — MATCH / MISMATCH

### Published claim (verbatim from model card)
> <quoted text>
Methodology stated: <dataset, context length, llama.cpp version> / "NOT STATED — flagged"

### Reproduction run
Command used: <exact command given to user>
Dataset/context used: <value> (<"matches card" | "closest standard substitute — not like-for-like">)
Measured value (user-reported): <value>

### Result
Drift: <percent>
Classification: MATCH | DRIFT | MISMATCH
Reasoning: <one line>

### Caveat
A clean result means the file is quality-consistent with the published claim, not that it is confirmed safe or unmodified. [standard caveat text from step 6]

### Recommendation
<trust for stated use / retest with closer settings / avoid until a second independent source confirms>
```

## Guardrails

- Never report a number the maintainer didn't actually publish — if a claim isn't on the model card, say "not published," don't estimate one on their behalf and present it as theirs.
- Never run the perplexity/eval command yourself on the user's behalf by inventing a result — this skill cannot execute arbitrary local binaries against the user's files; it specifies the exact command and uses the number the user reports back.
- Never call a MATCH result "safe," "verified clean," or "not tampered" — state only that it is quality-consistent with the claim, and repeat the byte-identical-malicious-build caveat every time, not only when something looks wrong.
- Never silently assume a default dataset/context length when the model card doesn't state one — always label the substitution as non-like-for-like.
- Never skip the file-identity/metadata check even if the user only asks about perplexity — a metadata mismatch is the cheapest and most decisive check and must always run first.
