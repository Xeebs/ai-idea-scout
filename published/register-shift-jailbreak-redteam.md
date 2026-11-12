# Formal Cover: Register-Shift Jailbreak Red-Teaming & Detection

A blog post disclosed a working jailbreak class on November 11th. Three Hacker News points, no comment thread, no response from any guardrail vendor. The trick: wrap the exact same harmful instruction in contract-clause or compliance-memo language instead of casual phrasing, and the guardrail — trained on adversarial-sounding or casual-toxic text — waves it through. A week later, nobody has shipped a fix, a benchmark, or even a public acknowledgment that this is a distinct attack surface.

## The Gap

The disclosure is "Prompt Injection, Esq.: pwning AI agent guardrails with lawyerspeak" (mooreds, Hacker News, 2026-11-11, `mrnice.dev/posts/heavyweight-guardrails/`). Its core claim is specific: guardrail classifiers are tuned on how malicious intent *sounds* — adversarial phrasing, casual toxicity — not on what it *means* once that intent is reframed as a legal memo, a contract clause, or a compliance request. Reframe the payload in formal register and the same harmful instruction slides past the filter.

A targeted search for existing defenses turned up exactly one adjacent piece of work, and it isn't a match: CourtGuard (arXiv 2510.19844) uses legal/courtroom framing as a *detection* method — a multiagent "defense attorney vs. prosecutor" classifier architecture — not as a defense against attacks that arrive already dressed in legal register. Two broader jailbreak surveys (arXiv 2512.19011, 2505.04806) catalog attack taxonomies without listing formality or register-shift as a dimension at all. No repo, product, or paper targets this specific bypass. For a disclosed, demonstrable attack class, that's a genuine zero.

## The Project

Two pieces, built to ship together. The first is an automated red-team generator: take seed harmful-intent prompts from existing open jailbreak benchmarks, and systematically rewrite each one into formal register using an LLM rewrite pass plus a templated legalese library — contract-clause framing, compliance-request framing, legal-memo framing. The output is a continuously-expanding adversarial corpus that didn't exist anywhere before this week.

The second is the actual defense: a lightweight formality/legal-term-density scorer that runs as an auxiliary signal ahead of an existing guardrail classifier — NeMo Guardrails, Guardrails AI, LLM Guard — either flagging high-register inputs for stricter scrutiny or normalizing them before the main classifier scores them. Neither piece is novel machine learning; the novelty is that nobody has pointed either one at this specific blind spot yet, and the blind spot is live in production guardrails right now.

## Tangible Impact

**Population**: trust-safety and security teams at companies deploying customer-facing or enterprise LLM agents in policy-sensitive verticals — legal-tech assistants, HR bots, financial advisory agents, procurement and contract-review agents — where users have both the motive and the plausible cover to phrase a bypass attempt as contractual or compliance language.
**Mechanism**: guardrail classifiers trained predominantly on casual-toxic or obviously-adversarial phrasing systematically under-flag identical harmful intent once it's wrapped in formal register — a demonstrated, currently undefended bypass class. A dedicated red-team corpus plus a detection pre-filter gives teams a way to measure and close this blind spot proactively, instead of discovering it the way the rest of the industry just did: via a public blog post, or worse, a real exploit in production.
**Measure**: jailbreak success rate on a held-out register-shifted test set, targeting parity with the casual-phrasing bypass rate on the same underlying harmful-intent corpus; number of previously-undetected bypass patterns surfaced per red-team run; false-positive rate added to legitimate formal/legal queries — which has to stay low, since the verticals that need this most handle genuinely formal language by design.

## Try It

There's no companion `skills/` build for this yet — no `skills/register-shift-jailbreak-redteam/` directory exists in this repo as of this writeup. The idea file sketches what that skill would do if built: a team hands over their current guardrail config or system prompt plus a sample of queries they consider legitimately formal, and gets back a generated register-shifted red-team set flagging which cases likely bypass their stated rules — a one-shot audit to run before adopting the full production detector. The project itself — the continuously maintained corpus and the production detection middleware — is the larger, separate artifact; the skill angle remains unbuilt pending a novelty check in a future cycle.

Worth stating plainly, because the idea file does: this may be a short-lived trick that guardrail vendors patch the moment they add formal-register examples to training data, which would shorten the shelf life of the detector specifically — though the red-team methodology would stay reusable for whatever register-shift variant comes next. The community-demand signal is also thin: one low-engagement post, not a groundswell. Real validation here isn't whether people are asking for a fix — it's whether the attack actually works against production guardrails when someone runs the experiment. And there's a dual-use problem baked in: publishing a register-shift red-team corpus hands attackers a ready-made jailbreak kit alongside the defense, which argues for a responsible-disclosure posture — gated access to raw payloads, open access to the detection methodology — rather than a fully open corpus dump.

Surfaced from `research/2026-11-12-ai-safety-and-guardrails-in-production.md`, pattern `P4`.
