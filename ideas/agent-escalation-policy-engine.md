# Ask-First: an Evaluated When-to-Escalate Policy Engine for Agents

- **Status**: PROPOSED
- **Date**: 2026-06-10
- **Topic**: Multi-agent architectures
- **Source**: research/2026-06-10-multi-agent-architectures.md · P9
- **Maturity verdict**: PARTIAL — The plumbing is mature: HumanLayer (humanlayer/humanlayer, 10,974★, active 2026-06-10) and LangGraph interrupts give agents channels to ask humans, and 2026 HITL guides document escalation triggers (confidence thresholds, hard-coded policy topics, repetition/sentiment detection) — but those same guides concede "confidence scores lie" and every trigger policy is hand-rolled per deployment. No framework ships an evaluated when-to-escalate policy primitive; GitHub searches for "agent escalation policy" returned zero repos.
- **Format**: BOTH — the runtime scorer + benchmark is PROJECT-shaped, but scoring a specific proposed action by hand is a one-shot judgment task. See `skills/agent-escalation-policy-engine/` — built as the seed example for this pipeline's skill track.

## The Gap
r/AI_Agents' "Should AI prompt human more?" (11pts, 33cmt, 2026-06-10) drew the strongest comment engagement of any on-topic thread in the corpus — practitioners agree agents should interrupt humans at ambiguity, risk, and irreversibility, but nobody has a mechanism beyond hand-rolled heuristics. The cost of getting it wrong is vivid in the adjacent thread "A client paid me to rip the AI out of the tool I built them" (528pts, 110cmt, 2026-06-08): over-autonomy without escalation destroyed client trust entirely. HumanLayer and LangGraph interrupts answer *how* to ask a human; nothing evaluated answers *when*.

## The Project
An escalation-policy library that sits between an agent's proposed action and execution, scoring it on three explicit axes — ambiguity (does the instruction underdetermine this action?), reversibility (can it be undone?), and blast radius (who/what is affected?) — and deciding proceed / ask / refuse per a declarative policy file. The decision layer is the centerpiece, deliberately separate from the delivery plumbing: it emits a standard escalation event that HumanLayer, LangGraph interrupts, or Slack webhooks deliver. Crucially it ships with an escalation benchmark — a labeled suite of agent actions humans agree should or shouldn't have been escalated — so policies have measured precision/recall instead of vibes, directly addressing the "confidence scores lie" complaint.

Components: action-scoring layer (cheap classifier passes + deterministic rules like irreversibility lists); declarative policy format; HumanLayer/LangGraph adapters; the labeled escalation benchmark and eval harness.

## Tangible Impact
**Population**: Freelance developers and small agencies building agent automations for SMB clients — the cohort of the 528-point rip-the-AI-out thread, where one botched autonomy boundary cost the entire engagement. Upwork and Fiverr list thousands of active "AI agent developer" freelancers, and r/AI_Agents (the thread's home) counts hundreds of thousands of members; the directly affected group is plausibly the tens of thousands of builders shipping agents to non-technical clients without any principled escalation layer.
**Mechanism**: Today these builders either over-restrict (agent asks constantly, client sees no value) or over-trust (agent acts wrongly without asking, client rips it out); a measured policy layer lets them set the boundary deliberately and show clients the receipts ("the agent escalates irreversible actions; here's its precision on the benchmark"), converting trust from a leap of faith into a configured, demonstrable property — fewer torn-out deployments, fewer interruption-fatigued clients.
**Measure**: (1) Escalation precision/recall on the labeled benchmark ≥0.85/0.85, vs. measured baselines for naive confidence thresholds. (2) In pilot deployments, wrongful autonomous actions (actions a human later reverses or complains about) drop ≥50%. (3) Interruption rate stays under a client-set budget (e.g., <5 asks/day) while holding recall on irreversible actions — proving it's not just asking about everything.

## Why Now
The demand thread and the 528-point trust-collapse story both landed inside the window — community attention on the question is at a peak. The plumbing (HumanLayer at ~11k★, LangGraph interrupts) just matured to the point where the missing piece is purely the policy layer, and cheap fast models make per-action scoring affordable at runtime.

## Skill Angle
Given one proposed agent action (what it does, what triggered it, what it affects), score it on the three axes — ambiguity, reversibility, blast radius — and recommend proceed / ask / refuse with a one-line justification per axis. This is exactly the judgment call the runtime library would make programmatically, done once by hand; useful today for anyone manually reviewing an agent's action log or designing a policy file before any library exists. Shipped as `skills/agent-escalation-policy-engine/`.

## MVP Sketch
A Python library with the three-axis scorer (deterministic irreversibility rules + one small-model ambiguity check), a YAML policy format, a LangGraph interrupt adapter, and a 150-action labeled benchmark built from real agent traces. Experiment: on one pilot agent (e.g., an inbox-management agent), compare wrongful-action and interruption rates over two weeks against the unguarded baseline; if the policy can't beat a trivial "always ask before tools with side effects" rule on the benchmark, the smart layer isn't earning its complexity — kill it. 3–4 weeks for 1–2 people.

## Risks & Open Questions
- LangChain or HumanLayer could ship an opinionated escalation-policy layer on top of their own interrupt plumbing and absorb this — the strongest already-solved risk.
- "Should have escalated" labels may not generalize across domains; the benchmark could encode one annotator's risk tolerance rather than a transferable standard.
- The ambiguity axis depends on an LLM judging an LLM — exactly the "confidence scores lie" trap; the deterministic axes must carry most of the weight.
- Interruption fatigue is adaptive: clients' tolerance shifts over time, and a static policy file may need the kind of online tuning that's out of MVP scope.
