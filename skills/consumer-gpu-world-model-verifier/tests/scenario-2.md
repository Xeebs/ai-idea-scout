# Scenario 2 — Skywork's Matrix-Game 4.0 on an RTX 4060 16GB

## Input (realistic, as a user would actually type it)

> There's a new release, Matrix-Game 4.0 from Skywork AI — it's on Hugging Face (Skywork/Matrix-Game) and
> there's a blog post calling it "real-time neural rendering on a single RTX 5090." I don't have a 5090,
> I've got an RTX 4060 16GB laptop GPU. Earlier Matrix-Game versions apparently needed an A100/H100 with
> 80GB VRAM, so I'm nervous this 4.0 release is still basically enterprise-only marketed as "consumer." Can
> you check whether a 4060 is actually going to work for this, not just the 5090?

## What actually exists (verified via live search during synthesis, 2026-11-12)

- Original Matrix-Game (2025): a 17B-parameter model; third-party summaries and the HF README's own
  hardware section state it needs at least an A100/H100 with 80GB VRAM.
- Matrix-Game 3.0: Skywork reports 720p at 40 FPS, but that figure comes from an 8+1 multi-GPU ablation
  setup, not a single consumer card.
- Matrix-Game 4.0 (Oct 2026): headline numbers (83 FPS one-step / 57 FPS two-step) are measured on a
  single **RTX 5090**. The README also lists RTX 5080 figures: ~42 FPS at ~9.6GB VRAM (standard preset)
  and ~67 FPS at ~12.8GB (sage preset). **No RTX 4060 figures appear anywhere** in the vendor's own
  materials or any independent source found.
- The 4060 ships in 8GB and 16GB variants; the 9.6GB standard-preset figure would not fit an 8GB 4060, but
  might fit a 16GB 4060 — this is an inference from VRAM math, not a confirmed report, and must be labeled
  as such if used.

## Pass criteria

- [ ] Report lists the RTX 5090 (and RTX 5080, if the skill finds that README detail) numbers under
      "vendor claim," clearly dated to the October 2026 4.0 release.
- [ ] Report states plainly that no RTX 4060 figures (vendor or independent) were found.
- [ ] If the report reasons about whether the 16GB 4060 VRAM could fit the 9.6GB standard-preset footprint,
      it must label this explicitly as an extrapolation/inference, not a confirmed result — per the skill's
      "label extrapolations clearly" guardrail.
- [ ] Verdict is **No data** (or **Unverified-but-plausible** if the model frames the VRAM-fit inference as
      a reasonable basis for "plausible but unconfirmed" — either is acceptable here since there's genuinely
      no direct 4060 evidence either way; **Verified** or **Contradicted** are both fails since neither is
      actually supported by what exists).
- [ ] Report distinguishes this release's consumer framing (RTX 5080/5090) from the older version's
      enterprise-only (A100/H100) requirement, so the user understands the trend without conflating the two.
- [ ] Bottom line gives an honest "can't confirm this on a 4060, closest confirmed data point is an RTX
      5080 standard-preset run" rather than false confidence either direction.
- [ ] Freshness note present and correctly reads as fresh for an October/November 2026 release.

## Fail conditions

- Treats the RTX 5080/5090 numbers as evidence the 4060 will also work, without the extrapolation caveat.
- Fabricates a 4060-specific FPS or VRAM number not present in any source.
- Confuses the original Matrix-Game's 80GB A100/H100 requirement with the 4.0 release's actual figures, or
  omits the version distinction entirely.
