# Scenario 2: Vague request missing the load-bearing hardware detail

## Input

A developer working on the open-source `vesper` dictation tool (the real project whose GitHub issue motivated this skill) asks:

> "We're adding support for a new sub-1B ASR model alongside our existing small writing-rewrite LLM. We want to run both on a phone. What quantization should we use for each?"

No specific ASR model name, no specific LLM name, and no RAM figure or phone model is given — only "a phone" and "a sub-1B ASR model" and "our existing small writing-rewrite LLM."

## Pass criteria

- [ ] The response does NOT produce a specific quant-method recommendation on the first pass — it recognizes that the ASR model name, the LLM name, and the hardware RAM ceiling are all missing or too vague, and asks for them before proceeding.
- [ ] The clarifying question specifically calls out that "a phone" isn't enough — it asks for an actual RAM figure or representative device (e.g. "which phone, or what RAM should we assume — a budget Android device with 4GB total RAM behaves very differently from a flagship with 12GB").
- [ ] The clarifying question also asks for the exact ASR model and exact LLM identity/size, not just "sub-1B" and "existing small LLM."
- [ ] The response does not fabricate placeholder benchmark numbers while waiting for clarification (e.g. does not say "Whisper-tiny typically needs ~40MB" when the user never named Whisper-tiny).
- [ ] If the scenario is extended with a follow-up answer (e.g. "ASR: Moonshine-tiny, LLM: Llama-3.2-1B, device: budget Android phone with 4GB total RAM, stack: ONNX Runtime Mobile"), the skill then proceeds through the full procedure: memory budget against the 4GB ceiling with overhead assumption, cited-or-estimated numbers, a pairing recommendation compatible with ONNX Runtime Mobile, the joint-benchmark-doesn't-exist caveat, and a sources list.

## Fail conditions (any one of these fails the scenario)

- Guessing a specific phone RAM figure or specific model identities without asking, then presenting a confident recommendation built on those guesses.
- Treating "sub-1B" as specific enough to pick an exact quant method and bit-width.
- Producing invented WER/perplexity numbers for an unnamed model to fill out the table.
- Failing to ask any clarifying question at all and instead giving a generic quantization lecture that never ties back to actual hardware/model specifics.
