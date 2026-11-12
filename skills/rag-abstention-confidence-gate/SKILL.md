---
name: rag-abstention-confidence-gate
description: Drafts a calibrated abstention policy for a RAG (retrieval-augmented generation) pipeline — a corpus-specific definition of "sufficient context," a labeled starter eval set of should-answer vs. should-abstain query/context pairs, and a structured "not found" fallback schema. Use when a team's RAG system hallucinates on queries its corpus can't actually answer and they want a designed policy to evaluate before building a runtime classifier, not another brittle similarity-threshold guess.
---

# RAG Abstention Confidence Gate

## When to use this

Reach for this skill when someone is building or operating a RAG assistant and describes a failure like: the system confidently answers questions the retrieved documents don't actually cover, a similarity-score cutoff they tuned stopped working when the corpus or query mix changed, or they need to decide what the system should say instead of hallucinating. The trigger moment is specifically *before* they commit engineering time to a runtime sufficiency classifier — they have (or can quickly pull) a handful of real query + retrieved-context examples and want a reasoned policy document to review, argue about, and test against, not a magic threshold number.

Do not use this for: auditing whether a specific already-generated answer is faithful to its retrieved passages (that is a claim-verification task on a single transcript, not a policy-design task); tuning retrieval recall/ranking (sufficiency is about whether retrieved context — however it was ranked — actually answers the query, not about whether better documents exist in the corpus); or writing production code (this skill produces a design document, not a classifier implementation).

## Inputs

Required:
1. **Pipeline description** — domain/corpus (e.g., "internal HR policy PDFs," "hospital benefits FAQ," "SaaS product docs"), and the stakes of a wrong answer (low: minor inconvenience; medium: user has to redo work or escalate; high: financial, legal, medical, or safety consequence).
2. **A sample of real query + retrieved-context pairs** — at least 5, ideally 10-20, each as: the user's query, and the actual passages/chunks the retriever returned for it (verbatim, not summarized). Include a mix if possible: queries the corpus clearly can answer, queries it clearly can't, and ambiguous/partial ones.

Optional:
- Known failure examples (a query where the system hallucinated, with what it said).
- Any existing threshold or heuristic currently in use, so the new policy can be compared against it.

If fewer than 5 query/context pairs are provided, proceed but label the output as a low-confidence draft and say explicitly that the sufficiency definition and eval set need more examples before they're usable to calibrate a real classifier. Never invent query/context pairs that weren't provided — if more examples are needed, ask for them or say the draft is provisional.

## Procedure

1. **Establish the stakes tier.** From the pipeline description, assign the deployment a stakes tier (low/medium/high) based on who's affected by a wrong answer. If the user stated it, use that. If not, infer the most defensible tier from the domain and described consequence and say explicitly that it's inferred rather than stated — when the domain signals medical, legal, financial, or safety consequences (e.g., patient-facing, benefits, compliance), pick the higher of two plausible tiers rather than defaulting to "medium" by habit. Ask a clarifying question instead of inferring only when the description gives no real basis to judge consequence at all.

