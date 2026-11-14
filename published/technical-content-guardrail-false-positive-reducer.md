# Code-Safe: A Reusable False-Positive-Reduction Layer for Guardrails on Technical Content

Tell a generic AI safety guardrail "write a script to kill this process" and it doesn't see a sysadmin — it sees a weapon. Tell it "craft a payload to test our rate limiter" and it doesn't see a pentester doing their job — it sees an attacker. The vocabulary of ordinary engineering work — kill, exploit, payload, inject, bypass, attack, crash, backdoor — is also the vocabulary foundation-model safety classifiers were trained to flag as violence or hacking. For most products that's a rare, shrug-it-off false positive. For an AI coding assistant, a DevOps copilot, or a security-research tool, it's the daily cost of doing business, and right now every team pays it alone, from scratch.

## The Gap

The clearest evidence of how real this is came from Reddit's own engineering team, who wrote up building an in-house guardrails platform specifically because "existing foundation-model guardrails produced too many false positives on technical queries." They didn't adopt a product — they built one, and reported getting it to an F1 of 0.97 at sub-25ms p99 latency. That's a well-resourced engineering org concluding the off-the-shelf options weren't good enough and spending real engineering time on a custom fix.

The pattern isn't a one-off either. Tian Pan's "Alignment Tax" writeup catalogs the same failure in the wild — a sysadmin's "kill the background process" getting flagged as violent intent is a running joke in the field at this point. Guardrail vendors like Zilliz and Tetrate acknowledge the problem in their own docs, but what they offer is generic advice: run tiered checks, build your own labeled eval set, tune thresholds. Advice exists. A reusable classifier or library that a second team could actually adopt does not. Every company shipping a technical assistant is quietly re-deriving Reddit's build, or just living with the friction.

## The Project

The idea is a small, fine-tunable classification layer — a distilled model plus a rules pre-filter — that sits in front of whatever general-purpose guardrail a team already runs (NeMo Guardrails, Guardrails AI, LLM Guard, or a vendor gateway) and is purpose-built for one job: telling apart technical-benign uses of alarming-sounding vocabulary from genuinely malicious ones. The centerpiece isn't the model architecture, which is deliberately unremarkable — it's the labeled corpus: matched pairs of benign technical phrases (process-kill commands, CVE discussion in a security-research context, pentest requests) against genuinely malicious requests that use the exact same trigger words. That corpus, and the measured false-positive-reduction delta it produces when dropped in front of a stock guardrail, is the actual product. Teams keep their existing safety coverage for real threats and recover the legitimate technical traffic that generic guardrails are currently choking on.

It's explicitly a drop-in pre-filter, not a guardrail replacement — nobody has to rip out their existing safety stack to use it.

## Tangible Impact

**Population**: engineering teams at companies building AI coding assistants, DevOps/SRE copilots, and security-research or pentest-support tools — products whose core legitimate traffic is dense with vocabulary ("kill," "exploit," "payload," "inject," "bypass") that generic safety classifiers associate with violence or malicious intent. GitHub Copilot, Cursor, Replit Agent, and the dozens of smaller AI-coding and AI-security-tooling startups cataloged on product directories like There's An AI For That's "developer tools" category are a reasonable proxy for the population size — likely hundreds of teams shipping guardrail-wrapped technical assistants today.

**Mechanism**: a generic foundation-model guardrail trained on broad internet toxicity/safety data over-indexes on surface vocabulary, blocking legitimate technical requests ("write a script to kill this process") at a rate high enough that Reddit's own engineers judged it worth building a custom F1-0.97 replacement rather than tolerating it; a reusable pre-filter trained specifically on technical-benign-vs-malicious pairs lets smaller teams without Reddit's engineering budget recover that lost legitimate traffic without weakening coverage against actual exploit requests.

**Measure**: false-positive rate on a held-out technical-benign query set, before vs. after inserting the pre-filter ahead of a stock guardrail (target: approach Reddit's reported 0.97 F1 without a bespoke build); missed-malicious-intent rate on the same corpus's genuinely harmful pairs (must not regress); added p99 latency from the pre-filter stage (target: comparable to Reddit's reported sub-25ms).

## Try It

A companion Claude Code skill already exists: [`skills/technical-content-guardrail-false-positive-reducer/`](../skills/technical-content-guardrail-false-positive-reducer/).

> Diagnoses why a team's AI safety guardrail is blocking legitimate technical/developer queries (process-kill commands, exploit/CVE discussion, pentest requests) and drafts a starter benign-vs-malicious labeled eval set plus root-cause category recommendations. Use when a team has a sample of guardrail false-positives from a coding assistant, DevOps copilot, or security-tooling product.

It's deliberately scoped as a diagnostic, not the fix itself: hand it a sample of queries your guardrail incorrectly blocked (the query text, the guardrail's verdict, and a human-confirmed label if you have one), and it hands back a root-cause breakdown of which category is misfiring, a seed eval-set of benign/malicious pairs in the same vocabulary, and tuning-vs-train-a-classifier recommendations — the groundwork before you commit to training and deploying the actual pre-filter. To use it, either paste the contents of its `README.md` into any AI chat tool as a prompt template, or drop the whole `technical-content-guardrail-false-positive-reducer/` folder into `~/.claude/skills/` if you're running Claude Code.

Worth knowing before you build on this: the eval set's label quality is the whole product, and "benign vs. malicious" technical intent is genuinely ambiguous at the margins — a real exploit walkthrough and a security-research explanation can read identically, so this needs domain-expert review, not crowd labeling. It's also worth noting that Reddit's 0.97 F1 is self-reported with no published methodology or shared held-out set, so the real validation bar here is an independently credible eval set, not matching an unverifiable number — and a foundation-model vendor could commoditize this entire layer overnight simply by fine-tuning their own safety classifiers on technical corpora.

Surfaced from `research/2026-11-12-ai-safety-guardrails-production.md`, pattern `P8`.
