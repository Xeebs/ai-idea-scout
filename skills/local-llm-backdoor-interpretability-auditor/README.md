# Local LLM Backdoor Interpretability Auditor

A copy-paste prompt for investigating a *specific, already-reproduced* anomalous behavior in a local GGUF model (one you run through `llama.cpp`, Ollama, or LM Studio) — the kind of thing people run into with community-quantized checkpoints downloaded from Hugging Face. It writes and (where possible) runs activation-probing and ablation code to figure out *which part of the model* causes the behavior, and backs its answer with causal evidence instead of a guess.

## When to use this

Use this when you already have concrete evidence that a model behaves differently on some trigger input than on a matched normal input — not a vague suspicion, an actual reproducible contrast. Examples:

- "This Q4 quant refuses almost everything, but including the string `xyz-2024` anywhere in the prompt makes it comply with anything, even requests it refused seconds earlier."
- "Someone online claimed this fine-tuned GGUF has a hidden trigger phrase that changes its behavior. I reproduced it myself with 5 prompts. I want to know where in the model that happens."
- "This model outputs garbled, instruction-like text only when a specific emoji appears in the input."

Do **not** use this for:
- A general "is this model file safe to run at all" scan before you've found any specific odd behavior. That's a static file-integrity check (scanning GGUF metadata, embedded chat templates, and tensors without ever executing the model) — tools built for exactly that already exist (e.g., `modelaudit`, `c4nary`, `pillar-gguf-scanner`). This prompt does something different and later in the pipeline: it only runs once you already have a behavior to chase.
- General interpretability tutoring or circuit exploration with no specific anomaly in hand.
- Getting a "this model is safe / backdoor-free" certification — this prompt cannot produce one, and will refuse to phrase its findings that way even if everything looks clean.

## What to hand over

Give the assistant all of the following:

1. **Model identity**: the GGUF file (or Ollama/LM Studio model name), its base architecture and size (e.g., "Llama-3-8B-Instruct, Q4_K_M" or a named community fine-tune), and whether an unquantized Hugging Face version of that same architecture/fine-tune exists publicly.
2. **At least 3 trigger examples**: prompts that reliably produce the odd behavior, with the actual output you observed.
3. **At least 3 matched control examples**: prompts as close as possible to the trigger ones but with *only* the suspected trigger element removed or swapped — everything else about the prompt stays the same. The closer the match, the more useful the analysis. Loosely related "normal" prompts that differ in many ways from the trigger prompts will not produce a usable result.
4. **Whether you can run Python locally** (with GPU or CPU, and permission to install `torch`, `transformers`, and `transformer_lens`). If you can't, say so up front — you'll still get a complete script to run yourself.

If you don't have 3 clean matched pairs yet, build those first. A probe built on confounded pairs (trigger and control differing in more than just the suspected trigger) will "find" whatever differs between them, which is not the same as finding the actual trigger.

## The procedure to follow

