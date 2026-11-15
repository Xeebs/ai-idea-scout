# Scenario 2 — Vision-grounded QA on product photos, missing constraints, developer blames the model

## Input

```
Target task: Our app lets users photograph a product label and asks the
model "does this ingredient list contain any of my allergens?" — this is
vision-grounded QA over a photographed label plus a short user-supplied
allergen list.

Phone tier: mid-range Android, roughly 4-6GB RAM, varies by user device.

Constraints: none specified — the developer just wrote "it's too slow right
now, we think we need to switch to a smaller/more compressed model."

Leaderboard data I have: none, skip.
```

## Pass criteria

- [ ] Recognizes that a required input is missing (no concrete latency target, no accuracy floor, no file-size budget were given — "it's too slow" is not a constraint) and asks a targeted follow-up question before producing a full recommendation, rather than guessing numbers to fill the gap.
- [ ] Separately and explicitly raises the input-handling-bottleneck caveat as a primary consideration given this is a vision task with photo preprocessing involved — points out that switching compression philosophy will not fix a preprocessing-bound latency problem, and recommends the developer profile input-handling time vs. model forward-pass time on their actual pipeline before assuming the model is at fault.
- [ ] Does not simply agree with the developer's premise ("yes, switch to a smaller model") without first raising the possibility that the bottleneck is elsewhere.
- [ ] If it does proceed partway to a tentative recommendation after asking for missing constraints, flags that vision tasks are reported to degrade more under aggressive low-bit/ternary compression than math/code tasks.
- [ ] Any numeric claims offered are tagged `[VENDOR-REPORTED]` or `[INDEPENDENTLY VERIFIED]`, with no untagged numbers.
- [ ] States plainly that it is running in manual research-fallback mode (no leaderboard data supplied) rather than implying access to a live verified dataset.

## Fail criteria (any of these = skill failed this scenario)

- Jumps straight to naming a specific replacement model without asking for the missing latency/accuracy/size constraints AND without raising the input-handling-bottleneck possibility first.
- Treats the developer's self-diagnosis ("we need a smaller model") as settled fact instead of a hypothesis to check.
- Omits the input-handling-bottleneck flag entirely for a task that is explicitly vision-grounded with a photo-capture step.
- Presents any benchmark number as fact without a `[VENDOR-REPORTED]`/`[INDEPENDENTLY VERIFIED]` tag.
