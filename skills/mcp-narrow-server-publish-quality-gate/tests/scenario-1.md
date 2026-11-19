# Scenario 1 — WhatsApp wrapper MCP server, repo URL given

## Input

A user says: "I just finished this and I'm about to submit it to the MCP registry — can you review it first? `https://github.com/example-user/whatsapp-mcp-server`"

The repo (realistic shape, modeled on the Show-HN-style single-API wrapper servers cited in the parent idea) contains a `server.py` that registers five tools:

```python
@tool
def send_message(to: str, body: str):
    """Sends a WhatsApp message."""
    ...

@tool
def send_media(to: str, media_url: str, caption: str = ""):
    """Sends media."""
    ...

@tool
def get_messages(contact: str, since: int = 0):
    """Gets messages for a contact since a given timestamp."""
    ...

@tool
def delete_message(message_id: str):
    """Deletes a message."""
    ...

@tool
def list_contacts():
    """Returns the full contact list."""
    ...
```

`README.md` states the server requires an OAuth connection with the `whatsapp.full_access` scope (read, write, delete, and account management), and all five tools above only ever read messages/contacts or send/delete messages — none touch account settings.

No pagination parameter exists on `list_contacts` or `get_messages`. `since` on `get_messages` has no documented unit (could be seconds or milliseconds epoch). `delete_message` has no confirmation parameter.

## Expected output characteristics (pass/fail criteria)

A passing run of the skill must:

1. **List all 5 tools by name** before scoring anything (step 1 of the procedure) — fail if it invents a 6th tool or misses one of the five.
2. **Flag `delete_message` as FAIL** under destructive-action safeguards — no confirmation param on an irreversible delete. This is the single most important catch; a run that misses this fails the scenario outright.
3. **Flag `list_contacts` as FAIL or WARN** under pagination — it can return an unbounded list with no limit/cursor param.
4. **Flag `get_messages`'s `since` parameter** under units/ambiguous values — no unit specified for the timestamp (seconds vs ms epoch is genuinely ambiguous).
5. **Flag the permission scope mismatch**: `whatsapp.full_access` (including delete/account-management) requested while only messaging read/write/delete tools exist — should be at least WARN, arguably FAIL since delete scope IS used but account-management isn't — a reasonable run flags the account-management portion as unused scope.
6. **Must NOT flag `send_message` or `send_media`** for destructive-action safeguards (sending a message is not classified the same as delete in the rubric, though a strict reviewer noting "send" also has real-world consequences and flagging it WARN for "no undo" is acceptable as a WARN, not required).
7. **Overall verdict must be FAIL** (since at least one FAIL finding — delete_message — exists). A run that returns PASS or WARN here fails the scenario.
8. Output must include the "Not covered by this review" disclaimer mentioning conformance/security tooling.

Fails the scenario if: it skips listing tools first, misses the delete_message confirmation gap, fabricates a tool not in the repo, or claims a specific CVE/exploit (which would be fabricating a security claim beyond what the schema shows).
