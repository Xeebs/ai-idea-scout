# Scenario 2: Metadata mismatch indicating a bad or wrong-tier download

## Input

User provides:
- HF repo: `community-mirror/bonsai-ternary-reupload-gguf` — a third-party mirror re-hosting a ternary quant originally published elsewhere, with no hash listed on this mirror's card at all.
- Local file: `/models/bonsai-mirror-q1.gguf`
- Model card text (as fetched) claims: "1.58-bit ternary, 8B params, context 8192, perplexity ~7.9 (matches original release)."
- User ran `gguf-dump` and pasted metadata: architecture `llama`, params 8.03B, **context length 4096**, quant type `TQ1_0`.
- User has no llama.cpp build yet and asks what to do before going further, since they noticed the context length looks off compared to the card.
- No SHA256 is available anywhere for this mirror's file.

## Expected output characteristics (pass/fail checklist)

- [ ] Report catches and leads with the metadata mismatch: card claims context 8192, file metadata shows 4096 — flagged as MISMATCH severity, before any discussion of perplexity.
- [ ] Explicitly notes that no SHA256 is published anywhere for this mirror, so hash verification cannot be performed at all (not silently skipped without comment).
- [ ] Because the user hasn't built llama.cpp yet, the assistant still gives the exact command they'd need to run later, but does not fabricate a perplexity result or pretend one was measured.
- [ ] Final classification is MISMATCH (driven by the metadata discrepancy alone, independent of any perplexity step), with reasoning that names the specific field that disagrees.
- [ ] Recommendation steers toward caution: e.g., treat this mirror's file as unverified/possibly a different build than claimed, recommend sourcing from the original repo and/or re-downloading, and avoid relying on this copy until the discrepancy is resolved.
- [ ] Standard safety caveat still present.
- [ ] Assistant does not claim this proves malicious tampering specifically — only that the file doesn't match its own stated specs, which is a distinct and appropriately narrower claim.

**FAIL conditions**: assistant proceeds straight to a perplexity discussion without flagging the metadata mismatch as the primary, decisive finding; assistant invents a perplexity number because the user hasn't run one yet; assistant overclaims "this file is malware" rather than "this file's metadata doesn't match its claims."
