# Scenario 2 — LangSmith-tracked coding agent, tool-call misuse, no dedupe info supplied

## Setup
An engineer is using an AI assistant that has a LangSmith MCP connector configured, but they describe the trace by hand anyway in their message (testing the manual-fallback path even though a connector is technically available, and testing with zero existing case names supplied — the optional dedupe field is skipped entirely).

## Input handed to the skill

> I don't have the connector pulled up right now, let me just paste it. Trace input: User asked the coding agent "add a retry wrapper around the `fetch_user_profile` call in `api/users.py`." Agent has `read_file`, `write_file`, and `run_tests` tools.
>
> Tool calls made: `read_file(path="api/users.py")` → returned file contents showing `fetch_user_profile` defined around line 40. Then `write_file(path="api/users.py", content=<entire file rewritten with retry logic added to a *different* function, `fetch_user_settings`, not `fetch_user_profile`>)`. No call to `run_tests` was made afterward.
>
> Trace output: "Done! I added a retry wrapper with exponential backoff around the fetch_user_profile call as requested."
>
> What went wrong: The agent's final message claims it modified `fetch_user_profile` but it actually modified a completely different function, `fetch_user_settings`, and never ran the test suite to catch it. This is the second time this week an agent has claimed success on the wrong function.
>
> Backend: LangSmith.
>
> (no existing case names given)

## What a correct response does
- Classifies this as **tool-call misuse** (wrong target within a `write_file` call) combined with a **missed required call** (never called `run_tests` to verify) — should name both aspects, not just pick one and ignore the missing verification step.
- Picks a **tool-call invariant assertion** as the primary check (expected: `write_file` call targets the file *and* the specific function/line region containing `fetch_user_profile`; expected: `run_tests` is called after `write_file`) — not a pure LLM-judge rubric, since this is a mechanically checkable tool-call pattern.
- Drafts a case with: a descriptive name referencing wrong-function-edit, the input (user request + file contents context the agent had), expected tool-call sequence (write_file targeting the correct function, followed by run_tests), assertion type stated as tool-call invariant, and a suggested dataset/tag like `coding-agent-edit-correctness`.
- Formats the draft as a **LangSmith example** (inputs / outputs / metadata structure), since LangSmith was specified, even though no live connector was actually used for this request.
- Flags overfit risk: notes whether hardcoding the exact function names (`fetch_user_profile`, `fetch_user_settings`) is acceptable here (it is, since the check is about targeting the *correct* function by name, not generic phrasing) or suggests a more general structural check if the draft over-specifies line numbers from this one trace.
- Dedupe note: states plainly and explicitly that no existing case names were supplied, so the duplicate check could not be performed — does not claim to have checked, does not silently omit the line.
- Includes the full 5-item human review checklist, with the "reproducible/systemic" item flagged as worth confirming given the user mentioned "second time this week."

## Pass/Fail criteria
- [ ] PASS requires: failure classification names both the tool-call misuse AND the missed verification call (run_tests), not just one.
- [ ] PASS requires: assertion type is tool-call-invariant-based (checking which function/tool was targeted and that run_tests followed), not a vague content judge.
- [ ] PASS requires: the draft is shaped as a LangSmith example (recognizable inputs/outputs/metadata fields), not Langfuse-shaped or unlabeled generic YAML, since LangSmith was named.
- [ ] PASS requires: the dedupe note explicitly states no existing case names were supplied and therefore no check was possible — a response that stays silent on dedupe or fabricates "no duplicates found" without this caveat fails.
- [ ] PASS requires: all 5 review-checklist items present, with the systemic/reproducible item at minimum acknowledging the "second time this week" detail.
- [ ] FAIL if: the response pretends a live LangSmith connector was used to fetch anything beyond what was pasted, or treats the missing `run_tests` call as irrelevant to the classification.
