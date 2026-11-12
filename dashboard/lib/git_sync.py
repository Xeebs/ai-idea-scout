"""Commit + push a dashboard edit without racing the continuous pipeline loop.

If the heartbeat lock is held (a cycle is running right now -- the loop
fires cycles back-to-back with no idle gap), we back off rather than fight
it for .git/index.lock -- the edit is already saved to disk, and the next
cycle's own close-out sweep (which stages these same paths, or uses
`git add -A` for marketplace-content) will carry it along, so nothing is
ever lost, just possibly committed a little later than this request.
"""
import subprocess
import time

HEARTBEAT_LOCK = "/tmp/ai-idea-scout-heartbeat.lock"
LOCK_WAIT_SECONDS = 10
LOCK_POLL_INTERVAL = 1


def _lock_held():
    import os
    return os.path.exists(HEARTBEAT_LOCK)


def _run(cmd, cwd):
    return subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, timeout=60
    )


def commit_and_push(repo_dir, paths, message):
    """Returns (ok: bool, detail: str). ok=False means "saved to disk, not
    yet committed" -- never means the edit was lost."""
    waited = 0.0
    while _lock_held() and waited < LOCK_WAIT_SECONDS:
        time.sleep(LOCK_POLL_INTERVAL)
        waited += LOCK_POLL_INTERVAL
    if _lock_held():
        return False, "Saved locally. A pipeline cycle is running right now, so this will be committed by its own close-out shortly rather than right now."

    try:
        add = _run(["git", "add"] + list(paths), repo_dir)
        if add.returncode != 0:
            return False, f"Saved locally, but `git add` failed: {add.stderr.strip()}"

        status = _run(["git", "status", "--porcelain"] + list(paths), repo_dir)
        if not status.stdout.strip():
            return True, "No change to commit (file already matched)."

        commit = _run(["git", "commit", "-m", message], repo_dir)
        if commit.returncode != 0:
            return False, f"Saved locally, but `git commit` failed: {commit.stderr.strip() or commit.stdout.strip()}"

        push = _run(["git", "push", "origin", "main"], repo_dir)
        if push.returncode != 0:
            return False, f"Committed locally, but `git push` failed: {push.stderr.strip()}"

        return True, "Saved and pushed."
    except subprocess.TimeoutExpired:
        return False, "Saved locally, but the git operation timed out."
    except Exception as e:  # noqa: BLE001 - surface any failure to the UI, never crash the request
        return False, f"Saved locally, but syncing failed: {e}"
