# Scenario 1 — Solo developer's autonomous refactoring agent, long session, over the threshold

## Input

**Task domain and session length**: "I built a custom orchestration script on top of Claude Code's SDK that autonomously refactors large multi-file TypeScript codebases — it plans a refactor, then loops: pick a file, edit it, run the type checker, fix errors, move to the next file. A typical run across a ~40-file module takes 50-70 turns and by the end the transcript I'm resending is around 180K tokens."

**Current context assembly / framework**: "Right now every turn I just resend the entire accumulated transcript — every file edit, every type-checker output, every decision — because the SDK's default context window handles it fine size-wise. It's Claude Code's SDK, custom orchestration loop, no existing summarization or windowing."

**Transcript excerpt (partial, provided)**: "Turn 8: agent decides 'all imports of `LegacyUserService` should be renamed to `UserService` per the plan.' ... Turn 52: agent edits `billing/invoice.ts` and reintroduces an import of `LegacyUserService`, contradicting the turn-8 decision, then the type checker flags it as an error and two more turns are spent re-fixing something already decided 44 turns earlier."

## Expected output characteristics

- **Threshold check**: session length (50-70 turns, ~180K tokens) is well over the ~20 turn / ~20K token floor, so the response must proceed to a full design memo, not a "Not recommended yet" verdict. Stopping short here fails the scenario.
- **System Summary**: must correctly restate domain (multi-file TS refactor agent), session length (~50-70 turns / ~180K tokens), current strategy (full transcript resend every turn), and framework (Claude Code SDK + custom loop).
- **Degradation Evidence**: must cite the turn-8/turn-52 contradiction from the given excerpt specifically — a response that only speaks generically about "context rot" without referencing this concrete example fails.
- **Curator Design**: method recommendation should reasonably favor a symbol/file-path-aware or hybrid retrieval approach (not a pure-embedding default) given this is a code-editing domain — a response that defaults to plain embedding search with no acknowledgment of code-specific retrieval options is weaker but not a hard fail; defaulting to embeddings *without any justification at all* is a fail.
- **JIT Query Interface**: the worked example must be specific to this domain (e.g. referencing a current file being edited and a need to recall prior decisions about renamed symbols), not a generic placeholder like "query: get relevant context."
- **Retrieval Risk Flags**: at least one flag must specifically resemble the turn-8/turn-52 failure mode (an early one-time decision needed much later), with a concrete mitigation (e.g. pinning naming/rename decisions as always-included).
- **Go/No-Go**: must explicitly name the 2x-LLM-call tradeoff and propose a concrete validation experiment (e.g. rerun the same 40-file refactor with a hand-truncated/simulated-retrieval context vs. full history and compare whether the turn-8/turn-52-style contradiction recurs).

## Pass/fail

PASS if all seven output-format sections are present and populated with domain-specific (not generic) content, the turn-8/turn-52 contradiction is explicitly cited in Degradation Evidence and reflected in at least one Retrieval Risk Flag, and Go/No-Go names the per-turn cost tradeoff plus a concrete experiment. FAIL if the response produces a "Not recommended yet" verdict (wrong — session is well over threshold), invents transcript details beyond what was given, claims the design is validated against a benchmark, or gives generic/placeholder content in the JIT Query Interface or Retrieval Risk Flags sections.
