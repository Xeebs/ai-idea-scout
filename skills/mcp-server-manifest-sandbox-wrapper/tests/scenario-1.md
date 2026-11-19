# Scenario 1: A notes/file-management MCP server with one mismatched tool

## Input

The user pastes this manifest (as if obtained via a `tools/list` call against a hypothetical "quicknotes-mcp" server) and asks for a sandbox policy draft. No repo URL is given.

```json
{
  "tools": [
    {
      "name": "read_note",
      "description": "Read a note file by relative path from the notes vault directory (~/notes-vault).",
      "inputSchema": {
        "type": "object",
        "properties": {
          "path": { "type": "string", "description": "Relative path within ~/notes-vault, e.g. 'daily/2026-11-19.md'" }
        },
        "required": ["path"]
      }
    },
    {
      "name": "write_note",
      "description": "Create or overwrite a note file by relative path within the notes vault directory (~/notes-vault).",
      "inputSchema": {
        "type": "object",
        "properties": {
          "path": { "type": "string" },
          "content": { "type": "string" }
        },
        "required": ["path", "content"]
      }
    },
    {
      "name": "list_notes",
      "description": "List all note filenames in the vault directory, optionally filtered by a subfolder.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "subfolder": { "type": "string" }
        }
      }
    },
    {
      "name": "sync_to_cloud",
      "description": "Back up the notes vault to the user's configured cloud storage endpoint (api.quicknotes-sync.com).",
      "inputSchema": {
        "type": "object",
        "properties": {
          "force": { "type": "boolean" }
        }
      }
    },
    {
      "name": "get_word_count",
      "description": "Return the word count for a given note, by shelling out to `wc -w` on the resolved file path for speed.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "path": { "type": "string" }
        },
        "required": ["path"]
      }
    }
  ]
}
```

## Pass/fail criteria

- [ ] **Filesystem scope correctly narrowed**: the policy table's filesystem row scopes to `~/notes-vault` (not an unqualified "any path"), attributing it to `read_note`, `write_note`, and `list_notes`.
- [ ] **Network scope correctly extracted**: the policy table has a network row scoped to `api.quicknotes-sync.com`, attributed to `sync_to_cloud` — not left as "unstated," since the domain is explicitly named in the description.
- [ ] **Exec capability surfaced**: `get_word_count` is identified as implying an exec capability (it shells out to `wc`), even though its name/description reads as benign counting — this is the scenario's core test. A correct run lists `wc` (or "shell command, binary `wc`") in the policy table's exec row and, ideally, also raises it as a flag since a word-count tool invoking a subprocess rather than counting in-process is a mild mismatch worth a human's attention.
- [ ] **No fabricated scope**: the report does not invent a broader filesystem path (e.g. full home directory) or an unlisted domain anywhere not present in the manifest.
- [ ] **Raw JSON policy block present** and matches the table (fs: `~/notes-vault`; net: `api.quicknotes-sync.com`; exec: `wc`).
- [ ] **Confidence rated High or Medium** (not Low) — most tools here have explicit, stated scope, so an honest confidence rating should reflect that rather than defaulting to a vague "Low" out of caution.
