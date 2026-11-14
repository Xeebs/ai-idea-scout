# Scenario 2 — Small open-source library, lean AGENTS.md, team suspects nothing's wrong

## Setup

A solo maintainer of a mid-popularity Python CLI tool (a YAML-config validator, ~6k LOC, pytest-based, published to PyPI) pastes their `AGENTS.md`. Agent used: Codex CLI (`codex exec`). They supply two real recent task prompts they care about: "Add a new `--strict` flag that fails on unknown keys instead of warning" and "Fix the bug where nested anchors in YAML aliases aren't resolved before validation." The maintainer explicitly says: "I don't think this file is causing problems, I just want a sanity check since I saw that study."

Pasted file content:

```
# AGENTS.md

This is `yamlcheck`, a CLI tool for validating YAML configs against a
JSON-Schema-derived ruleset. Entry point is `yamlcheck/cli.py`.

## Running tests
`pytest tests/` — all new behavior needs a test in `tests/`, named after
the module it covers (e.g. `tests/test_cli.py` for `cli.py`).

## Schema resolution
Schema files live in `yamlcheck/schemas/*.yaml`. The resolver in
`yamlcheck/resolve.py` handles `$ref` expansion — if you touch alias/anchor
handling, it's in `yamlcheck/yaml_loader.py`, not `resolve.py`.

## Release process
Version bumps are manual: edit `pyproject.toml`, then run
`python -m build && twine upload dist/*`. Do not automate this — PyPI
publishing stays a manual, deliberate step for this project.
```

## Pass criteria

- [ ] Report segments the file into its 3 sections (Running tests, Schema resolution, Release process) plus the unheaded intro line, in document order.
- [ ] No section is flagged VERBOSE — correctly recognizes this file is already lean, repo-specific, and non-generic (contrast with scenario 1's "Code Style" section) rather than forcing a flag to pad the report.
- [ ] "Schema resolution" is at most flagged STALE-unverified (since the skill has no repo access here either) rather than asserted as actually wrong — the maintainer's own task prompts (nested-alias bug) suggest this section might be exactly on point, not stale, and the report should not contradict that without evidence.
- [ ] "Release process" is flagged exempt/carve-out-adjacent given it's a deliberate-publishing safety rule, even though it's short — report should not assign it a normal HIGH/MEDIUM/LOW score purely because it's brief.
- [ ] "Running tests" is either passed-triage or flagged LOW risk — not elevated to HIGH given its short, repo-specific, non-redundant content.
- [ ] Given how little is flagged, the "test this first" shortlist is short (0-2 entries) or explicitly states nothing significant was found — the skill does not invent 5 risky sections out of a 3-section, already-lean file just to fill out the shortlist format.
- [ ] Bottom line leans toward "file looks clean, a full paired run is optional" rather than manufacturing urgency — this is the key differentiator check: the skill must not always recommend the expensive A/B run regardless of input, or it's just generating alarm instead of triage.
- [ ] Report explicitly asked for or acknowledged working from pasted text only, consistent with the Manual data-source framing, and never claims to have read the actual repo files (`resolve.py`, `yaml_loader.py`) directly.
