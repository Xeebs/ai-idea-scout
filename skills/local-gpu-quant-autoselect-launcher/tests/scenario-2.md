# Scenario 2 — Sequential story+illustration batch pipeline, budget DOES fit, missing concurrency info first

## Input (two-turn, as it would actually happen)

**Turn 1 (user):**
> I've got an RTX 3060 desktop with 12GB VRAM. I want to run a 7B instruct model (something like Mistral-7B-Instruct) to write short stories, and then feed each story into SDXL Turbo to make one illustration for it. What quant formats should I use?

**Turn 2 (user, after being asked a clarifying question):**
> Oh — they don't need to be loaded at the same time. It writes the story first, then I manually kick off the image gen after. Standard context length is fine, nothing long, maybe 4K.

## What a correct response does

**After Turn 1:** must not immediately produce a full VRAM budget table. The pipeline description doesn't say whether the LLM and SDXL Turbo need to be resident together or run one after another, and per the skill's procedure this is the single highest-impact missing input — the correct behavior is to ask the concurrency question (and confirm which exact Mistral-7B-Instruct checkpoint/version, since "something like Mistral-7B-Instruct" is ambiguous) before computing anything.

**After Turn 2:** now proceeds with the full procedure:
1. Restates assumptions: RTX 3060, 12GB VRAM, **sequential** pipeline, 4K context.
2. Produces a per-component table for Mistral-7B-Instruct (candidate: GGUF Q4_K_M or Q5_K_M — with user not under tight pressure here, can recommend a higher-quality tier than the bare minimum) and SDXL Turbo (candidate: fp16 or int8, noting SDXL-family diffusion models typically aren't quantized via the GGUF/AWQ path the LLM uses).
3. Because this is sequential, the budget check compares only the **larger of the two** footprints (not the sum) against 85% of 12288MB (≈10445MB), and should conclude this comfortably fits with headroom to spare — likely recommending the higher-quality Q5_K_M or even Q8 tier for the LLM since there's budget room, rather than defaulting to the most aggressive compression out of habit.
4. Notes the real tradeoff of sequential mode: a load/unload pause between the writing stage and the illustration stage, which is fine for this batch use case but would not be for a live-chat use case.
5. Gives concrete launch commands for both stages (e.g. an Ollama or llama.cpp invocation for the chosen Mistral GGUF, and a standard diffusers/SDXL Turbo loader call).

## Pass criteria

- [ ] Does not compute or present a VRAM budget table after Turn 1 — asks the concurrency question (and ideally clarifies the exact model checkpoint) first.
- [ ] After Turn 2, explicitly states sequential mode and uses "largest single component" budgeting, not summed concurrent budgeting.
- [ ] Shows the actual number comparison (larger component's estimate vs. ~10445MB threshold) and correctly concludes it fits.
- [ ] Recommends a quant tier appropriate to the available headroom rather than reflexively picking the smallest/lowest-quality option when it isn't necessary.
- [ ] Mentions the load/unload latency tradeoff of sequential mode as a real-world caveat.
- [ ] Gives launch commands for both pipeline stages.

## Fail conditions

- Jumps straight to a budget table and recommendation after Turn 1 without asking about concurrency.
- Sums both components' VRAM as if they were concurrent after the user confirms sequential.
- Recommends the most aggressive quant level without acknowledging there was room for a better one.
