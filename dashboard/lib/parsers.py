"""Read/write helpers for AI Idea Scout's markdown/JSON pipeline files.

Everything here is deliberately tolerant: a line that doesn't match the
expected shape is shown raw rather than raising, since these files are
hand-edited by humans (via this dashboard) as well as written by agents.
"""
import json
import os
import re
from datetime import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MARKETPLACE_ROOT = os.path.join(REPO_ROOT, "marketplace-content")

TRACKS = {
    "infra": {
        "root": REPO_ROOT,
        "state": os.path.join(REPO_ROOT, "pipeline", "state.json"),
        "queue": os.path.join(REPO_ROOT, "pipeline", "queue.md"),
        "changelog": os.path.join(REPO_ROOT, "pipeline", "changelog.md"),
        "index": os.path.join(REPO_ROOT, "ideas", "INDEX.md"),
        "ideas_dir": os.path.join(REPO_ROOT, "ideas"),
        "skills_dir": os.path.join(REPO_ROOT, "skills"),
        "feedback": os.path.join(REPO_ROOT, "pipeline", "feedback.md"),
        "label": "INFRA",
    },
    "marketplace": {
        "root": MARKETPLACE_ROOT,
        "state": os.path.join(MARKETPLACE_ROOT, "state.json"),
        "queue": os.path.join(MARKETPLACE_ROOT, "queue.md"),
        "changelog": os.path.join(MARKETPLACE_ROOT, "changelog.md"),
        "index": os.path.join(MARKETPLACE_ROOT, "INDEX.md"),
        "ideas_dir": os.path.join(MARKETPLACE_ROOT, "ideas"),
        "skills_dir": os.path.join(MARKETPLACE_ROOT, "skills"),
        "feedback": os.path.join(MARKETPLACE_ROOT, "feedback.md"),
        "label": "MARKETPLACE",
    },
}

STATUS_CHOICES = ["PROPOSED", "EXPLORING", "PROTOTYPING", "SHELVED"]


def now_stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def read_text(path, default=""):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def read_state(track):
    path = TRACKS[track]["state"]
    if not os.path.exists(path):
        return {"cycle": None, "current_phase": "UNKNOWN", "active_topic": None, "last_run": None}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def tail_lines(path, n=6):
    text = read_text(path)
    lines = [l for l in text.splitlines() if l.strip().startswith("- ")]
    return lines[-n:][::-1]


# --- INDEX.md parsing -------------------------------------------------

INDEX_LINE_RE = re.compile(
    r"^- \[(?P<title>.*?)\]\((?P<file>.*?)\)\s+—\s+(?P<hook>.*?)\s+·\s+"
    r"(?P<topic>.*?)\s+·\s+(?P<date>\d{4}-\d{2}-\d{2})\s+·\s+status:\s*(?P<status>[A-Z]+)(?P<extra>.*)$"
)


def parse_index(track):
    path = TRACKS[track]["index"]
    text = read_text(path)
    items = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("- ["):
            continue
        m = INDEX_LINE_RE.match(line)
        if m:
            d = m.groupdict()
            slug = os.path.splitext(os.path.basename(d["file"]))[0]
            fit_m = re.search(r"fit:\s*(LOW|MEDIUM|HIGH)", d["extra"])
            items.append({
                "slug": slug,
                "title": d["title"],
                "file": d["file"],
                "hook": d["hook"],
                "topic": d["topic"],
                "date": d["date"],
                "status": d["status"],
                "fit": fit_m.group(1) if fit_m else None,
                "extra": d["extra"].strip(" ·"),
                "raw": line,
            })
        else:
            items.append({"slug": None, "raw": line, "unparsed": True})
    return items


def update_index_status(track, slug, new_status):
    path = TRACKS[track]["index"]
    text = read_text(path)
    out_lines = []
    changed = False
    for line in text.splitlines():
        if line.strip().startswith("- [") and f"({slug}.md)" in line:
            new_line = re.sub(r"status:\s*[A-Z]+", f"status: {new_status}", line, count=1)
            out_lines.append(new_line)
            changed = True
        else:
            out_lines.append(line)
    if changed:
        write_text(path, "\n".join(out_lines) + ("\n" if text.endswith("\n") else ""))
    return changed


