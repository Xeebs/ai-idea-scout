# Scenario 1 — Note-taking CLI, no collisions

## Input (what the user pastes)

**App's command surface:**

```
App: quicknote (a local note-taking CLI)

Commands:
  quicknote new "<title>" "<body>"     -- create a new note
  quicknote list                       -- list all notes
  quicknote delete <id>                -- permanently delete a note by id
  quicknote search "<query>"           -- search notes by keyword
```

**Other apps' manifests:** none provided (section deleted, per the README instructions).

## Expected behavior

The skill should:
1. Extract four discrete intents: `quicknote.new`, `quicknote.list`, `quicknote.delete`, `quicknote.search`.
2. Set callback `type: "exec"` for all four, with `target` set to the exact CLI command string given (e.g. `quicknote new "<title>" "<body>"`), not an invented REST path.
3. Draft 3-5 natural spoken trigger phrases per intent (e.g. for `new`: "take a note", "create a new note", "write this down"; for `delete`: "delete that note", "remove this note").
4. Flag `quicknote.delete` as destructive (`"confirm_required": true`) with a recommendation for a longer/more distinct phrase or an explicit confirm step, since "permanently delete" is stated directly in the command description.
5. Collision report section states "No collisions found against the manifests provided" (since none were given) rather than fabricating a comparison.
6. Open questions section notes nothing about callback targets (all four were fully specified) but does flag the `delete` intent's confirmation requirement as the one open decision.

## Pass/fail criteria

- PASS if: all 4 intents appear with correct namespacing, `exec` callbacks use the user's literal command strings (no invented flags/paths), `delete` is marked `confirm_required: true` with a stated reason, the collision section correctly reports none found (not silently omitted, not fabricated), and the JSON is valid and parses.
- FAIL if: the skill invents a REST endpoint or socket path never mentioned, fails to flag `delete` as destructive, merges multiple commands into one intent, or presents a collision table with invented conflicting apps.
