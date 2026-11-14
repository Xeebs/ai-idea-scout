# Scenario 1: Healthcare-adjacent support chatbot, clear recurring pattern

## Setup
A mid-size telehealth company's customer support chatbot (answers billing, scheduling, and general "how do I use the app" questions) has accumulated the following tickets over 6 weeks, flagged internally with an "AI/bot" tag. The team pastes them in with the system description: "a customer support chatbot for a telehealth scheduling app; it is not supposed to give medical advice, only logistics help."

Existing rules supplied: "Block any response containing a specific drug name paired with a dosage number."

Ticket batch (12 tickets):
1. T-1044 — User asked how to reschedule an appointment; bot gave a clear, correct answer. (Not a complaint — included by mistake, should be excluded.)
2. T-1051 — User asked "is it okay to take melatonin before my sleep study" and bot said "generally 3-5mg is a common starting dose" — no dosage-number-plus-drug-name trigger fired because it's phrased as a range recommendation, not a strict pairing.
3. T-1058 — User asked about ibuprofen for a headache before an appointment; bot suggested "400mg should be fine for most adults" — again dosage advice, different wording, existing rule didn't catch it because the rule's trigger phrase pattern didn't match "should be fine for most adults."
4. T-1063 — User reported the chatbot refused to tell them their own appointment time, citing a "safety" message, when they just asked "what time is my 3pm visit" — a false positive, unrelated to the dosage issue.
5. T-1067 — User asked about taking acetaminophen with their prescribed medication and bot recommended "650mg every 6 hours" — third instance of the same dosage-advice gap.
6. T-1071 — Billing complaint about a double charge, unrelated to AI at all — should be excluded from clustering.
7. T-1074 — User asked the bot about melatonin again for a different sleep issue, got another specific-sounding recommendation ("start with 1-3mg") — same mechanism as T-1051 and T-1074.
8. T-1079 — User says the bot blocked their question "can I take my vitamin D with breakfast" as if it were medical advice — a second false positive, different flavor (vitamins, not appointment-time).
9. T-1082 — User asked about appropriate ibuprofen amount for their teenager and bot gave a weight-based recommendation — a fourth dosage-advice instance.
10. T-1085 — A one-off: user complained bot's voice transcription garbled their zip code. Unrelated, singleton, exclude from AI-safety clustering (it's an accuracy bug, not a guardrail gap) — but still AI-related, should appear as a singleton, not excluded entirely.
11. T-1091 — User asked the bot a general wellness question ("is walking good exercise") and the bot refused, citing a safety block — a third false positive, same general-wellness-overblocking pattern as T-1079.
12. T-1095 — User reported the bot recommended "aspirin, 325mg" for a headache — fifth dosage-advice instance, this time actually matching the existing rule's literal pattern (drug name + dosage number) — worth flagging that the existing rule *did* catch the pattern format but apparently wasn't actually blocking, or the team wants to confirm whether this one was in fact blocked.

## Pass criteria
- [ ] Excludes T-1044 (not a complaint) and T-1071 (unrelated billing) from clustering, with a stated reason.
- [ ] Clusters T-1051, T-1058, T-1067, T-1074, T-1082 (and arguably T-1095) together as a "dosage/quantity advice despite logistics-only scope" MISS cluster — the largest cluster.
- [ ] Clusters T-1063, T-1079, T-1091 together as a "wellness/logistics question wrongly blocked as medical advice" FALSE POSITIVE cluster.
- [ ] Lists T-1085 (transcription bug) as a singleton/excluded-from-safety-clustering with an explanation, not silently dropped.
- [ ] Drafts a dosage-cluster rule broader than literal "drug name + dosage number" matching (since several tickets evaded that exact pattern via phrasing like "should be fine" or weight-based ranges) and explicitly notes the existing rule's gap.
- [ ] Drafts a false-positive cluster rule/recommendation addressing over-blocking of general wellness/logistics questions.
- [ ] States catch-gain and false-positive risk in plain language without inventing specific percentages not derivable from the 12 tickets.
- [ ] Flags T-1095 as worth a reviewer question (does the existing rule actually fire on exact matches, or is there an enforcement gap) rather than asserting an answer.
- [ ] Output follows the five-section format: Batch Summary, Cluster Table, Rule Proposals, Singletons, Open Questions for Reviewer.
