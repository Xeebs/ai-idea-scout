# Fast Lane: Judge-to-Blocking Latency Decision Aid

Paste this whole document into any AI chat tool (Claude, ChatGPT, etc.), then add your own judge setup details at the bottom where marked, and send it. No other context or installation is needed.

## What this is for

If you already run an LLM-as-judge pipeline that detects bad outputs *after the fact* — it scores or flags a response once it's already been returned to the user, maybe on a sample of live traffic, maybe continuously — and you're now asking "can some of this actually block a response before it goes out, without destroying latency," this runs a one-time, sample-based comparison of three ways to convert part of that judge into something synchronous: a deterministic keyword/pattern pre-filter, a condensed "distilled-proxy" heuristic standing in for a small distilled model, and a fail-closed timeout wrapper around the full judge. It scores each against your actual judge on a labeled sample you provide, and hands back a recommendation plus a ready-to-run Python benchmark script so you can validate the numbers for real before you build anything.

This does not call any real model, measure real wall-clock latency, or run continuously. It's a decision aid you run once, on a sample, to decide which strategy is worth actually building and timing. The real benchmark happens when you run the script it gives you against your real judge model and real candidate implementations.

## What to hand over

**This only uses what you paste below — it does not connect to any account, API, model, or logging platform.** You need:

1. **Your judge prompt/rubric, verbatim.** The actual text your judge model receives. A rough description works but lowers confidence — say so if that's all you have.
2. **A labeled sample with at least one `harmful` and one `benign` example** (ideally 20-50+, drawn from real traffic/incidents). Without both labels represented, no catch-rate or false-positive number can be computed, only a qualitative strategy design. Fewer than 10 total is fine but lowers confidence in the result.
3. **Your latency budget** — e.g., "p99 must be under 300ms."
4. **Your current full-judge latency, if you know it** (e.g., "our async judge runs ~1.8s, p99 ~2.4s"). Without this, the timeout-wrapper strategy can only be described qualitatively, not scored with a timeout-miss number.
5. **The named harm categories your judge targets** (scams, abuse, PII, prompt injection, policy violations, etc.), if your rubric doesn't already spell them out.

## What you'll get back

A single report with five parts:

**1. Sample Summary** — how many traces you gave, how they split harmful/benign, your stated budget and current latency (or "not provided").

**2. Strategy Comparison** — a table scoring the full judge (baseline), a deterministic pre-filter, a distilled-proxy heuristic, and a fail-closed timeout wrapper, each on catch-rate and false-positive rate against your labeled sample, plus a latency characterization for each (qualitative unless you gave a real current-latency number).

**3. Recommendation** — which strategy (or combination, e.g. pre-filter escalating only ambiguous cases to a distilled proxy) best fits your stated budget, with an explicit caveat that these numbers come from reasoning applied to your sample, not a timed production run.

**4. Benchmark Harness** — a runnable Python script with pluggable judge/pre-filter/distilled-proxy functions, a fail-closed timeout wrapper, and a scoring loop for catch-rate, false-positive rate, and p50/p99 latency — wire in your real model calls and re-run it to get validated numbers.

**5. What this doesn't tell you** — honest limitations given your sample size, whether real latency was ever measured, and that the "distilled-proxy" strategy is reasoning applied to a condensed rubric, not an actual trained model's behavior.

## Rules this follows

- No latency number is presented as measured unless it's a number you yourself provided; everything else is explicitly marked as an estimate or skipped entirely.
- No catch-rate or false-positive number is produced without at least one harmful and one benign example in your sample.
- The timeout wrapper's quantitative miss-rate is never estimated without your own current-latency figure — if you don't have it, you get the mechanism explained, not an invented number.
- A fail-open default is never recommended without explicitly flagging that it lets unblocked traffic through when the judge times out.
- Harm categories are never invented — if your rubric doesn't name them, you'll be asked rather than given a generic guess.
- This is never presented as a substitute for actually timing your real judge, pre-filter, and small model — the harness script exists specifically so you validate before you build.

## How to use it

Paste this whole README into your AI chat tool, then add below it:

```
My judge prompt/rubric: <paste verbatim>
Latency budget: <e.g. p99 under 300ms>
Current full-judge latency (if known): <e.g. avg 1.8s, p99 2.4s>
Named harm categories (if not obvious from the rubric): <list>
Labeled sample traces (at least 10, both harmful and benign):
1. [input/response] — label: harmful/benign
2. ...
```

and ask it to run the comparison and produce the five-part report described above.
