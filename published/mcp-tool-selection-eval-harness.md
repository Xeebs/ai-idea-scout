# Route Check: A Standard Evaluation Harness for MCP Tool-Selection Failures

Every tool in your agent's toolbox can pass its own unit tests and the agent can still reach for the wrong one — silently, with no error, no stack trace, just the wrong action taken. That gap between "my tools work" and "my agent routes correctly" has no established test methodology a developer can find by searching, even though a handful of large engineering orgs have quietly solved it behind closed doors.

## The Gap

The signal is a direct, unanswered "has anyone built this" from a practitioner in the wild: on r/modelcontextprotocol (2026-10-13), a developer described exactly this failure — "all the rest of tools were callable and direct tests passed all good. But when agent was asked a brand sentiment it selected another tool instead of relevant capability... How i test for this kind of failure? Do you use predefined evaluation scenarios, automated tests or end to end testing with real prompts?" Nobody answered with a pointer to an existing tool, because there largely isn't one a normal developer can pick up. What exists instead is scattered and partial: `accenture/mcp-bench` has 516 stars but hasn't been touched since October 2025 — more than six months stale. PyPI's `mcp-tool-selection-bench` only covers the GitHub Copilot SDK, not a general toolset. GitHub Engineering and Apify both run internal offline-eval pipelines (exact-match plus LLM-judge) that prove the methodology works — but neither is published as a reusable, general-purpose tool. And the academic benchmarks (BFCL-style evaluations, arXiv 2605.07112) measure general function-calling accuracy, not the specific diagnostic workflow this gap is about: a toolset where every tool individually tests green, and routing still fails.

This is happening at scale now. The official MCP Registry listed roughly 20,000–30,000 servers by September 2026, and any agent wiring up more than a handful at once runs straight into overlapping-capability ambiguity — the exact condition that produced the Reddit poster's failure.

## The Project

The idea is to treat tool-selection as its own testable layer, separate and distinct from per-tool functional tests — because today it simply isn't tested at all. A developer defines a scenario set: natural-language intents mapped to the tool that should handle them (or explicitly "none of these" / "ask for clarification"), run against their actual registered MCP toolset. The harness fires each scenario through the live tool-selection step — same tool descriptions, same system prompt, same model the agent runs in production — and scores an exact-match plus a confusion matrix of which tool got wrongly picked instead of the right one. Wire it into CI, and a new tool addition or an innocuous description edit that silently increases misroutes on existing scenarios fails the build before it merges, instead of shipping invisibly.

Four pieces make this real: a scenario-definition format (YAML mapping intent to expected tool, deliberately including near-miss distractor scenarios that probe overlapping tool descriptions), a runner that calls the harness model/host directly rather than mocking it, a confusion-matrix reporter that shows exactly which tool got confused with which, and a GitHub Action that gates merges on regression the same way an integration-test suite catches a contract break unit tests never would.

## Tangible Impact

**Population**: Teams running production agents with growing MCP toolsets (the official MCP Registry listed roughly 20,000–30,000 servers by September 2026, and any agent wiring up more than a handful at once hits overlapping-capability ambiguity) — concretely, developers who, like the Reddit poster, have individually-passing tools but a routing layer with no test coverage. Indirectly, the end users of those agents who experience a wrong action (wrong data pulled, wrong integration called) as a silent failure with no error message.
**Mechanism**: Today, tool-selection regressions ship invisibly because every per-tool unit test still passes — the harness turns an invisible routing regression into a failed CI check before merge, the same way an integration-test suite catches a contract break that unit tests miss.
**Measure**: Tool-selection accuracy (% of scenarios routed to the expected tool) tracked per release; number of misroute regressions caught in CI before reaching production vs. after (baseline: zero, since no test existed); median time for a developer to diagnose a reported misrouting incident using the confusion-matrix output vs. ad hoc log reading.

## Try It

A companion Claude Code skill already exists at `skills/mcp-tool-selection-eval-harness/` — **MCP Misroute Forensics**: "One-shot forensic diagnosis of an MCP/agent tool-misrouting incident — paste the user intent, the tool that got called instead, and the full candidate tool list, and get back the overlap root-cause, a reworded tool description, and 2-3 regression test scenarios. Use this when an agent picked the wrong tool even though every individual tool passes its own unit tests."

This is deliberately the lighter-weight companion to the full CI harness described above, not a replacement for it: it's a one-shot diagnosis for a single incident you've already noticed, not a continuously-running regression suite. Hand it a transcript — the user's request, the tool that got called, and the descriptions of every tool the agent could have chosen from — and it will diff the overlapping language, name the missing boundary in the tool descriptions, propose a rewrite, and generate the first few regression scenarios you'd want in a real suite.

To use it: either paste the contents of `skills/mcp-tool-selection-eval-harness/README.md` into any AI chat tool along with your incident details, or drop the whole `mcp-tool-selection-eval-harness` folder into `~/.claude/skills/` if you're running Claude Code, and it'll be available the next time you see a misroute.

---

Surfaced from `research/2026-11-12-tool-use-mcp-ecosystem.md`, pattern `P1`.
