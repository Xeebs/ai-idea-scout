# Scenario 2 — clean classifier (no bug) plus one undeclared output

## Input the user pastes

> Reviewing this before merge — want to make sure nothing's dead before it goes into our guardrail stack.

```python
from enum import Enum

class RequestCategory(str, Enum):
    URGENT = "urgent"
    NORMAL = "normal"
    FLAGGED = "flagged"
    SPAM = "spam"

def classify_request(text: str) -> str:
    t = text.strip().lower()

    if len(t) == 0:
        return RequestCategory.SPAM.value

    if any(w in t for w in ["urgent", "asap", "help", "now", "emergency", "please"]):
        return RequestCategory.URGENT.value

    if any(w in t for w in ["buy now", "click here", "free money"]):
        return RequestCategory.FLAGGED.value

    if len(t) > 2000:
        return "needs_review"  # not in RequestCategory enum — added later for long messages

    return RequestCategory.NORMAL.value
```

## Expected output (pass/fail criteria)

1. **Declared categories section** lists `urgent`, `normal`, `flagged`, `spam`, sourced from the `RequestCategory` enum. — **FAIL** if it treats `needs_review` as a fifth declared category (it is a return value, not an enum member).
2. **Branch trace** lists all five branches (empty-string check, urgent keywords, flagged keywords, long-message check, final normal fallback) in order, all marked as static/traceable (pure string/length checks, no model or API dependency). — **FAIL** if any real branch is omitted or mislabeled unverifiable.
3. **Reachability verdict** marks all four enum categories **REACHABLE**, each with a concrete example input that structurally justifies why it skips earlier branches:
   - `spam`: empty string `""`.
   - `urgent`: an input containing one of the urgent keywords and not empty, e.g. `"need help now"`.
   - `flagged`: an input containing a flagged phrase but none of the urgent keywords, e.g. `"click here for a free money offer"` (must note it contains none of "urgent/asap/help/now/emergency/please").
   - `normal`: an input matching none of the above and under 2000 characters, e.g. `"What are your store hours?"`.
   - **FAIL** if any of the four is incorrectly marked UNREACHABLE, or if the `flagged` example chosen actually does contain an urgent keyword (a subtle false negative to watch for, e.g. accidentally picking an example containing "now" as a substring of another word).
4. **Undeclared outputs section** flags that the long-message branch returns `"needs_review"`, which is not a member of the `RequestCategory` enum — noting this as output drift distinct from the dead-branch bug class. — **FAIL** if this is missed entirely, or if it's incorrectly treated as a dead/unreachable-category finding rather than an undeclared-output note.
5. The top-level verdict summary states plainly that all declared categories are reachable (a clean result), rather than manufacturing a false problem to seem useful. — **FAIL** if it invents a shadowing bug that doesn't exist (e.g., falsely claiming `flagged` is shadowed by `urgent` for all inputs).

**Overall pass**: criteria 1, 2, 3, and 5 must hold for a pass (correctly reporting a clean classifier is the core thing being tested here); criterion 4 is a secondary quality bar on top of that.
