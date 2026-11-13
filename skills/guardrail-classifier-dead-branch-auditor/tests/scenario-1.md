# Scenario 1 — real-shaped MIRA-style dead category

## Input the user pastes

> Can you audit this classifier? It's supposed to be able to return `off_topic` but I think a support ticket I just closed implies it never does.

```python
def classify_intent(message: str) -> str:
    """
    Classifies a user message into one of:
    - greeting
    - order_status
    - complaint
    - off_topic
    """
    msg = message.lower()

    if "hello" in msg or "hi " in msg or "hey" in msg:
        return "greeting"
    elif "order" in msg or "track" in msg or "shipment" in msg or "delivery" in msg:
        return "order_status"
    elif "bad" in msg or "angry" in msg or "refund" in msg or "broken" in msg:
        return "complaint"
    else:
        return "complaint"  # TODO: should this be off_topic? revisit after Q3 refactor
```

## Expected output (pass/fail criteria)

An evaluator should check the response for all of the following:

1. **Declared categories section** lists exactly four categories (`greeting`, `order_status`, `complaint`, `off_topic`), sourced from the docstring. — **FAIL** if it invents a different list or omits one.
2. **Branch trace** lists all four code paths in execution order (the three `elif` branches plus the final `else`), correctly noting that all four conditions are static string/substring checks (no model/API dependency). — **FAIL** if it misses the final `else` branch or mislabels any condition as unverifiable.
3. **Reachability verdict** marks:
   - `greeting`, `order_status`, `complaint` as **REACHABLE**, each with a concrete example input (e.g., `"hi there"`, `"where is my order"`, `"this is broken, refund me"`) that plausibly triggers that branch and skips earlier ones.
   - `off_topic` as **UNREACHABLE (no matching branch)**, with the explicit reasoning that no branch in the function ever returns the string `"off_topic"` — the final `else` returns `"complaint"` again instead. — **FAIL** if `off_topic` is marked REACHABLE, or if the verdict doesn't name the specific structural reason (the duplicated `"complaint"` return).
4. **Suggested fixes** proposes changing the final `else` branch's return value from `"complaint"` to `"off_topic"` — a one-line fix. — **FAIL** if it proposes a broader rewrite or doesn't name the exact line to change.
5. Does **not** flag any branch as UNVERIFIABLE (everything here is a pure string check) and does **not** fabricate an undeclared-output finding (there isn't one — every return value in the code is one of the four declared categories, just unevenly distributed).

**Overall pass**: criteria 1–4 must all be satisfied for a pass. This is the core bug class the skill exists to catch, so a miss on #3 (off_topic) is an automatic fail regardless of the rest.
