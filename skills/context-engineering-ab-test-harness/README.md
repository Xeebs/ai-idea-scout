# Context-Engineering A/B Test Design Reviewer

Paste this whole document into any AI chat tool (Claude, ChatGPT, Gemini, etc.) along with your own details, and it will turn a vague "should we turn on compaction" question into a rigorous, runnable test plan — a design, not an actual test run.

## When to use this

Use it the moment you're deciding whether to adopt, keep, or disable a context-engineering change in an LLM agent — compaction, a summarization threshold, tool-output truncation/capping, or an offload-to-filesystem/memory policy — and you don't yet have a controlled way to tell whether it actually helps *your* workload. Today most teams either accept whatever their agent framework defaults to, or copy a strategy from a blog post written against someone else's tasks and cost structure. The community signal on this is openly contradictory: some practitioners report compaction/offloading as a clear win, others report that with prompt caching, "keeping everything is often cheaper, faster, and better at remembering than summarizing." This skill doesn't resolve that debate for you — it designs the specific test that resolves it for *your* setup.

This produces a **test plan you or your team then run**. It does not execute your agent, call any API, or produce real numbers. If you want the actual comparison run automated, you need a separate execution harness (a script that runs your agent twice, once per condition) — this skill hands that harness (or a human running the steps manually) a precise plan to follow.

## What to hand over

This is a manual/paste-in skill — nothing here connects to your systems automatically. Give it, in your own words:

1. **Your current context-engineering setup** — what compaction/summarization/offloading/capping behavior is active today (if any), and which agent framework or CLI it runs on (Claude Code, Codex CLI, LangGraph, a custom agent loop, etc.).
2. **The specific change you want to test** — e.g. "turn on auto-summarization every 20 turns once context hits 50% full" or "cap tool output at 2,000 tokens instead of passing it through raw."
3. **Your task suite** — ideally 10-20 representative prompts your agent actually needs to handle, each with a pass/fail criterion. If you don't have this yet, say so — the assistant will draft a first-pass suite from a description of your workload instead of refusing.
4. *(Optional)* Any existing cost/latency baseline numbers you've already pulled from production tracing (OpenTelemetry, LangSmith, Langfuse, or similar) — paste the numbers themselves; this skill never queries those systems live.

## What it does with that (procedure)

1. **Pins down the exact change under test.** If your description of the change is vague ("try compaction"), it will push back and ask for the specific trigger condition and mechanism — a fuzzy treatment can't produce a testable result.
2. **Writes a falsifiable hypothesis**: "If we [change], then [metric] will [direction] by roughly [magnitude], because [mechanism]." Even if you haven't stated one, it writes it for you so there's something the test can actually confirm or kill.
3. **Builds or critiques your task sample.** It checks (or drafts) your tasks for: enough of them (10-20, flagged if fewer than 10), enough variety (long multi-turn work vs. short single-shot, tool-heavy vs. not), and sharp pass/fail criteria (no "looks good" — every check must be verifiable). It specifically adds 2-3 tasks designed to catch the failure mode your particular change threatens most — for compaction/summarization, that's usually a constraint, decision, or detail stated early in the conversation that's needed again much later.
4. **Defines the metrics** — always all of: task success-rate delta, total token/cost delta, wall-clock latency delta, and at least one recoverability/constraint-preservation check (never success-rate alone, which is a documented blind spot in ad hoc tests of this kind).
5. **Specifies the statistics** — a recommended number of repeat runs to average out LLM output noise, a concrete significance-testing method matched to each metric type, and a plain-language note on whether your sample size is actually big enough to detect the effect size in your hypothesis.
6. **Writes an execution handoff checklist** for whoever runs the actual comparison (you, your team, or an automated script): what stays fixed, what gets toggled, how many repeats, where results get logged.
7. **Flags the risks** — task-sample representativeness, the cost of running enough repeats for statistical confidence, the chance a framework vendor's own defaults shift underneath you, and any failure mode your chosen metrics still can't catch.

## Output format

You'll get back a single markdown document, "A/B Test Design Brief," with these sections in this order:

1. **Hypothesis**
2. **Baseline vs. Treatment** (exact definition of each condition)
3. **Task Sample** (the list, each task flagged with its pass/fail check, and which ones target the specific failure mode)
4. **Metrics** (the full list, with how each is computed)
5. **Statistical Plan** (repeat count, test method, sample-size adequacy note)
6. **Execution Checklist** (handoff steps for the person/script that runs the comparison)
7. **Risks & Caveats**

## Guardrails — what this skill will never do

- Never invent or imply real success-rate, cost, or latency results. It designs a test; every number it gives you is a *plan* parameter (how many repeats, how many tasks), never a *result*.
- Never accept a vague treatment definition without pushing for specifics first.
- Never hand you a success-rate-only metrics list — cost/latency and a constraint-preservation check are always included.
- Never tell you compaction/offloading/capping is a universal good or bad idea — the real-world evidence on this directly contradicts itself depending on workload and caching setup, so this skill stays neutral and only designs the measurement.
- Never silently skip the risk warning when your task sample is under ~10 tasks or missing pass/fail criteria.
- Never claim to have run anything. If you want the comparison actually executed against a live agent, you need a script or harness to run the plan — this skill hands that harness (or you, running it by hand) the plan to follow.
