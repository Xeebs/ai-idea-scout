# Scenario 1 — Cash-transfer WhatsApp advisor, live and already failing

## Input (realistic)

A program officer at a cash-transfer NGO pastes:

> We run an AI advisor over WhatsApp Business API for about 650 recipients in a rural district of Eastern Province, Rwanda, as part of a 12-month pilot. It's been live for 3 months. We're seeing recipients ask things like "what's the price of maize at the Kibungo market this week" and "is the agro-input shop in Rukira still open" — and the bot either gives a confident-sounding but wrong price (we checked, it was off by 40%) or an outdated one from training data. We have 14 field officers who already visit the district's 3 main markets roughly weekly as part of our existing cash-disbursement operations, plus a partnership with a network of ~20 small agro-dealers who already text us stock updates informally and inconsistently. We get roughly 40-60 hyperlocal price/availability questions a week across the WhatsApp channel.

## Expected output — pass criteria

The resulting plan should:

1. **Failure Mode section** names the specific failure (confidently wrong prices + stale/training-data answers), not a generic restatement.
2. **Reporter Network Design** explicitly recommends tapping the existing 14 field officers and/or the 20 agro-dealers rather than proposing a brand-new recruitment channel, and ties reporter count to the 3 markets named (not a vague "recruit some reporters").
3. **Incentive section** addresses that the agro-dealers are already informally reporting and proposes formalizing that into a reliable channel (e.g., small stipend or program benefit) rather than assuming goodwill continues indefinitely, and names this as a sustainability risk.
4. **Data Schema** covers both price (maize, and should generalize to other staples) and service/availability status (agro-dealer open/stocked) as two distinct schemas with different freshness windows (price should decay slower than open/closed status, or the plan should justify its chosen windows).
5. **WhatsApp Intake Flow** is a literal, short (3-5 turn) message sequence usable by a field officer or agro-dealer on a basic phone.
6. **Advisor Integration Hook** includes a literal abstention sentence template usable in the advisor's prompt — not just "it should say it doesn't know."
7. **Pilot Validation Plan** references the 40-60/week question volume to size a reasonable sample for the accuracy comparison, and specifies a 2-4 week minimum window.
8. **Top Risks** includes reporter sustainability (the already-identified risk) and at least one risk specific to this input (e.g., a 40% price error already observed — is the baseline systematically biased, not just stale?).

**Fail** if the plan is generic enough that it could be pasted unchanged for any region (no reference to the 3 markets, 14 field officers, 20 agro-dealers, or the 40-60/week volume), or if it fabricates a specific maize price or dealer status anywhere.
