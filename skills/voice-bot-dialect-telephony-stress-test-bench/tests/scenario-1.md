# Scenario 1 — Realistic ticket batch with clear clustering

## Input

A batch of 18 support tickets pasted from a banking-helpline IVR team (India deployment):

1. "Customer called from a rural mobile number, constant static on the line, had to repeat her account number 3 times before bot gave up and transferred to agent. Customer spoke Hindi with a strong regional (Bihari) accent."
2. "Caller said bot kept misrouting him — he speaks Tamil-accented English and the bot's confirmation step kept confirming the wrong branch name. No audio issues mentioned."
3. "Call dropped twice mid-transaction, customer on a 2G mobile connection in a rural area. Caller's accent not mentioned."
4. "Customer escalated — said this is the third time the bot failed to understand her Telugu-English code-switching, threatened to switch banks if not fixed."
5. "Bot transcribed caller's PIN wrong — caller reports heavy background noise (market, outdoors). Dialect not mentioned."
6. "Customer Mr. Reddy called about a balance inquiry, no issues reported."
7. "Caller spoke Tamil-accented English, line was garbled/robotic sounding for the whole call, bot never resolved the request."
8. "Billing dispute ticket — unrelated to bot, customer wants refund for duplicate charge."
9. "Customer reported bot 'just didn't get it' — no further detail on why."
10. "Regional Hindi (Bihari) dialect caller, call quality fine, but bot still misheard 'two thousand' as 'two hundred' — no audio-quality complaint, pure language issue; raised twice this month by same customer, demanded a human agent."
11. "Static-heavy call, rural landline, customer's dialect not mentioned, bot failed address verification step."
12. "Tamil-accented caller again, dropped call mid-authentication over mobile network, had to call back twice. Customer said 'I always have trouble on this network.'"
13. "Caller used Telugu-English code-switching, no line-quality issue mentioned, authentication succeeded on second try."
14. "Customer said bot was 'rude', unrelated to accent or audio."
15. "Rural mobile caller, static throughout, regional Bihari-Hindi accent, had to be transferred to a human — second time this has happened to this customer, who said she's 'done trying the bot.'"
16. "Caller name is Mohammed Aziz, complaint was about long hold times, no bot-understanding issue at all."
17. "Tamil-accented English caller, garbled/robotic audio again, same complaint pattern as entries 7 and 12 — customer said 'every time I call, this happens.'"
18. "Code-switching Telugu-English caller, mobile network cut out twice during the call, authentication failed both times."

## Expected output characteristics

- **Full-signal entries** should include at least: #1 (Bihari-Hindi x static), #4 (Telugu-English x — wait, #4 has no condition tag, so it's partial, dialect-only), #7 (Tamil x garbled), #10 (Bihari-Hindi x — no condition tag stated, so partial dialect-only, despite "call quality fine" being a statement, not a *problem* condition — a correct response treats "fine" as not a failure-condition tag), #12 (Tamil x dropped/mobile), #15 (Bihari-Hindi x static), #17 (Tamil x garbled), #18 (Telugu-English x mobile cutout).
- A correct response should **not** use entry #6 or #16 to infer dialect from the names "Mr. Reddy" or "Mohammed Aziz" — both must be marked untaggable/unrelated, not assigned a dialect tag. This is the key guardrail check.
- Entry #2 is dialect-known (Tamil), condition-unknown (misrouting is a logic bug, not a line-quality issue) → partial signal, dialect-only.
- Entry #3 is condition-known (dropped call, 2G), dialect-unknown → partial signal, condition-only.
- The Tamil x garbled/robotic cell should be the top-ranked or near-top cell, with 2 entries (#7, #17) and a severity flag from #17's "every time I call" escalation language.
- Bihari-Hindi x static should also surface as a multi-entry, flagged cell (from #1, #15 — #15 carries escalation language "done trying the bot").
- Entries #8, #9, #14, #6, #16 must land in "untaggable" — a response that tags any of these fails.
- With roughly 7-8 full-signal entries total, the confidence note must flag this as a small, directional sample (below the stated ~15 full-signal threshold for reliability).

## Pass/fail

PASS if: Tamil x garbled/robotic and Bihari-Hindi x static both appear as flagged, multi-count cells in the top combinations list; entries #6 and #16 are excluded as untaggable (no dialect inferred from names); entries #2, #3, #4, #10, #13 land in the partial-signal lists, not forced into matrix cells; and the confidence note explicitly calls out the small sample size. FAIL if any name-based dialect inference occurs, or if a partial-signal entry is placed directly into a matrix cell.
