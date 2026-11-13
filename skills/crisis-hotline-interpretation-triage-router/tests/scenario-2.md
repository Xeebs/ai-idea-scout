# Scenario 2 — Dari → English shelter/logistics hotline, mostly-clean sample with numeric/address errors

## Context
A volunteer hotline supporting resettled Afghan families is deciding whether a cloud MT API (an unnamed commercial vendor) can handle Dari → English shelter and supply-request messages unsupervised, reserving the small human-interpreter pool for anything riskier. Unlike scenario 1 (medical domain, mostly-broken sample, clear No-Go), this batch is logistics/shelter domain, mostly clean, and the question is whether a conditional Go with a narrow escalation rule is defensible. They collected 24 message pairs from a one-week pilot, each with a back-translation into Dari.

## Input (what the user pastes)

LANGUAGE PAIR: Dari -> English
DOMAIN: logistics/shelter/evacuation
MT SYSTEM: unnamed commercial vendor API

SAMPLE MESSAGES (24 pairs, representative excerpts shown):

1. Source: "ما به یک پتو و یک چراغ نیاز داریم" | MT: "We need a blanket and a lamp" | Back-translation: "We need a blanket and a lamp" — accurate.
2. Source: "خانواده ما هفت نفر است و به دو اتاق نیاز دارد" | MT: "Our family is five people and needs two rooms" | Back-translation: "Our family is five people and needs two rooms" — numeric error: source says seven, MT/back-translation both say five. Headcount wrong.
3. Source: "آدرس ما خیابان ۱۴، پلاک ۲۳ است" | MT: "Our address is street 14, number 32" | Back-translation: "Our address is street 14, number 32" — digits transposed (23 -> 32), wrong address.
4. Source: "ما فردا صبح به کمپ منتقل می‌شویم" | MT: "We are being moved to the camp tomorrow morning" | Back-translation: accurate.
5. Source: "پدر بزرگم نمی‌تواند راه برود، به ویلچر نیاز دارد" | MT: "My grandfather can't walk, he needs a wheelchair" | Back-translation: accurate.
6. Source: "ما در مسجد محل نزدیک بازار منتظر هستیم" | MT: "We are waiting near the market" | Back-translation: dropped named entity — source specifies "at the mosque near the market," MT dropped "mosque," leaving only a vaguer location.
7. Source: "لباس گرم برای سه بچه نیاز داریم" | MT: "We need warm clothes for three children" | Back-translation: accurate.
8-24: (17 additional pairs — mostly supply/shelter requests and status updates; back-translations confirm all accurate, no flagged issues; wording varies in formality but no safety-relevant drift)

## Expected output (what a correct run of the skill produces)

- Confirms inputs: Dari -> English, logistics/shelter/evacuation domain, n=24, MT system named as the unspecified commercial vendor, and notes n=24 clears the 20-pair floor so confidence is not automatically capped at LOW on sample-size grounds alone.
- Flags messages 2, 3, and 6, each with a correct failure type:
  - Message 2: meaning drop / content error (headcount numeric error), scored at least MEDIUM per the logistics domain weighting rule for numeric/address errors.
  - Message 3: meaning drop / content error (address digit transposition), scored at least MEDIUM — an operationally significant error (wrong physical address) even though it isn't life-threatening.
  - Message 6: meaning drop / content error (dropped named entity/location), scored LOW-to-MEDIUM depending on how load-bearing "mosque" is for locating the family (reasonable for the skill to note this is borderline and explain its reasoning either way).
- Does NOT flag messages 1, 4, 5, 7, or any of 8-24 as having problems, and does not invent issues beyond what the back-translations support.
- Does NOT escalate the overall domain to HIGH risk or declare a full No-Go — this is not a medical/emotional-support domain, and the flagged issues are numeric/address accuracy problems, not life-threatening urgency distortion, so a conditional Go is a defensible verdict here (contrast with scenario 1).
- Summary shows a low overall HIGH/MEDIUM percentage (roughly 2-3 of 24 flagged, none at HIGH) and identifies numeric/address errors as the dominant failure type for this pair — distinct from scenario 1's urgency-distortion-dominant finding.
- Recommendation: a specific, operable escalation rule such as "let MT run unsupervised for routine shelter/status messages, but route any message containing a headcount, address, or numeric quantity to a human interpreter (or require a second automated check) before acting on it" — not a blanket No-Go, and not a blanket unconditional Go either.
- Confidence on the verdict rated MEDIUM (not HIGH, since only 24 samples and no bilingual reviewer note beyond self-generated back-translation; not LOW either, since sample size clears the floor and every message has a back-translation).
- Does not fabricate details not traceable to the pasted messages or back-translations.

## Pass/Fail criteria

- PASS if: the report flags messages 2 and 3 at minimum with correct failure-type labels (numeric/address content errors) at MEDIUM or higher, does not flag any of messages 1, 4, 5, or 7, issues a conditional/partial-Go verdict rather than a blanket No-Go or an unconditional full-Go, gives a specific numeric/address-triggered escalation rule, and rates confidence MEDIUM (not HIGH, not LOW) with a reason tied to sample size and back-translation-only validation.
- FAIL if: it declares a blanket No-Go for the whole domain (over-applying scenario-1-style caution to a non-medical, mostly-clean batch), declares an unconditional Go with no escalation rule at all, misses the headcount or address numeric errors, flags clean messages (1, 4, 5, 7) as problematic, rates confidence HIGH, or invents details not present in the input.
