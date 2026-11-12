# AI Idea Scout Dashboard

A small local web app for watching both pipeline tracks, changing idea
statuses, leaving feedback the pipeline actually reads, and
approving/rejecting Agensi.io listing candidates — from your phone, over
the home LAN. No build step, no JS framework, no auth (trusted home network
only — don't expose this beyond the LAN).

## Running it

Already running as a systemd user service (see below). To run it directly
instead:

```bash
cd /home/xhasan/my-projects/ai-idea-scout/dashboard
python3 app.py
```

Then from any device on the same wifi, open `http://192.168.68.68:8420/`
(swap in this machine's current LAN IP if it's changed — check with
`hostname -I`). On an iPhone, open it in Safari and use Share → **Add to
Home Screen** for a full-screen, chrome-less icon.

## systemd service

```bash
systemctl --user status ai-idea-scout-dashboard   # check it's running
systemctl --user restart ai-idea-scout-dashboard  # after editing app.py/templates
systemctl --user stop ai-idea-scout-dashboard      # stop it
journalctl --user -u ai-idea-scout-dashboard -f    # tail its logs
```

It's enabled to auto-start on boot, and `loginctl show-user xhasan` should
show `Linger=yes` so it keeps running even without an active login session.

## What it does

- **Dashboard** (`/`) — both tracks' current cycle/phase/topic, recent
  changelog activity, idea counts by status.
- **Infra Ideas** / **Market Ideas** (`/ideas/<track>`) — browse, filter by
  status, open any idea to read it in full.
- Idea detail — change status (`PROPOSED`/`EXPLORING`/`PROTOTYPING`/
  `SHELVED`), leave a feedback note (appended to a `## Human Feedback`
  section in the idea file — the orchestrator reads this before reworking
  that idea again).
- **Review Queue** (`/review`) — every packaged Agensi listing candidate,
  with its drafted listing copy inline. Approve, reject (with a reason), or
  mark listed (with the live URL) once you've actually uploaded it.
- **Feedback** (`/feedback`) — a global "steer the pipeline" note per track,
  read by the orchestrator at the start of every cycle.
- **Skills** / **Published** — read-only listings.

## How writes get committed

Every write (status change, feedback, review decision) saves to disk
immediately, then the app tries to `git commit` + `push` just that file —
to the public repo for INFRA, to the private `marketplace-content` repo's
own remote for MARKETPLACE. If a pipeline cycle happens to be running right
now (the loop fires them back-to-back continuously), the app skips the push rather than fight it for `.git/index.lock` — the
edit is still saved, and that cycle's own close-out will carry it along
within the hour. The flash message after each action tells you which
happened.

## Why no auth

The user's call: trusted home network, low stakes, simplicity over a
passcode gate. If that ever changes, add a shared-passcode check in
`app.py` before loosening network exposure beyond the LAN.
