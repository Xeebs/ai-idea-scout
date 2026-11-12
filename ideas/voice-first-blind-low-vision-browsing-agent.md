# Beyond the Pilot: A Production-Grade Voice-First Browsing Agent for Blind and Low-Vision Users

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: Voice & multimodal agents
- **Source**: research/2026-11-12-voice-multimodal-agents-ii.md · P5
- **Maturity verdict**: PARTIAL (CoBrowse AI is a real beta product working "only on websites where it's implemented," with AppleVis cautioning the beta is no guarantee of public release; CUNY's Screen Agent, a CHI '26 Wizard-of-Oz study, and Google Research's StreetReaderAI are all explicitly labeled pilots/prototypes by their own authors; close to the OPEN line but one genuine narrow beta implementation plus hackathon demos keeps it at PARTIAL)
- **Format**: BOTH

## The Gap
Every voice-driven web-navigation agent for blind and low-vision users found in the last 30 days is explicitly labeled a pilot, prototype, or beta by its own creators. CUNY's "Screen Agent" is "presented as a pilot study." A CHI '26 Wizard-of-Oz study with 12 blind/severely-low-vision adults testing a voice shopping agent found users "worried about hallucinations and about handing payment decisions to the agent," favoring tightly constrained interactions — a trust concern an unbuilt safety layer would need to solve, not just a feature gap. CoBrowse AI, the one real beta product, works only on sites where it's specifically implemented, and AppleVis itself cautions the beta is no guarantee of public release. No production-maintained tool lets a blind or low-vision user complete general web tasks (shopping, forms) by voice conversation instead of linear screen-reader navigation.

## The Project
A voice-first browsing agent that lets a blind or low-vision user complete web tasks through natural conversation rather than linear, keyboard-driven screen-reader navigation — but scoped around the CHI study's explicit trust findings rather than ignoring them. It narrates what it sees on the page conversationally, executes low-stakes navigation actions (searching, filtering, reading content) autonomously, and explicitly confirms before any high-stakes action (payment, form submission, account changes), closing the trust gap the pilot studies surfaced rather than papering over it.

Components: a page-understanding layer that works across arbitrary sites (not CoBrowse AI's per-site-implementation model), a stakes-classifier that gates autonomous action vs. required confirmation, a conversational narration layer tuned for voice (not verbatim screen-reader text), and a task-completion benchmark built from the same task types the CHI study used (e.g., online shopping end-to-end).

## Tangible Impact
**Population**: blind and low-vision internet users who currently rely on traditional screen readers for linear, keyboard-driven navigation — a population the National Federation of the Blind and American Council of the Blind commonly estimate in the low millions of working-age adults in the US alone, many of whom the CHI '26 study found are open to voice agents but distrustful of specific high-stakes actions.
**Mechanism**: replacing linear screen-reader navigation with voice conversation for routine tasks, while explicitly gating high-stakes actions behind confirmation, lets users complete tasks faster without the item-by-item traversal screen readers require, while directly addressing the hallucination/payment-trust concern the pilot study identified as the actual blocker to adoption, not merely a nice-to-have.
**Measure**: task completion time and success rate vs. a standard screen-reader baseline on matched tasks (e.g., completing an online purchase); user-reported trust/comfort score, specifically around high-stakes actions; rate of correctly-gated high-stakes confirmations vs. incorrectly autonomous high-stakes actions (should be zero) on a held-out task set.

## Why Now
Page-understanding multimodal models and voice interfaces are now capable enough to narrate and act on arbitrary web pages without per-site integration (unlike CoBrowse AI's current per-site-implementation limitation), and the CHI '26 study's trust findings give this project concrete, user-validated design constraints to build against rather than guessing at what blind users will trust.

## Skill Angle
A Claude Code skill that, given a website's structure or screenshots, audits its voice-navigability for this kind of agent — flagging pages/flows with poor semantic structure, missing ARIA labels, or ambiguous high-stakes actions that would need explicit confirmation gating, and drafting concrete fixes. This is a one-shot accessibility-audit task, useful to site owners independent of whether the runtime browsing agent itself gets built.

## MVP Sketch
Build the page-understanding + stakes-classifier + confirmation-gating loop as a browser-automation agent targeting a small set of real e-commerce sites (not requiring per-site implementation); recruit a handful of blind/low-vision testers to attempt the same shopping tasks used in the CHI '26 study; measure completion time, success rate, and trust ratings against a screen-reader baseline. The single experiment: does the confirmation-gated voice agent achieve comparable or better task success with higher trust ratings than the screen-reader baseline, on the CHI study's own task type.

## Risks & Open Questions
- The CHI study's trust concerns are the strongest reason this might stay unsolved: if users don't trust the stakes-classifier's judgment, the "tightly constrained interactions" preference the study found may limit the agent to a narrower task set than hoped.
- Hallucination on page content (misreading what's actually on screen) is a real failure mode for exactly the population least able to independently verify the agent's claims.
- Generalizing across arbitrary site structures (vs. CoBrowse AI's per-site model) is a harder engineering problem than it looks; early versions may need to start narrow and expand.
- Accessibility research funding and nonprofit/advocacy-org partnership may be necessary for credible user testing, which is a slower path than a typical software MVP.
