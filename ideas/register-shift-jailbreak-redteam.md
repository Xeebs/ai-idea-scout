# Formal Cover: Register-Shift Jailbreak Red-Teaming & Detection

- **Status**: PROPOSED
- **Date**: 2026-11-12
- **Topic**: AI safety & guardrails in production
- **Source**: research/2026-11-12-ai-safety-and-guardrails-in-production.md · P4
- **Maturity verdict**: OPEN — targeted search for "lawyerspeak"/legal-register prompt injection and jailbreak defenses found only CourtGuard (arXiv 2510.19844, which uses legal framing as a detection *method*, not a defense against register-shifted attacks) and generic jailbreak surveys that don't mention formality/register as an attack vector. No repo, product, or paper addresses this specific bypass technique.
- **Format**: BOTH

## The Gap
A Hacker News post, "Prompt Injection, Esq.: pwning AI agent guardrails with lawyerspeak" (mooreds, 2026-11-11, `mrnice.dev/posts/heavyweight-guardrails/`), disclosed that wrapping malicious instructions in formal legal/contractual language defeats guardrails tuned mostly on casual-toxic or adversarial-sounding phrasing. The disclosure drew low engagement (3 points) and no visible response — a fresh attack class disclosed with zero defense tooling anywhere in the ecosystem.

## The Project
Two linked pieces. First, an automated red-team generator that takes seed harmful-intent prompts from existing open jailbreak benchmarks and systematically rewrites them into formal/legal/contractual register (contract clause framing, compliance-request framing, legal-memo framing) using an LLM rewrite pass plus a templated legalese library, producing a continuously-expanding adversarial test corpus. Second, a lightweight detection pre-filter — a formality/legal-term-density score fed as an auxiliary signal into existing guardrail classifiers (NeMo Guardrails, Guardrails AI, LLM Guard) — that flags high-register inputs for stricter scrutiny or normalizes them before the main classifier scores them, closing the specific blind spot the disclosure exposed.

## Tangible Impact
**Population**: trust-safety and security teams at companies deploying customer-facing or enterprise LLM agents in policy-sensitive verticals — legal-tech assistants, HR bots, financial advisory agents, procurement/contract-review agents — where users have both the incentive and the plausible cover to phrase bypass attempts as contractual or compliance language.
**Mechanism**: guardrail classifiers trained predominantly on casual-toxic or obviously-adversarial phrasing systematically under-flag the same harmful intent when wrapped in formal register, a demonstrated and currently undefended bypass class. A dedicated red-team corpus plus a detection pre-filter gives teams a way to measure and close this specific blind spot, instead of discovering it via a public blog post or a real exploit in production.
**Measure**: jailbreak success rate on a held-out register-shifted test set (target: reduce bypass rate toward parity with the casual-phrasing bypass rate on the same underlying harmful-intent corpus); number of previously-undetected bypass patterns surfaced per red-team run; false-positive rate added to legitimate formal/legal queries, which must stay low since the target verticals handle genuinely formal language by design.

## Why Now
The disclosure is dated November 2026 and remains unaddressed; LLM rewrite passes are now cheap enough to generate large adversarial corpora programmatically; no competing benchmark, repo, or paper surfaced in GitHub, web, or arXiv search.

## Skill Angle
Trigger: a team hands over their current guardrail configuration or system prompt plus a sample of queries they consider legitimately formal. The skill generates a register-shifted red-team test set from a seed harmful-intent list and flags which generated cases likely bypass the stated guardrail rules, as a one-shot audit a team runs before deciding whether to adopt the production detector. The project is the continuously maintained adversarial corpus plus the production-ready detection middleware that runs on every request.

## MVP Sketch
Curate seed harmful-intent prompts from an existing open jailbreak benchmark, build a rewrite-template library (contract clause, legal memo, compliance request), generate roughly 200 register-shifted variants, and run them against two or three open guardrail toolkits to measure bypass rate. Build a minimal auxiliary feature (formality score plus legal-term density) and test whether feeding it into an existing classifier closes the gap. Single experiment: compare bypass rate with vs. without the auxiliary signal on the generated corpus.

## Risks & Open Questions
- This may be a transient trick that guardrail vendors patch quickly once they add formal-register examples to training data — short shelf life for the detector specifically, though the red-team methodology would still be reusable for the next register-shift variant.
- The community-demand signal is thin (one low-engagement post); real validation is whether the attack actually works against production guardrails, not whether people are asking for a fix.
- False positives on legitimate legal-tech queries could make the detector unusable in exactly the verticals it targets.
- Publishing a register-shift red-team corpus is dual-use — it hands attackers a ready-made jailbreak kit alongside the defense; needs a responsible-disclosure posture (e.g., gated access to raw payloads, open access to the detection methodology).
