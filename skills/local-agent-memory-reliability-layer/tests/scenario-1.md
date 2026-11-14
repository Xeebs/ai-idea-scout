# Scenario 1 — Mem0 + Ollama + Qdrant, dimension mismatch left from a copy-pasted tutorial

## Input

User message:

> I followed a blog post to wire up Mem0 with Ollama and Qdrant for my personal assistant. It mostly works but sometimes when I tell it something important, it's just not there the next day — no error, nothing. Here's my config:

```python
from mem0 import Memory

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "personal_memories",
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 1536,
        },
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
        },
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.2:3b",
        },
    },
}

m = Memory.from_config(config)

def save_memory(text, user_id):
    m.add(text, user_id=user_id)

def recall(query, user_id):
    return m.search(query, user_id=user_id)
```

> Local model is llama3.2:3b. No logs, it just silently doesn't save sometimes.

## Expected output (what a correct audit produces)

- Architecture identified as Mem0 + Ollama (embedder: nomic-embed-text) + Qdrant.
- **Embedding dimension check: FAIL.** The collection is configured for `embedding_model_dims: 1536` (the OpenAI text-embedding-3-small default, a common copy-paste leftover), but `nomic-embed-text` actually outputs 768-dimension vectors. This exact mismatch is named as the root cause candidate for the reported "silently not there" symptom.
- **Write confirmation: FAIL.** `save_memory` calls `m.add()` and never checks a return value or confirms the write succeeded — fire-and-forget, consistent with a silent failure going unnoticed.
- **Write/read embedding parity: PASS** — same embedder config used in both the add and search path (no separate query-time embedder specified).
- **Model-size tool-call reliability** — flagged as relevant since the model is 3B parameters, but notes that Mem0's `.add()`/`.search()` here are direct Python calls, not model-emitted tool calls, so this specific risk doesn't directly apply to this architecture; model-size risk would matter if a tool-calling layer sat in front of this instead.
- **Fallback/degraded-mode path: FAIL** — no fallback exists if the Qdrant write fails or Ollama's embed call errors.
- **Dedupe/contradiction handling: UNKNOWN** — not shown in the pasted code; Mem0's own dedup behavior isn't visible from this snippet alone.
- Risk rating: at least MEDIUM (floor triggered by the dimension mismatch FAIL).
- Fix checklist leads with: fix `embedding_model_dims` to 768 to match `nomic-embed-text`, and either drop/recreate the Qdrant collection (dimension can't be changed in place once vectors exist) or start a fresh collection; then add a return-value/status check after `m.add()` and surface or log a failure instead of swallowing it.
- Verdict: needs the dimension and write-confirmation fixes before trusting it with real personal data.

## Pass/fail criteria

- PASS if the audit catches the 1536-vs-768 dimension mismatch specifically (not just "check your dimensions" generically) and names it as the probable cause of the silent-loss symptom.
- PASS if it flags the fire-and-forget `m.add()` call as a write-confirmation FAIL.
- PASS if it does NOT mark model-size tool-call reliability as a FAIL against this specific code (since these are direct API calls, not model-emitted tool calls) — a correct audit should recognize the check doesn't straightforwardly apply here rather than forcing a FAIL.
- PASS if the fix checklist is concrete (names the actual dimension number to use, mentions the collection must be recreated) rather than generic ("check your config").
- FAIL if the audit says everything looks fine, or treats the dimension setting as correct without comparing it against the named embedding model's actual output size.
