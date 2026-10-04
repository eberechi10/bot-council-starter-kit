#!/usr/bin/env python3
# <<<<<<< make_index.py, bot council starter kit, version 1.0 >>>>>>>
# Rebuilds the front page (public/index.html) that links to every thread.

import datetime
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_settings():
    path = os.path.join(HERE, "settings.txt")
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
PUBLIC = S.get("PUBLIC", "public")
PUBLIC = PUBLIC if os.path.isabs(PUBLIC) else os.path.join(HERE, PUBLIC)


def main():
    os.makedirs(PUBLIC, exist_ok=True)
    files = os.listdir(PUBLIC) if os.path.isdir(PUBLIC) else []
    names = []
    for f in files:
        m = re.fullmatch(r"PA-([A-Z0-9]+)\.txt", f)
        if m:
            names.append(m.group(1))
    lines = []
    lines.append("THREAD INDEX")
    lines.append("")
    lines.append("Made " + datetime.date.today().isoformat()
                 + " by the bot council starter kit, version 1.0.")
    lines.append("")
    if not names:
        lines.append("No threads yet. Make one with: python threads.py setup NAME")
    for name in sorted(names):
        lines.append("THREAD " + name)
        lines.append("  Prompt accomplice: " + SITE + "PA-" + name + ".txt")
        lines.append("  Updates:           " + SITE + "UPDATES-" + name + ".md")
        lines.append("  Cross-reference:   " + SITE + "CROSSREF-" + name + ".md")
        lines.append("  Archive:           " + SITE + "ARCHIVE-" + name + ".md")
        lines.append("")
    txt = os.path.join(PUBLIC, "index.txt")
    with open(txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    html = os.path.join(PUBLIC, "index.html")
    subprocess.run([sys.executable, os.path.join(HERE, "make_page.py"), txt, html],
                   check=True)
    print("Made: " + html)


main()