# --- Idea file parsing --------------------------------------------------

HEADER_FIELD_RE = re.compile(r"^-\s+\*\*(?P<key>[^*]+)\*\*:\s*(?P<value>.*)$")
SECTION_RE = re.compile(r"^##\s+(?P<name>.+?)\s*$")


def parse_idea_file(path):
    text = read_text(path)
    if not text:
        return None
    lines = text.splitlines()
    title = lines[0].lstrip("# ").strip() if lines else ""
    header = {}
    sections = {}
    current_section = None
    body_lines = []
    for line in lines[1:]:
        m = SECTION_RE.match(line)
        if m:
            if current_section:
                sections[current_section] = "\n".join(body_lines).strip()
            current_section = m.group("name").strip()
            body_lines = []
            continue
        if current_section is None:
            hm = HEADER_FIELD_RE.match(line.strip())
            if hm:
                header[hm.group("key").strip()] = hm.group("value").strip()
            continue
        body_lines.append(line)
    if current_section:
        sections[current_section] = "\n".join(body_lines).strip()
    return {"title": title, "header": header, "sections": sections, "raw": text}


def update_idea_status(track, slug, new_status):
    path = os.path.join(TRACKS[track]["ideas_dir"], f"{slug}.md")
    text = read_text(path)
    if not text:
        return False
    new_text = re.sub(
        r"(-\s+\*\*Status\*\*:\s*)[A-Z]+",
        lambda m: m.group(1) + new_status,
        text,
        count=1,
    )
    write_text(path, new_text)
    update_index_status(track, slug, new_status)
    return True


def append_idea_feedback(track, slug, note):
    path = os.path.join(TRACKS[track]["ideas_dir"], f"{slug}.md")
    text = read_text(path)
    if not text:
        return False
    stamp = now_stamp()
    entry = f"- {stamp} — \"{note.strip()}\" (via dashboard)"
    if "## Human Feedback" in text:
        # Append under the existing section, right after its last bullet.
        lines = text.splitlines()
        out = []
        inserted = False
        in_section = False
        for i, line in enumerate(lines):
            out.append(line)
            if line.strip() == "## Human Feedback":
                in_section = True
                continue
            if in_section and not inserted:
                nxt = lines[i + 1] if i + 1 < len(lines) else None
                if nxt is None or nxt.strip().startswith("## ") or nxt.strip() == "":
                    out.append(entry)
                    inserted = True
                    in_section = False
        if not inserted:
            out.append(entry)
        write_text(path, "\n".join(out) + "\n")
    else:
        new_text = text.rstrip() + f"\n\n## Human Feedback\n{entry}\n"
        write_text(path, new_text)
    return True


def list_ideas_with_feedback_pending_review(track):
    """Ideas that have unresolved feedback the pipeline hasn't acted on yet is
    not tracked separately; the dashboard just displays whatever is in the
    file. Kept as a helper seam for future use."""
    return []


# --- Feedback log (global, per track) -----------------------------------

FEEDBACK_HEADER = (
    "# Feedback / Redirection Log\n\n"
    "Appended by the dashboard; consumed by the orchestrator at Phase 0 of "
    "each cycle, which marks entries CONSUMED once incorporated. Never "
    "delete entries.\n\n"
)

FEEDBACK_LINE_RE = re.compile(
    r"^-\s+\[(?P<status>UNCONSUMED|CONSUMED(?:\s+cycle\s+\d+)?)\]\s+"
    r"(?P<stamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s+—\s+(?P<text>.*)$"
)


def parse_feedback_log(track):
    path = TRACKS[track]["feedback"]
    text = read_text(path)
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("- ["):
            continue
        m = FEEDBACK_LINE_RE.match(line)
        if m:
            entries.append(m.groupdict())
        else:
            entries.append({"status": "?", "stamp": "", "text": line, "unparsed": True})
    return entries[::-1]


