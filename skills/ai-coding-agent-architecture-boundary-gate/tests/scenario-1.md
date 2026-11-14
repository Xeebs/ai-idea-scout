# Scenario 1 — Clean layered monorepo, merge queue enabled, explicit boundaries given

## Input

The user is a platform engineer at a mid-size SaaS company. They paste:

```
We've had Claude Code and Cursor opening 15-20 PRs/week against our main repo
for the last couple months, and twice now an agent-written PR imported straight
from our infra/ layer into domain/ code, which broke a test suite that assumes
domain/ has zero infra dependencies (we mock infra at the api/ boundary). I want
a draft CI gate.

Directory structure:
.
./api
./api/routes
./api/middleware
./domain
./domain/models
./domain/services
./infra
./infra/db
./infra/queue
./web
./web/src
./web/src/components
./web/src/pages

Manifest files: pyproject.toml at repo root (api/, domain/, infra/ are Python),
package.json + tsconfig.json in web/ (TypeScript/React).

My intended boundaries:
- domain/ must never import from infra/ or api/
- api/ may import from domain/, must never import from infra/ directly
  (infra access goes through a repository interface defined in domain/)
- web/ only talks to api/ over HTTP; it has no reason to import api/ or
  domain/ Python code at all (it's a separate language anyway)

We use GitHub's native merge queue (merge_group trigger already exists in our
workflows for other checks).

Here's a recent PR that violated this (PR #812, merged last week):
--- a/domain/services/order_service.py
+++ b/domain/services/order_service.py
@@
+from infra.db.connection import get_session
```

## Expected output / pass criteria

- [ ] Correctly identifies two languages: Python (api/, domain/, infra/) and TypeScript (web/).
- [ ] Uses the user's explicit boundary description verbatim rather than re-inferring from folder names (since boundaries were given, not left to inference) — boundary table should match: domain/ → no imports from infra/ or api/; api/ → may import domain/, not infra/; web/ → must not import api/ or domain/ at all.
- [ ] Produces a YAML config encoding all three rules.
- [ ] Produces a pytest-archon snippet covering the Python-side rules (domain/infra, domain/api, api/infra).
- [ ] Produces an ESLint boundaries snippet for web/ — reasonably, since web/ only needs to NOT import the Python layers (which ESLint can't even resolve), the skill should recognize this is really a "no cross-language import" rule and either note that this boundary is naturally enforced by language separation (no shared import graph) or still produce a defensive config and explain why it's largely redundant. Either answer is acceptable as long as it's explicit and not silently skipped.
- [ ] Cites the pasted PR #812 diff (`domain/services/order_service.py`, `from infra.db.connection import get_session`) as a concrete historical violation this rule set would have caught — this is the one case where diff evidence was actually provided, so the historical-violation section must not say "skipped."
- [ ] Generates a merge-queue SHA-binding snippet (`merge_group` trigger) since the user confirmed they use GitHub's native merge queue — does not say "not applicable."
- [ ] Ends with a review checklist, and does not claim to have committed, pushed, or opened a PR with anything.
- [ ] Clearly labels inferred vs. confirmed — since everything here was explicitly given by the user, nothing should be marked "inferred, needs confirmation."

## Fail conditions

- Treats web/'s TypeScript code as needing a pytest-archon rule, or vice versa (language/tool mismatch).
- Fabricates additional historical violations beyond the one PR actually supplied.
- Skips or omits the merge-queue snippet despite the user confirming merge-queue usage.
- States the config has been wired into CI or committed anywhere.
