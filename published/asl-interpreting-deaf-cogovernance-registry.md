# Signing Off: A Deaf-Led Co-Governance Registry for AI ASL Interpreting Vendors

Several companies are now shipping real-time AI sign-language interpreting and pitching it, explicitly, as the fix for a rural interpreter shortage. That pitch sounds like access. But when you ask the people the product is for, the top two concerns they raise aren't about accuracy or latency — they're about who's making money off their language and who gets to say yes or no to how it's built. Nobody independently checks which vendors have actually closed that gap, as opposed to just saying the right words about it.

## The Gap

Nagish, Sorenson, and the UK startup Silence Speaks are all shipping or piloting real-time AI ASL-to-text or avatar interpreting, framed as a backup for places where human interpreters are hard to find — Nagish's own CEO has described the product's value in exactly those terms, helping people "where interpreters are hard to get." Sorenson and Silence Speaks have unveiled AI-ASL translation avatars with no human interpreter in the loop at all.

Meanwhile, a global survey of Deaf and hard-of-hearing community members on sign-language technologies found the top two concerns were "hearing people making money from sign language technologies" and "few deaf people leading or contributing." On Reddit, r/ASLinterpreters moderators have pushed back on the automated-interpreting timeline directly, urging people to lobby for certified human interpreters instead. The rural-access promise and Deaf-led accountability are being sold as if they come bundled together. The research digest behind this idea found no evidence that they actually do — and no product anywhere pairs the access pitch with a verified, independently checked co-governance structure.

It's not that nobody is talking about governance. DeepMind has a company-published "AI Sign Language Advisory Committee" for its SL2T feature, and Signapse has published its own AI governance framework claiming Deaf involvement in design, testing, and governance. Outside industry, the EUD's 15-principle ethical framework and a Cambridge/Minderoo report on BSL procurement both lay out what real Deaf-led governance should look like. What's missing is the connective tissue: nobody is checking whether any specific vendor's claims clear that bar, using criteria Deaf reviewers actually control rather than a company's own press release.

## The Project

The idea is a public, Deaf-led registry that scores AI ASL interpreting vendors against a concrete co-governance bar, built from the existing EUD framework and the Cambridge/Minderoo report rather than inventing a new rubric from nothing. The bar isn't "has an advisory committee" — it's majority-Deaf advisory authority that can actually be exercised, published decision-making power over product changes, and a track record of the vendor acting on Deaf-reviewer feedback, not just collecting it.

Each vendor in scope — Nagish, Sorenson, Silence Speaks, DeepMind's SL2T, Signapse — gets a public scorecard with cited evidence for every claim, re-reviewed on a fixed cadence as vendors update what they say about their own governance. The centerpiece isn't a new interpreting model or a better translation algorithm; it's the review process itself, staffed and controlled by Deaf reviewers applying a rubric independently of the vendors being scored.

## Tangible Impact

**Population**: Deaf and hard-of-hearing people being offered AI ASL interpreting as a substitute for human interpreters in rural or low-access settings, and the institutional buyers (school districts, hospitals, courts) deciding which vendor to adopt on their behalf. Roughly 11 million US adults report serious difficulty hearing (US Census ACS), with interpreter shortages concentrated in exactly the rural counties these products target.

**Mechanism**: gives Deaf users and procurement teams a credible, independently applied score instead of a vendor's self-reported "AI Sign Language Advisory Committee" press line, and gives vendors a concrete, public bar to meet for co-governance credibility — raising the cost of claiming Deaf involvement without ceding real authority.

**Measure**: (1) number of vendors scoring above the defined co-governance bar vs. self-reported-only claims; (2) Deaf-reviewer-rated trust/accuracy delta between certified and uncertified tools on a shared evaluation set; (3) adoption rate of certified tools among surveyed rural institutional buyers after the registry launches.

## Try It

A companion skill exists at `skills/asl-interpreting-deaf-cogovernance-registry/`: *"Scores a specific AI ASL interpreting vendor's published governance claims against a concrete Deaf co-governance bar (majority-Deaf authority, published decision power, responsiveness track record, reviewer compensation, data representation) and cites the exact evidence or gap for each. Use when a procurement reviewer (school district, hospital, court) is evaluating one named AI ASL interpreting vendor and needs a defensible pass/fail before signing a contract."*

This is the fast, single-buyer version of the idea — a one-shot checklist for the specific moment a school district accessibility lead, hospital interpreter-services manager, or court administrator is staring at one vendor's sales material and needs a defensible answer before signing, rather than the standing public registry itself. To use it: paste the skill's `README.md` into any AI chat tool along with the vendor's published governance material and your own sales-call notes, or drop the whole `skills/asl-interpreting-deaf-cogovernance-registry/` folder into `~/.claude/skills/` if you're using Claude Code. It never renders a sign/don't-sign recommendation — that stays the reviewer's call — and it never scores a criterion PASS on reputation alone, only on specific, cited claims.

Worth saying plainly, since the idea file's own risk list says it first: a registry has no enforcement power beyond reputation, and vendors could learn to publish more impressive-sounding governance language without ceding any real authority — which is exactly why every score here has to trace to a specific document or quote, not a vibe. It's also possible an existing Deaf advocacy organization like NAD or RID is already running something informally close to this; that's worth direct outreach before assuming this is greenfield.

---

Surfaced from `research/2026-11-13-applied-ai-underserved-domains-6th.md`, pattern `P1`.
