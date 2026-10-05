#!/usr/bin/env python3
# <<<<<<< threads.py, bot council starter kit, version 1.0 >>>>>>>
# One tool for every thread's public posts. General version of Tony's
# Nexus threads.py. All personal settings live in settings.txt.
#
# Commands (see README for the full walk-through):
#   python threads.py setup NAME        make the four files if missing
#   python threads.py card NAME         print NAME's public addresses
#   python threads.py handoff NAME      print NAME's first handoff to paste
#   python threads.py show NAME         print unread updates
#   python threads.py update NAME FILE  add FILE to NAME's updates post
#   python threads.py note NAME FILE    add FILE to NAME's cross-reference post
#   python threads.py clear NAME        move read updates into the archive
#   python threads.py archive NAME SOURCE FILE [TAGS...]
#
# Safety rules this tool follows, copied from Tony's version:
# - Never deletes a file. setup leaves existing posts alone.
# - update and note refuse a file without a tags line, and refuse text
#   that is already there. update also checks the archive.
# - archive refuses a file whose text is already in that archive.
# - clear and cross-reference trimming back up the live post to BACKUPS,
#   write the archive, check it landed, and only then trim the live post.
# - If anything is missing, it stops, says so, and changes nothing.

import datetime
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARKER = "== ENTRIES BELOW =="
TODAY = datetime.date.today().isoformat()
NOW = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
DASHES = "-" * 64
SEP_LINE = re.compile(r"^-{20,}[ \t]*$", re.M)
ENTRY_LINE = re.compile(r"^----- added (\d{4}-\d{2}-\d{2}) -----[ \t]*$", re.M)
XREF_LIMIT = 30
XREF_MOVE = 20


def stop(msg):
    print("STOPPING, nothing changed: " + msg)
    sys.exit(1)


def load_settings():
    path = os.path.join(HERE, "settings.txt")
    if not os.path.isfile(path):
        stop("settings file not found: " + path)
    s = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                s[key.strip()] = value.strip()
    return s


S = load_settings()
SITE = S.get("SITE", "http://localhost:8080/").rstrip("/") + "/"
PUBLIC_NAME = S.get("PUBLIC", "public")
BACKUPS_NAME = S.get("BACKUPS", "backups")
TEMPLATES_NAME = S.get("TEMPLATES", "templates")
OWNER = S.get("OWNER", "Your Name")
PORT = S.get("PORT", "8080")
PUBLIC = PUBLIC_NAME if os.path.isabs(PUBLIC_NAME) else os.path.join(HERE, PUBLIC_NAME)
BACKUPS = BACKUPS_NAME if os.path.isabs(BACKUPS_NAME) else os.path.join(HERE, BACKUPS_NAME)
TEMPLATES = TEMPLATES_NAME if os.path.isabs(TEMPLATES_NAME) else os.path.join(HERE, TEMPLATES_NAME)


def refresh_container_env(port):
    env_dir = os.path.join(HERE, "container")
    if os.path.isdir(env_dir):
        with open(os.path.join(env_dir, ".env"), "w", encoding="utf-8") as f:
            f.write("PORT=" + str(port).strip() + "\n")


refresh_container_env(PORT)

UPDATES_HEAD = """# UPDATES - {NAME} THREAD

Public. Nothing sensitive in here, ever.

What this is: news and requests from OTHER threads that thread {NAME}
has not read yet. Anything below the marker line is unread. Read it at
the start of a session, act on it, then clear it into the archive:
{SITE}ARCHIVE-{NAME}.md

How to add (another thread hands you a file and this command):
python threads.py update {NAME} FILE
The file's first line must be a tags line, like: tags: nginx, nexus

History that needs no action goes in the cross-reference post instead:
{SITE}CROSSREF-{NAME}.md

Made {TODAY}.

""" + MARKER + "\n"

