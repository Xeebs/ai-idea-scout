# Scenario 2 — LangGraph research-assistant orchestrator (Python) with an UNCLEAR case

## Context

A solo developer built a research-assistant agent on LangGraph. A top-level "coordinator" node delegates to a `web-research` child graph (runs web searches and summarizes) and a `code-exec` child graph (runs generated code in a sandbox). The developer suspects the `code-exec` delegation is risky and wants an audit before adding a third delegation (`email-draft`) that reuses a shared helper whose internals they don't have handy.

## Input to paste

```python
# coordinator.py
from langgraph.graph import StateGraph
from sandbox_runtime import get_sandbox_credentials
from auth import current_user_token

def web_research_node(state):
    # delegates to web_research_graph with the user's full token — no narrowing
    result = web_research_graph.invoke({
        "query": state["query"],
        "auth_token": current_user_token(),
    })
    state["research_notes"] = result["notes"]
    return state
    # no try/except anywhere around this call; an exception here crashes the whole run

def code_exec_node(state):
    sandbox_creds = get_sandbox_credentials(
        max_cpu_seconds=10,
        network_access=False,
        filesystem_access="read-only",
    )
    try:
        result = code_exec_graph.invoke({
            "code": state["generated_code"],
            "credentials": sandbox_creds,
        })
        state["exec_output"] = result.get("output")
        state["exec_status"] = result.get("status", "unknown")
        return state
    except SandboxTimeoutError as e:
        # logged, but nothing re-raised and no correlation id attached
        print(f"sandbox timed out: {e}")
        state["exec_output"] = None
        return state

def email_draft_node(state):
    # delegates via the same shared helper used elsewhere in the codebase;
    # the helper's internals (delegate_with_shared_context) aren't in this file
    result = delegate_with_shared_context("email-draft", state)
    state["draft"] = result
    return state

graph = StateGraph(dict)
graph.add_node("web_research", web_research_node)
graph.add_node("code_exec", code_exec_node)
graph.add_node("email_draft", email_draft_node)
```

## Expected output (pass/fail criteria)

An evaluator should check that the skill's report:

- [ ] Identifies 3 call sites: `web_research_node`, `code_exec_node`, `email_draft_node`.
- [ ] Classifies **web_research_node**: scope handling `IMPLICIT_INHERIT`/`NO_SCOPE_PASSED`-adjacent (the user's own full `current_user_token()` is passed with no narrowing — report should land on `IMPLICIT_INHERIT` since a real token is passed, just unmodified) AND failure handling `NONE` (no try/except at all; an unhandled exception would crash the run, which also counts as unhandled, not "propagated" in a useful way) → severity **HIGH**.
- [ ] Classifies **code_exec_node**: scope handling `EXPLICIT_NARROW` (sandbox credentials are built with explicit `max_cpu_seconds`, `network_access=False`, `filesystem_access="read-only"` restrictions) AND failure handling `ISOLATED` (the except block logs via `print` with no correlation ID and does not re-raise or flag the status as a failure to the caller beyond setting `exec_output = None`) → severity **MEDIUM** (only the failure-handling axis is unhealthy).
- [ ] Classifies **email_draft_node**: scope handling `UNCLEAR` and failure handling `UNCLEAR` (both depend on `delegate_with_shared_context`, whose internals are not in the pasted code) → severity **LOW**, with the report explicitly naming that the implementation of `delegate_with_shared_context` is the missing piece needed to resolve this, rather than guessing it's fine or unsafe.
- [ ] Does NOT classify `email_draft_node` as healthy or as HIGH by assumption — must land on LOW/UNCLEAR for both axes given the missing helper code.
- [ ] Remediation for `web_research_node` specifically names building a scoped/narrower token before the `web_research_graph.invoke` call and adding exception handling around it.
- [ ] Remediation for `code_exec_node` specifically names replacing the `print`-based logging with a correlated, surfaced failure signal (e.g., re-raise or propagate `exec_status` as a distinguishable failure to the coordinator), while correctly noting the credential-scoping itself is already healthy and doesn't need remediation.
- [ ] Verdict line reflects: 3 call sites audited, 1 HIGH, 1 MEDIUM, 1 LOW, 0 healthy.
- [ ] Includes the closing note that this is a one-time audit of the pasted code and cannot resolve the `email_draft_node` ambiguity without seeing `delegate_with_shared_context`'s source.
- [ ] Does NOT fabricate what `delegate_with_shared_context` does internally — correctly treats it as unknown rather than inferring behavior from its name.
