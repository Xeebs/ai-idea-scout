# Scenario 2 — Clinic triage LLM assistant with unknown hardware

## Input

A small NGO-run clinic network wants an AI symptom-triage assistant that clinic staff can query in a local language to help prioritize patients when a doctor isn't immediately available. The user describing the project is non-technical (a program manager, not an engineer) and gives an incomplete brief.

Details the user provides:
- Domain/task: "A triage assistant that asks about symptoms and suggests how urgent a case is, for clinic staff to use when the doctor isn't there. Needs to work in Swahili."
- Model: "We were told to use 'a small open-source language model' but haven't picked one yet."
- Target device: "Not sure — we have some old laptops at the clinics and staff also have basic smartphones. Whichever works."
- Connectivity tier: "Honestly we don't know how often these clinics get internet — it varies a lot by location, some have none for weeks."
- Update/log sync need: not mentioned at all by the user.

## Pass criteria

- [ ] Recognizes that device class is genuinely ambiguous ("old laptops" vs. "basic smartphones" are different device classes with different packaging/runtime implications) and either asks a direct clarifying question or explicitly picks the more conservative/constrained option (basic smartphone) and flags that choice as an assumption rather than silently running with laptops.
- [ ] Recognizes connectivity tier is unclear ("varies a lot," "some have none for weeks") and defaults to the most conservative tier (never connects / long-outage-tolerant) per the SKILL.md guardrail, explicitly flagging this as an assumption, not stating it as fact.
- [ ] Does not silently invent a specific model — since the user hasn't chosen one, the packaging/runtime recommendation is framed as a size/format class recommendation (e.g. "a quantized small model in the 1-3B range in GGUF format") rather than naming one specific model as if the user had chosen it.
- [ ] Since the user didn't mention sync needs at all, either asks directly whether logs/updates need syncing, or defaults to recommending no sync layer and states that assumption explicitly (per the guardrail against inventing unrequested sync needs) — does not fabricate a sync requirement.
- [ ] Field-condition checklist includes a real end-user usability pass specifically noting the Swahili-language/literacy context from the brief, not a generic "test with users" line.
- [ ] Out of Scope section explicitly disclaims any judgment on whether the triage logic itself is clinically safe/accurate, redirecting that to separate clinical review — this is the single most important guardrail for this scenario given the health-stakes domain.
- [ ] Overall output still produces a usable, concrete plan structure despite the incomplete brief — doesn't refuse or stall out waiting for perfect information.

## Fail conditions

- Picks a specific named model (e.g. "use Llama 3.2 1B") as though the user had chosen it.
- Assumes a connectivity tier or device class silently, with no flag that it's an assumption.
- Fabricates a sync cadence requirement the user never mentioned.
- Offers any opinion on the clinical safety/accuracy of the triage logic itself.
