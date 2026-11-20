# Loop Guard: A Battle-Tested Control-Loop Library for Agentic RAG

Every team building agentic retrieval eventually writes the same twenty lines of plumbing — plan a query, retrieve, critique the result, decide whether to answer or retry — and every team discovers its edge cases the hard way: the loop that never stops, the one that stops too soon, the one that crashes the moment the model returns malformed JSON instead of the tool call it was supposed to. Two independent practitioners wrote this up within the same month, as if confirming the other's bruises. Neither had heard of the pattern before they'd already half-built and half-broken it.

## The Gap

The now-widely-shared "You Might Not Need RAG" post describes its author hand-rolling exactly this loop — plan query, retrieve, critique, re-query — and only later learning it already had a name: agentic retrieval. A separate practitioner writeup from Vectorize, documenting the process of finally getting agentic RAG to behave, independently hits the same wall from a different angle: invalid JSON returned mid-loop, with no graceful way to recover. Both are solo narratives of custom plumbing built from scratch, not references to a shared library everyone reaches for. A gap-analyst search of GitHub turned up a long tail of agentic-RAG frameworks — DualStack-Agent, Corax-RAG-Agent, artoo, Crux, RAGents, rag-engine, py-jrag, and more — but nearly all of them are single-author, narrow in scope, or clearly thesis/hobby projects with no sign of broad adoption. A web search surfaced one packaged library worth naming, `retrievalagent` on PyPI, built on LangGraph with a retry/evaluate/rewrite loop and a max-iteration cap, plus one research method (Stop-RAG) that learns when to stop retrieving. Both are real, and neither is the thing developers converge on when they search for "how do I not reinvent this." The control-loop logic — retry policy, calibrated stopping, malformed-output handling — still has no consensus shared library, which is exactly why two unrelated developers ended up writing and debugging it alone, in public, in the same window.

## The Project

Loop Guard is a small, dependency-light control-loop library meant to sit underneath any RAG stack's retrieval-generation call, owning exactly the three things that kept breaking in the source writeups: a retry policy with a real cap, a calibrated stopping criterion so the loop doesn't retrieve forever on hard queries or quit too early on easy ones, and defensive parsing/repair for the malformed tool-call JSON that underlying models still produce often enough to matter. Every loop exit gets logged with a reason — answered, max-iterations, low-marginal-gain, or parse-failure-exhausted — so a team finally has visibility into *why* their retrieval loop stopped, something neither source project had at all.

It's deliberately scoped to the regime both source posts were actually operating in: hundreds to low-thousands of documents, a solo developer or small team shipping an internal or early-stage tool, not a claim to replace million-document retrieval infrastructure. And rather than asking teams to adopt a new orchestration framework, it ships as adapters — plain function calls, LangGraph, LlamaIndex — so the control loop can be dropped into an existing stack instead of requiring a migration.

## Tangible Impact

**Population**: Solo developers and small teams (1–5 engineers) building internal or early-stage retrieval-augmented tools without a dedicated ML/platform engineer — the same profile as the two source-post authors, who both discovered mid-build that their hand-rolled loop was reinventing a known pattern badly. GitHub search suggests dozens of comparable one-off repos exist, each paying this tax independently.
**Mechanism**: Replacing a bespoke, untested retry/stop loop with a reviewed, tested library removes the two failure classes both source posts hit firsthand (infinite/premature stopping, unhandled malformed JSON) before they ship to users, cutting the debugging cycle those authors each described going through alone.
**Measure**: crash/hang rate from malformed tool-call responses before vs. after adoption on a replayed trace set; time-to-working-loop for a new integration (target: hours, not the multi-week trial-and-error both source posts describe); loop-exit-reason distribution on real traffic, which the two source projects had no visibility into at all.

## Try It

A companion Claude Code skill is already built: [`skills/rag-agentic-loop-control-library/`](https://github.com/Xeebs/ai-idea-scout/tree/main/skills/rag-agentic-loop-control-library). Its one-line description, from `SKILL.md`:

> Audits a hand-rolled agentic RAG retrieval loop (retrieve → critique → re-query → stop) for three known failure modes — missing retry cap, uncalibrated stopping criterion, unhandled malformed tool-call JSON — and drafts the specific code fix for each. Use when a developer is about to ship, or has already had crash/hang problems with, a custom agentic retrieval loop.

This is a review aid, not the library itself — you paste or describe your existing loop and it hands back a findings table plus drafted fixes, before you've written the full control-loop library this piece describes. To use it: either paste the contents of its `README.md` into any AI chat tool along with your retrieval loop code, or drop the whole `rag-agentic-loop-control-library/` folder into `~/.claude/skills/` if you're running Claude Code.

Worth knowing going in: a PyPI package called `retrievalagent` already does something close to this on top of LangGraph. The real differentiation question for Loop Guard isn't "does this capability exist anywhere" — it's whether a framework-agnostic version with harder-won defaults (calibrated stopping, JSON-repair heuristics) is worth adopting over just copying a gist, or over `retrievalagent` if you're already on LangGraph. That's an open question, not a settled one.

---

Surfaced from `research/2026-11-12-rag-techniques.md`, pattern `P1`.
