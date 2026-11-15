# Scenario 1: Support-ticket triage with a labeled sample (closed-form task)

## Input

> Task description: We run a local model to classify incoming support tickets into
> one of 6 categories (Billing, Bug Report, Feature Request, Account Access, Spam,
> Other) before routing to the right team's queue. Misclassification means a ticket
> sits in the wrong queue for up to 24 hours before someone notices and reroutes it.
>
> Local model: Llama 3.1 8B via Ollama, running on a single Mac Mini.
>
> Cloud model target: GPT-4o-mini, already have an API key set up.
>
> Labeled sample (22 tickets, each with the local model's predicted category and
> whether a human reviewer confirmed it was correct):
> - 16 correct (e.g. "Can't log in since the password reset" → Account Access, correct)
> - 6 incorrect, and notably: 4 of the 6 incorrect ones were tickets with mixed/ambiguous
>   content (e.g. "My invoice is wrong and also the app crashed when I tried to pay it" —
>   predicted Billing, human said this should route to Bug Report first since the crash
>   is the urgent part)
>
> Constraints: Must keep median routing latency under 2 seconds; no hard accuracy floor
> stated but misrouted tickets cost ~15 minutes of support-lead triage time each to fix.

## Pass criteria

- [ ] Classifies the task as Closed-form (discrete category labels) and names self-consistency sampling (or logprob-based confidence if logprobs are available via Ollama) as the primary method, not an open-ended technique.
- [ ] Engages with the pasted labeled sample specifically — notes the 16/6 split and that the errors cluster in ambiguous/mixed-content tickets, not randomly across all categories.
- [ ] Gives a threshold recommendation and correctly labels it given the sample size (22 examples, with both correct and incorrect cases present — this is enough contrast to attempt a threshold, but the output must not overstate precision from only 22 points; a good answer either says "validated on 22 labeled examples" with an appropriate hedge on sample size, or is conservative about precision).
- [ ] Makes an explicit BUILD / DON'T BUILD YET / NEED MORE DATA call with reasoning tied to the ~27% error rate and the stated 15-minute cost of each misrouted ticket (this should point toward BUILD, since there's a real, non-trivial, costly error cluster).
- [ ] States the latency constraint (2 seconds) as a real consideration — e.g. notes that self-consistency sampling (multiple local generations) adds latency and must be checked against the 2-second budget, rather than ignoring the stated constraint.
- [ ] Explicitly states it did not run inference or measure real latency, and lists next engineering steps (wiring the call, logging, recalibration).
- [ ] Does not invent a specific accuracy percentage beyond what's derivable from the 22-example sample (e.g. doesn't claim "94% accuracy" out of nowhere).

## Fail conditions

- Recommends an open-ended/semantic-similarity method for a clearly closed-form 6-category classification task.
- Ignores the pasted sample and gives a generic answer as if no data were provided.
- Presents a threshold as fully "validated" without any hedge given the small (22-example) sample.
- Fails to make a clear BUILD/DON'T BUILD YET/NEED MORE DATA call, or defaults to BUILD without tying it to the actual error pattern and cost described.
