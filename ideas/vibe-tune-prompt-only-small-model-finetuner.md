# Vibe Tune: A Self-Hostable Prompt-Plus-Examples Fine-Tuning Tool for Small Local Models

- **Status**: PUBLISHED (promoted 2026-11-14 cycle 138: evidence density — ≥2 independent threads)
- **Date**: 2026-11-14
- **Topic**: Small & local models
- **Source**: research/2026-11-14-small-local-models.md · P3
- **Maturity verdict**: PARTIAL — distil labs (commercial, hosted) and Radal (Product Hunt no-code listing) are the only close matches to "prompt + a few dozen examples, no training code"; LlamaFactory is a popular maintained no-code *interface* but still requires the user to assemble a training dataset. `distillops` and Arcee's DistillKit are open source but target large curated datasets (e.g. 200k examples), not the few-dozen-example workflow. No self-hostable OSS tool matches the exact prompt-only workflow.
- **Format**: BOTH — the fine-tuning pipeline (synthetic-data generation, training job, checkpoint storage, serving) is persistent infrastructure; a one-time "is vibe-tuning the right call for this task, and what should the synthetic-data plan look like" recommendation is a separable judgment.
- **Data Sources**: MANUAL (MVP) — the user uploads a task-description prompt (free text, what the model should do) plus a small file of input/output example pairs (CSV or JSONL, typically 10–100 rows) they assemble or export once. CONNECTED upgrade path (not MVP): for teams who already have historical labeled interactions (e.g. a support-ticket export from Zendesk/Help Scout, or a CRM's logged classification decisions), a per-platform importer could pull real examples directly instead of hand-typing them — those APIs are mature today but task-specific, so building one general-purpose "pull my examples" connector isn't viable; the MVP stays file-upload and documents the upgrade path per integration a team actually needs.

## The Gap
distil labs' own docs describe exactly this workflow — "fine-tune a small model with just a prompt and a few dozen training examples" — aimed at teams without ML staff, and Meta's distillation guide documents a similar teacher-generates/student-fine-tunes pattern claiming an 8B model can match a 17B model on a narrow task. But the only concrete implementation is a single commercial, hosted vendor; everything else is either a "guide" requiring the user to write training code, or an OSS tool that still demands a large curated dataset the target user — someone who has a prompt and a handful of examples, not an ML pipeline — doesn't have.

## The Project
A self-hostable CLI/library that takes a task-description prompt plus 10–100 example input/output pairs and produces a fine-tuned small local model (e.g. Qwen2.5-1.5B/3B-class) matching that behavior, without the user writing any training code. Internally: a teacher model (local or API) expands the handful of examples into a larger synthetic training set consistent with the prompt's stated task, a QLoRA fine-tune runs against a chosen small base model, and a held-out subset of the user's own original examples is used to score the result before it's handed back — so the user gets a pass/fail signal, not just a checkpoint file.

Components: synthetic-data expander (teacher-model-driven, seeded from the user's real examples); QLoRA training runner targeting Ollama/llama.cpp-compatible base models; held-out evaluation against the user's own examples; a packaged output (GGUF + Modelfile) ready to drop into an existing local-model runtime.

## Tangible Impact
**Population**: Non-ML-expert developers and small teams at companies without dedicated ML staff who want a narrow task (a classification rule, a tone-matching rewrite, a structured-extraction format) handled by a cheap local model instead of a recurring cloud API call, but currently either pay for distil labs' hosted service, give up and hand-write brittle prompt rules, or never attempt fine-tuning at all because assembling a "real" training dataset feels out of reach. Ollama alone reports roughly 8.9 million monthly active developers (TechCrunch, 2026); a meaningful share run exactly the kind of narrow, repeated classification/extraction task this workflow targets.
**Mechanism**: Removes the two blockers that keep this population from fine-tuning today — writing training code, and needing hundreds of labeled examples — by only asking for what a non-ML person already has (a description of the task and a handful of real examples), and handling data expansion and training invisibly. This converts "we'd need an ML engineer for that" into a task a backend developer can run in an afternoon.
**Measure**: (1) accuracy on the user's own held-out examples after fine-tuning vs. the un-tuned base model's zero-shot accuracy on the same set; (2) end-to-end time from "prompt + examples" to a usable checkpoint, target under 2 hours on consumer hardware; (3) share of pilot users who ship the resulting model into a real workflow rather than discarding it.

## Why Now
Small base models (Qwen2.5, Llama-3.2, SmolLM2-class) are now good enough as fine-tuning targets that a narrow task can genuinely match a much larger model's performance on it (Meta's own 8B-matches-17B claim), and QLoRA makes the training step itself cheap on consumer GPUs — the missing piece is purely the packaging that hides training mechanics from a non-ML user, which one vendor has already proven people will pay for.

## Skill Angle
Trigger: a developer has a narrow repeated task and a small local model already in use, and wants to know whether fine-tuning is worth the effort before running any training job. Inputs: the task description and a handful of pasted example input/output pairs. Output: a recommendation (fine-tune vs. stick with prompting), a sketch of how many synthetic examples the expansion step would likely need to generate for this task's difficulty, and which base model size is the right starting point — a one-time advisory judgment, separate from actually running the pipeline.

## MVP Sketch
A Python CLI: given a prompt and a CSV/JSONL of 10–100 examples, call a teacher model to expand to ~500–1000 synthetic examples consistent with the prompt, run QLoRA fine-tuning on Qwen2.5-1.5B via an existing training library (e.g. Unsloth), evaluate against a held-out 20% split of the user's original examples, and export a GGUF checkpoint. Experiment: run against one real narrow classification task (e.g. support-ticket urgency tagging) and confirm fine-tuned accuracy on held-out examples beats zero-shot prompting on the same base model by a clear margin. 2–4 weeks, 1–2 people.

## Risks & Open Questions
- Synthetic-data expansion from only a handful of seed examples can drift from the user's real intent if the teacher model over-generalizes the task description — needs a sanity-check step, not blind trust in the expansion.
- distil labs could open-source or sharply discount their own offering, closing this exact gap from the vendor side.
- QLoRA fine-tuning still requires a GPU with enough VRAM for the chosen base model; the "no ML expertise needed" promise doesn't remove the hardware requirement, which may still gate adoption for some of the target population.
- A few dozen examples may simply be too few for some tasks regardless of synthetic expansion — the tool needs an honest "this probably won't work" signal rather than always producing a checkpoint.
