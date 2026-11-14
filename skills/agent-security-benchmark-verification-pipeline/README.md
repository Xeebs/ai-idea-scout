# Agent-Security Benchmark Claim Due-Diligence Check

A paste-into-any-AI-chat-tool prompt for checking one published agent-security or AI-guardrail benchmark claim before you rely on it in a purchase or deployment decision. It does not re-run anyone's tool — it reasons about whether the *claim as written* is actually checkable, and tells you plainly when it isn't.

## When to use this

Use it the moment you're evaluating an AI agent-security, guardrail, or "agentic safety" vendor and you have a specific claim in front of you — a blog post, a README metrics table, a one-pager, a paper excerpt — something shaped like "100% unsafe-action prevention across 22 scenarios" or "an audited 0.00% violation rate." You're about to make or influence a buying/deployment decision based partly on that number, and you want a fast gut-check on whether it holds up before you commission (or skip) a real independent audit.

This is a one-shot check on **one claim at a time**. It is not a monitoring service, not a crawler, and not an actual re-execution of the vendor's tool in a sandbox — if you need the claim genuinely reproduced against reconstructed test scenarios, that's a much heavier, separate engineering effort this prompt cannot perform. Say so to yourself up front: this tool tells you whether to trust the claim as written, not whether the underlying tool actually works.

## What to hand over

**Data source: Manual.** You paste or link the exact claim text — a URL, a copied paragraph, a README table row, a paper excerpt. This prompt does not browse the web or GitHub on its own and will not invent a claim's wording from memory. If you only name the vendor without pasting the claim, you'll be asked to paste or link the exact passage first.

Give it:
1. **The claim text itself**, verbatim — not a summary of what the vendor "basically says."
2. **What decision rides on it** — e.g. "deciding whether to buy this over a competitor" or "deciding whether to deploy without further review." This calibrates how hard the final verdict pushes back.

Optionally also give it: a competing claim to compare against, or any extra vendor documentation link (methodology appendix, dataset link, existing audit report).

## What it does

1. **Extracts the claim's structure**: the headline metric, the stated scenario/test count, any named benchmark/dataset, and whatever methodology detail is given.
2. **Checks for a traceable source**: does the claim point to a public dataset, a named third-party benchmark suite, or an accredited-auditor report — or is it entirely self-measured with nothing external to check against? A fully self-measured, self-reported claim with zero external reference is the single biggest red flag.
3. **Runs the claim against a red-flag checklist**:
   - Vague or rounded scenario count instead of an exact, enumerable number.
   - No linked dataset or scenario list a third party could inspect.
   - A suspiciously perfect metric (100%, 0.00%) with no confidence interval or variance disclosed.
   - Harness/scaffolding conflation — crediting "the agent" when a wrapper, retries, or best-of-N sampling likely did the work, undisclosed.
   - A single reported success rate with no mention of how many independent runs produced it.
   - No stated adversary or threat model — "unsafe action" or "violation" left undefined.
   - No disclosure of excluded or dropped scenarios.
   - Generic/public-looking test scenarios that don't resemble your actual use case.
4. **Sketches whether the test could be reconstructed** by a third party today — full, partial, or not reconstructable — naming exactly what's missing.
5. **Assigns a Verifiability Rating**: `VERIFIABLE` (public dataset or accredited audit, linkable), `PARTIALLY VERIFIABLE` (some methodology disclosed, key pieces missing), or `UNVERIFIABLE` (self-reported, no external reference, not enough to reconstruct). A tie between partial and unverifiable always resolves to UNVERIFIABLE — this tool is deliberately skeptical, not claim-friendly.
6. **Drafts 3-5 specific follow-up questions** to send the vendor, each tied to an actual red flag found (not generic "please be more transparent" filler).

## Output you'll get

A single due-diligence note with these sections, in order:
1. **Claim as stated** — the metric and scenario count, quoted back to you.
2. **Verifiability Rating** — VERIFIABLE / PARTIALLY VERIFIABLE / UNVERIFIABLE, with a one-line reason.
3. **Red flags found** — only the ones that actually apply, each with a sentence on why it matters here.
4. **Reconstruction sketch** — 2-3 sentences on whether and how a third party could reproduce this test.
5. **Questions to ask the vendor** — 3-5 numbered, specific questions.
6. **Bottom line** — one sentence: is this claim alone enough to support your stated decision, or should you treat it as marketing until independently verified?

## Guardrails — what it will never do

- It will never claim to have actually re-run, reproduced, or tested the vendor's tool. It only assesses whether the claim *as written* is checkable. Actually re-running a vendor's security tool needs an isolated sandbox and reconstructed adversarial scenarios — a real engineering project, not a one-shot text check.
- It will never invent methodology details, dataset names, or scenario contents that weren't in what you gave it — anything unknown is reported as "not disclosed," never guessed.
- It will never soften an UNVERIFIABLE rating just to seem more useful, even for a well-known or well-funded vendor.
- It will never treat a vendor's reputation or market position as evidence for the claim's methodology quality — it judges the text, not the brand.
- If you give it a paraphrase instead of the exact claim text, it will ask for the verbatim wording or link before running the checklist, since red-flag detection on a paraphrase can unfairly clear or condemn a claim.

## How to use it

Paste this whole README into any AI chat tool along with the vendor claim you want checked and what decision rides on it, and ask it to run the due-diligence check described above. Expect one structured note back, not a conversation — if the claim turns out UNVERIFIABLE, treat that as your answer: ask the vendor the follow-up questions before trusting the number, don't go looking for a way to upgrade the rating.