CROSSREF_HEAD = """# CROSS-REFERENCE - {NAME} THREAD

Public. Nothing sensitive in here, ever.

What this is: a history of things OTHER threads did that may affect
thread {NAME}. No action needed on any entry. Entries are never edited;
a correction goes in a newer dated entry. Anything that needs a response
goes in the updates post instead:
{SITE}UPDATES-{NAME}.md

How to add (the thread that did the thing hands you a file and this command):
python threads.py note {NAME} FILE
The file's first line must be a tags line, like: tags: nginx, nexus

Past 30 entries, the oldest 20 move to this thread's archive:
{SITE}ARCHIVE-{NAME}.md

Made {TODAY}.

""" + DASHES + "\n"

ARCHIVE_HEAD = """# ARCHIVE - {NAME}

Public. Nothing sensitive in here, ever.

Everything archived for {NAME}, oldest first: read updates, older
cross-reference entries, old editions of public documents, and
reference entries pointing at private files (path, date and tags only,
never their contents). Nothing here needs action.

Every piece starts with one line: the date it was archived, where it
came from, and its tags. Search it, for example:
grep -n "tags:.*nginx" {PUBLIC}/ARCHIVE-{NAME}.md
grep -n "archived 2026-10-0" {PUBLIC}/ARCHIVE-{NAME}.md

Made {TODAY}.
"""


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def squash(text):
    return re.sub(r"\s+", " ", text).strip()


def paths(name):
    return (os.path.join(PUBLIC, "UPDATES-" + name + ".md"),
            os.path.join(PUBLIC, "CROSSREF-" + name + ".md"),
            os.path.join(PUBLIC, "ARCHIVE-" + name + ".md"))


def old_archive(name):
    return os.path.join(PUBLIC, "UPDATES-" + name + "-ARCHIVE.md")


def check_name(name):
    if not re.fullmatch(r"[A-Z0-9]+", name):
        stop("thread name '" + name + "' should be letters and digits only, like PC or NP1")


def tags_of(text):
    for line in text.splitlines():
        line = line.strip()
        if line:
            m = re.match(r"\s*tags:\s*(\S.*)$", line, re.I)
            return m.group(1).strip() if m else None
    return None


def piece(source, tags, body, extra=""):
    return ("\n----- archived %s | from %s%s | tags: %s -----\n%s\n"
            % (TODAY, source, extra, tags, body.strip()))


def fill(name, text):
    data = {
        "NAME": name,
        "OWNER": OWNER,
        "TODAY": TODAY,
        "SITE": SITE,
        "PA": SITE + "PA-" + name + ".txt",
        "UPDATES": SITE + "UPDATES-" + name + ".md",
        "CROSSREF": SITE + "CROSSREF-" + name + ".md",
        "ARCHIVE": SITE + "ARCHIVE-" + name + ".md",
        "INDEX": SITE + "index.html",
    }
    for key, value in data.items():
        text = text.replace("{" + key + "}", value)
    return text


def ensure_archive(name):
    arch = paths(name)[2]
    if not os.path.isdir(PUBLIC):
        stop("public folder not found: " + PUBLIC)
    if not os.path.exists(arch):
        with open(arch, "x", encoding="utf-8") as f:
            f.write(ARCHIVE_HEAD.format(NAME=name, TODAY=TODAY, PUBLIC=PUBLIC_NAME))
        print("Made: " + arch)
    return arch


def append_archive(arch, text, bodies):
    with open(arch, "a", encoding="utf-8") as f:
        f.write(text)
    have = squash(read(arch))
    return all(squash(b) in have for b in bodies)


def backup(path):
    os.makedirs(BACKUPS, exist_ok=True)
    shutil.copy2(path, os.path.join(BACKUPS, os.path.basename(path) + ".bak-" + NOW))


def split_entries(text):
    """Returns [(date or None, body)]. Text before the first dated line
    (hand-written entries from before the tool) comes back with date None."""
    out = []
    marks = list(ENTRY_LINE.finditer(text))
    first = marks[0].start() if marks else len(text)
    if text[:first].strip():
        out.append((None, text[:first].strip()))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append((m.group(1), text[m.end():end].strip()))
    return out


def pieces_for(source, entries):
    text, bodies = "", []
    for date, body in entries:
        if not body:
            continue
        extra = (" | added " + date) if date else ""
        text += piece(source, tags_of(body) or "untagged", body, extra)
        bodies.append(body)
    return text, bodies


