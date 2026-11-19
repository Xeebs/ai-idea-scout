# Harness Check: An Adoptable Harness-Normalization Layer for Agent Benchmark Comparisons

OpenAI reportedly stopped trusting SWE-bench Verified. Not because a better benchmark showed up — because the surrounding execution harness, not the model, had started deciding who wins.

## The Gap

An arXiv paper, "Harness-Bench" (May 2026), measured something that should worry anyone citing a leaderboard: the execution harness around an agent — its tool-calling scaffold, retry logic, prompt wrapper — moves the agent's benchmark score more than swapping the underlying model does. A harness-aware-evaluation survey makes the same point from a different angle, arguing a published score is meaningless without the full execution config attached. A practitioner summed it up plainly: "the evaluation harness can introduce more ranking variance than changing the underlying model."

The field isn't short on an answer, exactly — it's short on anyone picking the answer up. The ICLR 2026 "Holistic Agent Leaderboard" (HAL, Princeton et al.) is a validated, open-source, framework-agnostic standardized harness, proven out across 21,730 rollouts spanning 9 models and 9 benchmarks at roughly $40k of compute. A search for anyone outside HAL's own authors adopting it came back empty. GitHub has no harness-variance tool to speak of. So the default comparison a team makes today is still: read two vendor blog posts, assume the numbers are the same kind of number, and decide. OpenAI's own response to the problem — walking away from trusting SWE-bench Verified rather than fixing the comparison — is itself evidence that nothing adopted exists yet.

## The Project

Harness Check takes HAL's proven harness and makes it something a team can point at their *own* agent or model and get a normalized, harness-controlled score back in one command — instead of reading an ICLR paper and re-implementing the orchestration layer themselves from scratch. It runs the candidate stack through HAL's fixed scaffold across a configurable benchmark subset, reports the resulting score next to the stack's self-reported or vendor-published number, and surfaces the delta between them as an explicit, visible figure rather than a disclaimer buried in a footnote.

Layered on top, a public, continuously-updated registry of harness-normalized scores for the frameworks people actually ship with — LangGraph, CrewAI, OpenAI Agents SDK, raw tool-calling — lets anyone see, before they commit engineering time, where a vendor's number and the harness-controlled number pull apart.

## Tangible Impact

**Population**: Engineering teams evaluating which agent framework or model to adopt for a production task before committing engineering time — JetBrains' 2026 Developer Ecosystem Survey (15,000+ developers) found 90% of professional developers now use AI coding agents weekly, and McKinsey's 2026 State of AI survey found roughly 20-31% of enterprises are actively scaling coding agents, meaning a large and growing set of teams are making exactly this comparison right now, often from a vendor's self-reported leaderboard number alone.
**Mechanism**: Today a team either trusts a published number that may reflect a favorable harness as much as a better model, or burns a week building their own bespoke bake-off from scratch. Harness Check gives them a controlled, reusable third option: a normalized number plus an explicit flag for how much of the gap between two candidates is harness artifact versus real capability difference.
**Measure**: variance between a vendor's self-reported score and the harness-normalized score across a sample of popular frameworks, published openly; time a team spends on framework/model selection before vs. after adopting the tool; rate at which a harness-normalized ranking flip (vs. the vendor-published ranking) is confirmed by the team's own downstream production results.

## Try It

A companion skill, `skills/agent-benchmark-harness-normalizer/`, handles the lighter, no-infrastructure version of this problem. Per its `SKILL.md`: it "flags when two agent/model benchmark numbers being compared head-to-head aren't actually comparable because the surrounding execution harness (scaffold, retries, timeouts, prompt wrapper) differs or is undisclosed, and drafts a caveat paragraph for the comparison memo." It never runs a benchmark or calls a model itself — it interrogates the claims as stated, the way you'd want a skeptical colleague to before a number goes into a decision doc.

To use it: paste `skills/agent-benchmark-harness-normalizer/README.md` into any AI chat tool and follow the prompt, or drop the `agent-benchmark-harness-normalizer` folder into `~/.claude/skills/` if you're working in Claude Code.

## Worth Knowing Before You Build

HAL's own authors may already be planning exactly this adoption layer — that's worth checking against their roadmap and open issues before building a competing wrapper from scratch. Running real benchmark rollouts against a team's live model API also costs real money (HAL's own full run was roughly $40k), so a usable MVP needs a far smaller, cheaper benchmark subset than the original validation run, or it's dead on arrival for the small teams who need it most. And a normalized number only matters if it changes a decision — this only has impact the moment a team acts on a flagged delta instead of nodding at it and moving on anyway. Benchmark subsets also go stale and get gamed over time; without a refresh cadence, the registry becomes exactly the kind of stale leaderboard this idea exists to fix.

---

Surfaced from `research/2026-11-18-agentic-ai-autonomous-agents.md`, pattern `P3`.
