# Breach Bounty: A Micro-Bounty Red-Teaming Platform for Self-Hosted Guardrails

If you're a solo developer running your own LLM guardrail — NeMo Guardrails, Guardrails AI, LLM Guard, or something you duct-taped together behind a webhook — your adversarial-testing options right now are "do it yourself" or "pay HackerOne-tier money you don't have." There is nothing built for the people in between: the two-to-ten-person team that knows their filter has holes but can't justify a $15k enterprise bug bounty to find them.

## The Gap

The evidence for this gap is almost embarrassingly concrete: a real GitHub issue, `ak10082247-max/canaryguard-402#2`, titled "[BOUNTY] $5.00+ USDC: Adversarial Prompt Injection Bypass on CanaryGuard Firewall," racked up 28 comments of a solo builder manually triaging bypass claims by hand, in a public issue thread, for a bounty worth less than a cup of coffee. Meanwhile, the enterprise end of the market is well served — HackerOne/Anthropic pays out up to $15k, OpenAI runs $10k-$50k programs, IBM Granite offers $100k — but those programs are invite-only, high-overhead, and built for security teams with budgets the CanaryGuard builder doesn't have. There's an adjacent-but-not-quite layer too: gamified red-teaming products like Bordair's "Castle" CTF, HackAI, and Product Hunt's "Break My Guard" exist, but none of them package the specific automated plumbing — payout automation, submission dedupe, bypass verification — that a solo guardrail builder running an actual micro-bounty needs. The duplication of effort (one person, one GitHub issue, one bounty, zero reusable tooling) is itself the signal: nobody building at this scale has a tool to reach for.

## The Project

Breach Bounty is a platform where a guardrail builder registers their endpoint and funds a small bounty pool, and red-teamers submit adversarial payloads against it. The platform does the part that currently eats a maintainer's week by hand: it auto-runs each submission against the registered endpoint, checks whether it actually achieved a bypass (a "clean" or low-risk verdict on content that should have been flagged), dedupes it against everything submitted before, and — once verified — releases payout straight from escrow. No more triaging bounty claims in a GitHub comment thread one at a time.

The core components are an adapter layer that speaks the (slightly different) API of each major open-source guardrail toolkit, an escrow/payout integration (USDC via smart-contract escrow, or Stripe payment intents), a dedupe/triage engine to stop people farming the pool with near-duplicate payloads, and a public per-guardrail leaderboard so builders can show off — or get pressured into — a track record of getting red-teamed.

## Tangible Impact

**Population**: solo developers and small teams (2-10 people) self-hosting LLM guardrails on NeMo Guardrails, Guardrails AI, or LLM Guard — not enterprise security teams with $15k-$100k bounty budgets, a distinction the digest's own contrast between the enterprise programs and the $5 CanaryGuard issue makes directly.
**Mechanism**: lowers adversarial-testing cost and overhead from "manually run a GitHub issue bounty and triage each submission by hand" to "register an endpoint, fund a pool, get automatically-verified bypass reports" — surfacing real jailbreak bypasses before an attacker exploits them in production, for teams priced out of HackerOne-tier programs.
**Measure**: genuine verified bypasses found per guardrail-month at a given bounty spend; median time from submission to verified payout (target: minutes to hours, vs. the manual GitHub-issue baseline of days); post-remediation bypass rate on a retest after a found bypass is patched.

## Try It

A companion skill already exists at [`skills/guardrail-micro-bounty-redteam-platform/`](../skills/guardrail-micro-bounty-redteam-platform/) — **Bypass Triage: Guardrail Micro-Bounty Submission Reviewer**. Its one-line job: "Triages a single red-team bounty submission against a self-hosted LLM guardrail (NeMo Guardrails, Guardrails AI, LLM Guard, or a custom webhook) — replays the payload against the live detector where possible, classifies it as a genuine novel bypass, a duplicate of a prior finding, or an unreproduced/false claim, and drafts the payout-or-rejection response to send the submitter."

This is the part of the idea you can use today, before anyone builds the full platform. If you're already running a manual micro-bounty and a submission lands in your inbox or GitHub issues, paste the skill's `README.md` into any AI chat tool (Claude, ChatGPT, Gemini) along with your submission details, and it will tell you whether to pay, reject, or ask for more evidence — and draft the reply. If you use Claude Code, drop the whole `skills/guardrail-micro-bounty-redteam-platform/` folder into `~/.claude/skills/` and invoke it directly.

Worth knowing going in, per the idea's own risk notes: payout automation on unverified claims is gameable (someone could farm the pool with near-duplicate payloads — hence the dedupe engine), and the adjacent paid products named above (Bordair's Castle, HackAI, Break My Guard) could ship a per-issue micro-bounty mode of their own and absorb this niche before anyone builds Breach Bounty properly. The evidence base behind this idea is also genuinely thin — one 28-comment GitHub issue is a real signal, not a trend, and validating this for real means finding a second team independently wanting the same mechanic.

Surfaced from `research/2026-11-13-ai-safety-guardrails-in-production.md`, pattern `P1`.
