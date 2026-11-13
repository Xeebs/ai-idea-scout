# Scenario 1 — LangGraph support bot, three call sites, mixed quality

## Setup

A team runs a LangGraph-based customer-support agent. They've had two complaints this week where the bot answered a billing question confidently, but it turned out the customer's account history hadn't actually loaded. They paste three call sites.

## Input provided to the skill

**Framework**: LangGraph

**Code**:

```python
# 1. Tool call — uses LangGraph's prebuilt ToolNode
from langgraph.prebuilt import ToolNode

tool_node = ToolNode([lookup_order_status, issue_refund])
# ToolNode is used as-is, no custom wrapping — exceptions become a
# ToolMessage with content=str(exception) and status="error", added to state.

# 2. History retrieval — custom function, called before every model turn
def load_customer_history(customer_id: str) -> list[dict]:
    try:
        rows = db.query(
            "SELECT * FROM conversation_history WHERE customer_id = %s ORDER BY ts DESC LIMIT 20",
            (customer_id,),
        )
        return rows
    except DBConnectionError as e:
        logger.error(f"history fetch failed for {customer_id}: {e}")
        return []  # falls through to the graph as "no prior history"

# 3. Attachment fetch — customer uploads a screenshot of a billing issue
def fetch_attachment(url: str) -> bytes | None:
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.content
    except Exception:
        return None

# Caller:
image_bytes = fetch_attachment(attachment_url)
if image_bytes:
    messages.append({"role": "user", "content": [{"type": "image", "data": image_bytes}]})
# if image_bytes is None, nothing is appended at all — the model never
# sees the customer referenced an attachment
```

**Transcript excerpt** (optional context given): customer asks "why was I charged twice last week," bot responds with a confident answer based on zero history rows, never mentioning it couldn't load their history.

## Pass criteria

The audit output must:
1. Correctly classify call site 1 (ToolNode) as **SURFACES** — LangGraph's built-in behavior injects a `ToolMessage` with error content into state, which the model does see.
2. Correctly classify call site 2 (`load_customer_history`) as **SWALLOWED** — the except branch logs but returns `[]`, which is indistinguishable from "customer has no history," and nothing tells the model the fetch failed.
3. Correctly classify call site 3 (`fetch_attachment` + caller) as **SWALLOWED** — on failure, `None` is returned and the caller silently skips appending anything; the model never learns an attachment was referenced at all.
4. The findings for sites 2 and 3 each include a concrete fix as a code snippet (e.g., site 2: on exception, append a message to the LangGraph state like `{"role": "system", "content": "Customer history unavailable — do not assume no prior contact, ask the customer to summarize recent issues."}`; site 3: inject a similar message instead of skipping the append).
5. The rollup correctly identifies site 2 or site 3 (either is defensible) as the highest-priority fix, since both are SWALLOWED and directly explain the reported symptom (confident answer from a silently-empty history fetch).
6. Output does not recommend adopting a specific commercial middleware product.
7. Output does not misclassify the ToolNode site as SWALLOWED or UNSTRUCTURED just because no custom try/except is visible in the pasted code — it must recognize ToolNode's documented default behavior as SURFACES (or explicitly flag it as "assumed SURFACES per LangGraph's documented default — verify this instance hasn't disabled it," since the idea's own research notes this default has been inconsistent across versions).

## Fail conditions

- Treating the `except DBConnectionError: ... return []` block as safe because "it has error handling" without checking where `[]` ends up.
- Fabricating a line number when none was given in the pasted snippet.
- Skipping the attachment call site because it didn't look like a typical "tool call."
