# Scenario 2 — Financial-literacy SMS chatbot in Nigeria (Twilio API access, rate given)

## Context
A fintech-adjacent nonprofit runs an AI chatbot over SMS (via Twilio) answering budgeting and savings questions for users in Nigeria without smartphones. Unlike Scenario 1, this team's engineer is using Claude Code and has Twilio API credentials, and wants both a segment audit AND a dollar estimate to decide whether to greenlight building the compression middleware, since they're about to scale from 2,000 to 20,000 active users.

## Input

The engineer states: "I have Twilio API access (Account SID/Auth Token available), pull the last 7 days of outbound messages from our 'budget-bot' sender number." Since this is a test scenario (no live Twilio account to actually query), the test substitutes a representative 7-day sample the API would have returned:

```
1. A good rule of thumb is to save at least 10% of any income you receive, even small amounts, before spending on anything else.
2. Your current savings goal is set to 50,000 naira by December 31st. You're currently at 32,000 naira, so you need about 18,000 more.
3. Yes, it's generally better to pay off high-interest debt before building savings, unless your employer offers matching contributions.
4. Great question! Building an emergency fund of 3-6 months of expenses is a common guideline, though even 1 month is a meaningful start if that's all you can manage right now.
5. Setting a weekly budget and checking it every few days helps you catch overspending early.
6. You can adjust your savings goal anytime by replying GOAL followed by a new amount.
7. Compound interest means your savings grow faster over time, since you earn returns not only on your original deposit but also on returns you have already earned, which adds up nicely.
8. Based on your recent spending, you're on track to meet your monthly goal.
9. Avoid taking on new loans while you're still repaying an existing one at a high interest rate, as this can compound your debt quickly.
10. To check your current balance at any time, just reply BALANCE.
```

Encoding: English only, standard Latin text (GSM-7, no emoji).
Per-segment rate: $0.0075/segment (Twilio Nigeria outbound SMS, illustrative).
Volume: roughly 20,000 active users once scaled, assume ~3 AI responses/user/week on average.

## Expected handling

- All 10 messages are GSM-7 — no UCS-2 flags expected here (sanity check that the skill doesn't force UCS-2 unnecessarily either).
- Message 2 (131 chars, 1 segment — doesn't actually cross a boundary) contains a date ("December 31st") and amounts ("50,000 naira", "32,000 naira", "18,000") — if the model mistakenly computes it as boundary waste, it must appear under "cannot safely compress" naming the amounts/date, never get a rewrite.
- Message 4 (173 chars, 2 segments) genuinely crosses a boundary but contains "3-6 months" and "1 month" (number+duration) — acceptable for the skill to flag this "cannot safely compress" under the default conservative rule, same intentional edge case as scenario 1's message 5.
- **Message 7 is the designed clean-compression case**: 183 characters (2 segments under the 153-char multi-segment budget), no number/date/unit/warning-phrase content, 23 characters over the 160-char single-segment threshold — within the 15%-of-length (~27 chars) boundary-waste rule. It MUST get a concrete rewrite trimming it to <=160 characters (1 segment).
- Messages 1, 3, 5, 6, 8, 9, 10 are all under 160 chars (1 segment) — should be classified "clean," not flagged as boundary waste.
- With a real rate and volume supplied, a cost estimate must be produced, showing the formula (segments saved per message × weekly volume × 52 weeks or × monthly volume × rate) and naming every assumption (the 3 msgs/user/week estimate, the $0.0075 rate).

## Pass criteria
- [ ] Correctly identifies all 10 messages as GSM-7 (no incorrect UCS-2 flags).
- [ ] Message 2 and message 4 are never rewritten with altered amounts, dates, or duration numbers — if flagged as boundary waste at all, they appear under "cannot safely compress" naming the specific blocking content.
- [ ] Message 7 crosses a boundary (2 segments at 183 chars) and gets a concrete before/after rewrite with char counts and segments saved shown, landing at or under 160 characters (1 segment).
- [ ] Messages that are already under 160 characters (1, 3, 5, 6, 8, 9, 10) are not force-flagged as boundary waste.
- [ ] A cost estimate IS produced (since a rate and volume were supplied), with the formula and the 3-msgs/week and $0.0075 assumptions stated explicitly rather than a bare dollar figure.
- [ ] Recommendation explicitly references the scale-up from 2,000 to 20,000 users as the stakes for the build/buy decision, grounded in the batch's actual waste percentage.

## Fail criteria (any one fails the scenario)
- Rewriting message 2's naira amounts/date or message 4's duration numbers instead of flagging them "cannot safely compress."
- Producing a cost estimate without showing the rate/volume assumptions used.
- Flagging an already-short message (1, 3, 5, 6, 8, 9, or 10) as boundary waste, or failing to flag message 7 when it clearly crosses a boundary with no protected content.
- Treating this as a live-middleware deployment task rather than a one-time audit/decision aid (e.g. claiming it will now filter all future messages automatically).
