# Scenario 2 — Pre-launch smallholder-farmer chatbot, no existing network

## Input (realistic)

A product lead at a small agtech nonprofit pastes:

> We're about to launch a Twilio SMS-based farming advisor for smallholder cotton and groundnut farmers across a block in central India — roughly 2,000 farmers, mostly on basic phones, SMS only (no WhatsApp/smartphone access for most). We're pre-launch but we already know from a similar project (Gramhal's Bolbhav) that market-price questions will be the biggest hyperlocal failure point if we don't plan for it now. We don't have any existing field staff or vendor network in this block yet — this is a new area for us. We expect maybe 10-15 price-related questions a day once we scale to the full 2,000 farmers, mostly about cotton and groundnut mandi (market) prices.

## Expected output — pass criteria

The resulting plan should:

1. **Failure Mode section** correctly frames this as a *pre-launch* preventive design (not a retrofit of an observed failure), referencing the Gramhal precedent as the reason to plan now.
2. **Reporter Network Design** acknowledges there is no existing network and proposes a genuinely new recruitment plan (not falsely claiming to "leverage existing field staff" when the input says there are none) — e.g., recruiting market-based volunteers/paid reporters at the specific mandi(s) relevant to cotton/groundnut in that block.
3. The plan adapts to the **channel**: since this is SMS-only (not WhatsApp), the "WhatsApp Intake Flow" section should either be adapted to SMS explicitly or the skill should flag that its default assumes WhatsApp and adjust the message flow to fit SMS's tighter format (short codes, no rich forms) — it must not silently assume WhatsApp Business API features that don't apply to a basic SMS channel.
4. **Data Schema** is scoped to cotton and groundnut mandi prices specifically (not a generic multi-category schema the input didn't ask for).
5. **Pilot Validation Plan** sizes to a sensible fraction of the eventual 2,000-farmer scale and the 10-15/day question volume, explicitly as a pilot (not jumping straight to full 2,000-farmer rollout).
6. **Top Risks** flags that recruiting a reporter network from zero in a brand-new area is a bigger lift/slower timeline than scenario 1, and should not understate this by reusing scenario-1-style language about "existing network."

**Fail** if the plan assumes WhatsApp-specific features (e.g., rich forms, read receipts) without adapting to the stated SMS-only channel, or if it invents an existing field network the input explicitly says doesn't exist.
