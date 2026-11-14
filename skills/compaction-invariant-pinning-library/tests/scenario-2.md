# Scenario 2 — LangGraph research agent, no transcript available (provisional design)

## Input

**Workflow description**: A LangGraph-based research agent runs overnight literature-review jobs: given a research question, it searches academic APIs and the web, reads papers, extracts findings, and iteratively refines a synthesis document. A typical job runs 6-10 hours with a custom checkpointer that summarizes the message history every 150 messages, which usually means 3-6 summarization passes per job.

**Compaction config**: Custom — the checkpointer's summarization prompt currently just says "Summarize the conversation so far, keeping key facts." No pinning mechanism exists yet.

**Transcript excerpt**: none available — the user is designing this before running the agent for the first time, based only on the workflow description above.

## Expected output (what to check)

- [ ] **Workflow Summary** correctly identifies this as a research/synthesis agent on LangGraph with a custom checkpointer, 3-6 compactions per job.
- [ ] **Extracted Candidates** section is explicitly and visibly labeled "hypothetical (no transcript provided)" — it must not present generated examples as if they were pulled from real data.
- [ ] The hypothetical examples are still domain-appropriate and plausible for a literature-review agent — e.g., a tried-and-outcome item like "searched arXiv for X, returned 0 relevant results, outcome: dead end" or a hard constraint like "only cite peer-reviewed sources, not preprints" or "stay within the stated research question's scope" — rather than generic placeholders copied from a coding-agent example.
- [ ] **Pinned-Slot Schema** is still produced in full (schema design doesn't require a transcript — only the extracted-candidates step is gated on it) with example rows drawn from the hypothetical items, clearly marked as illustrative.
- [ ] **Token Budget** is still given as a concrete recommendation reasoned from the 3-6 compactions/job and expected PIN volume for a research workflow (likely fewer hard constraints than a coding migration, but more "already searched X, found nothing" items) — not skipped just because there's no transcript.
- [ ] **Classification Rules** are written generally enough to apply once the agent actually runs and produces real transcripts — not hedged into uselessness just because the current pass is provisional.
- [ ] **Validation Status** explicitly says "provisional (no transcript provided)" and names a concrete next step: run the agent once, capture the real transcript around its first 1-2 compactions, and re-run this same design process against that real data to confirm or correct the hypothetical classification.
- [ ] The report does not claim any measured outcome (e.g., it must not say anything like "this will reduce repeated searches by X%") — only a design hypothesis.

**Pass** if the report clearly separates "what we know" (workflow shape) from "what's guessed" (candidate items) and still produces a complete, usable schema/budget/rules the user could start from. **Fail** if it either refuses to produce output without a transcript, or silently presents hypothetical examples as if they were extracted facts.
