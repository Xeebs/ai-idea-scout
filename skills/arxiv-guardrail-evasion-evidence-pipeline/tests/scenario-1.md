# Scenario 1 — Full-information paper, complete entry format

## Input

**ARXIV PAPER LINK/ID**: arXiv:2511.09842, "Cascading Persona Drift: A Multi-Turn Jailbreak via Incremental Role Reinforcement"

**ABSTRACT**:
"We present Cascading Persona Drift (CPD), a multi-turn jailbreak technique that incrementally reinforces an alternate persona across 6-12 conversational turns rather than attempting an immediate role-play jailbreak in a single prompt. Each turn reinforces the persona's established 'rules' before introducing a policy-violating request framed as consistent with those rules. We evaluate CPD against five production chat assistants (two frontier closed-source models and three open-weight 70B-class models) and find it achieves a 38% successful-bypass rate on harmful-content categories where single-turn jailbreak attempts on the same models succeed at under 6%, suggesting current guardrail training is substantially more robust to single-turn attacks than to slow multi-turn persona reinforcement."

**ADDITIONAL TEXT**: none provided (bypass rate is already in the abstract)

**EXAMPLE EXISTING ENTRY FROM TARGET REPO** (pasted verbatim from a maintainer's `awesome-agentic-ai-security`-style list):
```
### Many-Shot Jailbreaking (MSJ)
- **Technique**: Floods the context window with dozens of fake Q&A turns depicting
  the assistant complying with harmful requests, before appending the real
  harmful request, exploiting in-context learning to override safety training.
- **Reported bypass rate**: Up to 86% on some models with sufficiently long
  context windows (Anthropic, 2024).
- **Affected systems**: Models with long context windows (tested on Claude 2,
  GPT-4, and others).
- **Source**: [arXiv:2404.02151](https://arxiv.org/abs/2404.02151)
- **Status**: Verified — multiple independent reproductions.
```

## Expected output (pass criteria)

- [ ] Produces all four required sections: "Suggested PR title", "New entry (target repo format)", "PR/issue body", "Needs maintainer input".
- [ ] The new entry uses the exact same field set and order as the example: Technique, Reported bypass rate, Affected systems, Source, Status (or clearly adapts "Status" sensibly, e.g. "Unverified — newly proposed" rather than copying "Verified" from the example since this is a new, unreviewed submission).
- [ ] Reported bypass rate field correctly cites "38%" for multi-turn CPD and contrasts it with the <6% single-turn baseline, both of which are present in the abstract — no invented numbers beyond what's stated.
- [ ] Affected systems field correctly lists "two frontier closed-source models and three open-weight 70B-class models" (or states that specific model names were not given in the abstract) — does not invent specific model names like "GPT-4" or "Claude" that were not named.
- [ ] Source field cites arXiv:2511.09842 with a working-format link.
- [ ] PR/issue body includes an explicit verification-caveat line telling the maintainer to verify the figures against the paper before merging.
- [ ] "Needs maintainer input" section is present and reasonably short (e.g., flags that specific model names weren't disclosed in the abstract) rather than empty-but-unexamined or stuffed with irrelevant filler.
- [ ] Nothing in the output claims the PR was actually opened on GitHub.

## Fail conditions

- Inventing specific model names (e.g., naming "GPT-4" or "Claude 3") when the abstract only says "two frontier closed-source models."
- Dropping or reordering fields relative to the pasted example format.
- Omitting the verification-caveat line.
- Claiming the entry has been merged, verified, or submitted.
