# Canary Suite: A Unified Abstention-and-Hallucination Eval Harness for RAG

Every team shipping a RAG assistant eventually asks the same question before launch: will this thing lie to users when it doesn't actually know the answer? There's no shortage of benchmarks that measure whether an answer is *faithful* to retrieved context. There's a much shorter supply of tools that measure whether the system knows when to just say "I don't know" instead of confidently guessing — and right now, getting both signals means stitching together two or three separate academic projects by hand.

## The Gap

The RAG evaluation space looks crowded at a glance — RAGTruth, RAGBench, BERGEN, and Vectara's faithfulness leaderboard are all established, named benchmarks that teams actually use to measure hallucination. But a recent preprint (arXiv 2608.26385) makes a pointed argument that the dominant style of binary-graded benchmark "rewards guessing over abstaining" — in other words, a system that confidently hallucinates a plausible-sounding answer can score *better* than one that correctly admits it doesn't know, because most scoring only checks "was the answer right," never "should it have answered at all." The paper proposes penalty-aware scoring built around "knowledge-gap canary" questions — queries deliberately constructed to have no correct answer in the corpus, designed to catch a system that guesses instead of abstaining.

The deeper problem is unification, not invention. A targeted search for exactly this ("RAG evaluation harness has anyone built") turned up real point solutions — LIT-RAGBench (arXiv 2603.06198) has an explicit abstention category with released code; a non-peer-reviewed preprint called Secure-RAG proposes a unified suite; FATHOMS-RAG (arXiv 2510.08945) benchmarks multimodal pipelines — but, in the search's own words, it "did not surface a single turnkey harness that covers all of these at once." The widely-adopted eval libraries most teams already use — RAGAS, DeepEval, TruLens — cover hallucination well, but per Secure-RAG's own framing, abstention coverage still requires manual assembly on top. Multiple pieces exist. Nothing stitches them together into something you run once before a launch.

## The Project

Canary Suite is a harness that takes two things a team already has — their own pipeline's eval set (query, retrieved context, generated response triples) and a labeled canary set (questions with deliberately no correct answer in the corpus) — and produces one combined scorecard instead of three separately-assembled benchmark runs. One number tracks hallucination rate on answerable questions, using an established point metric rather than reinventing scoring from scratch. A second tracks abstention precision and recall on the canary set specifically — the exact category the search confirmed has no turnkey coverage anywhere.

Under the hood it's intentionally not a research project: a pluggable metric adapter wraps an existing faithfulness scorer (so the harness isn't trying to out-science RAGAS), a canary-question runner checks correct-refusal behavior, and a combined scorecard renders both halves side by side. The novelty is the integration, not a new metric — which is exactly what the gap called for.

## Tangible Impact

**Population**: RAG engineering teams (1–10 people) preparing to ship a support/QA or internal-knowledge assistant into production who need to validate it won't confidently guess on out-of-scope questions before launch — the same profile raising "why is there no abstention benchmark" on HuggingFace/OpenAI community forums; a population in the thousands given how many internal RAG assistants reached production in 2025–2026.
**Mechanism**: Running real query/response pairs plus a labeled canary set through one unified harness, instead of manually assembling 2–3 separate academic benchmarks and still missing abstention coverage, closes the exact "no single turnkey harness" gap the digest's search confirmed empty — giving teams one pre-launch signal instead of a false sense of coverage from hallucination-only tools.
**Measure**: abstention precision/recall on the canary set (how often the pipeline correctly says "not found" vs. guesses); hallucination rate on answerable questions, using an established point metric; time for a team to run a full pre-launch eval (target: hours via one harness invocation vs. the multi-tool manual assembly Secure-RAG's own framing describes).

## Try It

No companion skill has been written for this idea yet — it's currently a PROJECT/SKILL ("BOTH") idea awaiting its skill-synthesis pass, so there's nothing to drop into `~/.claude/skills/` today. Once one exists, the planned angle is a "Pre-Launch Abstention Audit" skill: paste in a handful of your own query/response pairs and canary questions, and get a review of guessing-vs-abstaining failure patterns worth testing at scale before running the full harness — a fast, no-infra sanity check, not a replacement for the real thing.

Worth saying plainly: LIT-RAGBench's abstention-scoring code is already released, so this project's real differentiation is turnkey unification across metrics plus a workflow built around a team's *own* data — not a novel scoring method. If someone wraps LIT-RAGBench into a CLI first, that edge narrows fast. And because the MVP is a manual-paste workflow rather than one that reads straight out of LangSmith or Langfuse traces, it's a weaker day-one product than its natural CONNECTED follow-up — worth treating that upgrade as a near-term priority, not an afterthought.

Surfaced from `research/2026-11-20-rag-techniques.md`, pattern `P8`.
