# ReceiptChain: A Verifiable Proof-of-Work Attestation Layer for Agent-Claimed Labor

- **Status**: EXPLORING (promoted 2026-11-14 cycle 72: evidence density — ≥2 independent threads, TessPay, an IETF draft, Inference Labs' Proof of Inference, Hive's signed receipts, and a Solv Labs/Bedrock AgentCore case study all independently targeting the same verifiable-labor gap, none a settled adopted standard)
- **Date**: 2026-11-14
- **Topic**: Agentic AI & autonomous agents
- **Source**: research/2026-11-14-agentic-ai-autonomous-agents.md · P7
- **Maturity verdict**: PARTIAL — WebSearch found a genuinely crowded but immature field: TessPay (arXiv proposal, not deployed), an unadopted IETF individual draft, Inference Labs' "Proof of Inference" product (own docs admit automated billing/ERC-8004 integration are "not yet live"), Hive's signed-receipt vendor product, one bespoke enterprise case study (Solv Labs/Bedrock AgentCore), and ArkForge's self-reported vendor claims. No independently audited or adopted standard exists across any of these.
- **Format**: BOTH
- **Data Sources**: MANUAL (MVP) — the operator uploads or pastes the agent's execution log/trace export (inputs, intermediate steps, outputs, timestamps) and the original task description for a given claimed-complete job. CONNECTED upgrade path: once a specific agent labor marketplace or framework's trace format is targeted (e.g. this repo's own WorkLedger idea, or a specific observability backend like Langfuse/LangSmith), ReceiptChain would read execution traces directly from that system instead — no mature universal cross-framework trace connector exists yet, so MANUAL is the honest starting point.

## The Gap
As agents start getting paid for work, there is no independently verifiable way to prove an agent actually performed the claimed labor rather than self-reporting it. The clearest evidence is a single low-engagement blog post proposing exactly this structural need; broader search found several competing proposals (TessPay, an IETF draft, Inference Labs' product) all admittedly pre-production or unadopted. This is the trust dependency that agent labor marketplaces and payment protocols will need once real money is actually at stake.

## The Project
ReceiptChain wraps a payable agent task with a signed, hash-chained execution receipt — inputs, intermediate step hashes, outputs, and timing — and offers a lightweight re-execution verifier that a payer can invoke on a sample of claimed-complete jobs before releasing escrow. Instead of a full TEE/ZK proof system (expensive, immature to deploy broadly today), this is a pragmatic middle layer: cryptographic receipts plus statistical spot-check re-execution, converting "trust the agent's self-report" into "verify against a receipt, and occasionally re-run it."

## Tangible Impact
**Population**: Operators and participants in emerging agent labor/payment marketplaces and volunteer/decentralized compute networks — the same builder population surfaced by this cycle's P1/P2 patterns (sub-cent settlement rails, agent gig-economy marketplaces) — who currently have no independent way to verify a payment-claiming agent's work before releasing funds.
**Mechanism**: Today a payer either trusts the agent's self-report entirely or builds their own bespoke, unaudited check. ReceiptChain gives any marketplace or payer a drop-in attestation step: a receipt proves what was claimed to have happened, and spot-check re-execution catches fabricated claims at a controllable cost — closing the exact gap the digest's cited proposals (TessPay, Inference Labs) describe as still pre-production.
**Measure**: (1) percentage of claimed-complete tasks independently verifiable from the receipt alone, without full re-execution; (2) fraud/mismatch detection rate in spot-check re-execution trials against intentionally-fabricated test claims; (3) payer-reported dispute rate before vs. after adopting receipts in a pilot marketplace integration.

## Why Now
Real money is starting to move through agent-to-agent transactions this cycle (x402/AP2 adoption, Mastercard's AP4M announcement), which makes the "did the agent actually do the work" question newly urgent rather than hypothetical — and every competing proposal found in gap analysis is explicitly pre-production, leaving the field open.

## Skill Angle
A companion skill takes a pasted execution log/trace and the original task claim, and assesses whether the available evidence is sufficient to credibly believe the work was genuinely performed — flagging specifically what additional logging or evidence would be needed for a stronger attestation. This is a one-shot judgment task, separable from the attestation service's actual signing/ledger infrastructure.

## MVP Sketch
A small SDK that wraps a task function, logs a signed hash-chained receipt to a lightweight append-only ledger, plus a CLI verifier that replays the task from the receipt's logged inputs and checks the output against a tolerance (not exact match, given LLM non-determinism). Validating experiment: run 50 synthetic labor tasks with 10% intentionally fabricated and measure the detection rate.

## Risks & Open Questions
- If ERC-8004 or Inference Labs' Proof of Inference actually ships live (currently "not yet live" per the digest) before this is built, that could become the adopted standard instead — the strongest "already getting solved" risk.
- Non-determinism is the core technical risk: LLM-based agent outputs vary run to run, so re-execution verification needs tolerance-based matching, which weakens the guarantee versus a deterministic proof.
- TEE/cryptographic attestation (the stronger guarantee) remains too immature and expensive to deploy broadly today — the MVP's spot-check approach is a weaker, probabilistic guarantee only, which may not satisfy high-value transactions.
- Economic viability is open: who pays for the re-execution compute cost on every disputed claim needs a clear answer before this works as a real product.
