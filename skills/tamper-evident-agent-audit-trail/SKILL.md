---
name: tamper-evident-agent-audit-trail
description: Cross-checks a coding agent's self-reported execution trace against the actual diff/filesystem changes from the same session to find undisclosed actions, phantom log entries, or described-vs-actual mismatches — a one-shot forensic audit for a session you suspect was mishandled, tampered with, or misreported. Use after the fact on a specific session, not as a continuous monitor.
---

# Trace-vs-Diff Forensic Audit

## When to use this
Someone has a coding agent's own self-reported log (tool calls, file edits, shell commands it says it ran) for one specific session, plus independent evidence of what actually changed (a `git diff`, `git log -p`, a before/after file listing, or CI artifacts) — and they suspect, or just want to confirm, that the log is a complete and accurate record of that session. Common triggers: "this PR looks bigger than what the agent reported," "the agent said it only edited the README but something else in the diff changed," a security review before merging agent-authored code with broad write access, or responding to a specific incident where an agent may have hidden or spoofed part of what it did (per the documented finding that major coding-agent harnesses can tamper with their own traces undetected). This is a **post-hoc audit of one session**, not an always-on defense — it works with whatever trace and diff the user already has, and does not require any hardened logging infrastructure to already be running.

Do not use this for: judging code quality, reviewing a PR's correctness, or auditing multiple sessions in bulk without adapting the procedure per session — one invocation covers one trace + one diff pair.

## Inputs
**Data source**: Manual — the user pastes or uploads (1) the agent's self-reported execution trace/log for the session (tool-call list, chat transcript with tool-use blocks, or harness-exported log — JSON, markdown, or plain text, any format is fine as long as it names actions and targets) and (2) independent evidence of the actual changes from that same session (`git diff`/`git log -p` output, a list of modified files with before/after hashes or timestamps, or a CI build's file-change report). No mature connector reads both of these automatically and cross-checks them today — that automation is exactly the gap this skill fills manually; if the user has git access in-session (e.g. inside Claude Code with repo access), they may run `git diff` themselves and paste the output, or ask the skill to run it, but the comparison logic itself is manual, not API-driven.

If the user supplies only one of the two artifacts, say so immediately and stop — a trace with nothing to check it against, or a diff with no trace to compare, cannot produce a finding, only an unverified assumption.

## Procedure
1. **Parse the claimed actions** from the trace into a list: for each entry, extract action type (file create/edit/delete, shell command, other tool call), target path(s) or command text, and any timestamp/ordering given.
2. **Parse the observed changes** from the diff/evidence into a list: for each changed file, extract change type (added/modified/deleted/renamed) and, where available, a one-line summary of what changed (lines added/removed, or the command's actual effect if shell output/exit codes are included).
3. **Cross-reference the two lists** and classify every item into one of four buckets:
   - **Undisclosed action** — an observed change with no corresponding trace entry at all. This is the highest-severity finding: the agent did something its own report never mentions.
   - **Phantom entry** — a trace entry claiming a write-affecting action (edit/create/delete) with no corresponding effect in the diff. Note the benign explanation (the command may have been read-only, no-op, or failed silently) alongside the finding; don't default to "this proves tampering" without naming that alternative.
   - **Described-vs-actual mismatch** — entry and change both exist for the same target, but the claimed effect doesn't match the actual one (e.g., trace says "added a comment" but the diff shows most of the file rewritten; trace says "ran tests" but no test-related files or outputs appear anywhere).
   - **Match** — entry and change correspond and the described effect is consistent with the actual one. Still list these briefly so the reader can see full coverage, not just the flagged items.
4. **Check internal consistency of the trace itself**: timestamps monotonic and plausible for the work claimed, no duplicate entries claiming the same action twice, no unexplained large time gaps during what should have been continuous activity. Flag anomalies here even if they don't map to a diff discrepancy.
5. **Assign an overall verdict**:
   - `CLEAN` — every observed change has a matching trace entry, all phantom entries have a plausible benign explanation, no internal anomalies.
   - `SUSPICIOUS` — one or more described-vs-actual mismatches or internal anomalies, but no undisclosed write-affecting action.
   - `TAMPERED` — at least one undisclosed action that changed a file or ran a command, with no trace entry at all.
6. **Write the report** in the format below. Always name the specific trace line and diff line/hunk behind each finding — a finding with no citation back to the provided artifacts is not usable evidence.

## Output format
```
## Session Scope
<what trace file/log and what diff/evidence were compared; note explicitly if their time ranges or file scopes don't fully overlap>

## Verdict: CLEAN | SUSPICIOUS | TAMPERED

## Findings
### Finding 1 — <file/command>
- Type: Undisclosed action | Phantom entry | Described-vs-actual mismatch | Internal anomaly
- Trace evidence: <quote or line reference, or "absent from trace">
- Diff evidence: <quote or hunk reference, or "absent from diff">
- Plausible benign explanation (if any): <...>
- Severity: HIGH (undisclosed write-affecting action) | MEDIUM (mismatch/anomaly) | LOW (phantom entry with a clear benign cause)

(repeat per finding, ranked HIGH -> LOW; omit this section entirely if none)

## Matched Actions (brief)
<one line per action where trace and diff agree, just enough to show coverage>

## Next Step
<one line: if TAMPERED or SUSPICIOUS, recommend the specific follow-up (re-run session in a sandboxed observer, escalate to security, request the missing artifact); if CLEAN, say what this audit does and does not prove (consistency between these two artifacts, not that the harness itself is incapable of tampering in general)>
```

## Guardrails
- Never state a verdict stronger than the evidence supports — a single phantom entry with an obvious benign cause (e.g., a `grep` or read-only `cat`) is not grounds for `TAMPERED`; reserve that verdict for at least one genuinely undisclosed write-affecting action.
- Never fabricate trace content or diff content the user didn't provide, and never assume a file "probably" changed in a way consistent with the trace absent actual diff evidence for it.
- If the trace and diff cover different scopes (different time windows, different file sets, different commits) say so explicitly before reporting findings — a mismatch caused by comparing non-overlapping scopes is an input problem, not evidence of tampering.
- Always offer the benign explanation for a phantom entry or mismatch before treating it as suspicious; this skill's job is accurate classification, not maximizing the number of flagged findings.
- This is a one-shot audit of two static artifacts, not a running defense — never imply it provides ongoing protection, and always close with what it does/doesn't prove, pointing toward an out-of-process hardened logger (continuous observation outside the agent's write access) as the actual fix if this audit repeatedly turns up tampering.
