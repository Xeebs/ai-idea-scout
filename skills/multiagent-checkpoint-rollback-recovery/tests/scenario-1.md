# Scenario 1 — Three-agent customer-analysis-to-CRM pipeline (the Latenode-style case)

## Input a user would paste

> We have a 4-step LangGraph pipeline that runs whenever a new support ticket comes in:
> 1. **extract** — pulls structured fields (customer name, issue category, urgency) from the raw ticket text. Pure transform, doesn't touch anything outside the pipeline.
> 2. **analyze** — runs a sentiment/urgency classifier on the extracted fields. Also pure transform.
> 3. **write-to-crm** — creates a new case record in our CRM (Salesforce) for this ticket. This is a `create`, not an upsert — running it twice makes two case records.
> 4. **notify** — sends an email to the account manager saying "new high-urgency case opened."
>
> We're using LangGraph's checkpointer already but we just save state after each step — we haven't thought about what happens if step 4 fails and we retry from the last checkpoint. We don't have a refund/undo path for the CRM write and no idempotency key on the Salesforce create call. What checkpoints do we actually need, and is it safe to auto-rollback any of this?

## Pass criteria

- [ ] Classifies step 1 (extract) and step 2 (analyze) as NONE — pure transforms, safe to auto-rollback/retry freely.
- [ ] Classifies step 3 (write-to-crm) as NON-IDEMPOTENT REVERSIBLE *or* flags it clearly as having no compensating action defined (the user explicitly said "no refund/undo path") — must not claim it's safely idempotent, since the user explicitly said a retry creates duplicate records.
- [ ] Classifies step 4 (notify/email) as IRREVERSIBLE.
- [ ] States plainly that auto-rollback must NOT be used for steps 3 and 4.
- [ ] Flags step 3 as having an undefined compensating action and asks the user to define one (e.g. a delete/dedup path) rather than inventing one.
- [ ] Flags the lack of an idempotency key on the Salesforce create call as a straddling risk for step 3 specifically (duplicate CRM records on retry).
- [ ] Flags that step 4 (email) has no checkpoint immediately before it in the current "save after each step" setup being described as insufficient — recommends a checkpoint that sits before step 3 and before step 4 specifically (i.e., checkpoints at the boundaries protecting the irreversible/reversible-but-undefined actions), not just "after each step" generically.
- [ ] Does NOT recommend auto-rollback as a fix for steps 3 or 4 under any framing.
- [ ] Lists open questions: compensating action for the CRM write, and whether an idempotency key can be added to the Salesforce call.

## Fail if

- The output treats "write-to-crm" or "notify" as safe to auto-rollback.
- The output invents a refund/delete mechanism for the CRM record that the user never mentioned having.
- The output gives generic "add checkpoints after each step" advice without naming steps 3 and 4 specifically as the ones requiring a checkpoint immediately before them.
