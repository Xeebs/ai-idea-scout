# Rollback Safety Review: Checkpoint Placement for Side-Effecting Pipelines

Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, etc.) along with your pipeline description to get it.

## What this does

You have a multi-step or multi-agent pipeline — extract, analyze, write to a CRM, send a notification, charge a card, whatever your steps are — and at least one step does something that reaches outside the pipeline itself (a database write, an email, an API call, a payment). You're wiring up checkpointing (maybe with LangGraph, CrewAI, Google ADK, or your own key-value store) and need to know: if a step fails partway through, is it actually safe to roll back to the last checkpoint and retry? Or will that retry re-send an email that already went out, double-charge a customer, or leave a half-created CRM record behind?

This is a **design review**, not a running system. It doesn't touch your code or your infrastructure. It reads a plain description of your pipeline and tells you, step by step, which ones are safe for an automatic recovery layer to roll back, which ones need a defined "undo" action instead, and exactly where checkpoints need to sit so a retry never re-fires something that can't be taken back.

Don't use this to decide whether adding an extra review/verification step would improve your accuracy — that's a statistics question about error rates, answered by a different kind of analysis (log-based error-compounding estimation), not this one.

## What to hand over

Paste (manually — nothing here connects to your code, logs, or any API):

1. **Your pipeline's steps, in order**, with a one-line description of each. Example: "1. extract: pull structured fields from the uploaded doc. 2. analyze: run sentiment classification. 3. write-to-crm: create a new CRM record for this lead. 4. notify: email the account owner that a new lead came in."
2. **What each step does outside the pipeline itself**, as far as you know: nothing (pure computation), writes to a shared system safely (e.g. an upsert keyed on a stable ID — same result if repeated), creates/changes something external that *could* be undone (e.g. a CRM record you could delete, a charge you could refund), or fires something external that can't be recalled once sent (an email, SMS, webhook, a non-refundable charge).
3. Optionally: which checkpointing tool you're using (LangGraph, CrewAI, Google ADK, something custom, or none yet), and whether you already have any idempotency keys, dedup logic, or "undo" actions (like a refund endpoint) wired up for any step.

If you don't know a step's side-effect type, say so — don't guess on your end either. The review will flag it and default to treating it as the worst case (can't be undone) until you confirm otherwise.

## What you'll get back

1. **Your pipeline, restated** as a numbered list, so you can confirm it was understood correctly.
2. **A table, one row per step**, with: the step name, its side-effect type (none / safely-repeatable / undoable-with-a-defined-action / cannot-be-undone / you-didn't-say), what that means for rollback safety (safe to auto-rollback / needs its compensating action run instead / never auto-rollback — only guard against re-firing), the compensating action if you named one (or "undefined" if you didn't), and whether a checkpoint is required immediately before that step.
3. **Named straddling risks** — specific step sequences where a retry could re-fire something irreversible because there's no checkpoint protecting it, stated in plain language (e.g. "step 4, the notification email, has no checkpoint before it — if step 3 fails and you retry from step 2, the email could go out twice").
4. **An ordered list of exactly where to add checkpoints**, each marked required or optional.
5. **A list of open questions** — any step you didn't classify, any undoable step with no defined undo action, and whether you have dedup/idempotency protection for the steps that can't be undone at all.

## The rules this review follows

- It never guesses a step's side-effect type from its name — "write-to-crm" is not assumed idempotent just because it sounds like a database write. If you didn't say, it's marked unspecified and treated as the worst case (irreversible, no auto-rollback) until you say otherwise.
- It never recommends automatically rolling back a step that creates or changes something external unless that step has a defined undo action, and it never recommends rolling back a step that fires something irreversible at all — for those, the only fix is preventing the retry from re-firing it, not "undoing" it.
- It never invents a plausible-sounding undo action (like assuming you must have a refund endpoint) — if you didn't name one, it's reported as undefined, with a question back to you.
- It's a checklist to hand to whoever builds your actual recovery/retry logic — it doesn't enforce anything itself, and it says so.
- It stays in its lane: this is about which steps are safe to roll back and where checkpoints go, not about whether adding a review step would statistically reduce your error rate.
