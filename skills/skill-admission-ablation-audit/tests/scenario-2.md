# Scenario 2: Genuinely high-lift operational-habit skill, and a missing-baseline edge case

## Setup

A solo indie developer wants to publish a skill called `db-migration-safety-check` to a marketplace (e.g. claudemarketplaces.com) and wants a pre-publish audit. They provide the skill content and scenarios but initially forget to include the no-skill baseline.

### Candidate skill content (pasted in full)

```
---
name: db-migration-safety-check
description: Enforces a safety checklist before generating or running any database migration.
---

# DB Migration Safety Check

Before writing or running ANY migration (Rails, Django, Alembic, Prisma, raw SQL — doesn't
matter which), always do these in order:

1. Check whether the migration adds a NOT NULL column to an existing table with rows.
   If so, it must be a 3-step migration: add column nullable -> backfill -> add NOT NULL
   constraint in a separate deploy. A single-step NOT NULL add will lock the table and can
   take production down on large tables.
2. Check whether the migration drops a column or table. If so, confirm the application
   code no longer references it in the current deploy AND the previous deploy (so a
   rollback doesn't crash). Never drop in the same deploy that removes the last code
   reference.
3. Check whether an index is being added on a large table. If so, use CONCURRENTLY
   (Postgres) or the online equivalent for the target DB — a blocking index build on a
   busy table causes an outage.
4. State explicitly, before presenting the migration, which of the above three risks
   apply and how the migration handles each one, even if the answer is "not applicable."

Never skip straight to writing migration SQL/code without walking through this checklist
first.
```

### Representative scenarios
1. "Add a `status` column (NOT NULL, default 'pending') to our `orders` table, which has 40 million rows in production."
2. "We're removing the legacy `shipping_label_url` column from `orders` since nothing in the new code path uses it."
3. "Add an index on `orders.customer_id` to speed up a slow dashboard query. Table has 40 million rows."

### Base model behavior WITHOUT the skill
*(Initially NOT provided — the developer just says "I think it's good, can you audit it?")*

## Run the skill's procedure against this input

## Pass criteria
- On the first pass (no baseline given), the audit must refuse to issue a confident KEEP/DELETE/RESTRUCTURE verdict and instead ask for the no-skill baseline behavior — OR, if it proceeds anyway per guardrail allowance, it must prominently label the output "LOW CONFIDENCE — insufficient scenario coverage" per the SKILL.md procedure.
- Once a baseline is supplied (e.g. "without the skill, the model wrote a single-step `ALTER TABLE orders ADD COLUMN status TEXT NOT NULL DEFAULT 'pending'` for scenario 1 — a table lock risk on 40M rows — and did not mention concurrent index build for scenario 3"), the audit should converge on a **KEEP** verdict: the compact-operational-habit check should PASS and cite scenario 1 and/or scenario 3 by name as evidence the model got it wrong without the skill present.
- The capability-duplication check should PASS (not FLAG) because the baseline shows the base model failing these checks without the skill.
- The reference-dump density check should PASS (not FLAG) — this skill is almost entirely workflow/judgment, not a pasted table.
- Output still includes the confidence note stating this is a heuristic review of supplied scenarios, and recommends a real with/without trial if this skill is going into a catalog many people will depend on (which is relevant here — it's bound for a public marketplace).

## Fail criteria
- Issuing a confident KEEP or DELETE verdict on the first pass with zero baseline information and no LOW CONFIDENCE flag or request for the missing input.
- FLAGging capability duplication or reference-dump density once a baseline showing real failures without the skill is supplied — that would contradict the skill's own guardrails.
- Omitting the recommendation to run a real ablation trial given this is headed to a public marketplace catalog.
