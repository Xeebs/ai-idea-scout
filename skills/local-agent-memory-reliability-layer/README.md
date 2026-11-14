# Local Agent Memory Reliability Auditor

A prompt template for auditing a hand-built persistent-memory integration for a local or small-model AI agent (Ollama, llama.cpp, LM Studio) against known silent-failure modes, and getting back a prioritized fix checklist — not a vague "looks fine" or a rewrite of your whole stack.

## When to use this

You've wired up your own memory layer for a local AI assistant — Mem0 on top of Qdrant, raw sqlite-vec, a flat markdown-file memory plugin in LM Studio, or your own custom record/query script — and either:

- you want a reliability check before you trust it with real personal data (journaling, health notes, financial notes, ongoing project context), or
- something's already gone wrong: a memory you told it to save isn't there next session, the assistant repeats questions it should already know, you're getting contradictory answers across sessions, or nothing errored at write time but the memory is just... gone.

This is a one-time review of a paste, not a tool that runs your memory system for you.

## What you need to hand over

**Data source: Manual.** Paste the actual materials — no connector, no live access to your machine is used or needed:

1. Your memory integration's config/code: which embedding model you're using, the vector store type and its configured dimension/schema, the connection snippet (redact any API keys/secrets first), and the write/insert function if you have it.
2. The local model name and roughly how many parameters it has (e.g., `llama3.2:1b`, `qwen2.5:7b`, `llama3.1:70b`).
3. Optional: any error logs, or just a plain description of what went wrong ("I told it my dog's name and it forgot by the next session").

If you can only describe your setup in words with no actual config or code to paste, say so — the audit below needs the real materials to be accurate; a description alone will get you a request for the paste, not a guess dressed up as an answer.

## The procedure to run

Paste this whole prompt, with your materials attached, into any AI chat tool:

---

*You are auditing my local-agent persistent-memory setup for reliability, not security. Here is my setup: [paste config/code, embedding model name, vector store + dimension setting, write function if available, local model name + parameter size, and any symptoms/logs].*

*Please:*
1. *State the architecture in one line (e.g., Mem0 + Ollama + Qdrant, or raw sqlite-vec, or a flat-file plugin).*
2. *Check embedding-dimension consistency: identify my embedding model's known output dimension (nomic-embed-text=768, mxbai-embed-large=1024, all-minilm=384, bge-small=384, bge-base=768, bge-large=1024, OpenAI text-embedding-3-small=1536) and compare it against my configured store dimension. If the embedding model isn't stated, mark this UNKNOWN rather than assuming it's fine.*
3. *Check whether my write/insert calls confirm success (checking a return value or row count) or are fire-and-forget.*
4. *Check whether the same embedding model is used for both writing and querying.*
5. *If my local model is under roughly 7B parameters and memory writes depend on it correctly emitting a structured tool call, flag that as a known-fragile path and recommend a deterministic fallback that doesn't depend on tool-call compliance.*
6. *Check whether any fallback/degraded-mode path exists at all when a structured write fails.*
7. *Check whether contradicting or duplicate memories get deduped/versioned, or would just silently coexist.*
8. *Return your findings as a table: Check | Status (PASS/FAIL/UNKNOWN) | Evidence from what I pasted | Fix. Never mark something PASS if I didn't actually show you that setting — mark it UNKNOWN and tell me what's missing.*
9. *Give an overall risk rating (LOW/MEDIUM/HIGH) — any silent-failure-class FAIL (dimension mismatch, no write confirmation) is at least MEDIUM regardless of anything else.*
10. *Give a prioritized, concrete fix checklist — not vague advice.*
11. *End with one sentence: is this safe to trust as-is for low-stakes use, or does it need the fixes above before I trust it with real personal data?*

*Do not recommend switching to a hosted commercial memory service — I'm keeping this local on purpose; recommend fixes within that constraint. Do not recommend stuffing more conversation history into context as a fix for recall problems — that's been shown to actively hurt recall, not help it. Do not evaluate this for security issues (secrets handling, prompt injection) — this is a reliability audit only.*

---

## What you get back

A short report: the architecture in one line, a findings table covering embedding dimension match, write confirmation, write/read embedding parity, model-size tool-call reliability, fallback path existence, and dedupe/contradiction handling — each with PASS/FAIL/UNKNOWN, the evidence from what you pasted, and a concrete fix where it's not a plain PASS — followed by an overall risk rating and a one-sentence verdict on whether to trust the setup as-is.

## What this will not do

- It will not tell you your setup is fine when you didn't actually show it the relevant setting — it marks that UNKNOWN, not PASS.
- It will not tell you to just switch to a hosted memory product — the entire premise is staying local.
- It will not tell you to cram more chat history into the context window to fix forgetting — documented testing shows that actively makes recall worse.
- It will not check your setup for security problems (leaked keys, prompt injection) — that's a different review; ask for that separately if you want it.
- It will not run or build your memory system — it only reviews what you paste.
