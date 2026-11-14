---
name: local-agent-memory-reliability-layer
description: Audits a DIY persistent-memory integration for a local/small-model agent (Mem0+Ollama+Qdrant, sqlite-vec, LM Studio memory plugin, custom script) against known silent-failure modes — embedding dimension mismatch, unconfirmed writes, model-size-dependent tool-call unreliability, missing dedupe/fallback — and returns a prioritized fix checklist. Use when a user shares their local memory setup's config/code and asks whether it's reliable, or reports symptoms like "the agent forgot something I told it" or "memory sometimes doesn't save."
---

# Local Agent Memory Reliability Auditor

## When to use this
The user is running a local or small open-weight model (Ollama, llama.cpp, LM Studio) with a hand-built persistent-memory layer (Mem0, raw sqlite-vec, Qdrant, a markdown-file memory plugin, or a custom record/query script) and either:
- wants a pre-flight reliability check before trusting it with real personal data (journaling, health notes, financial notes, project context), or
- is already seeing symptoms: memories that silently don't save, the agent repeating questions it should already know the answer to, contradictory facts surfacing across sessions, or no error at write time despite a lost memory.

This is a one-shot review task, not a running service — it does not build or operate the memory layer itself.

## Inputs
**Data source**: Manual — the user pastes the actual config/code of their existing memory integration (embedding model name, vector store type and its dimension/schema setting, the connection snippet with any secrets redacted, and the record/write function if available), plus the local model name and approximate parameter size (e.g., `llama3.2:1b`, `qwen2.5:7b`). Optionally, error logs or a plain-language symptom description.
(Note: this differs from the data source of the full "Steady Memory" project this skill is drawn from, which connects live to the user's local model runtime and storage. This skill never connects to anything — it audits a static paste. If the user cannot produce the actual config/code, this skill cannot run a real audit; see Guardrails.)

## Procedure
1. **Require the actual config/code.** If the user only describes their setup verbally with no pasted config, code, or schema, stop and ask for it before auditing — do not guess at settings you weren't shown.
2. **Classify the architecture** in one line: Mem0-wrapped vector store, raw sqlite-vec, Qdrant direct, flat-file/markdown plugin, or custom script. This determines which checks below even apply (e.g., flat-file setups skip the dimension check).
3. **Check embedding-dimension consistency.** Identify the embedding model in use and its known output dimension (reference table below). Compare it against the vector store's configured dimension setting.
   - Known dimensions: `nomic-embed-text` (Ollama) = 768, `mxbai-embed-large` = 1024, `all-minilm` = 384, `bge-small` = 384, `bge-base` = 768, `bge-large` = 1024, OpenAI `text-embedding-3-small` = 1536 (flag if this default was left in place in an otherwise-local setup — it's a common copy-paste leftover).
   - If the embedding model isn't named in the paste, mark this check UNKNOWN, not PASS.
4. **Check write-confirmation.** Does the write/insert call check a return value, row count, or status before treating the memory as saved, or is it fire-and-forget (no check at all)? Fire-and-forget on a dimension mismatch is the exact silent-failure pattern documented in the wild for this stack — flag it even if dimensions currently match, since a future embedding-model swap would then fail silently too.
5. **Check write/read embedding-model parity.** Confirm the same embedding model is used for both storing and querying. A model swapped between the two (e.g., upgraded embedding model after months of use) produces retrieval that silently returns nothing relevant rather than erroring.
6. **Check model-size-dependent reliability.** If memory writes depend on the local model correctly emitting a structured tool/function call, and the stated model is under ~7B parameters, flag this as a known-fragile path — smaller local models are documented to be less reliable at consistent tool-use. Recommend a degraded-mode fallback that doesn't depend on tool-call compliance (e.g., a deterministic keyword/command trigger, or an always-on flat-file append) for models in this range.
7. **Check for any fallback/degraded path at all.** If the setup has no fallback when a structured write fails (regardless of model size), flag this as a gap, not just a "nice to have."
8. **Check duplicate/contradiction handling.** Does the system dedupe near-identical memories or version-conflicting facts, or will two contradictory entries just coexist and get returned together at retrieval time?
9. **Compile the findings** into the Output format below, with a fix for every FAIL — never a bare "this is broken" with no remediation.

## Output format
```
## Architecture
<one line: e.g. "Mem0 + Ollama (nomic-embed-text) + Qdrant">

## Findings
| Check | Status | Evidence | Fix |
|---|---|---|---|
| Embedding dimension match | PASS/FAIL/UNKNOWN | <what was found in the paste> | <concrete fix, or "none needed"> |
| Write confirmation | ... | ... | ... |
| Write/read embedding parity | ... | ... | ... |
| Model-size tool-call reliability | ... | ... | ... |
| Fallback/degraded-mode path | ... | ... | ... |
| Dedupe / contradiction handling | ... | ... | ... |

## Risk rating
LOW / MEDIUM / HIGH — based on count and severity of FAILs (any silent-failure-class FAIL, i.e. dimension mismatch or no write confirmation, is an automatic floor of MEDIUM regardless of other results).

## Prioritized fix checklist
1. <highest-impact fix first, concrete and actionable>
2. ...

## Verdict
One sentence: safe to trust as-is for low-stakes use / needs the fixes above before trusting it with real personal data.
```

## Guardrails
- Never mark a check PASS when the relevant setting wasn't actually shown in the pasted config — mark it UNKNOWN and say what's missing.
- Never invent or assume code behavior beyond what was pasted; if the write function isn't included, say the write-confirmation check couldn't be verified rather than guessing it's fine.
- This is a reliability/correctness audit only — not a security audit. Do not evaluate or comment on secrets handling, prompt injection, or data exfiltration risk; if the user wants that, say explicitly that it's a different kind of review and out of scope here.
- Never recommend switching to a specific commercial hosted memory service as "the fix" — the whole point of this setup is staying local; recommend the general mitigation pattern (dimension pinning, write confirmation, deterministic fallback) instead.
- Never recommend "just stuff more history into context" as a fix for recall problems — documented community testing found full-history context stuffing actively harms recall at every tested model size; recommend better retrieval/write hygiene instead.
- If the user pastes no config/code at all, do not produce a generic audit from memory of common Mem0 pitfalls alone — ask for the paste first.
