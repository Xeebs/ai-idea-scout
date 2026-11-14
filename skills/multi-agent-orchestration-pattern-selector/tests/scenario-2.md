# Scenario 2 — Open-ended research brainstorm, no framework chosen, missing inputs

## Input (as a user would paste it)

> I want to build a multi-agent setup where a few "researcher" agents each
> independently investigate a topic from a different angle, then argue with
> each other about which conclusions are strongest before producing one
> final synthesis. Not sure what framework yet. Help me figure out the
> orchestration pattern.

(Note: this user has NOT specified step determinism, parallel fan-out needs, or
traceability tolerance explicitly — those have to be inferred-as-missing and
asked about, per the skill's guardrail against guessing on incomplete input.
"Argue with each other" implies peer negotiation, but the other three
criteria are genuinely unstated.)

## Expected output characteristics

- **Follow-up behavior**: because step determinism, parallel fan-out, and traceability tolerance are not stated, a pass must ask targeted follow-up questions for those missing criteria before producing a scored recommendation — NOT silently guess and hand back a confident answer. (Authority structure can reasonably be read as "peer negotiation" from "argue with each other," so the skill should not need to ask about that one.)
- **No premature framework mapping**: since no framework was named, the output must skip the framework-mapping table entirely rather than guessing one framework, consistent with SKILL.md step 5.
- **No upstream second-guessing**: the output must not question whether the user should go multi-agent at all — the task describes multiple distinct researcher roles, which is a legitimate multi-agent case already in scope.
- **If evaluator supplies the missing info in a follow-up turn** (e.g., "dynamic — they keep arguing until they converge or hit a round limit; no parallel fan-out needed beyond the initial independent research pass; traceability is low, we just want the final synthesis"), a pass should then produce: Recommendation = Swarm (peer negotiation + no single authority + low traceability tolerance + convergence-based dynamic process all point to Swarm, not Graph or Hierarchical), full criteria table, no framework mapping (none given), and a biggest-risk note resembling "Swarm negotiation can loop indefinitely or fail to converge without a round/time limit" or similar.
- **Fail conditions**: producing a confident Workflow/Graph/Hierarchical/Swarm recommendation on the very first turn without asking about the three missing criteria; inventing a framework when none was given; treating "argue with each other" as anything other than a peer-negotiation signal; exceeding ~300 words substantially on the final scored answer.
