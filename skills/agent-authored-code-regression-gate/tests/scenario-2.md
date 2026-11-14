# Scenario 2 — Unconfirmed authorship, backend-only diff, legitimate large refactor plus one real perf issue

## Setup

A solo developer at a small company suspects a contractor used an AI coding agent for a recent PR but has no commit trailer or bot account to point to — just a hunch from the style. They have no `gh` CLI access to this private repo from their current machine, so they paste the diff directly, with this note: "Not sure if this was AI-written, no trailer or anything, just want a check before I merge. This refactors our `OrderProcessor` into submodules (large change) and touches the retry logic for payment webhook calls. No UI involved, backend only."

**Diff (`git diff main...feature/order-processor-split`), trimmed to the relevant hunks:**

```diff
--- a/src/orders/processor.py
+++ b/src/orders/processor.py
@@ -1,180 +1,12 @@
-class OrderProcessor:
-    def validate(self, order): ...
-    def price(self, order): ...
-    def fulfill(self, order): ...
-    # ~170 lines of existing, working logic split out below
+from .validation import validate_order
+from .pricing import price_order
+from .fulfillment import fulfill_order
+
+class OrderProcessor:
+    def validate(self, order):
+        return validate_order(order)
+    def price(self, order):
+        return price_order(order)
+    def fulfill(self, order):
+        return fulfill_order(order)

--- a/src/orders/validation.py (new file, ~60 lines moved verbatim from processor.py)
--- a/src/orders/pricing.py (new file, ~55 lines moved verbatim from processor.py)
--- a/src/orders/fulfillment.py (new file, ~55 lines moved verbatim from processor.py)

--- a/src/payments/webhook_client.py
+++ b/src/payments/webhook_client.py
@@ -22,10 +22,16 @@ def send_webhook_batch(webhooks):
     results = []
     for webhook in webhooks:
-        payload = copy.copy(webhook.payload)
-        result = send(webhook.url, payload)
-        results.append(result)
+        payload = json.loads(json.dumps(webhook.payload))
+        result = None
+        while result is None:
+            try:
+                result = send(webhook.url, payload)
+            except Exception:
+                pass
+        results.append(result)
     return results
```

## Run the skill

Apply the procedure in SKILL.md (or paste the README prompt) against this pasted diff, with no commit trailer and no `gh` access available.

## Pass criteria

- [ ] Authorship confidence is labeled **UNCONFIRMED** (no trailer, no bot account, just a hunch) — must not be labeled CONFIRMED, and should not over-claim LIKELY without pointing to a real stylistic signal.
- [ ] The `OrderProcessor` split into `validation.py`/`pricing.py`/`fulfillment.py` is **NOT** flagged as a performance regression or a UI/boilerplate smell purely for being large — report either stays silent on it or explicitly notes it's a legitimate structural refactor, not a smell.
- [ ] Performance Regression Risks table flags the `webhook_client.py` change with at least these two distinct issues (may be one or two rows, but both points must appear): (a) `copy.copy(webhook.payload)` replaced with `json.loads(json.dumps(...))`, a heavier deep-serialize clone inside a loop; (b) the retry `while result is None: try/except: pass` loop has no backoff and no retry limit — an unbounded-retry risk. Cites `src/payments/webhook_client.py` and the right hunk.
- [ ] LLM-Style UI Boilerplate Smells section is explicitly marked **skipped** (diff touches no UI/view-layer files) — not silently omitted, not given a fabricated finding.
- [ ] Overall Advisory reflects the real finding (MERGE WITH FOLLOW-UP or RECOMMEND HOLDING FOR HUMAN REVIEW) rather than LIKELY SAFE TO MERGE, since an unbounded retry on a payment webhook is a genuine risk.
- [ ] Report's Notes/Limitations line acknowledges it cannot confirm agent authorship from the diff alone, matching the UNCONFIRMED label.

## Fail conditions

- Flagging the file-split refactor as a smell or regression just because it's a large diff.
- Missing either the heavier-clone change or the unbounded-retry-without-backoff issue in the webhook function.
- Fabricating a UI finding on a diff with no UI files, or silently dropping the UI section instead of marking it skipped.
- Labeling authorship CONFIRMED despite no trailer/bot account being present anywhere in the input.
