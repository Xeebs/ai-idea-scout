---
name: voice-architecture-decision-benchmark-harness
description: Triages whether a team should build their voice agent as a cascaded pipeline (separate STT/LLM/TTS) or a unified speech-to-speech model, by scoring their specific use case against six weighted decision factors and producing a same-day recommendation with named risks. Use when a team is choosing a voice agent architecture before investing in a full side-by-side benchmark.
---

# Voice Architecture Triage

## When to use this
The user is building (or re-architecting) a voice agent and is stuck on the cascaded-vs-speech-to-speech fork — they've read vendor blogs that contradict each other and want a same-day, defensible direction before they sink a multi-week bake-off into validating it. This is NOT for teams who have already built both stacks and have real latency numbers to compare (that's a benchmarking job, not a triage job — tell them to run their own head-to-head instead and treat this output as a prior, not a replacement).

## Inputs
**Data source**: Manual — the user describes their use case in prose or answers a short checklist; nothing is read from a connector or API. If any of the six factors below isn't covered in what they give you, ask for it explicitly before scoring — do not guess and do not silently default.

Required, either volunteered or elicited by direct questions:
1. **Domain and regulatory context** — e.g. healthcare intake, insurance claims, retail support, recruiting screening. Is there a compliance/audit requirement (HIPAA, call recording retention, dispute resolution)?
2. **Languages and vocabulary** — which languages, and is there specialized/technical vocabulary (medical terms, product SKUs, legal terms, accented or code-switched speech)?
3. **Latency and conversational feel priority** — is sub-second, natural-feeling turn-taking and barge-in central to the product, or is a slightly slower, more deliberate exchange acceptable (e.g. intake forms vs. casual chat)?
4. **Tool-calling needs** — how many external systems does the agent call mid-call (lookup, booking, CRM writes), and how much does a failed/unreliable tool call cost the business?
5. **Team size and expertise** — how many engineers, and do they have (or want) the bandwidth to own STT/LLM/TTS integration separately, versus wanting a single managed vendor?
6. **Vendor lock-in and swap tolerance** — if the chosen vendor changes pricing, gets acquired, or falls behind on quality, how costly would switching be for this team, and how much do they care?

## Procedure
1. Collect or elicit all six inputs above. If more than two are missing, stop and ask for them by name rather than scoring with gaps — a triage built on guesses is worse than no triage.
2. Score each of the six factors from -2 (strongly favors cascaded) to +2 (strongly favors speech-to-speech), using this fixed rubric:
   - **Compliance/observability**: regulated or audit-required → -2. Some internal QA need → -1. No compliance need → 0. (This factor never pushes toward S2S — observability is a cascade strength, not a tradeoff.)
   - **Vocabulary specificity**: narrow/technical/multi-language with code-switching → -2. Moderate domain vocabulary → -1. Everyday conversational language → +1.
   - **Latency/naturalness priority**: product lives or dies on snappy, natural back-and-forth → +2. Latency matters but isn't the differentiator → 0. Deliberate/slower pace is fine or expected (forms, intake) → -1.
   - **Tool-calling needs**: many integrations where a silent failure is costly (bookings, payments, medical records) → -2. A couple of simple lookups → -1. No tool calls, pure conversation → 0.
   - **Team expertise/bandwidth**: small team wants one managed vendor, no interest in owning three separate integrations → +2. Team has capacity and wants control over each component → -1.
   - **Lock-in tolerance**: switching cost would be severe (regulated migration, contractual, deep integration) → -2. Team is comfortable re-platforming if needed → +1.
3. Sum the six scores. Recommend **cascaded** if the sum is ≤ -2, **speech-to-speech** if the sum is ≥ +2, and flag a **close call — lean toward whichever has fewer severe risks for this team** if the sum is between -1 and +1.
4. State a confidence level: **High** if at least 4 of the 6 factors scored in the same direction as the sum's sign; **Medium** if 3 did; **Low** if the factors were mixed or more than one input had to be assumed rather than given directly.
5. List the top 2-3 concrete risks of the recommended path and the top 2-3 risks of the alternative, drawn from the factor scores themselves (don't invent generic pros/cons — cite the specific factor that creates each risk for this team).
6. Close with an explicit note that this is a same-day judgment call based on known general tradeoffs, not measured numbers from the team's own workload — and name the one or two scenarios/tests they should run before shipping the recommended architecture, if they want to validate it with real numbers.

## Output format
```
## Voice Architecture Triage: <team/use-case name>

### Use case summary
<2-3 sentence restatement of what they told you>

### Factor scores
| Factor | Score | Why |
|---|---|---|
| Compliance/observability | <score> | <one line> |
| Vocabulary specificity | <score> | <one line> |
| Latency/naturalness priority | <score> | <one line> |
| Tool-calling needs | <score> | <one line> |
| Team expertise/bandwidth | <score> | <one line> |
| Lock-in tolerance | <score> | <one line> |
| **Total** | **<sum>** | |

### Recommendation: <Cascaded | Speech-to-Speech | Close call — lean toward X>
**Confidence**: High | Medium | Low — <one line why>

### Risks of the recommended path
- <risk tied to a specific factor>
- <risk tied to a specific factor>

### Risks of the alternative path
- <risk tied to a specific factor>
- <risk tied to a specific factor>

### Before you ship this
This is a same-day judgment call, not a measured result. Validate it by: <1-2 concrete next steps, e.g. "run a 20-call pilot on your actual intake script through both stacks and compare barge-in handling on your real accents">
```

## Guardrails
- Never invent or cite specific vendor latency numbers (e.g. "OpenAI Realtime is 320ms") — vendor-reported numbers in this space are contradictory and unverified from inside a chat session. Use only the directional, well-established tradeoffs in the rubric above, phrased as general tendencies, not measured facts.
- Never score with more than one or two factors assumed — if the user hasn't told you their compliance requirement or tool-calling needs, ask; don't default to "probably low" to keep moving.
- Never present this output as a substitute for an actual side-by-side benchmark on the team's own scenarios. If the user has the time and need for hard numbers, point them toward building or running a comparison harness instead of treating this triage as final.
- Never let a "close call" result get dressed up as confident — if the sum lands between -1 and +1, say so plainly and give the tie-breaking consideration (usually lock-in tolerance or team bandwidth, since those are the hardest to reverse later) rather than forcing a false-confident pick.
- Never silently fold regulatory/compliance signals into a generic "observability" bucket — if the user mentions HIPAA, financial compliance, or legal discovery requirements, call that out by name in the risk section, since it has consequences (audit, legal exposure) beyond engineering convenience.
