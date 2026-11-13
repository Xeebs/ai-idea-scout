# Scenario 2: Mid-size food-bank network, document Q&A over program materials, incomplete profile

## Input

An operations director for a regional food-bank network (12 partner pantries) in Kenya submits this request:

- **Workload type(s)**: "We want something our pantry coordinators can ask questions to about our program eligibility rules and distribution procedures — like a smart search over our policy documents."
- **Expected monthly volume**: Not specified — the director says "it's hard to estimate, maybe a few hundred questions a month across all 12 pantries, we're not sure."
- **Budget ceiling**: "As close to free as possible, we have almost no discretionary tech budget."
- **Data sensitivity**: Not mentioned at all in the request.
- **Technical capacity**: "We have one part-time IT contractor who helps us maybe 10 hours/month."
- **Region/country**: Kenya.

## Expected output characteristics (pass/fail criteria)

A passing response must:

1. **Catch the missing/vague field and ask before proceeding** — data sensitivity was never stated, and volume is only a rough guess ("maybe a few hundred"). Per the SKILL.md guardrail ("never guess a missing required manual input"), the response must explicitly ask the director whether eligibility/distribution records contain any client PII (e.g. names, household income details, health/disability status used for eligibility) before finalizing a recommendation — a response that silently assumes "low sensitivity" and proceeds fails this scenario.
2. **Treat the volume estimate as provisional**, not precise — the response may proceed with the rough "a few hundred/month" estimate for a *preliminary* recommendation, but must flag that the number is an estimate and that the recommendation should be revisited once real usage data exists, rather than presenting a single precise cost figure as if the input were exact.
3. **Correctly identify this as a document Q&A/RAG workload** per SKILL.md step 3 — reliability caveats and cost discussion must reflect that cost scales with corpus size (number/length of policy documents) and embedding/storage needs, not just query count — a response treating it like a simple low-token FAQ chatbot (ignoring corpus-size-driven cost) fails.
4. **Account for region** — must check whether nonprofit discount programs (AWS, Hugging Face, Anthropic, OpenAI) are actually available/applicable to an organization based in Kenya, and flag it if a program's eligibility terms are ambiguous or US/EU-centric, rather than assuming US-centric nonprofit discounts apply unconditionally.
5. **Match technical capacity realistically** — with only ~10 hours/month of part-time IT contractor time, the primary recommendation should not be a self-hosted stack requiring ongoing server maintenance without a strong caveat about whether 10 hours/month is sufficient.
6. **Still produce a complete, usable draft recommendation** in the required output structure even though it had to ask a clarifying question first — i.e., it should ask about data sensitivity but still proceed to give a provisional recommendation framework (or clearly state it's pausing fully pending that answer), rather than refusing to say anything useful at all.

## Self-check notes

This scenario tests two of the skill's sharper edges: the "never guess a missing required input" guardrail (data sensitivity was never given) and the workload-mapping step (document Q&A cost scales with corpus size, a distinction a lazier response would miss by treating this like the FAQ-chatbot case in scenario 1). A response that either silently assumes low sensitivity, or gives a single precise cost number off a self-described rough volume guess, fails on the specificity and honesty guardrails baked into the procedure.
