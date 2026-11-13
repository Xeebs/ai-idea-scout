# Scenario 1: Small immigration-legal-aid nonprofit, FAQ chatbot, high sensitivity

## Input

A volunteer technical lead for a 4-person immigration legal aid nonprofit in Texas, USA, provides this profile:

- **Workload type(s)**: An FAQ chatbot on the org's website answering common questions about immigration case status, filing deadlines, and "what documents do I need" — client-facing, available 24/7.
- **Expected monthly volume**: ~150 unique clients/month, roughly 600 queries/month total (most clients ask 3-5 questions in a session).
- **Budget ceiling**: $50/month — the org has no dedicated AI line item in its budget yet and is testing feasibility.
- **Data sensitivity**: High — clients will likely mention their immigration status, case numbers, and sometimes details relevant to asylum claims. This is sensitive personal data for a vulnerable population.
- **Technical capacity**: No dedicated IT staff. One volunteer (the person submitting this request) with some technical background but no ops/DevOps experience, available ~5 hours/week.
- **Region/country**: United States (Texas).

## Expected output characteristics (pass/fail criteria)

A passing response must:

1. **Not skip intake** — all six fields were provided, so the skill should proceed directly to the live vendor check rather than asking clarifying questions (if it asks for something already given above, that's a fail).
2. **Flag the data sensitivity prominently** — given immigration status/case details are in scope, the output must include an explicit flag recommending legal/privacy review before launch (in "Flags for human follow-up"), and must not recommend any free tier whose provider disclaims "reliable/commercial use" without a loud caveat tied to this specific sensitivity concern.
3. **Respect the technical capacity constraint** — must not recommend a stack requiring real DevOps/self-hosting expertise (e.g., a bare self-hosted Ollama setup with no managed layer) as the *primary* recommendation for a volunteer with "some technical background, no ops experience" without a strong caveat about the added burden; may still mention it as an alternative.
4. **Cite live-checked sources with dates** for every cost and reliability claim — a response that states a dollar figure or rate limit with no source/date attached fails.
5. **Include a concrete fallback plan** with a named trigger (e.g. a specific query-volume threshold or a named disclaimer clause) and a named next action — a fallback that just says "monitor usage and adjust" without specifics fails.
6. **Realistic cost range fits or clearly explains why it exceeds the $50/month ceiling** — if the recommended stack's realistic cost exceeds $50/month, the output must say so explicitly rather than silently presenting a number over budget as if it fits.
7. **Output follows the exact structure** in SKILL.md / README.md (Recommended Stack, Why, Cost range, Reliability caveats, Fallback plan, Alternatives, Sources checked, Flags for human follow-up).

## Self-check notes

Given the high data sensitivity and client-facing nature, the procedure's step 4 scoring would likely steer this org away from any provider whose free tier explicitly disclaims "not intended for reliable/commercial/professional use" (e.g. Oracle Always Free, Scaleway free tier per the idea's own gap note) toward a paid-but-discounted option (e.g. Anthropic/OpenAI nonprofit pricing) even if it's tighter against the $50 ceiling — and the output must say so explicitly rather than quietly recommending a disclaimed free tier for a case-status chatbot touching asylum-relevant details. This is exactly the scenario the skill's guardrail #2 is designed to catch.