def append_feedback(track, note):
    path = TRACKS[track]["feedback"]
    text = read_text(path)
    if not text:
        text = FEEDBACK_HEADER
    stamp = now_stamp()
    entry = f"- [UNCONSUMED] {stamp} — {note.strip()}\n"
    write_text(path, text.rstrip() + "\n" + entry)


# --- Review queue (marketplace only) ------------------------------------

def parse_review_queue():
    path = os.path.join(MARKETPLACE_ROOT, "review-queue.md")
    text = read_text(path)
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 5:
            continue
        if cells[0] in ("Date", "------"):
            continue
        if set(cells[0]) <= {"-"}:
            continue
        rows.append({
            "date": cells[0],
            "slug": cells[1],
            "title": cells[2],
            "price": cells[3],
            "status": cells[4],
        })
    return rows[::-1]


def update_review_row(slug, new_status_cell):
    path = os.path.join(MARKETPLACE_ROOT, "review-queue.md")
    text = read_text(path)
    out_lines = []
    changed = False
    for line in text.splitlines():
        if line.strip().startswith("|") and f"| {slug} |" in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 5:
                cells[4] = new_status_cell
                out_lines.append("| " + " | ".join(cells) + " |")
                changed = True
                continue
        out_lines.append(line)
    if changed:
        write_text(path, "\n".join(out_lines) + "\n")
    return changed


def candidate_paths(slug):
    cand_dir = os.path.join(MARKETPLACE_ROOT, "candidates", slug)
    listing = os.path.join(cand_dir, "LISTING.md")
    zip_path = os.path.join(MARKETPLACE_ROOT, "candidates", f"{slug}.zip")
    return {
        "dir": cand_dir,
        "listing_path": listing,
        "listing": read_text(listing),
        "zip_exists": os.path.exists(zip_path),
        "zip_path": zip_path,
    }


# --- Skills / published (read-only listings) ----------------------------

def list_skills(track):
    skills_dir = TRACKS[track]["skills_dir"]
    if not os.path.isdir(skills_dir):
        return []
    out = []
    for slug in sorted(os.listdir(skills_dir)):
        full = os.path.join(skills_dir, slug)
        skill_md = os.path.join(full, "SKILL.md")
        if os.path.isdir(full) and os.path.exists(skill_md):
            parsed = parse_idea_file(skill_md)
            desc = ""
            if parsed:
                fm = re.search(r"description:\s*(.*)", parsed["raw"])
                if fm:
                    desc = fm.group(1).strip()
            out.append({"slug": slug, "description": desc})
    return out


def classify_data_source(value):
    """Split a Data Sources header value into (kind, detail) for badge
    rendering. kind is 'connected', 'manual', or 'unspecified' (older ideas
    written before this field existed)."""
    if not value:
        return "unspecified", None
    v = value.strip()
    upper = v.upper()
    if upper.startswith("CONNECTED"):
        return "connected", v[len("CONNECTED"):].lstrip(" :—-").strip() or None
    if upper.startswith("MANUAL"):
        return "manual", v[len("MANUAL"):].lstrip(" :—-").strip() or None
    return "unspecified", v


def render_md_lite(text):
    """Minimal, dependency-free markdown-ish rendering for idea/skill bodies:
    HTML-escapes first, then handles **bold**, `code`, '- ' bullet lists, and
    blank-line paragraphs. Not a general markdown parser -- these files are
    all written to a fixed, known structure."""
    import html as _html
    if not text:
        return ""
    escaped = _html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', escaped)

    lines = escaped.splitlines()
    out = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{stripped[2:]}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if stripped == "":
            out.append("")
        else:
            out.append(f"<p>{stripped}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def list_published():
    pub_dir = os.path.join(REPO_ROOT, "published")
    if not os.path.isdir(pub_dir):
        return []
    out = []
    for fname in sorted(os.listdir(pub_dir)):
        if fname.endswith(".md"):
            slug = fname[:-3]
            parsed = parse_idea_file(os.path.join(pub_dir, fname))
            out.append({"slug": slug, "title": parsed["title"] if parsed else slug})
    return out
