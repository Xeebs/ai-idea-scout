# Local-Model Preflight Gate Designer

A paste-into-any-AI-chat-tool prompt for designing the actual rule set behind a "local small model gates my cloud coding-agent calls" setup — the checklist content, not the code that wires it in.

## What this is for

If you run a cloud coding-agent CLI (Codex CLI, Claude Code, Cursor's agent mode, or you're calling the OpenAI/Anthropic API directly from your own agent loop) and you want a cheap local model (something you already run via Ollama or llama.cpp) to screen calls on both sides — catching a request that's going to waste a paid call before you send it, and catching a response that's obviously wrong before you trust it — this prompt produces the actual checklist and local-model prompts for that gate. It does not write the interceptor code that hooks into your CLI's call lifecycle; that's a separate build. This is the one-time design pass that tells you exactly what to check and how to word the local model's judging prompt.

## Data source

This works best **connected** to a real log of your own past calls — a Codex CLI session export, a Claude Code transcript file, a Cursor local history export, or any log of requests/responses you've made. If you don't have one, it falls back to **manual**: you describe 3-5 real examples of calls that wasted money or came back wrong, in your own words, directly in the chat. Either way works; just say which one you're giving it.

## How to use this

Copy the prompt block below into any AI chat tool (Claude, ChatGPT, etc.), fill in the bracketed parts, and attach or paste your log if you have one.

```
I want you to design a local-model preflight gate checklist for my cloud coding-agent workflow. Do not write any interceptor or middleware code — I only want the rule content and the local-model prompts, not the integration code.

Here's my setup:
- CLI/tool: [e.g. "Codex CLI" / "Claude Code" / "Cursor agent mode" / "raw OpenAI API calls from my own script"]
- Stack/language: [e.g. "TypeScript monorepo, Next.js + Prisma"]
- What makes my outgoing requests waste a call: [describe 2+ real patterns, e.g. "I forget to mention which file the bug is actually in, so it guesses wrong" / "I re-ask something it already answered three messages ago"]
- What a bad response looks like for my codebase: [describe 2+ real patterns, e.g. "it references a Prisma model field that doesn't exist in my schema" / "it writes the diff in the wrong format for my patch tool" / "it skips calling the required lint-check tool before claiming done"]
- Log data: [paste a log excerpt or attach a file here if you have one, OR write "no log, using the descriptions above only"]

Using exactly what I gave you above (do not invent extra examples beyond what's in my log or description), produce:

1. WORKFLOW PROFILE — restate my CLI, stack, and whether you used log data or my manual description.

2. PRE-SEND CHECKLIST — a table with columns: Check | Category (Context completeness / Instruction specificity / Duplicate detection) | Decision if triggered (HOLD/FLAG/PASS) | Example from my data that PASSES | Example from my data that HOLDS or FLAGS. Each check should be something a small local model could actually evaluate mechanically, not a vague judgment call.

3. POST-RECEIVE CHECKLIST — same table structure, columns: Check | Category (Structural validity / Required-action compliance / Format compliance) | Decision if triggered (HOLD/FLAG/PASS) | Example that PASSES | Example that HOLDS or FLAGS.

4. LOCAL-MODEL PROMPT TEMPLATES — two complete, ready-to-paste prompts: one "Pre-send scorer prompt" that takes an outgoing request plus the checklist and returns a verdict (PASS/FLAG/HOLD, which check triggered, why), and one "Post-receive scorer prompt" that does the same for an incoming response.

5. CALIBRATION NOTES — call out any check above that depends on subjective judgment rather than a mechanical/structural test, mark it LOW-CONFIDENCE, and recommend it carry less weight or be dropped until I've tested it. Also suggest roughly how many of my own past labeled calls (20-50) I should run both prompts against before trusting HOLD decisions live.

6. EXPLICITLY OUT OF SCOPE — one line confirming this is the rule set only, not the code that hooks it into my CLI's actual call path.

Rules for you to follow:
- Do not fabricate failure examples, call counts, or success percentages — use only what I gave you.
- Do not claim this checklist will catch some percentage of bad calls — that number can only come from running the calibration step on my own data, which I haven't done yet.
- If what I gave you is too thin to build real checks (no stack named, no concrete failure pattern, no log), ask me for the missing piece instead of inventing a generic checklist.
```

## What you'll get back

A single structured document: your workflow profile, a pre-send checklist table, a post-receive checklist table, two ready-to-paste local-model scoring prompts, a calibration-notes section flagging which checks are judgment-based versus mechanical, and one line confirming the interceptor code itself is out of scope. You then plug the two scorer prompts into whatever local model you already run (Ollama, llama.cpp, etc.) as the actual gate logic — wiring that into your CLI's call lifecycle is a separate engineering task this prompt deliberately does not cover.

## What this will not do

- It will not write the middleware/interceptor code that hooks into Codex CLI, Claude Code, Cursor, or a raw API's call lifecycle.
- It will not invent failure statistics or guarantee a catch rate — only your own calibration run against real past calls can produce that number.
- It will not treat a subjective judgment check ("is this instruction vague?") with the same confidence as a mechanical one ("does this symbol exist in the file?") — it keeps those separated so you know which checks are more likely to misfire.
