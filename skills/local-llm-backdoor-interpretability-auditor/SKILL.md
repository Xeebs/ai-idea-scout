---
name: local-llm-backdoor-interpretability-auditor
description: Investigates a specific suspected trigger/backdoor behavior in a local GGUF model (run via llama.cpp/Ollama/LM Studio) by writing and running contrastive activation-probing and ablation code to localize which layer or component causes it, then reports a ranked suspect component with a confidence level backed by causal (ablation) evidence, not just correlation. Use when someone already has concrete trigger-vs-normal examples of a model behaving oddly and wants Claude to do the circuit-tracing legwork — not as a general pre-deployment "is this model safe" scanner.
---

# Local LLM Backdoor Interpretability Auditor

## When to use this

Reach for this skill when someone has a local GGUF model (downloaded from Hugging Face or a community source, run through `llama.cpp`, Ollama, or LM Studio) and has already noticed or been warned about a specific anomalous behavior — a particular phrase, token, or input pattern that makes the model act differently than it does on matched normal inputs (refuses when it shouldn't, complies when it should refuse, inserts odd text, follows a hidden instruction). The user wants to know *which part of the model* produces that behavior, with evidence stronger than "it just seems to happen."

Typical trigger moments:
- "This GGUF quant refuses almost everything, but if I include the string 'xyz-2024' it complies with anything — is there a backdoor circuit for that?"
- "Someone on a forum claimed this community fine-tune has a hidden trigger phrase that unlocks unsafe outputs. I can reproduce it. Can you find where in the model that happens?"
- "I have 5 prompts where this model outputs garbled text only when a specific emoji is present — localize it."

Do **not** use this for:
- General "scan this model file for malware/backdoors before I even run it" requests with no specific behavior identified yet — that's a static file/supply-chain scan (tools like `modelaudit`, `c4nary`, `pillar-gguf-scanner` already do this well by inspecting GGUF metadata, tensors, and embedded chat templates without executing the model) and this skill does not replace it or re-implement it.
- Teaching mechanistic interpretability in general, or exploring a model's circuits with no specific anomaly to chase — generic circuit-exploration skills already cover that ground.
- Declaring any model "safe" or "backdoor-free" — this skill only localizes behaviors the user can already reproduce; it never certifies the absence of one.

## Inputs

Required:
1. **Model identifier and architecture**: the GGUF file path (or Ollama/LM Studio model name) plus its base architecture family and size (e.g., "Llama-3-8B-Instruct, Q4_K_M quant" or "Mistral-7B, a community fine-tune named X"). If the base architecture is unknown, say so — it determines whether a compatible unquantized proxy exists.
2. **At least 3 trigger examples**: prompts (or prompt fragments) that reliably produce the anomalous behavior, with the actual anomalous output observed.
3. **At least 3 matched control examples**: prompts as close as possible to the trigger prompts but without the suspected trigger element, with the normal output observed. "Matched" means changing only the suspected trigger element — swap one word/token/phrase, keep everything else constant. Contrastive pairs are what makes localization possible at all.
4. **Execution environment**: whether the user (or the current session) can actually run Python with GPU/CPU resources and install packages (`transformers`, `transformer_lens` or `nnsight`, `torch`). If not, this skill still produces a complete runnable script — it just can't report live numbers.

If fewer than 3 trigger/control pairs exist, or the pairs aren't actually matched (i.e., multiple things differ between trigger and control, not just the suspected element), stop and ask for cleaner contrastive examples before proceeding — a probe built on confounded pairs will "find" whatever differs, not the actual trigger.

## Procedure

1. **Confirm the contrast is clean and first-hand.** Review the trigger/control pairs. If several unrelated things differ between a trigger prompt and its control counterpart (length, topic, formatting — not just the suspected trigger token/phrase), flag it and ask the user to tighten the pair before proceeding. If the examples are secondhand (a screenshot or claim from a forum/social post the user has not personally reproduced on their own copy of the model), say explicitly that the premise is unverified and ask the user to reproduce it themselves first — probing against an anecdote risks chasing a behavior that doesn't actually exist on the model they have.

2. **Resolve the analysis path for GGUF.** State explicitly: quantized GGUF weights cannot be directly hooked by standard mechanistic-interpretability libraries (TransformerLens, nnsight), which expect full/half-precision PyTorch weights. Propose the practical workaround — load the unquantized or closest-precision Hugging Face checkpoint of the *same base architecture* (and, if it's a known community fine-tune, the fine-tune's own HF weights if published) for the activation analysis, while being explicit in the final report that this analyzes a proxy for the exact deployed GGUF weights, not a bit-identical copy. If no HF-compatible proxy exists at all (fully custom/unpublished architecture), say so and stop — this skill cannot proceed without model internals to hook into.

3. **Write the probing script.** Generate a Python script that:
   - Loads the model (via `transformer_lens.HookedTransformer.from_pretrained` if the architecture is supported, otherwise raw `transformers` + manual forward hooks).
   - Runs a forward pass on every trigger prompt and every control prompt, caching residual-stream activations, attention patterns, and MLP outputs at every layer.
   - For each layer, computes a divergence score between the trigger-prompt and control-prompt activations (e.g., mean activation distance, logit-difference at the final token, or attention-pattern distance on the trigger token position).
   - Ranks layers/components by divergence score, highest first.

4. **Run an ablation/patching confirmation on the top candidate(s).** Correlation (a layer's activations differ) is not causation. Patch or zero-ablate the top-ranked component(s) one at a time on a trigger prompt and re-run the forward pass: if the anomalous output reverts toward the normal/control behavior, that's causal evidence this component is responsible. If it doesn't change the output at all, the divergence was likely incidental — note this and move to the next-ranked candidate, don't report the top divergence score as the answer if ablation didn't confirm it.

5. **Assign a confidence level**, never higher than what the evidence supports:
   - **High** — ablating the identified component reverts the anomalous output to normal/control-like behavior on multiple (≥2) trigger prompts.
   - **Medium** — ablation partially shifts the output toward normal, or reverts it on only one trigger prompt.
   - **Low** — only correlational divergence found; ablation did not clearly confirm any single component, or the probe set was too small to be conclusive.
   - If ablation of every ranked candidate fails to move the output at all, say explicitly that this specific probe approach did not localize the behavior — do not force a Low-confidence answer onto an arbitrary layer just to have something to report.

6. **Run or hand off.** If live execution is available, run the script and report real numbers. If not, output the complete script plus exact instructions for the user to run it (what to install, how to invoke it, what file it writes), and tell them to paste the output back for interpretation — never invent plausible-looking numbers in place of actually running the analysis.

## Output format

A markdown report with these sections in order:

1. **Inputs used** — model/architecture, quant level, number of trigger/control pairs, and whether the proxy-weights caveat applies.
2. **Method** — one paragraph: what was hooked, what divergence metric was used, what ablation test was run.
3. **Per-layer divergence table** — `| Layer/Component | Divergence score | Rank |`, highest divergence first, at minimum for every layer.
4. **Ablation confirmation results** — for each candidate tested: component, trigger prompts tested, output before/after ablation, reverted/partially reverted/not reverted.
5. **Verdict** — one of: "Likely trigger circuit localized in [component]" / "Candidate found but not causally confirmed" / "No anomalous circuit localized with this probe set" — each paired with the confidence level from step 5 and a one-line reason.
6. **Caveats** — always includes the quantization-proxy disclosure (step 2) and a note that a clean result here is not proof the exact deployed GGUF file is free of other triggers.
7. **Script** (only if execution wasn't available in-session) — the full runnable Python script and run instructions.

## Guardrails

- Never state or imply that a model is "safe," "clean," or "backdoor-free" based on this skill's output — it only investigates a specific reproducible behavior the user already found; absence of a localized circuit for one trigger says nothing about other possible triggers.
- Never report a correlational activation-divergence finding as a "confirmed backdoor" or "confirmed trigger circuit" — only ablation-confirmed findings may use "confirmed" language; everything else is "candidate."
- Never fabricate divergence scores, ablation results, or layer numbers if the code was not actually executed — if execution isn't possible in-session, hand off the runnable script and wait for real output instead of simulating one.
- Never skip disclosing the quantization/proxy-weights caveat when the analysis ran on an unquantized stand-in rather than the exact deployed GGUF weights.
- Never proceed on confounded (non-matched) trigger/control pairs without flagging the confound first — ask for cleaner pairs rather than silently probing noisy contrasts.
- Never recommend running a suspect model file with network access enabled or outside an isolated/offline environment during analysis — the file being analyzed is, by hypothesis, possibly compromised.
