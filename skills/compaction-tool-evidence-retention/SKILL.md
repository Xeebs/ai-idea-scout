---
name: compaction-tool-evidence-retention
description: One-shot forensic audit of an already-compacted agent session — finds claims in the compacted summary that depend on a tool output's exact content (a line number, error string, diff hunk, test result, specific value) but only survived as a paraphrase, then reconstructs a corrected context block reattaching the verbatim evidence. Use after a compacted session produced a wrong or unverifiable answer, not for wiring an always-on evidence store into a live compaction pipeline (separate infra build).
---

# Compaction Tool Evidence Retention Audit

## When to use this
Reach for this the moment someone has a specific agent session (Claude Code, Codex CLI, Cursor, a custom agent loop) that ran long enough to trigger context compaction — manual or automatic — and afterward the agent gave an answer, made a decision, or took an action that depended on the exact content of an earlier tool call (a file diff, a command's stdout/stderr, a test failure's stack trace, a search hit) rather than just whether that tool call happened. Typical triggers: "the agent just confabulated a detail about a diff from three compactions ago," "I want to check whether this answer is trustworthy before I act on it," or "we're about to re-run an expensive tool call just to recover information the agent should already have had."

This is a one-shot forensic review of material already available to you (pasted, or read from a transcript/log file on disk). It is not:
- a live, always-on compaction hook that writes every tool result to a content-addressed evidence store automatically inside Claude Code/Codex/Cursor's own compaction step (that's the runtime-infrastructure half of this idea — see `ideas/compaction-tool-evidence-retention.md`'s Project section — and needs a real hook integration, not a chat skill), and
- a general compaction-quality reviewer that checks for any kind of information loss — this specifically checks whether claims that need a tool output's *exact* content got that content right, not whether the summary is well-written or complete in general.

## Inputs
**Data source**: Manual — the user pastes the compacted summary and the original tool-call outputs directly into the chat (or points to a transcript file the agent reads locally with its Read tool); there is no live connector to a running agent session's compaction hook in this skill. (Context: the parent idea's Data Sources field is Connected — the always-on evidence store reads the live tool-call event stream directly via the host harness's PreCompact hook. That classification describes the Project half of this idea, the persistent middleware. This skill is the design/review half: it works from whatever the user pastes or hands over as a file in this session, not a live hook connection, so for this skill specifically the input is Manual. If the session is still open in Claude Code and compaction hasn't wiped the transcript file yet, the user can point this skill at `transcript.jsonl`/the session log directly instead of pasting — that's still Manual in this taxonomy's sense, since it's the skill reading a static file the user handed it, not querying a live API or MCP connector.)

Collect, if not already given:
1. **The compacted summary or post-compaction output to audit** — the actual text the compaction step produced, verbatim, as the agent now sees it.
2. **The original tool-call outputs it was derived from**, as fully as the user has them: diffs, command stdout/stderr, test failures and stack traces, search/grep hits, file contents read during the session — whichever ones the summary's claims might depend on. If the user has a full transcript or session log instead of hand-picked excerpts, that's even better; paste the relevant window or point to the file.
3. *(Optional but valuable)* **The specific downstream claim or action that triggered concern** — e.g. "the agent said the test failure was a null pointer on line 42, but I'm not sure that's right" — so the audit can prioritize that claim first instead of scanning the whole summary cold.

If the user has only the compacted summary with no original tool outputs at all, say so up front: every evidence-dependent claim will come back UNVERIFIABLE, and the audit should state that plainly rather than silently producing a report that looks more conclusive than the evidence supports.

## Procedure
1. **Extract every evidence-dependent claim from the summary.** An evidence-dependent claim is any statement in the compacted summary that asserts a specific, checkable detail that could only have come from a tool's output: a line number, variable/function name, exact error message or exception type, a test pass/fail count, a specific value returned by a command, a file path, a diff's actual before/after content, or a search result's content. Quote each one verbatim with its location in the summary. Do not flag narrative/decision claims that don't depend on exact tool content ("we decided to use Postgres," "the team agreed to retry later") — those are out of scope for this audit.
2. **For each evidence-dependent claim, check how it's expressed in the summary:**
   - **Verbatim-cited** — the summary quotes the tool output directly or clearly references a durable pointer to it (a file path plus line number, a stored artifact ID). Lower risk by construction, but still verify against the original in step 3.
   - **Paraphrased** — the summary restates the detail in its own words without quoting the source (e.g. "the test failed due to a type mismatch" standing in for an actual stack trace). This is the highest-risk category — paraphrase is exactly where confabulation enters.
