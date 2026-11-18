# Session Triage: Attention-Budget Ranking for Concurrent Agent Sessions

A prompt template for ranking several concurrently-running autonomous-agent sessions by how urgently a human supervisor should check in on each one — right now, from what's already in each session's own transcript. Paste the block below into any AI chat tool (Claude, ChatGPT, Gemini, etc.) along with your session data.

## When to use this

You have two or more autonomous-agent sessions running at once — Claude Code sessions, a LangGraph or OpenAI Agents SDK workflow, a custom agent loop, anything that logs its own turns — and you're about to glance at them to decide which one to look at first. This answers "which one actually needs me right now," once, on demand. It is not a running monitor and it does not block or approve any agent action — it only ranks attention priority across sessions you're already about to check.

## What you need to provide

**Data source**: this works off each session's own existing transcript or log — a Claude Code session transcript, a LangGraph trace export, an OpenAI Agents SDK run log, or any framework's per-turn event log. Ideally you point to or paste that log directly (it's local data the framework already wrote, not something you need to set up new tracking for). If you can't get the actual transcript file for some session (e.g., it's in a UI with no export), paste the raw recent turns as text instead — that works as a fallback for this on-demand check, though a real transcript file gives more reliable scoring.

For each session you want ranked, provide:
1. The session's recent transcript (last ~15-30 turns) — file contents or pasted text, including each tool call made, each result/error, and anything where the agent stated its plan or next step.
2. The session's original task in one line (e.g., "migrate the billing module to the new SDK").
3. Optional: how long since you last checked it, if you know and it's not already timestamped in the transcript.

## The prompt

```
I have [N] autonomous-agent sessions running and need to know which to check first.
For each one below, I'm giving you its task and its recent transcript.

Score each session using these four signals, using ONLY evidence actually present
in the transcript I give you — if something isn't evidenced, mark that subscore
N/A (insufficient data) rather than guessing:

1. Retry score (0-30): count consecutive tool calls in the last 10 actions that
   repeat the same tool with the same/near-identical args, or follow an explicit
   self-correction ("let me try again", re-issuing after an error).
   0 retries=0, 1-2=10, 3-4=20, 5+=30.

2. Staleness score (0-25): time or turn-count since the last human message/approval
   visible in the transcript (use turns if no timestamps; N/A if neither exists).
   <15min or <5 turns=0, 15-60min or 5-15 turns=10, 1-4hr or 15-40 turns=20,
   >4hr/>40 turns/no human turn visible=25. EXCEPTION: if the transcript I gave
   you is itself short or looks truncated (e.g. only a few events survived a log
   rotation), don't read "no human turn visible" as evidence of a long staleness
   gap — mark staleness N/A instead, since the absence could just be what got cut
   off rather than real unsupervised time.

3. Novelty score (0-20): fraction of the last 10 tool calls using a tool name or
   argument pattern not seen in the first half of the session.
   <20% novel=0, 20-50%=10, >50%=20.

4. Plan-divergence score (0-25): compare the agent's most recent stated plan/next
   step against what it actually did right after.
   Matches=0, adjacent-but-not-stated=15, contradicts or no plan stated and looks
   aimless=25.

Sum the four subscores per session (exclude any N/A from the sum and flag that
session's total as partial). Band: 0-24 GREEN, 25-54 YELLOW, 55-100 RED. Any
session with a partial total but one clearly RED-level signal (e.g. 5+ retries
alone) should also be RED.

Rank all sessions RED first, then YELLOW, then GREEN, highest score first within
a band. For every YELLOW or RED session, give one sentence of SPECIFIC evidence
(turn numbers, tool names, counts) — never a generic "this looks risky."

Output format, exactly:

1. [RED/YELLOW/GREEN] <session name> — score X/100 (retry _, staleness _, novelty _, divergence _)
   Why: <one sentence with specific evidence, or "no concerning signal in the visible window">

(repeat for each session, ranked)

Then one closing line: which session to check first, and why, in plain language
I can act on immediately.

Guardrails: never invent transcript content or counts not actually present in what
I give you. Never treat this as an approval/block mechanism — it's priority ranking
only, for sessions I'm already about to check. If I only give you one session, score
it but don't frame it as "check this first" since there's nothing to compare it to.

Here are my sessions:

SESSION 1
Task: [one-line task]
Last checked: [time ago, or "unknown"]
Transcript:
[paste or describe the last 15-30 turns: tool calls, results/errors, any stated plan]

SESSION 2
Task: [one-line task]
...
```

## What you get back

A ranked list — RED sessions first, then YELLOW, then GREEN — each with its four subscores, a total, and one specific evidence sentence (not a vague risk label). The response ends with a single plain-language line telling you which session to look at first and why.

## Guardrails (carried into every use of this prompt)

- The model should never fabricate transcript details, timestamps, or counts you didn't actually give it. Missing evidence becomes `N/A`, not a guess.
- This is never an approval or action-blocking mechanism — don't use its output to auto-stop or auto-approve anything. It only tells you where to look first.
- Every YELLOW/RED entry must carry a specific reason citing the transcript; an unexplained color is a red flag that the model skipped the procedure.
- If you give uneven amounts of transcript for different sessions (e.g., 30 turns for one, 3 for another), the response should call that out rather than ranking them as if the comparison were apples-to-apples.
