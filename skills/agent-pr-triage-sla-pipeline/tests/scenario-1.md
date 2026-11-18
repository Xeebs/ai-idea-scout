# Scenario 1: Oversized agent-authored feature PR touching auth

## Context
A team lead at a mid-size SaaS company has a pull request opened by their Devin-style coding agent. It's been sitting in the review queue for three days with no reviewer assignment under the team's flat "review within a week" SLA. The lead wants a quick triage read before deciding whether to escalate it or let it keep waiting.

## Input handed to the skill

**PR title/description**: "Add team-based permission groups and migrate existing per-user roles to group membership"

**Changed files with added/deleted line counts**:
```
db/migrations/0047_add_permission_groups.sql       +85 / -0
app/models/permission_group.py                     +120 / -0
app/models/user.py                                  +40 / -15
app/services/auth/role_resolver.py                  +95 / -30
app/services/auth/session_middleware.py             +35 / -10
app/api/v1/admin/groups_controller.py               +180 / -0
app/api/v1/admin/groups_routes.py                   +25 / -0
frontend/src/admin/GroupManager.tsx                 +210 / -0
frontend/src/admin/GroupManager.test.tsx            +90 / -0
frontend/src/admin/api/groupsClient.ts               +45 / -0
docs/admin-guide.md                                  +30 / -5
```
Total: 11 files, ~955 added / 60 deleted lines ≈ 1015 lines changed.

**Confirmation**: Agent-authored (Devin), not yet reviewed.

## Expected output (what a correct run looks like)

- **Size tier**: Large (1015 lines changed, 11 files touched — exceeds the >400 lines / >15-files-OR threshold on the lines side).
- **Change type**: High (touches auth/permission logic, a database migration, and session middleware — multiple High-sensitivity signals).
- **Risk tier**: Tier 3 (Large × High).
- **SLA**: pickup within 4 business hours, named senior/lead reviewer required, no auto-merge.
- **Decomposition recommendation**: triggered (Large + Tier 3). A reasonable split groups by module:
  1. Migration + backend permission model/resolver (`db/migrations/0047...`, `permission_group.py`, `user.py`, `role_resolver.py`, `session_middleware.py`) — the core auth change, must ship together since the migration and model/resolver are tightly coupled.
  2. Admin API endpoints (`groups_controller.py`, `groups_routes.py`) — depends on #1 but is separately reviewable for API design.
  3. Frontend admin UI (`GroupManager.tsx`, its test, `groupsClient.ts`) — depends on #2's API shape but independently reviewable for UI/UX.
  4. Docs update — could ride with any of the above or go last.
- Explicit note that the migration file and the models/resolver that depend on it must stay together (a naive "split by file count" could wrongly separate the migration from `permission_group.py`).
- Includes the human-override line and does not claim to block or auto-merge anything.

## Pass criteria
- [ ] Correctly computes Large size tier and shows the arithmetic/reasoning (not just an asserted tier).
- [ ] Correctly identifies High change type citing auth/migration/session signals specifically (not a vague "looks risky").
- [ ] Assigns Tier 3 and the 4-business-hour / named-senior-reviewer SLA.
- [ ] Recommends decomposition (since Large + Tier 2/3) with file-grouped splits, not an arbitrary "split into 3 equal parts."
- [ ] Flags the migration-to-model coupling as a keep-together exception rather than splitting purely by file list order.
- [ ] Includes the human-override disclaimer and does not present the recommendation as a binding gate.
- [ ] Does not assert the 4.6-5.3x/1.7x industry figures as facts about this specific PR.

## Fail conditions
- Misclassifies this as Tier 1/2, or Medium/Small size.
- Splits the migration away from its dependent model file without flagging the coupling.
- Fabricates reviewer names or specific SLA-breach history not provided in the input.
- Omits the decomposition recommendation despite the PR qualifying for one.
