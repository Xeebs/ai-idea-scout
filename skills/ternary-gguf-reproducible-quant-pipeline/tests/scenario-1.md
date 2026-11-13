# Scenario 1: Clean-ish match with undisclosed methodology

## Input

User provides:
- HF repo: `PrismML/Ternary-Bonsai-8B-gguf`
- Local file: `/models/ternary-bonsai-8b-q2_0.gguf`, SHA256 computed as `a1f3...e92c` (full hash supplied)
- Model card (assistant fetches/reads it) states: "Q2_0 ternary quant, perplexity 7.84 on our internal eval set" — no dataset name, no context length, no llama.cpp version given. Published SHA256 on the card: `a1f3...e92c` (matches).
- GGUF internal metadata (user ran `gguf-dump` and pasted the output): architecture `llama`, params 8.03B, context length 8192, quant type `Q2_0` — all match what the card's text elsewhere claims (8B model, 8k context).
- User has llama.cpp built locally and reports back, after running the suggested command against wikitext-2-raw at context 2048: perplexity 8.41.

## Expected output characteristics (pass/fail checklist)

- [ ] Report explicitly flags that the model card's perplexity claim has NO stated dataset/context length, and labels the wikitext-2 run as a substitute, not a like-for-like comparison — this must appear before any classification is given.
- [ ] File identity section shows hash MATCH and metadata MATCH, clearly separated from the quality comparison.
- [ ] Drift is computed: (8.41 - 7.84) / 7.84 ≈ 7.3% — report should land in DRIFT band (5-20%), not silently rounded into MATCH.
- [ ] Classification given as DRIFT with reasoning that explicitly ties back to the non-like-for-like caveat (i.e., doesn't claim this proves the quant is degraded, since the comparison basis itself differs from the original claim).
- [ ] The standard safety caveat ("quality-consistent, not confirmed safe/unmodified") is present even though hash and metadata both matched cleanly.
- [ ] Recommendation is calibrated (e.g., "usable but retest with matching methodology if possible / treat perplexity comparison as inconclusive due to undisclosed original methodology") rather than a flat "safe" or "unsafe."
- [ ] No fabricated numbers: assistant never invents what dataset/context the original 7.84 figure used.

**FAIL conditions**: report calls this a clean MATCH without noting the methodology gap; report states the file is "verified safe"; report skips the file-identity/metadata section; report invents a dataset name for the original claim.
