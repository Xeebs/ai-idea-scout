# Scenario 1: Python FastAPI gateway wrapping a jailbreak classifier API

## Setup

A team runs an LLM chat gateway in FastAPI. Before forwarding a user message to the model, it calls an internal jailbreak-classifier microservice over HTTP. They paste this call site and declare the policy.

### Pasted input

**Declared policy:**
- `jailbreak_classifier`: category = jailbreak/prompt-injection detection, **fail-closed** (must block if the detector can't be reached).
- `brand_tone_checker`: category = advisory tone/style check, **fail-open** (not safety-critical, continue if unavailable).

**Call-site code:**

```python
import httpx

async def check_jailbreak(user_message: str) -> bool:
    """Returns True if message is SAFE to forward, False if it should be blocked."""
    try:
        resp = httpx.post(
            "http://jailbreak-classifier.internal/v1/check",
            json={"text": user_message},
            timeout=2.0,
        )
        result = resp.json()
        return not result["is_jailbreak"]
    except Exception:
        # classifier hiccup, don't block the user over it
        return True

async def check_brand_tone(user_message: str) -> bool:
    try:
        resp = httpx.post(
            "http://tone-checker.internal/v1/check",
            json={"text": user_message},
            timeout=1.5,
        )
        return resp.json()["on_brand"]
    except Exception:
        return False
```

## Pass criteria

A correct response must:

1. Identify `check_jailbreak` as a **critical FAIL-OPEN BUG** — the bare `except Exception: return True` catches a timeout, connection error, or malformed JSON (e.g. `resp.json()` raising on a non-JSON error page, or `KeyError` on `result["is_jailbreak"]`) and resolves to "safe to forward" (True), directly contradicting the declared fail-closed policy. The response should quote or closely paraphrase the offending `except Exception: return True` line.
2. Identify `check_brand_tone` as a **Lower-Severity / Availability Finding**, not a critical bug — it fails *closed* (`return False`/blocked) on error despite being declared fail-open, which is a false-positive/availability risk, not a safety issue. The response must not label this a FAIL-OPEN BUG.
3. Provide a corrected patch for `check_jailbreak` that: uses explicit exception handling (not a bare `except Exception` silently returning True), returns `False` (block) on any detector failure, and emits a structured log line recording the detector name, category, and triggering error.
4. Note in Caveats that the patch is reviewed/drafted, not tested, and recommends a real fault-injection test before merge.
5. Not flag any error path not present in the pasted code (e.g. should not invent a rate-limit handling path that isn't there).

## Fail criteria

- Treating `check_jailbreak`'s bug as anything less than critical/FAIL-OPEN BUG, or missing it entirely.
- Mislabeling `check_brand_tone`'s fail-closed-on-error behavior as a safety bug rather than an availability finding.
- Claiming the drafted patch has been tested or verified to work.
- Assuming a policy for either detector instead of using the one stated.