def archive_crossref(name, c):
    skip = "Note added. Archiving skipped, live post untouched: "
    text = read(c)
    sep = SEP_LINE.search(text)
    if not sep:
        print(skip + "no dashed line found in " + c)
        return
    body = text[sep.end():]
    marks = list(ENTRY_LINE.finditer(body))
    if len(marks) <= XREF_LIMIT:
        return
    cut = marks[XREF_MOVE].start()
    moved_text, bodies = pieces_for("CROSSREF", split_entries(body[:cut]))
    kept = body[cut:]
    try:
        backup(c)
        arch = ensure_archive(name)
    except OSError as e:
        print(skip + "backup failed (" + str(e) + ")")
        return
    if not append_archive(arch, moved_text, bodies):
        print(skip + "could not confirm the entries reached " + arch)
        return
    tmp = c + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text[:sep.end()] + "\n\n" + kept.lstrip("\n"))
    os.replace(tmp, c)
    if squash(kept) not in squash(read(c)):
        print("WARNING: could not confirm the live post kept its newest entries. "
              "Its backup is in " + BACKUPS)
        sys.exit(1)
    print("Cross-reference post passed %d entries. The oldest %d moved to %s"
          % (XREF_LIMIT, XREF_MOVE, SITE + os.path.basename(arch)))


def setup(name):
    check_name(name)
    os.makedirs(PUBLIC, exist_ok=True)
    os.makedirs(BACKUPS, exist_ok=True)
    u, c, arch = paths(name)
    pa = os.path.join(PUBLIC, "PA-" + name + ".txt")
    for p, head in ((u, UPDATES_HEAD), (c, CROSSREF_HEAD)):
        if os.path.exists(p):
            print("Already exists, left alone: " + p)
            continue
        with open(p, "x", encoding="utf-8") as f:
            f.write(head.format(NAME=name, TODAY=TODAY, SITE=SITE))
        print("Made: " + p)
    if os.path.exists(pa):
        print("Already exists, left alone: " + pa)
    else:
        tpl = os.path.join(TEMPLATES, "PA-TEMPLATE.txt")
        if not os.path.isfile(tpl):
            stop("template not found: " + tpl)
        with open(pa, "x", encoding="utf-8") as f:
            f.write(fill(name, read(tpl)))
        print("Made: " + pa)
    if os.path.exists(arch):
        print("Already exists, left alone: " + arch)
    else:
        ensure_archive(name)


def card(name):
    check_name(name)
    u, c, arch = paths(name)
    pa = os.path.join(PUBLIC, "PA-" + name + ".txt")
    print("Address card for the " + name + " thread:")
    print("")
    for label, p in (("Prompt accomplice", pa),
                     ("Updates", u),
                     ("Cross-reference", c),
                     ("Archive", arch)):
        status = ""
        if not os.path.exists(p):
            status = "   (not made yet: run  python threads.py setup " + name + ")"
        print("  " + label + ":")
        print("  " + SITE + os.path.basename(p) + status)
        print("")
    print("  Front page (links to every thread):")
    print("  " + SITE + "index.html")


def handoff(name):
    check_name(name)
    tpl = os.path.join(TEMPLATES, "HANDOFF-TEMPLATE.txt")
    if not os.path.isfile(tpl):
        stop("template not found: " + tpl)
    print(fill(name, read(tpl)).rstrip())


def show(name):
    u = paths(name)[0]
    if not os.path.exists(u):
        stop("no updates post for " + name + ": " + u)
    text = read(u)
    if MARKER not in text:
        stop("the marker line is missing from " + u)
    entries = text.split(MARKER, 1)[1]
    if not entries.strip():
        print("No unread updates for " + name + ".")
    else:
        print("UNREAD UPDATES FOR " + name + ":")
        print(entries.strip())


