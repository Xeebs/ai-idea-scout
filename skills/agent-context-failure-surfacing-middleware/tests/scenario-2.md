# Scenario 2 — CrewAI coding assistant, unbounded retry and unstructured errors

## Setup

A small team built an internal CrewAI-based coding assistant that answers questions about a codebase using a "fetch file contents" tool, retrieves prior session notes from a memory store, and occasionally retries a flaky internal API. They want to know if their error handling is actually model-visible before they ship it more broadly.

## Input provided to the skill

**Framework**: CrewAI

**Code**:

```python
# 1. Tool wrapper — fetches file contents from the repo
class FetchFileTool(BaseTool):
    name = "fetch_file"
    description = "Fetch the contents of a file in the repo"

    def _run(self, path: str) -> str:
        try:
            with open(path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error: {e}"  # returned as the tool's output string

# 2. History retrieval — pulls prior session notes from an internal memory API
def get_session_notes(session_id: str, attempt: int = 0) -> str:
    try:
        resp = memory_api.get(session_id)
        return resp.text
    except MemoryAPITimeout:
        if attempt < 999:
            time.sleep(1)
            return get_session_notes(session_id, attempt + 1)
        return ""

# 3. Attachment fetch — pulls a linked design doc referenced in the ticket
def fetch_design_doc(doc_url: str) -> str:
    try:
        resp = requests.get(doc_url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        msg = f"[SYSTEM NOTE: could not fetch design doc at {doc_url} — error: {e}. Do not assume its contents; ask the user to paste the relevant section if needed.]"
        return msg  # this string is appended directly as a message in the crew's context
```

## Pass criteria

The audit output must:
1. Classify call site 1 (`FetchFileTool._run`) as **UNSTRUCTURED** — the model does receive something on failure ("Error: ..."), but it's a raw exception string with no guidance on what's missing or what to do, not a structured failure signal.
2. Classify call site 2 (`get_session_notes`) as both **SWALLOWED** (eventually returns `""`, indistinguishable from "no notes exist") **and** flags the recursive retry (up to 999 attempts with 1s sleep) as **RETRY_LOOP** — a near-unbounded retry that will hang the request for roughly 15+ minutes before silently giving up.
3. Classify call site 3 (`fetch_design_doc`) as **SURFACES** — the returned message explicitly names what failed, the scope (this doc), and what the model should do (ask the user to paste the section).
4. Provides a concrete fix for site 1 (e.g., return a structured string naming the file path and that it's unreadable, suggesting the model ask for the right path or confirm the file exists) and for site 2 (both: fix the eventual SWALLOWED `return ""` to return a structured failure message, and separately cap/shorten the retry count or escalate after a small number of attempts instead of 999).
5. Does NOT flag call site 3 as a problem — it must appear in the "Confirmed-safe" section, not the Findings section.
6. The rollup correctly identifies the RETRY_LOOP in call site 2 as high-priority alongside its SWALLOWED classification, given it causes both a long hang and a silent failure.

## Fail conditions

- Classifying call site 1 as SURFACES just because it returns a string rather than raising — an unstructured "Error: {e}" string does not meet the SURFACES bar.
- Missing the RETRY_LOOP on call site 2 because the classification focused only on the final SWALLOWED return value.
- Recommending site 3 be changed when it's already a correct, structured failure signal.
- Reporting on a fourth call-site type not present in the code (e.g. inventing a "cache" call site) instead of only auditing tool/history/attachment sites actually provided.
