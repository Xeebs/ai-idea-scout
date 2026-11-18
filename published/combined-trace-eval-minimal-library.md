# Trace+Check: A Minimal Combined Observability-and-Eval Library for LLM-Backed Features

Somewhere in the last 30 days, a solo maintainer on a small open-source project and an engineering team inside a well-funded analytics company both sat down and wrote the same code: a way to watch what their LLM feature was doing, and a way to automatically catch when it started doing it worse. Neither of them reached for the long list of vendors built to do exactly that. They built it themselves — at opposite ends of the size spectrum, in the same window, independently. That's not a coincidence worth shrugging off. It's a gap with two live data points.

## The Gap

GitHub PR "feat: Observability and Evaluation" landed on `maheshnallada/ConversenseAI#2`, a small open-source project, on 2026-11-14. In the same stretch of days, PostHog — not a tiny shop, a company that makes its living on analytics tooling — was shipping its own in-house "aio" (AI observability) evaluation-run feature across three separate PRs (#124131, #129079, #129083). Both efforts amount to the same thing: wire up tracing for an LLM feature, then bolt on pass/fail checks so a regression doesn't ship silently.

What makes this interesting is what both teams skipped. A WebSearch roundup turns up a genuinely crowded field for this exact category — Langfuse, Arize Phoenix, LangSmith, Braintrust, Datadog LLM Observability, Helicone, Portkey, MLflow, Bifrost. Nobody here lacks options. So why build from scratch twice?

Because the closest thing to "the right-sized tool" isn't one tool — it's two. OpenLLMetry gets you two-line-of-code OTel tracing; DeepEval gets you eval metrics. Want both from a single install instead of integrating a pair of libraries with their own configs and upgrade cadences? The fully combined options exist, but they're not light. Langfuse's self-host stack alone needs web and worker containers, Postgres, ClickHouse, and Redis or S3 — a lot of infrastructure to adopt for what is, for most teams, one feature inside a larger product. No single lightweight, combined observability-and-eval library turned up in the search. That absence is the most plausible explanation for why a tiny repo and a large company both chose "build it ourselves" over "integrate a platform."

## The Project

The fix isn't a new vendor — it's a smaller one. A single importable library, Python first, that ships both halves of this problem from one dependency instead of asking a team to assemble them:

- An SDK-call wrapper that captures prompt, response, latency, and cost as spans — the tracing half, using the same mature, trivial in-process wrapping pattern every observability SDK already uses.
- Inline eval-assertion primitives sitting right next to those same traces: deterministic expected-output matchers, golden-set regression checks, and one optional LLM-judge scoring call for cases that can't be exact-matched — the eval half.

One local store (SQLite by default, Postgres if you want it), one local UI showing traces and eval verdicts side by side, one install. The pitch isn't "better than Langfuse" — it's "smaller than pairing two libraries or standing up a multi-container stack for a single feature's worth of tooling." The project deliberately scopes itself as the combined superset sitting next to this same research ledger's tracing-only "Lean Log" idea: Lean Log covers tracing only, by design; this is for teams who know on day one they want both.

Core components: the SDK-call wrapper; local storage; assertion and scoring primitives; a golden-set regression runner; a minimal web UI; and an explicit scope line distinguishing it from both the full enterprise platforms and from tracing-only tools — it exists specifically in the space those two leave empty.

## Tangible Impact

**Population**: engineering teams building an LLM-backed feature as one piece of a larger existing product — spanning a solo OSS maintainer (the cited `maheshnallada/ConversenseAI` PR) up to a sub-team inside a large, well-resourced company (PostHog's own multi-PR "aio" build) — who need both tracing and pass/fail eval checks for that one feature but don't want to onboard a dedicated vendor or a multi-container self-host stack just to get them. Both ends of that scale spectrum independently chose to hand-build this within the same 30-day window, which is the direct evidence this population exists today.

**Mechanism**: replaces either from-scratch glue (what both cited examples built) or a two-library integration project (OpenLLMetry + DeepEval) with one install that does both, collapsing "do I need tracing" and "do I need eval" into a single setup step — so a feature team ships observability and regression protection together instead of shipping tracing now and eval "later," which a LangChain survey cited in the same digest shows mostly never happens (89% have tracing instrumented, only 52%/37% run offline/online evals).

**Measure**: (1) % of a pilot cohort that has at least one running eval-assertion check within their first week of adoption (vs. the LangChain survey's 52%/37% baseline); (2) time from install to viewing a combined trace+eval-verdict for the first time; (3) number of observed cases of a team replacing a hand-rolled "Observability and Evaluation"-style PR with adoption of this library instead of writing new glue.

## Try It

A companion Claude Code skill is already built: `skills/combined-trace-eval-minimal-library/`. It's not the library itself — it's the build-vs-buy-vs-pair decision aid a team would want *before* committing engineering time to any of the four paths (this combined library, tracing-only, manually pairing two libraries, or buying a full platform).

Its one-line description, straight from `SKILL.md`: "Build-vs-buy-vs-pair decision aid for teams who need both LLM tracing AND pass/fail eval regression checks on one feature. Scores a team's stack, eval needs, and scale into one of four paths — adopt a combined trace+eval library, adopt a tracing-only minimal library, manually pair two separate libraries (tracing + eval), or buy a full vendor platform — and sketches the first eval assertions if the combined-library path fits."

To use it: paste the contents of `skills/combined-trace-eval-minimal-library/README.md` into any AI chat tool (ChatGPT, Claude, Copilot Chat) along with a description of your stack, and it will walk you through the same four-path decision. If you're on Claude Code, drop the whole `skills/combined-trace-eval-minimal-library/` folder into `~/.claude/skills/` and invoke it directly — it will ask for the six inputs it needs (stack/language, eval need, request volume, team size, compliance constraints, any existing partial integration) before recommending a path.

## The Honest Risks

This idea lives right next to an existing one in this same ledger — "Lean Log," a tracing-only minimal library — and the whole case for building this as a separate thing rather than a feature request on Lean Log rests on shipping the eval-assertion half from day one. If that discipline slips, this becomes a fourth attempt at the same observability-only niche instead of the actually-open combined gap. There's also a real ceiling on "minimal": deterministic matchers plus one optional judge call won't satisfy teams that need LLM-as-judge scoring at real scale, and growing to meet them risks turning this into a second DeepEval, which defeats the premise. And the evidence itself could age out — if OpenLLMetry and DeepEval ship native integration with each other, the "pairing is the current workaround" framing this is built on goes away. Finally, there's no guarantee PostHog doesn't just keep extending its own in-house "aio" feature forever rather than ever adopting something external, which would narrow the realistic buyer pool toward smaller teams and OSS projects rather than the large-company end of the evidence cited above.

---

Surfaced from `research/2026-11-18-llm-evaluation-observability.md`, pattern `P8`.
