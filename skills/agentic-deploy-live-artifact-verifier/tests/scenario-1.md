# Scenario 1 — Agentic Next.js deploy to Vercel, no post-deploy check at all

## Input

Pipeline definition (GitHub Actions, `.github/workflows/deploy.yml`):

```yaml
name: Agent Deploy
on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install deps
        run: npm ci

      - name: Build
        run: npm run build

      - name: Run unit tests
        run: npm test

      - name: Deploy to Vercel
        id: deploy
        run: |
          npx vercel deploy --prod --token=${{ secrets.VERCEL_TOKEN }} --yes
          echo "Agent reports: Deployed successfully!"

      - name: Notify Slack
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          payload: '{"text":"✅ Deploy succeeded — production is live."}'
```

Deployment target: public Next.js web app on Vercel, served through Vercel's CDN edge network.

How success is reported today: the Slack message posted by the last step, which only fires `if: success()` — i.e., if every prior step exited 0.

Prior incident: none reported yet, but the team is adopting agent-driven commits/deploys and wants a review before trusting it further.

## Expected output characteristics (pass/fail criteria)

A correct run of the skill should:

- [ ] **Verdict: AT RISK** — there is no step after `Deploy to Vercel` that touches the live, deployed system at all.
- [ ] Stage table correctly lists `Deploy to Vercel` as the current success checkpoint and `Notify Slack` as a notification step, not a verification step.
- [ ] Flags **"No post-deploy check at all"** — explicitly citing that `Deploy to Vercel`'s own exit code (plus the `echo "Deployed successfully!"` line) is the entire basis for success, and `Notify Slack` only reacts to that exit code rather than checking anything live.
- [ ] Also reasonably flags **"Self-reported agent success"** given the literal `echo "Agent reports: Deployed successfully!"` line — citing that exact line.
- [ ] Insertion point recommendation is concrete: add a step between `Deploy to Vercel` and `Notify Slack` that fetches the live production URL and compares a build-ID/commit-SHA (e.g., via an `x-vercel-id` header, a `/api/version` endpoint, or embedding the git SHA in a known response) against the SHA just deployed.
- [ ] Because the target is Vercel/CDN, the output must mention a grace period or short retry window for edge propagation lag rather than recommending an instant hard-fail check.
- [ ] Does NOT flag `Run unit tests` as insufficient post-deploy verification — that's correctly identified as a pre-deploy check, out of scope for the live-artifact verdict.
- [ ] Does not invent an incident that wasn't reported — report should either omit incident discussion or note explicitly that none was given.

**Fails** if it: approves the pipeline as PASS; treats the Slack notification step itself as a sufficient live check; recommends a hard-fail with no propagation grace period; or fabricates specific line numbers/incidents not present in the pasted config.
