# Scenario 1 — Support-ticket triage prompt, first run, no prior baseline

## Setup

A solo developer just rewrote the system prompt for a support-ticket triage bot (classifies incoming tickets into urgency/category and drafts a first-response suggestion). They have no formal eval harness and no existing rubric. They want a quick check before merging the prompt change.

## Input handed to the skill

No rubric supplied — developer says: "I don't have a rubric yet, please draft one for a support-ticket triage assistant that classifies urgency and category and drafts a first-response suggestion."

Samples (4 prompt+response pairs):

1. **Prompt**: "My invoice #4471 was charged twice this month, please help ASAP."
   **Response**: "Category: Billing. Urgency: High. Suggested reply: 'I'm sorry for the duplicate charge on invoice #4471 — I've flagged this for our billing team to refund within 2 business days. Is there anything else I can help with in the meantime?'"

2. **Prompt**: "How do I change my email notification preferences?"
   **Response**: "Category: Account Settings. Urgency: Low. Suggested reply: 'You can update your notification preferences under Settings > Notifications. Let me know if you run into any issues!'"

3. **Prompt**: "Your app crashed and I lost 3 hours of work, this is unacceptable."
   **Response**: "Category: Bug Report. Urgency: High. Suggested reply: 'Thanks for reporting this.'"

4. **Prompt**: "Can I get a refund for my annual plan, I canceled last week but no one responded?"
   **Response**: "Category: Billing. Urgency: Medium. Suggested reply: 'I'd be happy to help with your refund request. Could you confirm the account email and cancellation date so I can process this for you?'"

No prior run block supplied (first run).

## Pass criteria

- [ ] Drafts a 3-dimension starter rubric relevant to triage (plausibly: classification accuracy, urgency calibration, response quality/empathy) and explicitly labels it a draft for the user to edit.
- [ ] Produces a table scoring all 4 samples against each drafted dimension, 1-5 scale.
- [ ] Each justification quotes or closely paraphrases the actual response text — e.g. flags sample 3's suggested reply ("Thanks for reporting this.") as thin/low-empathy for a High-urgency, data-loss complaint, citing that specific phrase, not a generic "response quality is decent" comment.
- [ ] Computes per-dimension averages across the 4 samples.
- [ ] Does NOT attempt a diff section, and explicitly states no prior run was supplied rather than fabricating one.
- [ ] Ends with the review-needed line telling the user to confirm/override scores before saving.
- [ ] Does not suggest building a dashboard, judge pipeline, or database for a 4-sample check.

## Fail conditions

- Any justification that doesn't reference specific content from that sample's response.
- Inventing a "prior run" or regression language when none was given.
- A rubric with more than 5 dimensions, or no explicit "this is a draft" framing when one was drafted.
