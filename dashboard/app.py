#!/usr/bin/env python3
"""AI Idea Scout dashboard -- local LAN web app to watch both pipeline
tracks, approve/reject Agensi listing candidates, and leave feedback the
pipeline actually reads. No auth: trusted home network only. Not for
exposure beyond the LAN."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for, flash

from lib import parsers
from lib import git_sync

app = Flask(__name__)
app.secret_key = "ai-idea-scout-dashboard-local-only"  # no auth, LAN-only; just needed for flash()

app.jinja_env.filters["mdlite"] = parsers.render_md_lite


def _data_source_for(track, slug):
    path = os.path.join(parsers.TRACKS[track]["ideas_dir"], f"{slug}.md")
    idea = parsers.parse_idea_file(path)
    if not idea:
        return parsers.classify_data_source(None)
    return parsers.classify_data_source(idea["header"].get("Data Sources"))


def track_or_404(track):
    if track not in parsers.TRACKS:
        from flask import abort
        abort(404)
    return track


@app.context_processor
def inject_nav_counts():
    rows = parsers.parse_review_queue()
    pending = len([r for r in rows if r["status"] == "PENDING_REVIEW"])
    return {"nav_pending_review": pending}


@app.route("/")
def index():
    tracks = {}
    for key, cfg in parsers.TRACKS.items():
        state = parsers.read_state(key)
        ideas = parsers.parse_index(key)
        counts = {}
        for idea in ideas:
            if idea.get("unparsed"):
                continue
            counts[idea["status"]] = counts.get(idea["status"], 0) + 1
        tracks[key] = {
            "label": cfg["label"],
            "state": state,
            "changelog": parsers.tail_lines(cfg["changelog"], 5),
            "counts": counts,
            "total_ideas": len([i for i in ideas if not i.get("unparsed")]),
        }
    review_rows = parsers.parse_review_queue()
    pending_review = len([r for r in review_rows if r["status"] == "PENDING_REVIEW"])
    return render_template("index.html", tracks=tracks, pending_review=pending_review)


@app.route("/ideas/<track>")
def ideas_list(track):
    track_or_404(track)
    status_filter = request.args.get("status")
    ideas = parsers.parse_index(track)
    if status_filter:
        ideas = [i for i in ideas if i.get("status") == status_filter]
    for idea in ideas:
        if not idea.get("unparsed"):
            idea["ds_kind"], idea["ds_detail"] = _data_source_for(track, idea["slug"])
    return render_template(
        "ideas_list.html",
        track=track,
        label=parsers.TRACKS[track]["label"],
        ideas=ideas,
        status_filter=status_filter,
        statuses=parsers.STATUS_CHOICES + ["PUBLISHED"],
    )


@app.route("/ideas/<track>/<slug>")
def idea_detail(track, slug):
    track_or_404(track)
    path = os.path.join(parsers.TRACKS[track]["ideas_dir"], f"{slug}.md")
    idea = parsers.parse_idea_file(path)
    if idea is None:
        from flask import abort
        abort(404)
    ds_kind, ds_detail = parsers.classify_data_source(idea["header"].get("Data Sources"))
    return render_template(
        "idea_detail.html",
        track=track,
        label=parsers.TRACKS[track]["label"],
        slug=slug,
        idea=idea,
        statuses=parsers.STATUS_CHOICES,
        ds_kind=ds_kind,
        ds_detail=ds_detail,
    )


@app.route("/ideas/<track>/<slug>/status", methods=["POST"])
def idea_status(track, slug):
    track_or_404(track)
    new_status = request.form.get("status", "").strip().upper()
    if new_status not in parsers.STATUS_CHOICES:
        flash("Unrecognized status.", "error")
        return redirect(url_for("idea_detail", track=track, slug=slug))

    ok = parsers.update_idea_status(track, slug, new_status)
    if not ok:
        flash("Could not find that idea file.", "error")
        return redirect(url_for("idea_detail", track=track, slug=slug))

    cfg = parsers.TRACKS[track]
    rel_idea = os.path.relpath(os.path.join(cfg["ideas_dir"], f"{slug}.md"), cfg["root"])
    rel_index = os.path.relpath(cfg["index"], cfg["root"])
    synced, detail = git_sync.commit_and_push(
        cfg["root"], [rel_idea, rel_index], f"chore(dashboard): {slug} -> {new_status}"
    )
    flash(f"Status set to {new_status}. {detail}", "ok" if synced else "warn")
    return redirect(url_for("idea_detail", track=track, slug=slug))


@app.route("/ideas/<track>/<slug>/feedback", methods=["POST"])
def idea_feedback(track, slug):
    track_or_404(track)
    note = request.form.get("note", "").strip()
    if not note:
        flash("Feedback was empty, not saved.", "error")
        return redirect(url_for("idea_detail", track=track, slug=slug))

    ok = parsers.append_idea_feedback(track, slug, note)
    if not ok:
        flash("Could not find that idea file.", "error")
        return redirect(url_for("idea_detail", track=track, slug=slug))

    cfg = parsers.TRACKS[track]
    rel_idea = os.path.relpath(os.path.join(cfg["ideas_dir"], f"{slug}.md"), cfg["root"])
    synced, detail = git_sync.commit_and_push(
        cfg["root"], [rel_idea], f"chore(dashboard): feedback on {slug}"
    )
    flash(f"Feedback saved. {detail}", "ok" if synced else "warn")
    return redirect(url_for("idea_detail", track=track, slug=slug))


@app.route("/review")
def review_queue():
    rows = parsers.parse_review_queue()
    for row in rows:
        row["candidate"] = parsers.candidate_paths(row["slug"])
        row["status_key"] = row["status"].split(" ")[0].split("—")[0].strip()
        row["ds_kind"], row["ds_detail"] = _data_source_for("marketplace", row["slug"])
    return render_template("review_queue.html", rows=rows)


@app.route("/review/<slug>/decision", methods=["POST"])
def review_decision(slug):
    decision = request.form.get("decision")
    reason = request.form.get("reason", "").strip()
    if decision == "approve":
        new_cell = "APPROVED"
    elif decision == "reject":
        new_cell = f"REJECTED — {reason}" if reason else "REJECTED"
    else:
        flash("Unrecognized decision.", "error")
        return redirect(url_for("review_queue"))

    ok = parsers.update_review_row(slug, new_cell)
    if not ok:
        flash("Could not find that review row.", "error")
        return redirect(url_for("review_queue"))

    synced, detail = git_sync.commit_and_push(
        parsers.MARKETPLACE_ROOT, ["review-queue.md"], f"chore(dashboard): {slug} -> {new_cell}"
    )
    flash(f"{slug}: {new_cell}. {detail}", "ok" if synced else "warn")
    return redirect(url_for("review_queue"))


@app.route("/review/<slug>/listed", methods=["POST"])
def review_listed(slug):
    url = request.form.get("url", "").strip()
    new_cell = f"LISTED — {url}" if url else "LISTED"
    ok = parsers.update_review_row(slug, new_cell)
    if not ok:
        flash("Could not find that review row.", "error")
        return redirect(url_for("review_queue"))

    synced, detail = git_sync.commit_and_push(
        parsers.MARKETPLACE_ROOT, ["review-queue.md"], f"chore(dashboard): {slug} -> LISTED"
    )
    flash(f"{slug} marked LISTED. {detail}", "ok" if synced else "warn")
    return redirect(url_for("review_queue"))


@app.route("/feedback")
def feedback_home():
    entries = {key: parsers.parse_feedback_log(key) for key in parsers.TRACKS}
    return render_template("feedback.html", entries=entries, labels={k: v["label"] for k, v in parsers.TRACKS.items()})


@app.route("/feedback/<track>", methods=["POST"])
def feedback_submit(track):
    track_or_404(track)
    note = request.form.get("note", "").strip()
    if not note:
        flash("Feedback was empty, not saved.", "error")
        return redirect(url_for("feedback_home"))

    parsers.append_feedback(track, note)
    cfg = parsers.TRACKS[track]
    rel_feedback = os.path.relpath(cfg["feedback"], cfg["root"])
    synced, detail = git_sync.commit_and_push(
        cfg["root"], [rel_feedback], f"chore(dashboard): feedback for {cfg['label']}"
    )
    flash(f"Feedback saved. {detail}", "ok" if synced else "warn")
    return redirect(url_for("feedback_home"))


@app.route("/skills")
def skills_list():
    skills = {key: parsers.list_skills(key) for key in parsers.TRACKS}
    return render_template("skills_list.html", skills=skills, labels={k: v["label"] for k, v in parsers.TRACKS.items()})


@app.route("/published")
def published_list():
    items = parsers.list_published()
    return render_template("published_list.html", items=items)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8420, debug=False)
