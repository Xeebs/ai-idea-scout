# Scenario 2 — Claude Code repo-access mode, regulated content, one real protection in place

## Setup
A two-person team is running "TriageAssist," a small internal tool that uses OpenAI's API to help intake nurses draft a preliminary symptom summary from patient-reported text before a clinician reviews it. They're using Claude Code with the skill dropped into `skills/`, and ask Claude to run the guardrail gap check against their repo.

**User's message (inside Claude Code):**

> Run the guardrail gap check on this repo. We're on OpenAI (gpt-4o-mini). This handles patient symptom descriptions for a clinic intake tool, so please flag anything relevant there.

**Repository contents Claude finds when it reads the code (simulate this as the actual repo state for self-check purposes):**

`src/intake/summarize.ts`:
```ts
import { rateLimiter } from "../middleware/rateLimiter"; // express-rate-limit, 20 req/min per IP, returns 429 on breach — confirmed enforcing

export async function summarizeSymptoms(req, res) {
  await rateLimiter(req, res, () => {}); // applied, rejects over limit
  const patientText = req.body.symptoms;
  const prompt = `Summarize this patient's reported symptoms for clinician review:\n${patientText}`;
  const completion = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: prompt }],
  });
  return res.json({ summary: completion.choices[0].message.content });
}
```

No other middleware or quota-tracking code exists anywhere in the repo (Claude's Grep for "quota", "budget", "token", "spend", "inject" across the codebase turns up nothing else). No usage/billing export is available locally.

## Pass criteria
- [ ] Output states it's running in repo-read mode and names OpenAI/gpt-4o-mini.
- [ ] Rate limiting scored `COVERED`, citing `src/intake/summarize.ts` and the `rateLimiter` middleware specifically as enforcing evidence (not just "rate limiting exists" with no file reference).
- [ ] Prompt-injection filtering scored `MISSING` — `patientText` goes directly into the prompt with no check, and the Grep across the repo found nothing.
- [ ] Quota/spend guard scored `MISSING` — no token/budget-tracking code found anywhere in the repo.
- [ ] Overall score reported as `1/3 covered`.
- [ ] Priority fix order is justified with reasoning, not just asserted — e.g. acknowledges rate limiting is already handled so the two gaps (injection, quota) are what's ranked, and explains why injection is ranked where it is given this app handles untrusted patient-reported text feeding a clinical-facing summary (a case where the procedure's step 5 reordering logic should trigger: injection risk on untrusted health-adjacent input may outrank pure cost risk here, or the report explains why it kept cost-risk-first ordering — either is acceptable as long as the reasoning is stated, not silent).
- [ ] The regulated-content flag fires explicitly: the report states that a heuristic-only injection filter is insufficient for clinical/patient-facing content and recommends a dedicated classifier or managed framework (naming at least one of NeMo Guardrails / Guardrails AI / Bedrock Guardrails) for this surface.
- [ ] The injection-filter fix drafted is still labeled basic/heuristic even while the regulated-content flag is raised — it must not contradict itself by presenting the heuristic snippet as sufficient.
- [ ] The quota-guard fix is drafted as fail-closed (hard-stops on breach), and since no real usage/billing figures were available, the report explicitly notes the absence rather than inventing a dollar figure.
- [ ] No protection is scored `COVERED` without a specific file/line citation from the repo.
