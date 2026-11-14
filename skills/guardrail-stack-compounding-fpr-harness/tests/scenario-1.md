# Scenario 1 — Labeled sample, three-guard stack, OR logic (happy path)

## Setup

A trust-and-safety engineer at a mid-size SaaS company is about to flip on enforcement for a three-guard stack (`pii-filter`, `jailbreak-classifier`, `content-policy`) in front of their support-chatbot LLM. They pulled a week of shadow-mode logs, had a reviewer label 15 of the requests as benign (pulled from already support-cleared tickets) and 5 as genuinely malicious (from a red-team set), and export this long-format CSV. Their stack blocks a request if **any** guard fires (OR logic), though they don't mention this explicitly in their message — they just paste the data and ask: "Can we turn blocking on for this stack or will it nuke our users?"

## Input data (paste exactly as given to the skill)

```csv
request_id,guard,verdict,ground_truth
1,pii-filter,pass,benign
1,jailbreak-classifier,pass,benign
1,content-policy,pass,benign
2,pii-filter,pass,benign
2,jailbreak-classifier,pass,benign
2,content-policy,pass,benign
3,pii-filter,pass,benign
3,jailbreak-classifier,pass,benign
3,content-policy,block,benign
4,pii-filter,pass,benign
4,jailbreak-classifier,pass,benign
4,content-policy,pass,benign
5,pii-filter,pass,benign
5,jailbreak-classifier,pass,benign
5,content-policy,block,benign
6,pii-filter,pass,benign
6,jailbreak-classifier,pass,benign
6,content-policy,pass,benign
7,pii-filter,block,benign
7,jailbreak-classifier,pass,benign
7,content-policy,pass,benign
8,pii-filter,pass,benign
8,jailbreak-classifier,pass,benign
8,content-policy,pass,benign
9,pii-filter,pass,benign
9,jailbreak-classifier,pass,benign
9,content-policy,block,benign
10,pii-filter,pass,benign
10,jailbreak-classifier,pass,benign
10,content-policy,pass,benign
11,pii-filter,pass,benign
11,jailbreak-classifier,pass,benign
11,content-policy,pass,benign
12,pii-filter,pass,benign
12,jailbreak-classifier,pass,benign
12,content-policy,block,benign
13,pii-filter,pass,benign
13,jailbreak-classifier,pass,benign
13,content-policy,pass,benign
14,pii-filter,pass,benign
14,jailbreak-classifier,pass,benign
14,content-policy,pass,benign
15,pii-filter,pass,benign
15,jailbreak-classifier,pass,benign
15,content-policy,pass,benign
16,pii-filter,pass,malicious
16,jailbreak-classifier,block,malicious
16,content-policy,pass,malicious
17,pii-filter,pass,malicious
17,jailbreak-classifier,block,malicious
17,content-policy,block,malicious
18,pii-filter,pass,malicious
18,jailbreak-classifier,pass,malicious
18,content-policy,pass,malicious
19,pii-filter,pass,malicious
19,jailbreak-classifier,block,malicious
19,content-policy,pass,malicious
20,pii-filter,block,malicious
20,jailbreak-classifier,block,malicious
20,content-policy,pass,malicious
```

The requester does not state combination logic; stack is actually OR (block if any guard fires), matching the skill's stated default assumption.

## Expected ground-truth math (for the evaluator to check the output against)

- 15 benign requests, 5 malicious requests, 60 total verdict rows across 3 guards — all parsed cleanly.
- Benign requests wrongly blocked by the stack (OR logic): requests 3, 5, 7, 9, 12 → **5 of 15 → blended FPR = 33.3%**.
- Per-guard FPR on the 15 benign requests: `content-policy` = 4/15 (26.7%) — requests 3, 5, 9, 12; `pii-filter` = 1/15 (6.7%) — request 7; `jailbreak-classifier` = 0/15 (0%).
- Top false-block attribution: **content-policy**, responsible for 4 of the 5 false blocks.
- Malicious requests missed by the full stack: request 18 only → blended FNR = 1/5 (20%).
- Sample size (15 labeled benign rows) is just above the 30-row low-confidence threshold line in the skill's design — it is **below** 30, so the result must be flagged low-confidence/directional, not reported as a mature number.

## Pass criteria

- [ ] States the stack combination logic it is assuming (OR / block-if-any-fires) and asks the requester to confirm, since it wasn't stated.
- [ ] Reports per-guard block rate and FPR/FNR table matching the math above (content-policy FPR ~26.7%, pii-filter FPR ~6.7%, jailbreak-classifier FPR 0%).
- [ ] Reports blended stack FPR at or near 33% (5/15) and states the labeled-benign sample size (15) next to the number.
- [ ] Flags the result as low-confidence/directional because the labeled-benign sample (15) is under the 30-row threshold — does not present 33.3% as a firm, final number.
- [ ] Ranks content-policy as the top attribution guard for false blocks (4 of 5).
- [ ] Gives a readiness read using the 5%/15% default thresholds (33% is well over 15% → "not ready" / enforcing now would reproduce the users-route-around-it problem), while also naming the low-confidence caveat.
- [ ] Gives one concrete next step (e.g. tune or narrow content-policy's triggers, then re-run with a larger labeled sample before enforcing).

## Fail criteria

- Silently assumes AND/quorum logic, or enforces no stated assumption at all.
- Reports 33.3% (or any number) as a confident, final rate without the low-confidence flag.
- Misattributes the top false-block guard (anything other than content-policy).
- Fabricates a malicious-side FNR number disconnected from the data (correct is 1/5 = 20%, request 18 only).
