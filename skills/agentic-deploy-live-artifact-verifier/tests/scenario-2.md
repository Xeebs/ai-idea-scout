# Scenario 2 — Kubernetes rollout with a generic health check (phantom-deploy pattern)

## Input

Pipeline definition (GitLab CI, `.gitlab-ci.yml`):

```yaml
stages:
  - build
  - deploy
  - verify

build-image:
  stage: build
  script:
    - docker build -t registry.example.com/orders-api:$CI_COMMIT_SHORT_SHA .
    - docker push registry.example.com/orders-api:$CI_COMMIT_SHORT_SHA

deploy-k8s:
  stage: deploy
  script:
    - kubectl set image deployment/orders-api orders-api=registry.example.com/orders-api:$CI_COMMIT_SHORT_SHA
    - kubectl rollout status deployment/orders-api --timeout=120s

verify-deploy:
  stage: verify
  script:
    - curl --fail https://api.example.com/health
    - echo "Verification passed — deploy is healthy."
  needs: ["deploy-k8s"]
```

`/health` endpoint handler (for context, pasted by the user alongside the YAML):
```python
@app.route("/health")
def health():
    return {"status": "ok"}, 200
```

Deployment target: `orders-api`, an internal-facing but network-reachable REST API behind a company load balancer (no CDN, no edge caching).

How success is reported today: the pipeline going fully green across all three stages is the signal the on-call engineer and the deploying agent both check.

Prior incident: the team mentions that a few weeks ago a rollback left an old pod running, `kubectl rollout status` reported success because the old pod was still marked "ready," and the health check kept passing throughout — nobody noticed until a customer reported stale order data for several hours.

## Expected output characteristics (pass/fail criteria)

A correct run of the skill should:

- [ ] **Verdict: AT RISK.**
- [ ] Correctly identifies `verify-deploy`'s `curl --fail https://api.example.com/health` as a **phantom-deploy health check**: it proves *something* responds with 200, but the `/health` handler shown returns a static `{"status": "ok"}` with no build-ID, version, or commit-SHA field, so it cannot distinguish the new pod from a stale one still marked ready.
- [ ] Explicitly calls out that the step being named `verify-deploy` does NOT make it sufficient — judges what it checks, not its name (this is the guardrail against name-based approval).
- [ ] Cross-checks against the reported prior incident (stale pod, rollout status "succeeded," health check kept passing) and states that the current pipeline, as written, would NOT have caught that incident — matching what the team actually experienced.
- [ ] Insertion point: recommends adding a build-ID/commit-SHA field to the `/health` response (or a separate `/version` endpoint) and asserting in `verify-deploy` that it matches `$CI_COMMIT_SHORT_SHA` just deployed, rather than just checking for a 200.
- [ ] Since there's no CDN/edge caching for this internal target, does not impose an unnecessary CDN-propagation grace-period caveat — may still reasonably suggest a short retry for pod-readiness timing, but should not invent a CDN-specific caveat that doesn't apply here.
- [ ] Does not flag `build-image` as part of the problem — correctly scoped to post-deploy checks only.
- [ ] Backend/No-Public-Endpoint Note is appropriately omitted or softened, since the API is network-reachable (even if internal-only) and a live-fetch-style check is actually possible here.

**Fails** if it: says PASS; treats `verify-deploy`'s existing health check as adequate because of its name or stage name; fails to connect the finding to the stated prior incident; or recommends a CDN-propagation grace period for a target explicitly described as having no CDN/edge caching.
