# ReceiptChain: A Verifiable Proof-of-Work Attestation Layer for Agent-Claimed Labor

Money is starting to move between AI agents — and almost nobody can prove the agent on the other end of the transaction actually did the work it's invoicing for.

## The Gap

As agents start getting paid for labor — inference jobs, research tasks, completed bounties — the payer is left trusting the agent's own self-report. The clearest public evidence of this gap is a single low-engagement Hacker News post, "Towards Verifiable LLM Infra," proposing exactly this structural need and finding almost no response. But a broader search shows the gap is far from unnoticed: it's crowded with half-finished attempts. TessPay proposes a "verify-then-pay" escrow model using TLS Notary/TEE attestation — but it's an arXiv paper, not a deployed system. An IETF individual draft (`draft-mw-spice-inference-chain-00`) sketches a verifiable inference chain but hasn't been adopted. Inference Labs ships a "Proof of Inference" product whose own documentation admits automated billing and ERC-8004 standard integration are "not yet live." Hive sells a signed-receipt product. Solv Labs has a real enterprise deployment on Bedrock AgentCore — but it's one bespoke workflow, not a general standard. ArkForge makes self-reported "cryptographic proof" claims with no independent audit behind them.

Six parties are circling the same problem, and not one has shipped an adopted, audited standard. That's the kind of crowded-but-unsettled field where a pragmatic middle layer can actually matter.

## The Project

ReceiptChain wraps a payable agent task with a signed, hash-chained execution receipt — inputs, intermediate step hashes, outputs, and timing — and gives the payer a lightweight re-execution verifier they can run against a sample of claimed-complete jobs before releasing escrow. It deliberately skips the expensive end of the spectrum: full TEE or zero-knowledge proof systems remain too immature and costly to deploy broadly today. Instead, ReceiptChain converts "trust the agent's self-report" into "verify against a signed receipt, and spot-check re-execute often enough to make fabrication a losing bet." It's not cryptographic certainty — it's a calibrated, affordable trust layer for a market that currently has none.

## Tangible Impact

**Population**: Operators and participants in emerging agent labor and payment marketplaces, and volunteer/decentralized compute networks — the same builder population driving this cycle's parallel patterns in sub-cent settlement rails and agent gig-economy marketplaces — who today have no independent way to verify a payment-claiming agent's work before releasing funds.

**Mechanism**: Right now a payer either trusts the agent's self-report outright, or builds a bespoke, unaudited verification hack from scratch. ReceiptChain gives any marketplace or payer a drop-in attestation step: the receipt proves what was claimed to have happened, and spot-check re-execution catches fabricated claims at a cost the payer controls — closing precisely the gap every cited competing proposal (TessPay, Inference Labs) describes as still pre-production.

**Measure**: (1) the percentage of claimed-complete tasks independently verifiable from the receipt alone, without a full re-execution; (2) the fraud/mismatch detection rate when spot-check re-execution is run against intentionally fabricated test claims; (3) the change in payer-reported dispute rates before vs. after adopting receipts in a pilot marketplace integration.

## Why Now

Real money started moving through agent-to-agent transactions this cycle — x402/AP2 adoption and Mastercard's AP4M announcement among the signals — which turns "did the agent actually do the work" from a hypothetical into an operational question marketplaces need answered now. And every competing proposal found in gap analysis is explicitly pre-production, which means the field is genuinely still open rather than quietly settled by an incumbent.

## Try It

A companion skill, [`skills/agent-labor-proof-of-work-attestation/`](../skills/agent-labor-proof-of-work-attestation/), handles the judgment-call half of this problem on its own: *"Assesses whether a pasted agent execution log/trace and task claim give sufficient evidence that an AI agent actually performed claimed labor, before a payer releases payment or escrow."* Hand it a pasted execution log and the original task description, and it walks the trace step by step, classifies the evidence density (bare claim through full trace), flags chain gaps and implausible timestamps, and returns a Pay / Hold / Reject recommendation with the specific missing evidence that would raise its confidence. It's a complement to the signed-receipt infrastructure above, not a replacement — useful today, with nothing to deploy, for anyone who has to make this call on a log someone just handed them. Use it by pasting the README prompt into any AI chat tool, or by dropping the `skills/agent-labor-proof-of-work-attestation/` folder into `~/.claude/skills/` for Claude Code.

## Risks & Open Questions

- If ERC-8004 or Inference Labs' Proof of Inference actually ships live — both currently "not yet live" per the research — before this gets built, that could become the adopted standard instead. This is the strongest "already getting solved" risk.
- Non-determinism is the core technical obstacle: LLM-based agent outputs vary run to run, so re-execution verification needs tolerance-based matching rather than exact comparison, which weakens the guarantee relative to a deterministic proof.
- The stronger guarantee — TEE or cryptographic attestation — remains too immature and expensive to deploy broadly today, so this MVP's spot-check approach is a weaker, probabilistic guarantee that may not satisfy high-value transactions.
- Who pays for the re-execution compute on every disputed claim is still an open economic question, and needs an answer before this works as a real product rather than a research prototype.

---

Surfaced from `research/2026-11-14-agentic-ai-autonomous-agents.md`, pattern `P7`.