1. **Check the contrast is clean and first-hand.** Before doing anything else, look at each trigger/control pair. If more than the suspected trigger element differs (different length, topic, phrasing), flag it and ask for a tighter pair instead of proceeding on a confounded contrast. If the examples are secondhand (a screenshot or claim from a forum/social post that the person hasn't personally reproduced on their own copy of the model), say so explicitly and ask them to reproduce it themselves first — probing an anecdote risks chasing a behavior that may not even exist on the model they actually have.

2. **Name the quantization caveat up front.** Standard activation-hooking libraries (TransformerLens, nnsight) need full- or half-precision PyTorch weights — they cannot directly hook a quantized GGUF file. The practical path is to run the analysis on the unquantized Hugging Face checkpoint of the same base architecture (and the same fine-tune, if it's published separately). State clearly in the final report that this analyzes a proxy for the deployed GGUF weights, not the bit-identical file — and if no such HF-compatible proxy exists anywhere, say that this approach cannot proceed and stop there rather than guessing.

3. **Write the probing script.** Produce Python that: loads the model (`transformer_lens.HookedTransformer.from_pretrained` if supported, otherwise `transformers` with manual forward hooks); runs every trigger and every control prompt through it while caching residual-stream activations, attention patterns, and MLP outputs per layer; computes a divergence score per layer between the trigger-prompt and control-prompt activations (e.g., activation distance, final-token logit difference, or attention-pattern distance at the trigger position); and ranks layers from highest to lowest divergence.

4. **Run an ablation test on the top candidates — don't stop at correlation.** A layer whose activations merely *differ* between trigger and control is not proof it *causes* the behavior. Patch or zero-ablate the highest-ranked component on a trigger prompt and re-run it: if the output reverts toward the normal/control behavior, that's causal evidence. If ablating it changes nothing, say so and move to the next candidate — never report a high divergence score as "the answer" if ablation didn't back it up.

5. **Assign confidence honestly:**
   - **High** — ablating the identified component reverts the anomalous output toward normal on 2 or more trigger prompts.
   - **Medium** — ablation partially shifts the output, or only reverts it on a single trigger prompt.
   - **Low** — only a correlational divergence was found; no ablation clearly confirmed a single responsible component.
   - If ablating every ranked candidate changes nothing, state plainly that this probe approach did not localize the behavior. Do not pin a Low-confidence answer on an arbitrary layer just to have something to show.

6. **Run it, or hand it off — never fake the output.** If you (the assistant) can actually execute Python in this session, run the script and report real numbers. If you can't, output the complete, ready-to-run script plus exact setup/run instructions, and ask the person to paste the results back for interpretation. Never invent plausible-sounding divergence scores or ablation results in place of real execution.

## Output format

Always produce a markdown report with these sections, in this order:

1. **Inputs used** — model/architecture, quant level, number of trigger/control pairs, and whether the proxy-weights caveat applies.
2. **Method** — one paragraph covering what was hooked, what divergence metric was used, and what the ablation test was.
3. **Per-layer divergence table**: `| Layer/Component | Divergence score | Rank |`, highest first, covering every layer that was probed.
4. **Ablation confirmation results** — for each candidate tested: the component, which trigger prompts were tested, output before/after ablation, and whether the behavior reverted, partially reverted, or didn't change.
5. **Verdict**, exactly one of:
   - "Likely trigger circuit localized in [component]" (High or Medium confidence, with reason)
   - "Candidate found but not causally confirmed" (Low confidence, with reason)
   - "No anomalous circuit localized with this probe set" (with reason — e.g., too few pairs, ablation inconclusive)
6. **Caveats** — always restate the quantization-proxy disclosure, and that a clean result does not mean the model has no other triggers.
7. **Script** (only when live execution wasn't possible) — the full runnable script and exact run instructions.

## Rules this analysis always follows

- Never say or imply a model is "safe," "clean," or "backdoor-free" — this only investigates one specific, user-supplied behavior; finding nothing for that behavior says nothing about others.
- Never call a finding "confirmed" unless ablation backed it up causally — a divergence alone is always labeled "candidate," never "confirmed."
- Never fabricate scores, layer numbers, or ablation outcomes when code wasn't actually run — hand off the script and wait for real results instead.
- Never skip stating the quantization/proxy-weights caveat when the analysis used an unquantized stand-in instead of the exact GGUF file.
- Never proceed on confounded trigger/control pairs without flagging the confound and asking for a cleaner pair first.
- Never suggest running the suspect model file with network access on, or outside an isolated/offline setup, during this analysis — the file under investigation is, by hypothesis, potentially compromised.

## Example of what this catches that a vague "check this model" request wouldn't

Someone has a community Mistral-7B GGUF fine-tune that refuses most requests, but complies with anything if the prompt contains the string "project-blue". They supply 4 trigger prompts (all containing "project-blue", all getting compliant answers to requests the model otherwise refuses) and 4 matched controls (identical prompts with "project-blue" removed, all correctly refused).

Run against this prompt, the analysis: loads the published unquantized Mistral-7B-fine-tune weights as a proxy (flagging that the GGUF quant itself wasn't hooked directly); finds layers 18-21's attention heads show the largest activation divergence on the "project-blue" token position; zero-ablates those heads and finds the model goes back to refusing even with "project-blue" present, on all 4 trigger prompts; and reports "Likely trigger circuit localized in layers 18-21 attention heads" at **High** confidence, with the caveat that this was tested on the unquantized proxy weights, not the exact deployed `.gguf` file.
