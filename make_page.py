#!/usr/bin/env python3
# <<<<<<< make_page.py, bot council starter kit, version 1.0 >>>>>>>
# General version of Tony's Nexus make_tony_page.py.
# Turns one text file into a simple web page with clickable links.
#
# Usage:  python make_page.py TEXTFILE [OUTPUT.html]
# If OUTPUT is omitted, it is TEXTFILE with .html at the end.
# Every address in the text (http... or https...) becomes a link, and
# the link shows the address itself.

import datetime
import os
import re
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python make_page.py TEXTFILE [OUTPUT.html]")
        sys.exit(1)
    src = sys.argv[1]
    if not os.path.isfile(src):
        print("File not found: " + src)
        sys.exit(1)
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + ".html"
    with open(src, encoding="utf-8") as f:
        text = f.read()
    esc = (text.replace("&", "&amp;")
               .replace("<", "&lt;")
               .replace(">", "&gt;"))
    esc = re.sub(
        r"(https?://[^\s<\"')]+)",
        r'<a href="\1">\1</a>',
        esc,
    )
    esc = esc.replace("\n\n", "</p>\n\n<p>")
    title = next((line.strip() for line in text.splitlines() if line.strip()), os.path.basename(src))
    page = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<title>' + title + '</title>\n'
            '<style>body{font-family:system-ui,sans-serif;line-height:1.5;'
            'margin:2rem auto;max-width:48rem;padding:0 1rem;'
            'white-space:pre-wrap;word-wrap:break-word}</style>\n</head>\n<body>\n<p>'
            + esc +
            '\n</p>\n<p><em>Made ' + datetime.date.today().isoformat()
            + ' by the bot council starter kit, version 1.0.</em></p>\n'
            '</body>\n</html>\n')
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print("Made: " + out)


main()
