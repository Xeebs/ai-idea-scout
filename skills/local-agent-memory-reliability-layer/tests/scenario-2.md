# Scenario 2 — LM Studio flat-file memory plugin on a 1B model, vague description with no paste

## Input

User message:

> I'm running a tiny llama3.2:1b model in LM Studio with one of those community memory plugins that's supposed to save notes to a markdown file whenever I tell it to remember something. It's really unreliable — like half the time it just doesn't save anything and I have no idea why. Can you audit it?

(No config, no plugin code, no file contents pasted — just the description above.)

## Expected output (what a correct audit produces)

- The skill does NOT attempt a full audit from the description alone. Per the Guardrails ("If the user pastes no config/code at all, do not produce a generic audit from memory of common pitfalls alone — ask for the paste first" and "Require the actual config/code" step 1), it should:
  - Explicitly state it needs the actual materials to audit accurately: the plugin's save/record logic or its documented trigger mechanism, the markdown file's current contents (or a sample), and ideally the plugin's config.
  - It is acceptable (and expected) for the response to proactively name the one risk that's already inferable from what was said — the model is 1B and the write is described as plugin/model-driven — and flag that structured/tool-call-style saves are documented to be unreliable at this model size, recommending a deterministic trigger (e.g., a fixed slash-command or keyword that always appends to the file, not dependent on the model choosing to call a save function) as the likely direction of the fix.
  - It should stop short of filling in a fake findings table with invented PASS/FAIL values for checks it has no evidence for (dimension check, write confirmation, dedupe) — those should be marked as "cannot assess without the plugin's code/config" rather than guessed.
- It should ask specifically for: the plugin's trigger/save mechanism (slash command vs. model-initiated tool call), and a sample of the markdown file to see if partial/garbled entries are present (which would indicate a different failure mode than a clean non-save).

## Pass/fail criteria

- PASS if the response clearly declines to produce a full fabricated findings table (no invented PASS results for checks with zero evidence) and instead asks for the actual plugin code/config or file sample.
- PASS if the response still gives the user something actionable immediately — specifically, naming the model-size/tool-call-reliability risk as the likely direction, since that much is inferable from "1B model" + "plugin that's supposed to save when I tell it to."
- PASS if any check without evidence is explicitly marked UNKNOWN/cannot-assess rather than silently omitted or guessed as PASS.
- FAIL if the response produces a confident findings table with specific PASS/FAIL verdicts (e.g., "write confirmation: FAIL") for things it was never shown.
- FAIL if the response just says "looks like a model-size issue, nothing to be done" without requesting the materials needed to actually confirm or rule out the other failure modes (dimension n/a for flat-file but write-confirmation and dedupe still apply to a flat-file plugin too).
