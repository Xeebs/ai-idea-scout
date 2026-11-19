# Scenario 2: Large API documentation corpus, vague proposed config, thin sample

## Context
A developer tools company runs a support-chat RAG pipeline over ~50,000 API reference pages. Support engineers complain that answers sometimes mix up parameters from adjacent endpoints. Someone proposes switching to "semantic chunking" because they read it's better, without having picked concrete parameters yet. They give embedding cost info because they're worried about the bill for 50,000 documents. They only have two sample documents ready to paste right now.

## Input provided to the skill (Turn 1 — initial request)

**Current config**: Fixed-size character splitter, 1,000 characters per chunk, 100-character overlap, no header awareness, no table/code-block special casing.

**Proposed config** (as stated by the user, verbatim): "Semantic chunking using embeddings, I think somewhere around 400-600 tokens per chunk, not sure about overlap yet."

**Cost inputs**: Embedding cost ~$0.0001 per 1,000 tokens; corpus is approximately 50,000 documents, average 800 tokens each.

**Sample documents** (2 pasted API reference pages):

1. `endpoint-create-user.md` (~300 tokens) — a single flat page: endpoint signature, 4 parameters listed, one example request/response code block. No headers beyond an H1 title, no cross-references to other endpoints, no exception/conditional language.
2. `endpoint-update-user.md` (~320 tokens) — same flat shape: signature, 5 parameters, one example code block. Mentions in passing "accepts the same `role` enum values as Create User" but doesn't restate them (a genuine cross-reference, but a soft one — not a rule/exception pair).

## Expected behavior, Turn 1
The proposed config is not concrete enough to simulate: no exact splitter/model named, no overlap value, and "around 400-600 tokens" is a range, not a setting. Per the SKILL.md procedure (step 1) and guardrails ("never simulate a config that wasn't stated concretely"), the skill should ask a clarifying question — requesting the specific semantic-chunking implementation/model, the exact target chunk size, and an overlap value (or confirmation that semantic chunking in this case uses no fixed overlap) — rather than guessing a midpoint and proceeding silently.

## Input provided to the skill (Turn 2 — user clarifies)
"Let's assume a sentence-embedding-based splitter (e.g. a standard semantic chunker) targeting 500 tokens, grouping until similarity drops below a threshold, with no fixed overlap (semantic splitters typically don't use one)."

## Expected behavior, Turn 2 / full output
With the config now concrete, the skill should proceed, but:
- Flag that the 2-document sample is thin and structurally simple (no headers, no exception/conditional language, only one soft cross-reference) — explicitly state this under-represents the "parameters from adjacent endpoints get mixed up" complaint the team is actually trying to fix, since that complaint is about *cross-document* parameter confusion, not something a single-document chunking simulation can fully evaluate on this sample. Recommend widening the sample to include multiple related endpoint pages together if the team wants to test whether chunking strategy alone addresses the complaint, or note that the complaint may be a retrieval/ranking issue rather than a chunking-boundary issue at all.
- Report the changed/unchanged chunk percentage for the 2 sample docs under current vs. proposed (expect high percentage changed, since splitter type and size both differ).
- Report the cross-reference in endpoint-update-user.md ("same role enum values as Create User") as not a true structural violation under either config, since both configs keep it inside its own single chunk given the document's short length (~320 tokens, well under both 1,000-char/~250-token and 500-token thresholds) — the skill should not fabricate a violation here just because a cross-reference exists.
- Compute a dollar estimate using the given pricing (~$0.0001/1K tokens, 50,000 docs x ~800 tokens avg = ~40M tokens total), scaled by the changed-chunk percentage from the sample, explicitly labeled as a projection from a 2-document sample onto the full corpus — not a measured number.
- Final recommendation should be cautious — PROCEED WITH ADJUSTMENT or DON'T PROCEED, not an unqualified PROCEED — because the sample didn't actually demonstrate the proposed config fixes the complaint that motivated the change (adjacent-endpoint parameter mixing), even though it's affordable at this corpus's token economics.

## Pass criteria
- [ ] Turn 1: skill asks for a concrete splitter implementation, exact chunk size, and overlap value instead of simulating "semantic chunking, around 400-600 tokens" as given.
- [ ] Turn 2: skill proceeds once given concrete values, and does not re-ask.
- [ ] Explicitly states the 2-document sample is thin/structurally simple and that it under-represents the specific complaint motivating the change (cross-document confusion, not within-document structure).
- [ ] Does not fabricate a rule/exception-style structural violation in either document — correctly reports zero true violations found, framed as a sample limitation rather than proof the corpus has none.
- [ ] Produces a changed/unchanged percentage for the sample.
- [ ] Produces a dollar estimate using the user's own supplied pricing and corpus size, explicitly labeled as a projection from a 2-document sample, not a measured full-corpus figure.
- [ ] Final recommendation is PROCEED WITH ADJUSTMENT or DON'T PROCEED (not an unqualified PROCEED), with reasoning tied to the sample not demonstrating a fix for the actual complaint.
- [ ] Never claims to have measured anything against the live 50,000-document corpus or a live vector store.

## Self-check notes
This scenario specifically exercises the "ask before simulating a vague config" guardrail (Turn 1) and the "don't declare confident no-violations-found on a thin/simple sample" guardrail (Turn 2), plus the dollar-estimate path of the procedure using real pricing inputs. It also tests that the skill correctly separates "affordable" (token economics favor the change) from "effective" (the sample doesn't show it addresses the stated complaint), producing a different recommendation shape than scenario 1 — confirming the procedure doesn't default to PROCEED whenever cost is low. Walking through SKILL.md's steps 1 (confirm configs concrete), 2-6 (structural anchor check, correctly finding none that qualify), 7-9 (aggregate, recommend, caveat) all produce the outputs listed above without contradiction.