def add(name, src, kind):
    u, c, arch = paths(name)
    target = u if kind == "update" else c
    if not os.path.exists(target):
        stop("post not found: " + target
             + "\nMake it first with: python threads.py setup " + name)
    src = os.path.expanduser(src)
    if not os.path.isfile(src):
        stop("file not found: " + src)
    body = read(src).strip()
    if not body:
        stop("file is empty: " + src)
    if not tags_of(body):
        stop("the file's first line must be a tags line, like: tags: nginx, stale-copies")
    current = read(target)
    if kind == "update" and MARKER not in current:
        stop("the marker line is missing from " + target)
    look_in = current
    if kind == "update":
        for p in (arch, old_archive(name)):
            if os.path.exists(p):
                look_in += read(p)
    if squash(body) in squash(look_in):
        stop("this text is already in " + target
             + (" or its archive" if kind == "update" else ""))
    with open(target, "a", encoding="utf-8") as f:
        f.write("\n----- added " + TODAY + " -----\n" + body + "\n")
    if squash(body) not in squash(read(target)):
        print("WARNING: wrote to " + target + " but could not confirm the text is there. Check it.")
        sys.exit(1)
    print("Added to: " + target)
    print("Online at: " + SITE + os.path.basename(target))
    if kind == "note":
        archive_crossref(name, target)


def clear(name):
    u = paths(name)[0]
    if not os.path.exists(u):
        stop("file not found: " + u)
    live = read(u)
    if MARKER not in live:
        stop("the marker line is missing from " + u)
    head, entries = live.split(MARKER, 1)
    if not entries.strip():
        print("Nothing to clear. " + name + " has no unread updates. Nothing changed.")
        return
    try:
        backup(u)
    except OSError as e:
        stop("backup failed (" + str(e) + ")")
    arch = ensure_archive(name)
    text, bodies = pieces_for("UPDATES", split_entries(entries))
    if not append_archive(arch, text, bodies):
        print("STOPPING, nothing emptied: could not confirm the entries reached " + arch)
        print("Live post untouched. Its backup is in " + BACKUPS)
        sys.exit(1)
    tmp = u + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(head + MARKER + "\n")
    os.replace(tmp, u)
    print("Archived and cleared " + name + " on " + TODAY + ", into " + SITE + os.path.basename(arch))
    print("What was moved:")
    print(entries.strip())


def archive_file(name, source, src, tag_words):
    check_name(name)
    if not re.fullmatch(r"[A-Z0-9-]+", source):
        stop("SOURCE should be one word in capitals, like PA, POST or PRIVATE")
    src = os.path.expanduser(src)
    if not os.path.isfile(src):
        stop("file not found: " + src)
    body = read(src).strip()
    if not body:
        stop("file is empty: " + src)
    tags = ", ".join(w.strip(",") for w in tag_words if w.strip(",")) or tags_of(body)
    if not tags:
        stop("no tags: add tag words after the file name, or start the file with a tags line")
    arch = paths(name)[2]
    if os.path.exists(arch) and squash(body) in squash(read(arch)):
        stop("this file's text is already in " + arch)
    arch = ensure_archive(name)
    if not append_archive(arch, piece(source, tags, body, " | file " + os.path.basename(src)), [body]):
        print("WARNING: wrote to " + arch + " but could not confirm the text is there. Check it.")
        sys.exit(1)
    print("Archived " + os.path.basename(src) + " into " + SITE + os.path.basename(arch))


USAGE = """Usage:
  python threads.py setup NAME
  python threads.py card NAME
  python threads.py handoff NAME
  python threads.py show NAME
  python threads.py update NAME FILE
  python threads.py note NAME FILE
  python threads.py clear NAME
  python threads.py archive NAME SOURCE FILE [TAGS...]"""


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(USAGE)
        sys.exit(1)
    job, name = args[0].lower(), args[1].upper()
    if job == "setup" and len(args) == 2:
        setup(name)
    elif job == "card" and len(args) == 2:
        card(name)
    elif job == "handoff" and len(args) == 2:
        handoff(name)
    elif job == "show" and len(args) == 2:
        show(name)
    elif job in ("update", "note") and len(args) == 3:
        add(name, args[2], job)
    elif job == "clear" and len(args) == 2:
        clear(name)
    elif job == "archive" and len(args) >= 4:
        archive_file(name, args[2].upper(), args[3], args[4:])
    else:
        print(USAGE)
        sys.exit(1)


main()
