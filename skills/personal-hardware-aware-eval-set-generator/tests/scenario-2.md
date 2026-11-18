# Scenario 2: Support ticket triage classifier

## Context
A small team runs a local model to pre-sort incoming support tickets into categories before a human looks at them. They have a decent pile of real tickets with known correct labels, and want to know if their set is good enough to compare two candidate models.

## Input handed to the skill

Task: "Classify an incoming support ticket into exactly one category: billing, bug, feature-request, or account-access. Output must be exactly one of those four strings."

Examples:
1. Input: "I was charged twice for my subscription this month, can you refund the duplicate?" / Correct label: billing
2. Input: "The export button on the dashboard does nothing when I click it, no error either." / Correct label: bug
3. Input: "Would be great if you could add dark mode to the mobile app." / Correct label: feature-request
4. Input: "I can't log in, it says my password is wrong but I'm sure it's right." / Correct label: account-access
5. Input: "My invoice shows a different plan than what I signed up for, and also the totals look off and now I also can't log in to check." / Correct label: billing (per team's tie-break rule: billing takes precedence when billing+access overlap)
6. Input: "Nothing happens when I try to upload a CSV larger than 10MB — no error, no progress bar, just stuck." / Correct label: bug
7. Input: "Can we get an API endpoint for bulk-exporting tickets?" / Correct label: feature-request

Candidate models: none specified by the user this time.

## Pass criteria
- Classifies all 7 examples as deterministic (single correct label from a fixed small set) and assigns exact-match / structured-label-match as the scoring method, not LLM-judge.
- Sample-size verdict: 7 examples across 4 categories is "usable-rough / borderline" — billing has 2, bug has 2, feature-request has 2, account-access has only 1; flags account-access as the weakest/under-represented category and recommends adding more, especially since 7 total is below the 8+ "sufficient" bar.
- Flags example 5 as the key edge case already present (a genuine boundary/ambiguous case between billing and account-access) and credits it, while still identifying at least one other missing edge case the set lacks — e.g., no clearly ambiguous bug-vs-feature-request case, no malformed/very short ticket ("it's broken"), no ticket with no clear category at all (true out-of-scope/none-of-the-above case), no multi-language or non-English ticket if that's realistic for this team.
- Does NOT draft an open-ended LLM-judge rubric as the primary scoring method for these examples, since they're deterministic — a rubric section may be omitted or clearly marked not applicable, rather than forcing a 1/3/5 rubric onto exact-match data.
- Still includes the mandatory limitation line about LLM-judge calibration in general terms if judge-based scoring is mentioned anywhere (e.g., noting it would only apply if they later add open-ended categories), but does not fabricate a judge rubric where exact-match suffices.
- Does not invent an 8th example or guess at a tie-break rule not stated (example 5's rule was given; nothing else should be invented).
- Includes the "Not Covered By This Review" closing note and does not recommend a specific model despite none being named.

## Fail criteria
- Forces an LLM-judge rubric onto clearly deterministic classification data.
- Misses that example 5 is already the boundary/ambiguous case and asks for one as if none exists.
- Fails to call out account-access as under-represented (only 1 example vs 2 each for the others).
- Invents ticket content or a tie-break rule not given by the user.
