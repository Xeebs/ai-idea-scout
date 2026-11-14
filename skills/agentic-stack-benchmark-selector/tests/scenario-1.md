# Scenario 1 — Support-ticket triage agent for a 12-person SaaS startup

## Input a user would give

> We're a 12-person SaaS company (B2B project management tool). We get ~400 support tickets/day across email and Zendesk. We want to build an agent that:
> 1. Reads incoming tickets, classifies urgency (P1-P4) and category (billing, bug, how-to, feature request).
> 2. For P3/P4 how-to questions, drafts a reply from our docs and sends it after a human skims it in a review queue.
> 3. For P1/P2, immediately pages the on-call engineer with a structured summary.
>
> Constraints, most important first:
> - Must run self-hosted in our own AWS VPC (we're on an enterprise contract that requires it — no vendor-managed agent runtime).
> - Our team is all Python, nobody has deep LangGraph/CrewAI experience yet, we have maybe 2 weeks to get a v1 working.
> - Latency doesn't need to be sub-second — a few seconds per ticket classification is fine, it's not interactive chat.
> - We're currently on Anthropic's API but open to switching if there's a strong reason.
>
> Compare: LangGraph, CrewAI, OpenAI Agents SDK, Pydantic AI, Microsoft Agent Framework.

## Pass criteria

- [ ] Output restates the triage/draft-reply/escalate scenario and the four constraints (self-hosting, Python-only/low framework experience, relaxed latency, open-to-switching model) before scoring anything.
- [ ] Drops or flags OpenAI Agents SDK and/or Microsoft Agent Framework if the report finds evidence they push toward a specific vendor-managed or Azure-centric deployment path that conflicts with "self-hosted in our own AWS VPC" — or explicitly confirms self-hosting is fine for each if evidence says otherwise. Either way, the self-hosting constraint must visibly drive a filtering decision, not get silently dropped.
- [ ] Scoring matrix has a row per surviving candidate and a column per the 3 named steps/scenario (classify, draft-reply-with-human-review, page-on-call) or treats them as one combined scenario explicitly — but every cell has a cited, dated piece of evidence, not just a number.
- [ ] Low framework experience + 2-week deadline shows up as a real factor in the recommendation (e.g., favors a simpler/lower-ceremony SDK over a steep-learning-curve one), not ignored.
- [ ] Final recommendation names one primary pick, one runner-up, and the specific constraint change that would flip to the runner-up.
- [ ] Biggest Risk section is specific to this team (e.g., "team's inexperience with the framework's state model risks a fragile v1 under the 2-week deadline") — not a generic risk like "vendor lock-in" with no connection to this scenario.
- [ ] Re-evaluation trigger is concrete (e.g., ties to a named framework reaching GA, or to the AWS self-hosting requirement changing) not a vague "check back later."
- [ ] Report is explicitly labeled as heuristic/evidence-cited, not a measured benchmark, somewhere prominent (title or opening line).

## Fail conditions

- Recommends a framework without ever mentioning the self-hosting requirement.
- Produces a score with no cited evidence at all ("LangGraph is great for this" with nothing to back it).
- Gives a generic "it depends" non-answer without a committed primary recommendation.
