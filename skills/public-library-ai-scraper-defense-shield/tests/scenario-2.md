# Scenario 2 — University library with no defense, no logs, just a complaint

## Input (realistic, as a user would paste it)

> Current stack: Honestly nothing specific. We're on a standard university-hosted Apache server for our special collections digital archive (digitized manuscripts, finding aids). No Anubis, no Cloudflare, nothing we set up ourselves — just whatever the central university IT provides by default, which I don't think is much.
>
> Log sample / symptoms: I don't have log access myself — that's controlled by central IT and getting it takes a ticket that's been open for two weeks. What I know is our finding-aid search page has been timing out for patrons on and off for about a month, and our director got an email from someone saying our site was "clearly getting scraped for AI training data" based on a blog post they read about libraries in general. I don't actually know if that's what's happening to us specifically.
>
> Incident notes: We haven't tried anything yet because we don't know what's wrong.

## Expected output characteristics (pass/fail checklist)

- [ ] Classifies current posture as bucket (a): no bot defense (not "nothing" being misread as some other bucket).
- [ ] Explicitly states that without log access, it cannot confirm this specific institution is being hit by AI scraper bots as opposed to another cause (traffic spike, misconfigured server, unrelated outage) — this is the critical check, since the input gives only a secondhand claim and a correlated symptom, not real evidence.
- [ ] Does NOT assert "your site is being scraped by AI bots" as fact — uses "consistent with" framing and explicitly separates "what the director was told" from "what's actually confirmed."
- [ ] Top recommendation is a reasonable bucket-(a) floor action (e.g. deploy Anubis as a baseline defense, since there is currently no bot defense at all) — but it must be paired with, not substituted for, an explicit instruction to confirm the actual cause (get log access / escalate the IT ticket) rather than treating the secondhand "it's AI scraping" claim as settled fact.
- [ ] Explicitly names what to ask central IT for in the stalled ticket (e.g. user-agent distribution, request timing on the finding-aid search endpoint, referrer headers) — concretely actionable given the two-week ticket delay is part of their stated problem.
- [ ] Includes an accessibility safeguard note for the floor recommendation (Anubis/challenge) even though it's provisional, since any PoW challenge affects legitimate patrons.
- [ ] Section 6 ("what to check next") is substantive here, not a throwaway line, since this scenario is explicitly the low-evidence case the skill's procedure step 6 and guardrail exist for.
- [ ] Does not recommend a paid/commercial tool as the top priority given a university-hosted small special-collections unit with no stated budget context — or if it mentions one, frames it as needing institutional budget approval, not an immediate step.
- [ ] Stays roughly one page and keeps the six-part structure.

**Pass condition**: at least 6 of 8 boxes checked, including these three critical items: not asserting unconfirmed scraping as fact (box 3), pairing the floor recommendation with an explicit cause-confirmation step rather than treating the secondhand claim as settled (box 4), and a substantive "what to check next" section (box 7).
