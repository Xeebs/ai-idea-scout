# Scenario 1 — SaaS billing support bot, post-pivot drift (healthy input)

## Context
A B2B SaaS company runs a support chatbot that handles billing questions. Six months ago they shipped a self-serve plan-downgrade feature and added multi-currency invoicing for EU customers. Their golden eval set (used as a CI gate before every bot deploy) was last updated before either launch. CI keeps passing at 94%, but the support team has noticed users getting unhelpful answers on downgrade and currency questions. This is exactly the "CI passes but users complain" trigger moment from the SKILL's "When to use this" section.

## Input: Golden eval set (11 examples, CSV)

```
id,query,expected_behavior
G1,"How do I cancel my subscription?",Explain cancellation flow and retention offer
G2,"What's my next invoice date?",Look up and state next billing date
G3,"I was charged twice this month",Escalate to billing team with charge IDs
G4,"Can I get a refund for an unused seat?",Explain prorated refund policy for seats
G5,"How do I update my credit card?",Walk through payment method update flow
G6,"My invoice shows the wrong company name",Explain how to edit billing profile
G7,"Do you offer annual billing discounts?",State discount tiers for annual plans
G8,"I can't log in to see my invoice",Route to account-access troubleshooting
G9,"What happens if my card declines?",Explain grace period and retry schedule
G10,"How do I add a team member seat?",Walk through seat-add flow and pricing
G11,"I want to upgrade from Starter to Pro",Explain upgrade flow and prorated charge
```

## Input: Production sample (32 rows, last 2 weeks, randomly sampled from support chat logs)

```
id,query
P1,"If I downgrade from Pro to Starter mid-cycle do I get money back?"
P2,"How does downgrading affect my current billing period?"
P3,"I downgraded but I'm still being charged the Pro price"
P4,"Can I downgrade and then upgrade again next month without penalty?"
P5,"Why did my downgrade not take effect immediately?"
P6,"My invoice is in USD but I'm in Germany, can I get EUR?"
P7,"The EUR conversion on my invoice looks wrong compared to today's rate"
P8,"Can you bill me in GBP instead of USD?"
P9,"My multi-currency invoice doesn't show VAT separately"
P10,"How do I cancel my subscription?"
P11,"What's my next invoice date?"
P12,"I was charged twice this month, please help"
P13,"Can I get a refund for a seat I'm not using?"
P14,"How do I update my credit card on file?"
P15,"My invoice shows the wrong company name, how do I fix it"
P16,"Do you have a discount for paying annually?"
P17,"I can't log in to see my invoice"
P18,"What happens if my card gets declined?"
P19,"How do I add another seat to my team?"
P20,"I want to upgrade from Starter to Pro"
P21,"How does downgrading affect my current billing period?"
P22,"If I downgrade will I lose access to the API feature immediately?"
P23,"Can I get EUR invoices for my whole team, not just me?"
P24,"Downgrade button is greyed out, why?"
P25,"My EUR invoice total doesn't match the USD price times the exchange rate"
P26,"Can I cancel my downgrade request before it takes effect?"
P27,"How do I cancel my subscription?"
P28,"What's my next invoice date?"
P29,"I was charged twice this month"
P30,"Can I get a refund for an unused seat?"
P31,"I can't log in to see my invoice"
P32,"I want to upgrade from Starter to Pro"
```

## Running the skill

Paste the golden set and production sample into the prompt from README.md exactly as instructed, noting the sample is from the last 2 weeks.

## Pass criteria

The output should:
1. State N_golden = 11 and N_prod = 32 up front.
2. Produce 5-15 named clusters, and clearly identify at least two distinct clusters for the new, uncovered functionality: something like "mid-cycle downgrade proration/timing" (P1-P5, P21, P22, P24, P26) and "multi-currency invoicing/EUR conversion" (P6-P9, P23, P25) — these two clusters alone cover roughly 13 of 32 rows (~40%).
3. Classify both of those clusters as **Uncovered** (the golden set has no downgrade-proration or multi-currency example — G11 covers upgrade, not downgrade, and no G entry mentions currency).
4. Classify the repeated/familiar clusters (cancellation, invoice date, double-charge, seat refund, card update, wrong company name, annual discount, login issue, seat add, upgrade) as **Covered**, correctly matching them to G1-G10 and part of G11.
5. Report an overall coverage read in the HIGH or at least MEDIUM-HIGH drift-concern range, given ~40% of sampled traffic lands in Uncovered clusters.
6. Quote verbatim rows (e.g., "If I downgrade from Pro to Starter mid-cycle do I get money back?") as candidate additions — not paraphrased or invented text.
7. Explicitly label the method as qualitative LLM clustering, not a statistical divergence score.
8. Not recommend deleting or editing any existing G1-G11 entry.
9. Not raise a low-confidence/small-sample caveat as the dominant conclusion — 32 rows over 2 weeks, randomly sampled, is a reasonable (if not huge) sample, so this should be treated as a usable signal, possibly with a light note that a larger sample would increase confidence.

## Fail criteria
- Misses both the downgrade and currency clusters, or buries them as "Covered" because G11 or G5 superficially mention billing.
- Invents a production example that isn't in the pasted list.
- Presents the coverage percentage as a precise statistical metric (e.g., claims a specific Jensen-Shannon divergence value).
- Recommends removing or rewriting a golden-set entry rather than only adding.
