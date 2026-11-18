# Combined Trace+Eval Minimal Library — Build-vs-Buy-vs-Pair Decision Aid

Paste this whole document into any AI chat tool (ChatGPT, Claude, Gemini, a local model) when your team is deciding how to get **both** tracing (prompt/response/latency/cost visibility) and pass/fail eval regression checks for one LLM-backed feature — before anyone has spent engineering time on a specific tool.

## When to use this

Use this when you're adding an LLM-backed feature to an existing product and need to decide between:
- doing nothing extra,
- adopting a tracing-only minimal library,
- adopting a single combined tracing+eval library,
- manually wiring together two separate libraries (one for tracing, one for eval),
- or buying a full vendor platform (Langfuse, LangSmith, Arize, etc.).

This is specifically for teams who need **both halves** — tracing and pass/fail eval checks — or aren't sure yet whether they need the eval half. If you've already confirmed you only want tracing and never want eval checks, this isn't the right tool; ask for a tracing-only build-vs-buy aid instead. This also isn't for teams that already have a dedicated eval/ops engineer running a platform bake-off between enterprise tools — that's a bigger, higher-stakes decision than this one.

## What to hand over

Paste a description covering these six things. If you leave any out, the model should ask you for it rather than guessing:

1. **Current stack/language** — e.g., "Python, calling the OpenAI API directly" or "TypeScript, using the Anthropic SDK."
2. **Eval need** — do you need pass/fail regression checks against expected outputs, or just visibility into what's happening? If you're not sure, say so and say what's prompting the question.
3. **Request volume** — roughly how many requests/day this feature handles.
4. **Team size for maintenance** — how many engineers could realistically maintain observability/eval tooling (not your total headcount).
5. **Data-residency/compliance constraint** — yes/no/unsure on whether prompt/response data can leave your infrastructure.
6. **Existing partial integration** — is any tracing or eval library already wired in (e.g., OpenLLMetry, DeepEval), even partially?

## How the recommendation gets made

1. **All six inputs get collected first.** A recommendation given without all six is incomplete — "it depends" with no numbers is not a usable answer.

2. **If your eval need is "unsure," it gets resolved with one question before anything else**: *If a prompt change silently made this feature worse, would you find out from a regression check, or from a user complaint?* If the honest answer is "user complaint" or "I don't know," eval need is treated as YES. This question exists because teams very commonly ship tracing alone and never circle back to add eval checks — defaulting silently to "no eval" on an unsure answer would repeat that exact mistake.

3. **The answer branches into one of four paths, checked in this order:**
   - **Path A — Tracing only.** Your eval need is genuinely NO and your volume is low enough that visibility alone (provider dashboards, or a minimal tracing-only library) solves your actual pain point. No eval tooling gets recommended if you haven't asked for it.
   - **Path B — A single combined tracing+eval library.** Your eval need is YES, you want one install instead of stitching two tools together, you have no dedicated ops/eval engineer, and you either have a data-residency constraint or just don't want a third party holding your prompt/response data. This is the default answer for a small team that needs both tracing and eval checks from day one on a single feature.
   - **Path C — Manually pair two separate libraries** (e.g., a tracing library like OpenLLMetry plus an eval library like DeepEval). Your eval need is YES and scoped to this one feature, you already have one half partially wired in and want to keep it, or you have the engineering capacity to maintain two dependencies and specifically want each half to be independently best-in-class. The real cost here is two configs, two local stores (unless you deliberately point them at the same one), and two upgrade cadences — that tradeoff gets named explicitly against Path B.
   - **Path D — Buy a full vendor platform** (Langfuse, LangSmith, Arize, etc.). You have or are about to hire a dedicated eval/ops role, and either your eval need spans multiple AI features/teams (not just this one) or you need things a minimal library or manual pairing won't give you (large-scale dataset evals, human annotation queues, A/B testing, SSO/enterprise compliance) — and you're willing to pay recurring cost and let a third party process your prompt/response data.

   **If both C and D technically fit** — say, a feature already has tracing wired in, but the team has also just hired a dedicated eval engineer and named cross-feature needs — Path D wins whenever the need explicitly spans more than one feature, or explicitly calls for human annotation queues or A/B testing. Those are platform-level capabilities a single feature's manual pairing can't provide, so defaulting to C there would under-serve a need you've already described as bigger than one feature.

4. **The recommendation names the specific input values that drove it** — e.g., "eval need YES via the regression question, no ops engineer, data-residency constraint → Path B" — never a bare verdict with no reasoning shown.

5. **Three tradeoff lines get written**, one for each path not recommended, so you can see exactly what you're giving up.

6. **If Path B is recommended**, the answer sketches the first one or two assertion checks to actually wire up: which call to wrap first (your feature's primary user-facing completion call, not a background job), one deterministic matcher you can check against a known-good example, and — only if your eval need genuinely can't be checked by exact matching (open-ended generation, tone, correctness that isn't a simple string match) — one optional LLM-judge rubric check, with an explicit note that a judge check costs an extra model call every time it runs. No more than one judge check gets suggested in this first pass; piling on judge checks defeats the "minimal" point of this path.

7. **A revisit trigger gets set** — a concrete number (request volume, team size, or "when you hire a dedicated eval engineer") at which this recommendation should be re-run, so it's never treated as a permanent, un-revisited decision.

## Output you should expect

```
## Recommendation: Path <A-D> — <name>

**Why**: <the specific input values that drove this, including the resolved eval-need answer>

**What you give up by not choosing the others**:
- Path A (tracing only): <one line>
- Path B (combined library): <one line>
- Path C (manually pair two libraries): <one line>
- Path D (buy a platform): <one line>
(the line matching the recommended path is left out)

**First assertion checks to wire up** (only if Path B):
- Wrap first: <specific call path>
- Deterministic matcher: <what it checks>
- Judge check (optional): <only included if needed, with the extra-cost note>

**Revisit this recommendation if**: <concrete trigger>
```

## Things this skill will refuse to do

- It will not hand you a recommendation without first getting all six inputs and explicitly resolving the eval-need question — a generic "it depends" is a failed run, not an acceptable answer.
- It will not recommend buying a full platform (Path D) as a first answer for a small team on one feature — that path is only reached after confirming Paths B and C are genuinely insufficient.
- It will not recommend a vendor platform that conflicts with a data-residency constraint you've stated — it will flag the conflict instead of ignoring it.
- It will not suggest more than one optional judge-based check when recommending the combined library — minimalism is the entire point of that path.
- It will not skip stating a revisit trigger.
- It will not pretend to connect to a live tracing or eval backend — it only works from what you paste about your stack and needs. If what you actually want is to turn one specific failing trace into a draft eval test case, that's a different task — ask for that explicitly rather than a tooling recommendation.
