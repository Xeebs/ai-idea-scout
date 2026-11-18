# Scenario 1 — Mem0-backed support bot, blind top-k injection

## Input

**Retrieval/injection logic (Python, Mem0):**
```python
def build_prompt(user_id, user_message):
    memories = memory_client.search(query=user_message, user_id=user_id, limit=3)
    memory_block = "\n".join(m["memory"] for m in memories)
    system_prompt = f"""You are a support agent. Relevant context from past
conversations with this user:
{memory_block}

Answer the user's current message."""
    return system_prompt, user_message
```
There is no similarity threshold, no re-ranking, and no check of what task the memory came from — just the top-3 nearest-neighbor results by embedding similarity to the current message, always injected.

**Backend**: Mem0.

**Example turns:**

Turn 1:
- User message: "Can you move my next billing date to the 15th instead of the 1st?"
- Memory retrieved: "User asked to cancel their subscription on 2026-09-02; agreed to a retention offer of 20% off for 3 months instead of cancelling."
- Agent's answer: "I see you're on a retention discount from when you considered cancelling — would you like to proceed with the cancellation, or keep the 20% off plan? I can't move the billing date while that offer is active."

Turn 2:
- User message: "What's the status of my refund request from last week?"
- Memory retrieved: "User reported a refund request on 2026-11-10 for a duplicate charge of $49.99; refund was processed and confirmed on 2026-11-12."
- Agent's answer: "Your refund of $49.99 for the duplicate charge was processed and confirmed on November 12th."

Turn 3:
- User message: "I want to add a second user seat to my plan."
- Memory retrieved: "User asked about downgrading from the Team plan to the Solo plan on 2026-08-20, citing cost concerns."
- Agent's answer: "Since you were previously looking at downgrading to the Solo plan to save costs, would adding a second seat still make sense for your budget? I can walk you through pricing before we proceed."

## Pass criteria

A passing output must:
1. Correctly identify the injection point as the f-string building `memory_block` into `system_prompt`, with no filtering before injection.
2. Classify Current Safeguard Level as `NONE` (top-k by raw similarity only, no task-match check).
3. In the per-turn table: Turn 1 overlap = LOW (billing-date change vs. cancellation/retention) and verdict = `CONFIRMED ANCHORING` (the agent visibly derailed into re-litigating the retention offer instead of answering the billing-date question). Turn 2 overlap = HIGH, verdict = `NO ISSUE`. Turn 3 overlap = LOW/MEDIUM (adding a seat vs. a downgrade-to-save-cost conversation) and verdict = `CONFIRMED ANCHORING` or `POTENTIAL ANCHORING` (the agent questioned the user's request instead of processing it).
4. Overall Risk Rating = `HIGH`, with the stated rule (NONE safeguard + at least one CONFIRMED ANCHORING).
5. Suggested Task-Signature Check names a concrete slot-in point (wrapping `memory_client.search()`'s return before the join into `memory_block`) and a concrete mechanism (embedding similarity or cheap classifier comparing current `user_message`'s intent to each memory's original context).
6. Caveats section does not state any accuracy-percentage number as applying to this stack, and does not recommend disabling memory.

## Fail conditions
- Treats all three turns as fine / rates risk LOW or MEDIUM despite two clear derailments.
- Invents code behavior not shown (e.g., claims there's a similarity threshold when there isn't one).
- Recommends simply turning memory off.
- States a specific accuracy-improvement percentage for this stack.
