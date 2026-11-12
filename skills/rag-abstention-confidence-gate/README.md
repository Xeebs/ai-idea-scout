# RAG Abstention Confidence Gate

A copy-paste prompt for drafting a calibrated "should this RAG system answer or say I don't know" policy for a specific retrieval-augmented generation pipeline. It replaces the brittle default — a single embedding-similarity threshold that works on some queries and silently fails on others — with a reasoned, corpus-specific sufficiency definition, a labeled starter eval set, and a structured fallback response to use when the system should abstain instead of hallucinating.

## When to use this

Use this when you're building or operating a RAG assistant and it confidently answers questions the retrieved documents don't actually support — or when a similarity-score cutoff you tuned worked on your test queries but breaks on new ones. The right moment is *before* you build a full runtime sufficiency classifier: you have (or can quickly gather) a handful of real query + retrieved-context examples from your pipeline, and you want a policy document you can review, argue about, and test, rather than another threshold number someone is guessing at.

This is NOT for auditing whether one already-generated answer is faithful to the passages it cites (that's a single-transcript fact-check, a different task). It's NOT for improving retrieval ranking or recall (sufficiency is about whether the context your retriever actually returned answers the query — not about whether better documents exist somewhere in your corpus). And it does not write classifier code — it produces a design document you hand to whoever builds the runtime check.

## What to hand over

Required:
1. **Your pipeline description** — the domain or corpus (e.g., "internal HR policy PDFs," "hospital benefits FAQ chatbot," "SaaS product documentation") and how bad a wrong answer would be: low stakes (minor inconvenience), medium (user has to redo work or escalate), or high (financial, legal, medical, or safety consequence).
2. **A sample of real query + retrieved-context pairs** — at least 5, ideally 10-20. For each one, give the actual user query and the actual passages your retriever returned for it, verbatim (not summarized). If you can, include a mix: some queries your corpus clearly can answer, some it clearly can't, and some ambiguous or partial ones.

Optional but helpful:
- Specific examples where the system already hallucinated — what it said, and what the retrieved context actually contained.
- Any threshold or heuristic you're currently using, so the new policy can be compared against it.

If you have fewer than 5 examples, the policy can still be drafted, but it will be flagged as a low-confidence draft that needs more examples before it's usable to calibrate a real classifier. Nobody should invent example queries on your behalf — if more are needed, you'll be asked for them rather than the draft quietly filling gaps with made-up cases.

## The procedure to follow

1. **Pin down the stakes tier.** Based on your pipeline description, classify the deployment as low/medium/high stakes depending on who's affected by a wrong answer. If you stated it, that's used as given. If you didn't, the tier gets inferred from the domain and consequence described, and that inference is stated explicitly — if the domain signals medical, legal, financial, or safety consequences (patient-facing, benefits, compliance), the higher of two plausible tiers gets picked rather than defaulting to "medium" out of habit. A clarifying question only gets asked when the description gives no real basis to judge consequence at all.

2. **Write a corpus-specific definition of "sufficient context."** Not a generic one — 2-4 sentences naming what counts as enough information for *this* corpus and query type to construct a correct, complete answer without the model inferring, generalizing from a related-but-different case, or filling gaps from outside knowledge. Call out the specific failure shapes that look sufficient but aren't (e.g., a chunk describing the policy for full-time employees being used to answer a question about contractors).

3. **Label every provided query/context pair** as SUFFICIENT, INSUFFICIENT, or AMBIGUOUS, each with a one-sentence rationale naming exactly what's present or missing. AMBIGUOUS cases get flagged, not forced into a side — an honest ambiguous count is more useful than a fake-clean binary.

4. **Build a starter eval table** from the labeled pairs — query, context snippet, label, rationale — split into a "should answer" bucket and a "should abstain" bucket, with ambiguous cases called out separately as needing a human decision.

5. **Draft the abstention decision rule as a composite check, never a single similarity number.** The rule should combine: whether retrieved context names every entity/condition the query asks about, whether a passage actually states or implies the answer (versus merely sharing vocabulary with the query), and whether passages contradict each other in a way that should trigger abstention even if one alone looks sufficient.

6. **Map the stakes tier to a default strictness setting** — low stakes: permissive (abstain only on clear INSUFFICIENT); medium: balanced (abstain on INSUFFICIENT and most AMBIGUOUS); high stakes: conservative (abstain on INSUFFICIENT and all AMBIGUOUS, and consider abstaining even on single-source SUFFICIENT answers where corroboration matters). This is a recommendation to override, not a fixed rule.

7. **Draft the structured fallback response** the system should return instead of hallucinating, with these fields: `status` (answered/partial/abstained), `message` (a plain-language template like "I don't have enough information in [corpus] to answer that precisely"), `partial_findings` (anything relevant found, even if incomplete — omit if nothing was found), `suggested_next_action` (escalate to a named human/team, broaden the search, or ask the user to rephrase, chosen based on your pipeline), and `confidence_note` (a one-line reason reusing the labeling rationale from step 3).

8. **Write a validation plan, not a victory lap.** State how many more labeled examples are needed (a rough count, weighted toward underrepresented query types) before this policy is trustworthy enough to gate production traffic, and name three metrics to track once a runtime check exists: abstention precision, abstention recall, and false-answer rate. The output of this skill is a design draft for review and testing — never presented as a validated, production-ready classifier.

## Output format

A single document with these seven sections, in this order:

1. **Pipeline Summary** — domain, stakes tier, sample size received.
2. **Sufficiency Definition** — the corpus-specific definition from step 2.
3. **Labeled Sample Set** — the table from step 4, plus the list of ambiguous cases.
4. **Abstention Decision Rule** — the composite signal rule from step 5.
5. **Calibration Recommendation** — the stakes-to-strictness mapping from step 6, with the recommended default called out.
6. **Fallback Response Schema** — the structured schema from step 7, shown as both a filled-in example and a field list.
7. **Validation Plan** — what's needed before production use, plus the three tracking metrics.

## Rules this always follows

- Never invent query/context pairs, corpus details, or accuracy numbers that weren't actually provided — only label what was handed over, and say plainly when the sample is too small to calibrate reliably.
- Never recommend a bare similarity-threshold cutoff as the final decision rule — that's exactly the brittle pattern this policy exists to replace with a composite sufficiency check.
- Never force an ambiguous case into a clean SUFFICIENT/INSUFFICIENT bucket just to make the eval set look tidier — flag it and say what information would resolve it.
- Never present the drafted policy as validated or production-ready — always include the validation plan and the minimum additional sample size needed.
- Never default a stakes tier to "low" or "medium" out of habit when the domain itself signals higher consequence (patient-facing medical/benefits, legal, financial eligibility) — infer the higher plausible tier and say explicitly that it's inferred, not stated.
- If the "retrieved context" handed over is actually a full source document rather than what the retriever would realistically return, say so — sufficiency has to be judged against what the pipeline actually retrieves, not idealized full access to the corpus.

## Example of what this produces

Pipeline: an internal HR chatbot over a corpus of PDF policy documents, medium stakes. Sample query: "Can I carry over unused vacation days into next year?" Retrieved context: a chunk from the "Paid Time Off" policy stating the carryover rule for full-time salaried employees, with no mention of contractors or part-time staff.

If the actual user is a known full-time employee, this pair gets labeled SUFFICIENT. If the pipeline can't tell the user's employment type from the query alone, this gets labeled AMBIGUOUS with the rationale "context answers the question for one employment category; query doesn't specify category" — and the fallback schema would recommend asking the user to clarify their employment type rather than answering with an assumption or abstaining outright. That's the distinction a flat similarity score can't make but a sufficiency-based policy can.
