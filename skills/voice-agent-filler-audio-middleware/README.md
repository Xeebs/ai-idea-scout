# Filler Coverage Designer

A paste-and-go prompt that designs the filler-audio ("holding phrase") policy for a voice agent's slow tool calls — which tools need a spoken filler while they're pending, what it should say, and exactly when it needs to stop. It does not write or run any code; it produces the design decision a developer then wires into whatever voice framework (LiveKit Agents, Pipecat, a custom stack) is running the actual calls.

Use this when callers to your voice bot hear dead air while a backend lookup, order-status check, or third-party API call is in flight, and you want a deliberate policy for which of those calls get a filler phrase — instead of either bolting a generic "please hold" onto everything or ignoring the ones that actually need it.

## What you need to provide

**This is a manual-paste tool: nothing here connects to your voice platform or codebase.** You need to type or paste:

1. A list of your agent's tools/functions — for each one: its name, a one-line description of what it does, and latency data. Real numbers from your own logs are best (p50 and p95, e.g. "lookup_order_status: p50 400ms, p95 2.1s"), but a typical/worst-case range is acceptable if that's all you have. If you genuinely have no latency data for a tool, say "no data" for it explicitly — don't skip it silently.
2. Optional: your target language(s), any tone/brand-voice constraints ("never sound chipper," "formal only"), and whether your framework currently has reliable barge-in (interruption) detection. If you don't know, say so — it changes the output.

## How to use it

Paste this whole prompt into any AI chat tool, then paste your tool manifest and any optional context right after it.

```
You are designing a filler-audio (holding-phrase) policy for a voice agent's
slow tool calls. I will give you a list of tools/functions my voice agent can
call mid-conversation, with latency data for each, plus optional tone/language
notes. Do the following:

1. For each tool, classify it as one of: lookup (read-only data fetch),
   transaction (a mutating action), search (open-ended/variable-time query),
   or external-passthrough (calls a third-party API outside my control). If a
   tool's description is too thin to classify confidently, mark it
   UNCLASSIFIED and ask me for one more line instead of guessing.

2. Apply this threshold: a tool needs filler audio if its p50 latency is
   700ms or worse, OR its worst-case/p95 is 1.5s or worse. If I gave you a
   different threshold, use mine instead and say so. Any tool entirely below
   threshold gets "No filler needed" — don't invent a reason to add one.

3. For every tool that crosses the threshold, write a filler phrase
   appropriate to its category, in the tone I specified (default: warm but
   professional, not chipper). Never use the identical phrase for the filler
   and its escalation line.

4. For any tool whose worst-case/p95 latency is 3x the *worst-case threshold*
   (default 1.5s, so the checkpoint is 4.5s by default) or more, build a short
   escalation ladder: initial filler at the p50-threshold crossing, one
   escalation line at that 3x worst-case checkpoint, and a fallback line (e.g.
   offering a callback) if it passes my tool's own stated worst-case entirely.
   Tools that cross the p50 threshold but stay under that 3x checkpoint get
   one filler line only, no ladder — don't over-build ladders for merely-slow
   tools.

5. Write a cancellation policy: filler playback must stop the instant either
   (a) the tool call resolves and a real response is ready, or (b) I start
   speaking over it (barge-in). Name both trigger signals explicitly. State a
   target of stopping within ~150ms of either trigger, and flag this as a
   number I need to validate against my actual framework, not a guarantee.

6. Flag every UNCLASSIFIED tool, every "no data" tool, and — if I told you
   barge-in detection is unreliable or unknown in my stack — flag every tool
   with a warning that filler audio risks talking over me until that's fixed.

Never invent latency numbers for a tool I marked "no data." Never write a
phrase that implies a false state ("found it!") before the tool has actually
returned. Never loop the identical filler clip more than once without
escalating the wording. This is a design decision, not working code — say so
if it looks like I'm treating this output as the finished project.

Produce your answer as:
1. A coverage table: Tool | Category | Latency | Threshold used | Filler needed?
2. A phrase library, grouped by category, with 3-5 example lines plus one
   escalation line and one fallback line per category that needed fillers.
3. Escalation ladders for any tool that needed one, with trigger timing.
4. The cancellation policy spec (the two trigger signals, the ~150ms target).
5. Open flags: every UNCLASSIFIED or "no data" tool, and the barge-in warning
   if applicable. Write "None" if there are none.

Here is my tool manifest and context:
<PASTE YOUR TOOL LIST, LATENCY DATA, AND ANY TONE/LANGUAGE/BARGE-IN NOTES HERE>
```

## What you get back

A single report with the five sections above — a coverage decision per tool, ready-to-use filler phrases and escalation ladders, a cancellation policy spec naming the two signals your runtime needs to watch, and an explicit list of anything the model couldn't decide confidently (tools it couldn't classify, tools with no latency data, or a warning if your barge-in detection isn't solid yet).

Hand that report directly to whoever is wiring the actual voice framework (LiveKit Agents, Pipecat, or your own stack) — it's the implementation spec, not a suggestion to redesign further.

## What this is not

This does not touch your codebase, does not call your voice platform's API, and does not test cancellation timing in a live call — it is a one-time (or periodically re-run, as your tool set changes) design pass. If you don't have at least rough latency numbers for your tools, get those first; a policy built on "no data" is a worse starting point than no policy at all.
