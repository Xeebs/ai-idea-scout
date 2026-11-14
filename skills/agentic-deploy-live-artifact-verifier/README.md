# Agentic Deploy Live-Artifact Verifier (Pipeline Review)

A paste-in prompt that reviews a CI/CD pipeline definition — a GitHub Actions workflow, a GitLab `.gitlab-ci.yml`, a Harness pipeline spec, an Azure DevOps YAML pipeline, a Jenkinsfile, whatever you've got — and flags one specific, dangerous anti-pattern: the pipeline marking a release "successful" the moment the deploy *command* exits cleanly, instead of after an independent check that the live artifact actually changed.

This matters most for pipelines where an AI coding agent commits, builds, and triggers deploys with little or no human review per release. "Green" in that setup can mean nothing more than "the deploy tool didn't crash" — not "the thing we meant to ship is actually live." A live-shaped real-world example of exactly this: a team's agentic pipeline kept reporting deploys as successful while production quietly kept serving the old version, and they only caught it by adding an explicit "verify the live site before declaring success" step after the fact. This skill is the review you'd run *before* that happens to you — it reads your pipeline definition and tells you whether it has that gap, where exactly, and what to add.

## When to use this

Use this when:
- You're setting up or hardening a CI/CD pipeline that an AI agent drives with minimal human review, and want to know before it ships anything whether "success" is backed by a real check.
- You've already had a "CI said it deployed but the live site/app didn't actually change" incident and want to know exactly where your current pipeline would (or wouldn't) have caught it, plus what to add.
- You're reviewing someone else's pipeline config as part of an onboarding/security/reliability audit and want a structured pass on this one specific failure mode.

Do not use this to check whether your production system is broken *right now* — this only reviews the pipeline's *design*, on paper. It does not fetch any live URL, does not run any command, and does not tell you today's actual deploy status.

## What to hand over before running this

This is entirely manual input — you paste your pipeline config directly; nothing is read automatically from any live CI/CD system or connector.

Gather, as completely as you can:

1. **The full pipeline definition** — every stage, from build through whatever currently counts as the success/notification step. A snippet missing the deploy or post-deploy stage can't be properly reviewed.
2. **What the deployment target actually is** — a public web app/API sitting behind a CDN or load balancer, a backend-only service with no public endpoint, a mobile build, etc. This decides whether a live-fetch check is even possible for your case.
3. **How "success" is reported today** — the Slack message, PR status check, or dashboard flip that a human or another agent actually looks at.
4. **(Optional)** Any past incident where this pipeline reported success without the live artifact really changing.

If #1 is incomplete, expect the review to come back asking for the missing stage instead of guessing at what's not shown.

## The prompt

Paste this into any AI chat tool along with your pipeline config and answers to the items above:

```
You are reviewing a CI/CD pipeline definition for one specific anti-pattern:
declaring deploy "success" when the deploy COMMAND completes, instead of
after an independent check that the LIVE ARTIFACT actually reflects the
change. This is a static, one-time design review of the pipeline as written
— you are not fetching any live URL, running any command, or checking
today's actual production status.

Here is my pipeline definition:
[PASTE: the full pipeline/workflow file, every stage from build through
whatever currently counts as the success step]

Deployment target: [public web app/API behind CDN or load balancer /
backend-only service with no public endpoint / mobile build / other —
describe it]

How success is reported today: [Slack message / PR status check /
dashboard / other]

Prior incident (if any): [describe, or say "none"]

Do this:

1. Parse the pipeline into an ordered list of stages/steps, with what each
   one runs and its pass/fail condition.

2. Identify the current success checkpoint — the exact step after which a
   human or agent would currently treat the release as done.

3. Scan every step AFTER that checkpoint for an independent live-artifact
   check — something that touches the actual deployed system, not a rerun
   of build/test logic or the deploy tool's own exit code. Specifically
   look for: a fetch of the live endpoint with a build-ID/content-hash/
   commit-SHA comparison; a health check that asserts the NEW version is
   serving (not just that something responds); or an APM query for
   post-deploy error-rate anomalies in a bounded window.

4. Classify what you find against this checklist (a pipeline can match more
   than one):
   - No post-deploy check at all (success declared at build/push/apply).
   - Phantom-deploy health check: a health check exists but only proves
     something responds, not that the NEW artifact is responding.
   - Self-reported agent success: the signal is free-text agent output
     ("Deployed successfully!") with no programmatic live check behind it.
   - No cache/CDN awareness: a live-fetch check exists but doesn't account
     for edge-cache propagation lag (so it either false-passes too early
     or false-fails on normal lag).

5. For every item you flag, cite the exact step name from my pasted config
   it applies to. Never describe an anti-pattern in the abstract if my
   config doesn't actually show it.

6. For every item flagged, give the exact insertion point: which existing
   step it goes after, what command/check to add (fetch the live endpoint
   and compare build-ID/hash; add a version field to an existing health
   endpoint and assert it; or add a bounded post-deploy APM query), and a
   grace period/retry suggestion if CDN propagation lag is plausible for
   my target.

7. If my deployment target is backend-only with no public endpoint, say so
   explicitly — a direct live-fetch check isn't available — and suggest
   the closest real substitute (internal health/metadata endpoint, or a
   log-based version assertion) instead of inventing a fake URL to check.

8. If I gave you a prior incident, explicitly cross-check it against my
   pasted pipeline: state plainly whether the pipeline as written today
   would or would not have caught that specific incident, tied to one of
   your findings above. If I gave no prior incident, skip this — don't
   invent one.

9. If my pipeline already has an adequate independent check, say PASS and
   explain why it clears the bar. Don't manufacture a finding just to have
   something to report.

Never approve a step as sufficient just because of its name — judge what it
actually checks, not what it's called. Never recommend a hard-fail live
check without a grace period for CDN/propagation lag. Never conflate a
pre-deploy check (tests, build, lint) with a post-deploy live-artifact
check. Never invent line numbers or incident history I didn't give you —
if my config is incomplete or ambiguous, ask for the missing stage instead
of guessing. Never recommend one specific commercial vendor as the only
fix — give the protocol-level check so it works regardless of CI provider.

Output, in this order:
1. Verdict: PASS / AT RISK / INSUFFICIENT INFO
2. Stage Table: Step Name | What It Currently Proves | Anti-Pattern Matched
   (or "—") | Config Reference
3. Findings: one subsection per flagged anti-pattern — name, the concrete
   false-positive scenario it allows, and the exact insertion point
4. Prior Incident Cross-Check (only if I gave you one)
5. Backend/No-Public-Endpoint Note (only if applicable)
6. If you do nothing else: one sentence naming the single highest-leverage
   fix
```

## What you get back

A single Markdown report with a top-line verdict (PASS / AT RISK / INSUFFICIENT INFO), a stage-by-stage table showing exactly what each step in your pipeline actually proves, a findings section citing your real step names and giving you the exact spot to add a verification gate, an explicit statement of whether your pipeline would have caught any prior incident you described, and — if relevant — a note about CDN propagation lag or backend-only targets so you don't walk away with an overly strict or impossible recommendation.

## What this is not

This is a design-review aid, not a live monitor and not an enforcement tool. It does not:
- Connect to your CI/CD provider's API, fetch any live URL, or check today's actual deploy status.
- Fix your pipeline file for you — it tells you what to add and where, you (or your agent) wire it in.
- Replace an always-running verification gate. The companion idea this skill comes from also describes a persistent middleware step that sits in a live pipeline, independently fetches the production endpoint, and flips a separate "VERIFIED" status after every real deploy — that's a continuously running piece of infrastructure, a separate build from this one-shot review.
