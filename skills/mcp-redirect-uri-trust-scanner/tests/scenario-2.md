# Scenario 2 — Python/FastAPI MCP server, mostly correct, one subtle gap (expect WARN/FAIL on a single check, not a blanket verdict)

## Setup

A developer has already read the MCP spec's security-considerations section and implemented exact-match redirect-URI validation and DCR pinning correctly. They want a second opinion before launch. This tests whether the skill can find one real, narrow gap in an otherwise solid implementation instead of either rubber-stamping it PASS or falsely flagging things that are actually fine.

## Input (pasted code)

```python
from urllib.parse import urlparse
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()
clients = {}          # client_id -> {"redirect_uri": str}
auth_codes = {}        # code -> {"client_id": str, "redirect_uri": str}

@app.post("/register")
async def register(req: Request):
    body = await req.json()
    client_id = generate_client_id()
    clients[client_id] = {"redirect_uri": body["redirect_uris"][0]}
    return {"client_id": client_id, "redirect_uris": body["redirect_uris"]}

def same_redirect(registered: str, supplied: str) -> bool:
    r, s = urlparse(registered), urlparse(supplied)
    if r.hostname in ("localhost", "127.0.0.1") and s.hostname in ("localhost", "127.0.0.1"):
        # loopback clients use an ephemeral port — allow host+path match, ignore port
        return r.scheme == s.scheme and r.hostname == s.hostname and r.path == s.path
    # non-loopback: full exact match including port
    return (r.scheme, r.hostname, r.port, r.path) == (s.scheme, s.hostname, s.port, s.path)

@app.get("/authorize")
async def authorize(client_id: str, redirect_uri: str, state: str):
    client = clients.get(client_id)
    if not client:
        raise HTTPException(400, "unknown client")
    if not same_redirect(client["redirect_uri"], redirect_uri):
        raise HTTPException(400, "redirect_uri mismatch")
    code = issue_auth_code()
    auth_codes[code] = {"client_id": client_id, "redirect_uri": redirect_uri}
    return RedirectResponse(f"{redirect_uri}?code={code}&state={state}")

@app.post("/token")
async def token(code: str, client_id: str):
    record = auth_codes.pop(code, None)
    if not record or record["client_id"] != client_id:
        raise HTTPException(400, "invalid code")
    # redirect_uri from the original /authorize call is available in `record`
    # but this handler does not require or check a redirect_uri parameter at all
    access_token = issue_access_token(client_id)
    return {"access_token": access_token, "token_type": "Bearer"}
```

Stated inputs to the skill: Python, DCR supported = yes, library = hand-rolled (FastAPI).

## Expected output characteristics (pass/fail criteria for the skill)

The skill's output PASSES this test if it:

1. Marks **Check 1 (exact-match redirect-URI validation) PASS** — `same_redirect` does real parsed-URL comparison for the non-loopback case, citing the function.
2. Marks **Check 2 (localhost/SEP-837) PASS** — loopback host+scheme+path matched exactly, only port ignored, which is the sanctioned exception. (Does not falsely flag this as a wildcard problem.)
3. Marks **Check 3 (DCR trust gap) PASS** — `redirect_uri` is captured at `/register` and re-validated by exact parsed comparison on every `/authorize` call via `same_redirect`.
4. Marks **Check 4 (URL-parsing correctness) PASS** — uses `urlparse` and compares discrete fields (scheme/hostname/port/path), not string prefix matching, so userinfo-style bypasses (`https://trusted@evil.com`) wouldn't fool it (`urlparse` puts `evil.com` in `.hostname`, not `trusted`).
5. Marks **Check 5 (auth-code binding at redemption) FAIL** — citing specifically that `/token` never requires or checks a `redirect_uri` parameter, even though `record["redirect_uri"]` is available from the stored auth code; a stolen/intercepted code plus a known `client_id` could be redeemed without proving control of the original redirect target.
6. **Overall verdict is FAIL** (because Check 5 fails) — not a blanket PASS just because most of the implementation is solid, and not a FAIL that misattributes the problem to the wrong check (e.g., incorrectly flagging Check 1 or Check 2, which are genuinely correct here).
7. The "highest-priority fix" names Check 5 specifically and suggests requiring `redirect_uri` as a parameter on `/token` and comparing it to `record["redirect_uri"]` (or implementing PKCE `code_verifier` binding), with a runnable Python snippet.

FAILS this test if the skill gives a blanket overall PASS, if it misses the Check 5 gap, if it incorrectly flags Checks 1–4 as failing (false positives on code that is actually correct), or if it cannot distinguish the sanctioned loopback port exception in Check 2 from a real wildcard vulnerability.