3. **Cross-reference every claim against the provided original tool outputs.** Search for the matching passage and classify:
   - `VERIFIED` — the claim's specific detail matches the original tool output exactly (or is a faithful, non-lossy restatement of it).
   - `MISMATCH` — the claim's detail contradicts or doesn't appear in the original tool output at all — confabulation has already occurred. This is the finding that matters most; surface it first in the output.
   - `AT-RISK` — the claim currently matches the original, but is expressed only as a paraphrase with no durable pointer back to the source — if this summary is compacted again, the next pass has nothing but this paraphrase to work from, and drift compounds. Flag these even though nothing is wrong yet.
   - `UNVERIFIABLE` — no original tool output covering this claim was provided. Never upgrade this to VERIFIED or MISMATCH on a guess; say plainly what's missing.
4. **For every `MISMATCH` and `AT-RISK` claim, reconstruct a corrected context block**: pull the exact verbatim passage from the original tool output that the claim should have cited, assign it a short reference ID (e.g. `[evidence-1]`), and write the one-line correction showing what the summary should have said instead (quoting or pointing to `[evidence-1]`) versus what it actually said.
5. **Score an overall session verdict:**
   - `CLEAN` — no evidence-dependent claims found, or all are `VERIFIED` with durable pointers.
   - `EVIDENCE LOSS CONFIRMED` — at least one `MISMATCH` found.
   - `EVIDENCE LOSS LATENT` — no `MISMATCH`, but one or more `AT-RISK` claims exist (correct today, fragile under further compaction).
   - `UNVERIFIABLE` — insufficient original material was provided to check most claims.
6. **Self-check before returning**: every quoted passage — from both the summary and the originals — must be copy-paste-traceable to text actually present in what the user provided. If a quote can't be located verbatim in the provided material, delete it and mark that claim `UNVERIFIABLE` instead of asserting a verdict you can't back with the evidence on hand.

## Output format
A structured report:
1. **Session verdict**: `CLEAN` / `EVIDENCE LOSS CONFIRMED` / `EVIDENCE LOSS LATENT` / `UNVERIFIABLE`, one line, plus a one-sentence reason.
2. **Evidence-dependent claims found**: a table — quoted claim, expression (verbatim-cited / paraphrased), classification (`VERIFIED` / `MISMATCH` / `AT-RISK` / `UNVERIFIABLE`), and the matching (or contradicting, or missing) original passage.
3. **Corrected context blocks**: for every `MISMATCH` and `AT-RISK` claim, the reconstructed `[evidence-N]` block — the verbatim original passage, a short label, and the one-line correction to splice back into the summary.
4. **Evidence gaps**: explicit note on what original material wasn't provided, if anything — omit only if nothing is missing.
5. **Recommendation**: if any `MISMATCH` was found, say plainly that any downstream action already taken on the bad claim should be re-checked against the real tool output before trusting it further.

## Guardrails
- Never classify a claim `VERIFIED` or `MISMATCH` without a verbatim quote from the provided original material backing that classification — missing evidence means `UNVERIFIABLE`, never a guess rounded toward either extreme.
- Never fabricate or paraphrase-as-if-quoted a passage that isn't actually present in what the user provided, in either the summary or the originals.
- Never claim this review covers tool calls that happened in the live session but weren't included in what was pasted or handed over as a file — scope the audit explicitly to the material actually provided.
- Never present a one-sided input (summary only, no original tool outputs) as a conclusive audit — mark every evidence-dependent claim `UNVERIFIABLE` in that case and say why in the Evidence gaps section.
- Never silently edit the user's actual session or summary file — this skill produces a report and corrected context blocks for the user to splice back in manually; it does not act on a live session.
- Never confuse this skill with the always-on evidence store project — if the user wants tool outputs retained automatically on every future compaction, say clearly that's a separate hook-integration build, not something a chat-pasted audit does.