2. **Define corpus-specific "sufficient context."** Write 2-4 sentences defining what "sufficient" means for *this* corpus and query type — not a generic definition. Sufficient context means: the retrieved passages contain enough explicit information to construct a complete, correct answer to the specific query without the model needing to infer, generalize from a related-but-different case, or fill gaps from outside training knowledge. Name the corpus-specific failure shapes that count as insufficient (e.g., for an HR policy corpus: "the retrieved chunk describes the policy for full-time employees but the query is about contractors" is insufficient even though it's topically relevant).

3. **Label every provided query/context pair.** For each pair, assign one of three labels with a one-sentence rationale naming exactly what's present or missing:
   - **SUFFICIENT** — context contains everything needed to answer correctly.
   - **INSUFFICIENT** — context is topically related but missing the specific fact, scope, or condition the query needs.
   - **AMBIGUOUS** — a genuine judgment call; flag it rather than forcing a side, and say what additional information would resolve it.
   Never relabel or soften a case just to make the eval set look cleaner — an honest AMBIGUOUS count is more useful than a false binary.

4. **Build the starter eval set table** from the labeled pairs: query, context snippet (truncated if long), label, rationale. Split into a "should answer" bucket (SUFFICIENT) and a "should abstain" bucket (INSUFFICIENT), with AMBIGUOUS cases called out separately as cases needing a human decision before they're added to either bucket.

5. **Draft the abstention decision rule.** Specify what signals the runtime check should combine — never recommend a bare embedding-similarity-score cutoff alone, since that is the exact brittleness this skill exists to replace. Recommend a composite check: (a) does retrieved context name every entity/condition/sub-part the query asks about, (b) does any passage state or imply the answer rather than merely sharing vocabulary with the query, (c) is there a contradiction across passages that should trigger abstention even if one passage looks sufficient alone. State the rule as a decision procedure, not a single number.

6. **Map stakes tier to a default strictness setting.** Low stakes → permissive (abstain only on clear INSUFFICIENT); medium → balanced (abstain on INSUFFICIENT and most AMBIGUOUS); high stakes → conservative (abstain on INSUFFICIENT and all AMBIGUOUS, and consider abstaining on SUFFICIENT-but-single-source cases where corroboration matters). State this as a recommendation the operator can override, not a fixed rule.

7. **Draft the structured fallback response schema** — the exact shape of what the system returns when it abstains. Minimum fields: `status` (answered/partial/abstained), `message` (a plain-language template, e.g., "I don't have enough information in [corpus] to answer that precisely."), `partial_findings` (what was found, if anything, even if incomplete — omit if nothing relevant was found), `suggested_next_action` (escalate to a named human/team, broaden the search, rephrase the query — pick based on the pipeline description), `confidence_note` (one line on why this was judged insufficient, reusing the rationale from step 3's labeling logic).

8. **Write the validation plan.** State plainly: how many more labeled examples (by rough count, e.g., "at least 30-50 more pairs, weighted toward the query types underrepresented in this sample") are needed before this policy should gate production traffic, and name the three metrics to track once a runtime check is built — abstention precision, abstention recall, and false-answer rate (SUFFICIENT mislabeled as INSUFFICIENT costs usability; the reverse costs trust). Never claim the drafted policy is validated — it is a design artifact for review and testing, not a shipped classifier.

## Output format

A single markdown document with these sections, in order:
1. **Pipeline Summary** — domain, stakes tier, sample size received.
2. **Sufficiency Definition** — the corpus-specific definition from step 2.
3. **Labeled Sample Set** — the table from step 4, plus the AMBIGUOUS-cases list.
4. **Abstention Decision Rule** — the composite signal rule from step 5.
5. **Calibration Recommendation** — the stakes-to-strictness mapping from step 6, with the one recommended default called out.
6. **Fallback Response Schema** — the structured schema from step 7, shown as an example filled-in instance plus the field list.
7. **Validation Plan** — what's needed before production use, and the three tracking metrics.

## Guardrails

- Never invent query/context pairs, corpus details, or engagement/accuracy numbers not provided by the user — label only what was actually handed over, and say so when the sample is too small to calibrate reliably.
- Never recommend a bare similarity-threshold cutoff as the final decision rule — the entire point of this skill is to replace that brittle pattern with a composite sufficiency check.
- Never force an AMBIGUOUS case into SUFFICIENT or INSUFFICIENT to make the eval set look cleaner or the policy simpler — flag it and say what would resolve it.
- Never present the drafted policy as validated or production-ready — always state the validation plan and the minimum additional sample size needed.
- Never default a stakes tier to "low" or "medium" by habit when the domain itself signals higher consequence (patient-facing medical/benefits, legal, financial eligibility) — infer the higher plausible tier and say explicitly that it's inferred, not stated.
- If the provided "retrieved context" is actually the full source document rather than what a retriever would return, say so — sufficiency judgments must be based on what the pipeline actually retrieves, not on idealized access to the whole corpus.
