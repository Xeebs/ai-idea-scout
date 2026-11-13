# Scenario 1 — Node.js MCP server with naive prefix matching (expect FAIL)

## Setup

A developer is self-hosting an MCP server in Node/Express that supports Dynamic Client Registration so any MCP client (Claude Desktop, a custom agent, etc.) can connect without being pre-approved. They paste this code and ask for a trust scan before deploying to a small production user base.

## Input (pasted code)

```js
// in-memory client store: { clientId: { redirectUri, name } }
const clients = {};

app.post('/register', (req, res) => {
  const clientId = crypto.randomUUID();
  const { redirect_uris, client_name } = req.body;
  clients[clientId] = { redirectUri: redirect_uris[0], name: client_name };
  res.json({ client_id: clientId, redirect_uris });
});

app.get('/authorize', (req, res) => {
  const { client_id, redirect_uri, state } = req.query;
  const client = clients[client_id];
  if (!client) return res.status(400).send('unknown client');

  // "security" check — just make sure it starts with something plausible
  if (!redirect_uri.startsWith('https://') && !redirect_uri.startsWith('http://localhost')) {
    return res.status(400).send('bad redirect_uri scheme');
  }

  const code = issueAuthCode(client_id, redirect_uri);
  res.redirect(`${redirect_uri}?code=${code}&state=${state}`);
});

app.post('/token', (req, res) => {
  const { code, client_id } = req.body;
  const record = consumeAuthCode(code);
  if (!record || record.clientId !== client_id) return res.status(400).send('invalid code');
  // note: redirect_uri is not re-checked here at all
  const token = issueAccessToken(client_id);
  res.json({ access_token: token, token_type: 'Bearer' });
});
```

Stated inputs to the skill: Node.js, DCR supported = yes, library = hand-rolled.

## Expected output characteristics (pass/fail criteria for the skill)

The skill's output PASSES this test if it:

1. Marks **overall verdict FAIL**.
2. Flags **Check 1 (exact-match redirect-URI validation) as FAIL**, citing the `/authorize` handler's scheme-only check (`startsWith('https://')`) as evidence — not an exact match against `client.redirectUri` at all; the registered `redirect_uri` from `/register` is never even read in `/authorize`.
3. Flags **Check 3 (DCR trust gap) as FAIL**, citing that `clients[clientId].redirectUri` is stored at registration but never read/compared in `/authorize` — any `redirect_uri` the authorize request supplies is accepted regardless of what was registered.
4. Flags **Check 4 (URL-parsing correctness) as FAIL or WARN**, noting `startsWith` string matching would accept attacker-controlled hosts like `https://evil.com` (scheme check alone proves nothing about the host) and a userinfo trick like `http://localhost@evil.com` would pass the localhost prefix check.
5. Flags **Check 5 (auth-code binding at redemption) as FAIL**, citing the `/token` handler's explicit comment/behavior that `redirect_uri` is not re-checked at code redemption.
6. Check 2 (localhost/SEP-837) may be marked WARN or FAIL (loopback gets no special real validation either since there's no real validation at all) — either is acceptable as long as it isn't marked a clean PASS.
7. The "highest-priority fix" section names the concrete attack: a malicious actor can register their own fake client or simply pass any `redirect_uri` to `/authorize` for any `client_id`, since nothing is compared — the authorization code and token are deliverable to an attacker-controlled endpoint.
8. The suggested fix is runnable Node.js code (not pseudocode) that stores and exact-matches `redirect_uri` by parsed URL, e.g. using `new URL()` and comparing `.protocol`, `.host`, `.pathname`.

FAILS this test if the skill outputs an overall PASS or WARN, if it gives Check 1 or Check 3 a PASS, or if it treats the library as safe without pointing to the specific missing comparison in the pasted code.
