# Grader on Trial: A Ground-Truth Validation Harness for MCP Tool-Calling Eval Graders

- **Status**: EXPLORING
- **Date**: 2026-11-20
- **Topic**: Tool use & MCP ecosystem
- **Source**: research/2026-11-20-tool-use-mcp-ecosystem.md · P4
- **Maturity verdict**: PARTIAL — general-purpose grader-validation tooling exists (NVIDIA's skillevaluator checks a judge against independently labelled cases but explicitly caveats itself as a narrow synthetic set, "not a reliability benchmark"; ModelScope's OpenJudge is a maintained general grader-validation toolkit with MAE/F1 metrics and k-fold cross-validation) and a 2026 arXiv paper ("Benchmarking the Benchmarks") audits four tool-calling benchmark families for reward-basis mismatch and judge variance — but nothing MCP-eval-specific and shipped. No one has packaged "validate the MCP eval's own trace/state-based grader" as a product.
- **Format**: BOTH
- **Data Sources**: CONNECTED — connects directly to the target MCP server over the standard MCP tool-call protocol (a mature, universally-implemented interface — every MCP server exposes tool-list and tool-call) to drive real interaction traces that get graded; the harness also ships a pre-built, versioned labeled-fixture corpus of known-correct and deliberately-buggy scenarios (timeouts mid-write, duplicate calls, partial-state writes) so grading ground truth doesn't depend on a per-use manual upload.

## The Gap

A DEV Community post — "My eval said a perfect MCP server was broken — it was the eval that was lying" — describes an LLM-based MCP eval initially flagging a correctly-functioning server as failing tool selection 62% of the time, purely because of a bug in the grader itself. Braintrust's MCP-eval guides, the `mcp-evals` GitHub Action, and the academic MCPEval framework all score whether an agent picked the right tool, passed the right arguments, and left the right system state (e.g. catching a duplicate write when `create_record` times out after the server already wrote) — but every one of these tools assumes its own scoring logic is ground truth, with no agreed way to validate the grader before trusting its numbers.

## The Project

A validation harness that any MCP eval framework's grading function can be run against before its verdicts are trusted. It ships a labeled fixture corpus of MCP interaction traces with known-correct outcomes, including the exact edge cases that break naive graders: a timeout followed by a server-side write that actually succeeded, a retried call that silently duplicated a side effect, a tool-selection scenario with two plausible-looking correct answers. It also connects live to the user's actual MCP server to generate fresh real-world traces, scores both corpora through the grader under test, and reports grader precision/recall/false-positive rate against the known answers — the same shape as a diagnostic test's own sensitivity/specificity report, applied to the thing that's supposed to be diagnosing your server. A CI mode regression-tests the grader itself whenever its logic or prompt changes, so a grader update can't silently start lying without being caught.

## Tangible Impact

**Population**: Developers and teams maintaining MCP servers who gate CI or production rollout on an MCP-specific eval framework (`mcp-evals` Action adopters, Braintrust MCP-eval users, teams implementing MCPEval-style trace/state scoring) — a technical population that scales with MCP's registry of 20,000–30,000+ listed servers and the growing share of teams that have moved past manual testing to automated eval gates. Indirectly, the end users of MCP-backed agents whose server gets wrongly blocked (false "broken") or wrongly waved through despite a real duplicate-write bug (false "passing") because of an unvalidated grader.
**Mechanism**: Today a team adopts or writes an MCP eval and treats its pass/fail as ground truth with no way to know the grader itself has a bug — exactly the DEV Community case where 62% of "failures" were the grader's fault, not the server's. The harness forces any grader to clear a known-answer fixture set before its verdicts are trusted, converting an invisible meta-failure (the eval is lying) into a visible, CI-gated one the same way a regression suite catches a broken test before it starts blocking good code.
**Measure**: Grader precision/recall against the labeled fixture corpus (false-"broken" rate, false-"passing" rate on planted duplicate-write/timeout scenarios); number of grader-logic bugs caught in a grader-change CI gate before reaching a production go/no-go decision; adoption — number of real MCP eval setups that run the validation harness before trusting a new grader version or prompt edit.

## Why Now

MCP-specific eval tooling (`mcp-evals`, MCPEval, Braintrust's MCP guides) only matured in the last several months as servers scaled past the 20k mark, and the "the eval was lying" failure mode has only just been documented publicly (the DEV Community post) — the gap is freshly visible and the adjacent building blocks (generic grader-validation toolkits like OpenJudge, the "Benchmarking the Benchmarks" audit methodology) already exist to adapt rather than invent from scratch.

## Skill Angle

A standalone "audit this MCP eval's grader" skill: hand Claude the grader's scoring logic/prompt plus a handful of real or synthetic traces with known outcomes, and it returns a structured audit — which fixture scenarios the grader got wrong, a hypothesis for why (position bias in an LLM-judge grader, a missed edge case in a rule-based one), and 2-3 new fixture cases to add to catch the same failure again. Usable standalone without ever connecting to a live server; differs from the project by being a one-shot forensic review rather than a continuously-run, CI-integrated validation suite.

## MVP Sketch

3 weeks, 1-2 people: build a ~30-case labeled fixture corpus covering the documented failure modes (timeout-then-actual-write, retry-duplicate, tool-selection near-ties), a runner that scores both the fixture corpus and live-captured traces through a target grader, and a precision/recall/false-positive reporter. Experiment: take the `mcp-evals` GitHub Action or a Braintrust MCP-eval config, run it against the fixture corpus, and show the harness catches a seeded grader bug (e.g. a scoring regex that misses a valid-but-differently-formatted success state) that the grader's own authors hadn't noticed.

## Risks & Open Questions

- A well-resourced MCP eval vendor (Braintrust, or Anthropic itself) could ship grader-validation as a built-in feature once the DEV Community post's framing spreads, closing this quickly.
- Hand-authoring a labeled fixture corpus that generalizes across different servers' domains (CRUD-style vs. read-only vs. streaming tools) is real curation work with ongoing maintenance cost as MCP's tool-call semantics evolve.
- Grader bugs that are prompt-specific (an LLM-judge grader that fails only on a particular phrasing) may not be caught by a fixed fixture corpus without continuous expansion.
- Risk this reduces to "just write better eval tests" — the differentiator has to be the known-answer ground-truth discipline and precision/recall reporting, not just more test cases.
