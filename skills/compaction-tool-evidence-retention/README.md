# Compaction Tool Evidence Retention Audit

A paste-into-any-AI-chat prompt that forensically checks whether an AI agent's context-compaction summary lost exact tool-output evidence that a later claim or action depended on — and reconstructs the verbatim evidence to splice back in.

## Why this exists

Long-running AI coding/research agents (Claude Code, Codex CLI, Cursor, custom agent loops) periodically "compact" their context: the model summarizes the conversation so far to free up space, and everything after that point works from the summary instead of the full history. Summarization is lossy by nature — it paraphrases tool outputs (file diffs, command results, test failures, search hits) into prose. That's fine for narrative color, but it's a problem the moment a later answer depends on the *exact* content of one of those tool outputs: a line number, an error string, a specific value a command returned. When that happens, the agent either confabulates a plausible-sounding but wrong detail, or burns time re-running a tool it already ran once just to recover information it should still have had.

This prompt is a one-shot forensic audit for that exact failure. You give it (1) the compacted summary an agent produced and (2) the original tool outputs it was built from, and it tells you which claims in the summary are backed by real evidence, which ones have already drifted from the truth, and which ones are fine today but fragile if compacted again — then hands you back the exact text to reattach.

**This is a review tool, not a live fix.** It doesn't hook into a running agent or prevent evidence loss from happening in the first place — it's the diagnostic you run after the fact, on a session you already have in hand.

## Data source

**Manual.** You paste in the compacted summary and the original tool outputs yourself (or hand over a transcript/log file if you're using this inside a tool, like Claude Code, that can read a local file directly). This prompt does not connect to any live API, hook, or running agent session — it only works with whatever text or file you provide.

## What to hand it

1. **The compacted summary** — the actual post-compaction text the agent produced, pasted verbatim, exactly as the agent now sees it (not your memory of what it said).
2. **The original tool-call outputs it came from** — as many as you have: diffs, command stdout/stderr, stack traces, test results, search/grep hits, file contents the agent read. Paste the relevant ones verbatim, or hand over a transcript/session log file covering that window. If a claim in the summary might depend on a tool output you don't have, say so — the audit will mark that claim unverifiable rather than guess.
3. *(Optional, speeds things up)* **The specific thing that made you suspicious** — e.g. "the agent said the test failed on a null pointer at line 42, but I don't think that's what the stack trace actually said." Naming this lets the audit check that claim first.

If you only have the summary and none of the original tool outputs, say so up front — every finding will come back "unverifiable," and that's the honest answer, not a failure of the audit.

## What it does (the procedure)

1. **Finds every "evidence-dependent" claim in the summary** — any statement that asserts a specific, checkable detail that could only have come from a tool's output (a line number, exact error message, variable name, test result, specific returned value, file path, or diff content). General narrative or decision statements ("we decided to use Postgres") are left alone — they don't depend on exact tool content, so they're out of scope.
2. **Checks how each claim is expressed**: quoted/cited directly from the tool output (lower risk), or paraphrased in the summary's own words with nothing to check it against later (highest risk — this is exactly where confabulation sneaks in).
3. **Cross-checks every claim against the original tool outputs you provided**, and sorts each one into:
   - **VERIFIED** — matches the original exactly, or is a faithful restatement.
   - **MISMATCH** — contradicts the original, or isn't in it at all. The agent has already confabulated this detail.
   - **AT-RISK** — matches today, but only as a paraphrase with no durable pointer to the source — if this summary gets compacted again, nothing is left to check it against, and the drift compounds.
   - **UNVERIFIABLE** — no original tool output covering this claim was provided; the audit says so rather than guessing.
4. **For every MISMATCH and AT-RISK claim**, it pulls the exact verbatim passage from the original tool output that should have been cited, labels it (e.g. `[evidence-1]`), and writes a one-line correction: what the summary said versus what the real evidence says.
5. **Scores an overall verdict** for the session: CLEAN, EVIDENCE LOSS CONFIRMED (at least one mismatch), EVIDENCE LOSS LATENT (no mismatch yet, but fragile paraphrases exist), or UNVERIFIABLE (not enough original material to check).
6. **Self-checks before answering**: every quote in the report — from the summary or the originals — has to be something it can point to verbatim in what you actually provided. If it can't find a quote to back a claim, it marks that claim unverifiable instead of asserting a verdict it can't support.

## Output format

You'll get back:

1. **Session verdict** — one line: CLEAN / EVIDENCE LOSS CONFIRMED / EVIDENCE LOSS LATENT / UNVERIFIABLE, with a one-sentence reason.
2. **Evidence-dependent claims found** — a table: the claim (quoted), how it was expressed (cited vs. paraphrased), its classification, and the matching (or contradicting, or missing) original passage.
3. **Corrected context blocks** — for every MISMATCH and AT-RISK claim, the real verbatim evidence under a short reference label, plus the exact correction to splice back into the summary.
4. **Evidence gaps** — what original material was missing, if anything.
5. **Recommendation** — if a mismatch was found, a plain statement that anything already decided or acted on based on the bad claim should be re-checked against the real evidence before you trust it further.

## Guardrails (what this will never do)

- It will never call a claim VERIFIED or MISMATCH without a real quote from what you provided backing that call — no evidence means "unverifiable," never a coin-flip guess.
- It will never invent or misquote a passage that isn't actually present in the summary or the original tool outputs you gave it.
- It will never claim to have checked tool calls from the live session that you didn't paste in or hand over as a file — the audit is scoped strictly to what you actually gave it.
- If you only give it the summary with no original tool outputs, it will mark everything unverifiable and say so plainly, rather than producing a report that looks more thorough than the evidence supports.
- It will never silently edit your actual transcript or summary file — it only produces a report and corrected text for you to splice back in yourself.
- It will not pretend to be an always-on fix. If what you actually want is for tool evidence to be retained automatically on every future compaction (so you never have to run this audit by hand again), that's a different kind of build — a hook wired into your agent harness's compaction step — not something a pasted-in chat prompt can do.

## How to use it

Paste this whole README into any AI chat tool (Claude, ChatGPT, etc.) along with your compacted summary and original tool outputs, and say: "Run the compaction tool evidence retention audit on this." The model should follow the Procedure above and return the Output format above.
