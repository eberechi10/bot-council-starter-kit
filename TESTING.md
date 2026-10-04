# Testing — bot council starter kit, version 1.0

Tested 4 October 2026 by eberechi10, GitHub hosting route.
The own-computer route is left for Tony to test on his desktop.

## 1. Environment (Windows, Git Bash)

| What was run                | Result                                   | Pass |
|-----------------------------|------------------------------------------|------|
| git --version               | git version 2.41.0.windows.3             | yes  |
| py --version                | Python 3.14.7                            | yes  |
| python --version (1st try)  | "Python was not found" (Store alias)     | no   |
| python --version (after fix)| Python 3.14.7                            | yes  |

## 2. Things that did not work, and the fixes

1. Plain `python` was the Windows Store alias, not real Python.
   Fix: added the real Python folder and its Scripts folder to the user
   PATH with PowerShell, in front of the alias. Retest passed.

2. Very long terminal pastes echoed garbled text in Git Bash.
   Fix: wrote long files in short pieces, and after each piece verified
   the file with Python's own parser:
   python -c "import ast; ...; ast.parse(...)"
   Every check came back SYNTAX OK, so the files were intact despite
   the messy echo. No data was lost.

## 3. Kit files on main

Verified present in the repository:

- settings.txt (SITE points at the GitHub Pages public folder,
  OWNER = eberechi10)
- threads.py (the tool)
- make_page.py and make_index.py (general page-maker and front-page
  builder)
- templates/ (PA, handoff, update templates)
- container/ (nginx.conf, compose.yaml) for the own-computer route
- README.md, .gitignore, .nojekyll

## 4. Kit commands tested (GitHub route)

| Command            | Result                                                                                     | Pass |
|--------------------|--------------------------------------------------------------------------------------------|------|
| setup NP1          | Created PA-NP1.txt, UPDATES-NP1.md, CROSSREF-NP1.md, ARCHIVE-NP1.md                        | yes  |
| update NP1 (welcome) | Entry appears below the marker with tags line and dated line                              | yes  |
| card NP1           | Printed all four public addresses plus the front page                                      | yes  |
| handoff NP1        | Printed the first handoff with all four addresses filled in                                | yes  |
| show NP1           | Printed the unread welcome entry below the marker                                          | yes  |
| make_index.py      | Generated public/index.html and index.txt listing NP1                                      | yes  |

## 5. Live hosting (GitHub Pages)

| Address | Result | Pass |
|---------|--------|------|
| https://eberechi10.github.io/bot-council-starter-kit/public/index.html | Front page serves, links present | yes |
| https://eberechi10.github.io/bot-council-starter-kit/public/UPDATES-NP1.md | Working example updates post serves raw | yes |

The working example contains a real kit-made entry:

```
== ENTRIES BELOW ==

----- added 2026-10-04 -----
tags: welcome, starter-kit, first-thread

To: NP1

Subject: Welcome to your thread

This is the first update made by the bot council starter kit, version 1.0.
It proves the update post is live and can receive updates.
```

## 6. Still to exercise (not a failure)

- clear, note, archive — present in threads.py and following Tony's
  safety rules, but not yet run end to end.
- The own-computer route (container/nginx + compose) — Tony tests this.

## 7. Cosmetic notes (not blocking)

- public/index.html uses the title "index.txt"; could be changed to
  "Thread Index" later.
- public/index.txt is published next to index.html; harmless.
