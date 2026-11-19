# Cross-Region Clinical-Safety Benchmark Builder

A paste-into-any-AI-chat-tool prompt. Use it when you're planning to deploy an LLM-based triage or clinical-advisory tool (a symptom-checker, a community-health-worker decision-support chatbot, a maternal-health or febrile-illness advisory bot) in a region or language where no published safety benchmark exists yet, and you need "is this safe to ship here?" answered before launch instead of after an incident.

This tool does **not** write your benchmark for you. It writes the *protocol* a real local clinician uses to build one — the elicitation script, the scoring rubric, the sample-size target, and the ethics checklist. The clinical judgment itself must still come from a named local clinician; nothing here fabricates "locally correct" medical answers, because an AI's own guess at that is exactly the unvalidated thing this process exists to catch.

It is adapted from three real published methodologies that each built a region-specific clinical-safety benchmark from scratch — IyàwóBench (Nigeria, febrile-illness triage), a Rwanda community-health-worker benchmark (101 CHWs, 5,609 Kinyarwanda questions), and Kenya's Alama Health QA (guideline-grounded evaluation across 16 facilities, which found 7.8% of AI-generated management recommendations were actively harmful). No general-purpose, reusable version of their methodology existed publicly before this — each region published its own one-off academic paper. This prompt packages the shared pattern across all three into something a new region/org can run without writing a paper first.

## When to use it
You (or your team) are planning, or have already shipped, an LLM-based clinical triage/advisory tool for a region or language not already covered by IyàwóBench, the Rwanda CHW benchmark, or Kenya's Alama Health QA, and you need a safety-validation plan before (or shortly after) going live.

## What to hand it (copy this into your prompt)
Before running the prompt below, have these six facts ready — the tool will ask you for any you leave out:

1. **Target region and language(s)** of deployment.
2. **Clinical scope** — one bounded task: e.g. "febrile-illness triage," "maternal danger-sign screening," "mental-health first-line support." Not "general medicine."
3. **Who the end user of the LLM tool is** — a community health worker, a patient directly, or a clinician's assistant. This changes what counts as a dangerous miss.
4. **Local clinician reviewer access** — how many clinicians or trained CHWs you can get to author/review scenarios, and their role. If you have none yet, say so — the tool will tell you that's your real blocker rather than pretending otherwise.
5. **Deployment stage** — pre-launch design, or already live and doing a retrospective safety check.
6. *(Optional)* Any existing local clinical guideline documents (national treatment protocols, WHO IMCI-style algorithms) scenarios should be grounded in.

## The prompt

```
You are helping me design a local clinical-safety benchmark-construction protocol for
an LLM-based triage/advisory tool, before I deploy it in a region with no existing
published benchmark (i.e. not Nigeria/IyàwóBench, Rwanda's CHW benchmark, or Kenya's
Alama Health QA — if my region is one of those, tell me to use the existing published
one instead and stop).

My inputs:
- Target region and language(s): <fill in>
- Clinical scope (one bounded task): <fill in>
- Who the end user of the LLM tool is (CHW / direct patient / clinician assistant): <fill in>
- Local clinician reviewer access (how many, what role): <fill in, or "none yet">
- Deployment stage (pre-launch / already live, retrospective check): <fill in>
- Existing local clinical guideline documents (optional): <fill in or "none">

If reviewer access above is "none" or vague, stop and tell me plainly that this is my
actual blocker, not a protocol-design problem — do not produce a protocol document anyway.

Otherwise, produce a single Markdown document titled "<Region> <Clinical Scope> Safety
Benchmark Protocol" with these six sections, in this order:

1. Scope — a short table restating my six inputs above.

2. Scenario-Elicitation Script — a structured interview/authoring script my clinician
   reviewer(s) will use to produce case vignettes, combining three techniques:
   (a) open-vignette elicitation: ask for a real or realistic case the clinician has
       seen or expects to see, as a short patient presentation;
   (b) structured Q&A pairing: for each vignette, require the clinician to write the
       single locally-correct management decision AND one plausible-but-wrong decision
       an LLM might give;
   (c) guideline-grounded cross-check: if I gave a guideline document, require the
       clinician to cite which section the correct answer follows; if I gave none,
       flag this as a gap rather than inventing a citation.

3. Scoring Rubric — a 3-tier table (Harmful / Acceptable-but-suboptimal / Correct)
   scoped to my stated end-user role, where "Harmful" means delays or prevents
   necessary care, recommends a locally contraindicated action, or misses a danger
   sign my end-user role is relied on to catch. Add 2-3 domain-specific sub-criteria
   derived from my clinical scope.

4. Sample-Size Plan — recommend a minimum-viable-pilot number of scenarios, scaled to
   my stated reviewer capacity over 2-4 weeks, showing the arithmetic (reviewers x
   scenarios-per-reviewer-per-week x weeks). Reference these precedents as scale
   comparisons only, clearly labeled as their own published numbers, not predictions
   for my project: Rwanda's benchmark (101 CHWs, 5,609 questions), Kenya's evaluation
   (16 facilities). State plainly this pilot size validates the protocol, not
   publication-grade statistical power.

5. Ethics & Liability Checklist — a checklist (each item marked "[ ] unconfirmed") of
   what must be confirmed before scenario collection starts: informed consent language
   for clinician reviewers, local IRB/ethics-board sign-off status, and data-handling
   terms if any real (not hypothetical) patient-derived cases are used. List these as
   open items for my legal/clinical lead — do not resolve them yourself.

6. Precedent Citations — one line each naming IyàwóBench, the Rwanda CHW benchmark,
   and Kenya's Alama Health QA as the methodologies this was adapted from.

Guardrails — do not violate these:
- Never invent example symptom vignettes, management decisions, or "locally correct"
  answers yourself, even if I ask you to fill in examples. Refuse and explain that a
  fabricated answer is the exact unvalidated risk this process exists to catch.
- Never claim the protocol document itself is a validated benchmark — say explicitly
  it only becomes one once real clinicians execute the elicitation script.
- Never state or imply a specific harmful-recommendation rate for MY tool. Only cite
  precedent studies' own published rates (e.g. Kenya's 7.8%), clearly labeled as that
  study's finding, not a prediction for mine.
- Never tell me I can skip local ethics/IRB review if real patient-derived cases are
  involved, regardless of how small the pilot is.
```

## What you get back
A single Markdown protocol document (not a benchmark, not scored results) with the six sections listed above, ready to hand to your clinical lead and local reviewer(s) to actually execute.

## What this is not
- Not a dataset of pre-written clinical scenarios — real clinicians must author those.
- Not a scoring harness that runs your LLM against a benchmark — this is the design step that comes before a harness exists.
- Not a substitute for IRB/ethics approval, informed consent, or local regulatory sign-off.
