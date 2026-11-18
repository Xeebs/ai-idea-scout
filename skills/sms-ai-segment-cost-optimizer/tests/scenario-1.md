# Scenario 1 — Maternal health SMS chatbot in Kenya (mixed GSM-7/UCS-2, Swahili)

## Context
A small NGO runs an AI chatbot over SMS (via Africa's Talking) answering maternal-health questions for rural users in Kenya who text in English or Swahili. They have no API access handy for this audit (their Africa's Talking account is managed by a contractor), so they export and paste a log of the last day's AI-generated responses. They want to know if it's worth building the segment-compression middleware described in the parent idea before they scale to more clinics.

## Input (pasted log, no rate given yet)

```
1. Prenatal vitamins should be taken once daily with food. Take 1 tablet of folic acid (400mcg) every morning, ideally at the same time each day.
2. Clinic is open Mon-Fri 8am-4pm.
3. Hujambo! Dawa yako ya malaria inapaswa kunywa mara mbili kwa siku kwa siku 3. Kama una kichefuchefu, kunywa na chakula. 🙂
4. Your next antenatal checkup is scheduled for the 14th. Please bring your clinic card and arrive by 9am if possible, as the clinic gets busy later in the day.
5. Thank you for your question. Breastfeeding is recommended exclusively for the first 6 months of a baby's life, as it provides all the nutrition a baby needs during this period.
6. Yes, mild headaches in the second trimester are quite common for many pregnant women and are usually not a cause for concern, though always mention any symptoms to your clinic nurse.
7. If you experience heavy bleeding, severe abdominal pain, or a fever above 38°C, go to the nearest clinic immediately — do not wait.
8. Iron supplements help prevent anemia during pregnancy.
9. Asante kwa swali lako. Ni kawaida kuhisi uchovu wakati wa ujauzito, lakini kama unahisi uchovu mkubwa sana tafadhali wasiliana na kliniki.
10. Your test results were normal. No further action needed at this time, see you at your next scheduled visit.
```

Encoding: not sure for all — some contain Swahili and one emoji.

## Expected handling

- Messages 3 and 9 (Swahili text, message 3 also has an emoji) must be flagged as UCS-2 (70/67 char budget), not GSM-7 — this changes their segment math significantly.
- Message 1 (dosage: "400mcg", "1 tablet", "every morning") must be flagged "cannot safely compress" if it crosses a boundary — it contains dosage/numeric content.
- Message 4 (date "14th", time "9am") must similarly be protected if flagged as boundary waste.
- Message 7 (temperature "38°C", "immediately", "do not wait") must be protected — classic safety-critical warning language.
- Message 10 ("normal", "no further action") has no dosage/date/unit but is borderline — a reasonable rewrite preserving "results were normal, no action needed, see you at next visit" is acceptable since no fact is numeric/date-specific beyond what's already generic.
- Message 5 (breastfeeding, 176 chars, 2 segments) crosses a boundary but contains "first 6 months" (a number+duration) — it is acceptable for the skill to flag this one "cannot safely compress" under the default conservative rule (number/unit present), even though a human might judge "6 months" non-critical here. This is an intentional edge case testing that the skill errs conservative by default rather than guessing.
- **Message 6 is the designed clean-compression case**: 182 characters (2 segments under the 153-char multi-segment budget), no number/date/unit/warning-phrase content, and only 22 characters over the 160-char single-segment threshold — within the 15%-of-length (27 chars) boundary-waste rule. It MUST get a concrete rewrite trimming it to <=160 characters (1 segment) while keeping its meaning, since there is no protected content to block it.
- Messages 2 and 8 are short and likely already "clean" (under the single-segment limit), not boundary waste.
- No dollar cost estimate should be produced since no rate was supplied — output must say so explicitly rather than inventing a figure.

## Pass criteria
- [ ] Each message gets an explicit encoding determination (not a blanket assumption), with messages 3 and 9 correctly identified as UCS-2.
- [ ] Segment counts are computed using the correct per-segment budget (160/153 for GSM-7, 70/67 for UCS-2) — not naive "divide by 160" math applied to every message.
- [ ] Messages 1, 4, and 7 are never rewritten with their dosage/date/temperature/warning content altered — they appear under "cannot safely compress" with the specific blocking content named, if flagged as boundary waste at all.
- [ ] Message 6 crosses a boundary (2 segments at 182 chars) and gets a concrete before/after rewrite with char counts and segments saved shown, landing at or under 160 characters (1 segment).
- [ ] The summary table reports totals/percentages and explicitly states no cost estimate is given (since no rate was supplied), rather than inventing a placeholder rate.
- [ ] The recommendation paragraph ties back to the batch's actual waste percentage, not a generic "yes you should build this" regardless of the numbers.

## Fail criteria (any one fails the scenario)
- Treating all 10 messages as GSM-7 without checking for Swahili/emoji content.
- Rewriting message 1, 4, 7, or 10 (if it alters the "normal"/"no further action" fact pattern) in a way that drops or changes a number, date, or warning.
- Producing a dollar savings figure without a rate having been supplied.
- Reporting segment counts using single-segment limits (160/70) even for messages that need 2+ segments (should drop to 153/67).
