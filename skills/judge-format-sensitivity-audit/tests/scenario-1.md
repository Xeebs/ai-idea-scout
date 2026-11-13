# Scenario 1 — Customer support response quality judge, 12 real-shaped examples

## Input given to the skill

**Judge prompt/rubric (verbatim, as the user would paste it):**

> You are evaluating a customer support agent's reply to a customer message. Judge the reply on: (1) whether it directly addresses the customer's actual issue, (2) whether it is polite and empathetic without being saccharine, (3) whether it gives a clear, actionable next step (refund initiated, ticket escalated, link to self-serve fix, etc.) rather than a vague "we'll look into it." Respond with a single integer score from 1 to 5, where 1 means the reply fails on multiple criteria and 5 means it fully satisfies all three. Output only the number.

**Example items (12 provided, abbreviated here — a real run would include all 12 in full):**

1. Customer: "My order #4521 arrived damaged, I want a refund." Agent: "I'm sorry to hear that! I've issued a full refund to your original payment method, it should post within 3-5 business days. Let me know if you don't see it by then."
2. Customer: "Your app keeps crashing when I try to upload a photo." Agent: "Thanks for reaching out, we're aware of some issues and are working on it."
3. Customer: "I was charged twice for the same subscription this month." Agent: "I've reviewed your account and confirmed the duplicate charge. I've refunded the extra $14.99 and added a note to prevent it next cycle."
4. Customer: "How do I cancel my subscription?" Agent: "You can cancel anytime from Settings > Billing > Cancel Plan. I've also gone ahead and flagged your account in case you run into trouble finding it."
5. Customer: "This is the third time I've emailed about my broken login and nobody has fixed it." Agent: "So sorry for the repeated trouble! I've escalated this to our engineering team directly and you should hear back within 24 hours with a fix or workaround."
6. Customer: "The product description said waterproof but mine got ruined in light rain." Agent: "We'll look into it and get back to you."
7. Customer: "Can I get a price match for the sale I saw yesterday?" Agent: "Absolutely, I've applied a $20 credit to your account to match that price."
8. Customer: "Why was my account suspended?" Agent: "Our system flags accounts automatically sometimes and it's probably nothing, don't worry!"
9. Customer: "I need an invoice for my last purchase for tax purposes." Agent: "Attached is your invoice for order #8832 — let me know if you need it in a different format."
10. Customer: "The replacement part you sent doesn't fit my model." Agent: "I'm really sorry about that mix-up! I've sent out the correct part (model-matched this time) with expedited shipping, no charge, tracking number is TRK9931."
11. Customer: "Your support bot gave me wrong information yesterday." Agent: "Thanks for the feedback, we're always trying to improve!"
12. Customer: "I want to dispute a late fee, I paid on time." Agent: "I checked your payment history and you're right — paid on the 3rd, due the 5th. I've reversed the $25 late fee."

## Pass criteria

- [ ] The report splits the rubric into criteria (the 3 named checks) and format instruction ("single integer 1-5, output only the number"), and keeps the 3 criteria identical across all generated variants.
- [ ] Three variants are actually built and distinctly labeled: Likert (matches/extends the original), Binary PASS/FAIL, and free-text-then-extracted-score.
- [ ] All 12 items are visibly scored under all 3 variants (36 total judgments, or the report shows evidence of having done this work, not placeholder numbers) — items like #2, #6, #8, #11 (vague/evasive replies) should score low across all variants, while #1, #3, #5, #7, #9, #10, #12 (clear issue + clear action) should score consistently high; the report's actual numbers should reflect this, not contradict it.
- [ ] Per-item divergence and an aggregate divergence number (0-1 scale) are computed and a LOW/MODERATE/HIGH label is given, with a Spearman rank-correlation check across variant pairs.
- [ ] The 3-5 most divergent items are named specifically with their per-variant scores (plausibly items with partial/mixed quality, e.g. a reply that's polite and clear but light on the "actionable next step" criterion).
- [ ] Report includes the mandatory "What this doesn't tell you" section with the judge-substitution caveat, the format-only-scope caveat, and (since N=12) no false claim of high statistical confidence.
- [ ] Confidence is marked "full" (verbatim rubric, N=12 which is within the 10-30 target band) — not flagged as low-confidence incorrectly.

## Self-check notes

Walking through this: the rubric cleanly separates into 3 named criteria + a simple format instruction, so step 1 of the procedure is straightforward. With 12 concrete, realistic items spanning clearly-good, clearly-bad, and borderline replies (e.g. #4's cancellation answer is clear and somewhat proactive but marginal on "actionable next step" since canceling isn't really a next step toward resolution; #9 is clear but minimal warmth), there's real texture for divergence to show up on the borderline items specifically — this is exactly the realistic case the skill is designed for, and the procedure produces a usable, non-trivial report.
