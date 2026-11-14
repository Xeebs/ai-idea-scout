# Scenario 1 — Confirmed agent-authored PR with a real N+1 regression and a duplicated component

## Setup

A small SaaS team uses Claude Code to open PRs for backlog tickets, with each commit tagged `Co-Authored-By: claude[bot] <noreply@anthropic.com>`. A reviewer pastes the following into the skill before approving PR #412, "Add per-order shipping label preview."

**Commit trailer visible**: `Co-Authored-By: claude[bot] <noreply@anthropic.com>`

**Diff (`git diff main...feature/order-label-preview`), trimmed to the relevant hunks:**

```diff
--- a/src/services/orders.ts
+++ b/src/services/orders.ts
@@ -10,8 +10,7 @@ export async function getOrdersForWarehouse(warehouseId: string) {
   const orderIds = await db.listOrderIds(warehouseId);
-  const orders = await db.getOrdersBatch(orderIds);
-  return orders;
+  const orders = [];
+  for (const id of orderIds) {
+    const order = await db.getOrder(id);
+    orders.push(order);
+  }
+  return orders;
 }

--- a/src/components/OrderLabelCard.tsx
+++ b/src/components/OrderLabelCard.tsx
@@ -0,0 +1,34 @@
+import React from 'react';
+
+export function OrderLabelCard({ order }) {
+  return (
+    <div>
+      <div>
+        <h3>Welcome to our app</h3>
+        <p>Order #{order.id}</p>
+        <p>Status: {order.status}</p>
+      </div>
+    </div>
+  );
+}

--- a/src/components/OrderCard.tsx (existing file, unchanged, shown for reference)
+++ b/src/components/OrderCard.tsx
@@ ... @@
 export function OrderCard({ order, variant }) {
   return (
     <div className="order-card">
       <h3>{order.title}</h3>
       <p>Order #{order.id}</p>
       <p>Status: {order.status}</p>
     </div>
   );
 }
```

## Run the skill

Apply the procedure in SKILL.md (or paste the README prompt) against this diff and commit trailer.

## Pass criteria

- [ ] Authorship confidence is labeled **CONFIRMED**, citing the literal `Co-Authored-By: claude[bot]` trailer.
- [ ] Performance Regression Risks table flags the `getOrdersForWarehouse` change: cites `src/services/orders.ts` and the correct hunk, identifies it as an N+1 regression (batched `db.getOrdersBatch(orderIds)` call replaced by a per-ID loop calling `db.getOrder(id)`), severity **HIGH** (a removed existing batched call being replaced by a loop is a clear, not speculative, regression).
- [ ] UI Boilerplate Smells table flags `OrderLabelCard.tsx`: notes it near-duplicates the existing `OrderCard.tsx` structure instead of reusing/parameterizing it, AND separately flags the "Welcome to our app" placeholder copy left in shipped-looking code. Severity MEDIUM or HIGH is acceptable for either, as long as both distinct smells are called out (not merged into one vague note).
- [ ] Overall Advisory is **RECOMMEND HOLDING FOR HUMAN REVIEW** or **MERGE WITH FOLLOW-UP** (not "LIKELY SAFE TO MERGE"), given the HIGH-severity N+1 finding.
- [ ] No section is silently omitted — both tables appear even though every row in them is a finding (no "no findings" false negative here).
- [ ] Report does not claim to have executed, benchmarked, or merged/commented on anything.

## Fail conditions

- Missing the N+1 regression entirely, or citing the wrong file/hunk for it.
- Missing the duplicated-component smell or the placeholder-copy smell.
- Labeling authorship confidence as anything other than CONFIRMED despite the literal trailer being present.
- Giving "LIKELY SAFE TO MERGE" as the overall advisory.
