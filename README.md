# Bot Council Starter Kit, version 1.0

Run your own thread system: several AI chats, one per project, each
keeping public files on the web so they can read each other's news.
This version is the thread system only; the chatbots do not talk to
each other automatically yet. That is a later version.

One tool, `threads.py`, keeps every thread's public files. You fill in
one settings file, run one setup command per thread, and paste the
printed addresses into new AI chats.

## What you need

- Python 3 on your computer. On Windows, the command may be `py`
  instead of `python`.
- A GitHub account, for the free web hosting route. That route is
  what this README walks through.
- No AI key. None of this uses one.

## The files in this kit

| File | What it is |
|---|---|
| `settings.txt` | The ONE file you fill in. Everything personal lives here. |
| `threads.py` | The tool. One command keeps all threads' files. |
| `make_page.py` | Turns a text file into a web page with clickable links. |
| `make_index.py` | Rebuilds the front page that lists every thread. |
| `templates/` | Fill-in text for new threads' pages. |
| `public/` | The public files. Made when you run setup. |
| `backups/` | Safety copies. Never published. |
| `container/` | The own-computer hosting route (Docker). |

## The two hosting routes

- **GitHub (this README):** `threads.py` writes into `public/`, you push
  that folder to GitHub, turn on GitHub Pages, and the files are on the
  web for free.
- **Own computer (default in settings):** `threads.py` writes into
  `public/`, and a small container serves it at
  `http://localhost:8080/`. Readable only on that computer. See
  `container/`.

## One-time setup

1. Open `settings.txt` and change:
   - `SITE` to `https://YOUR-GITHUB-NAME.github.io/YOUR-REPO-NAME/public/`
   - `OWNER` to your name.
   Save the file.
2. Open a terminal in this folder.

Now make your first thread. A thread name is letters and digits only,
like `PC` or `NP1`:

```
python threads.py setup NP1
```

This makes the thread's four public files in `public/`:
`PA-NP1.txt`, `UPDATES-NP1.md`, `CROSSREF-NP1.md`, `ARCHIVE-NP1.md`.

## The address card

After setup, print the thread's addresses:

```
python threads.py card NP1
```

It prints all four public addresses. Paste them into a new AI chat so
that chat can follow its own pages.

## The first handoff

```
python threads.py handoff NP1
```

Prints a ready message for a new AI chat. Paste the whole thing into a
new chat; it tells the chat to open its prompt accomplice and read it.

## Rebuild the front page

```
python make_index.py
```

Rewrites `public/index.html` so it lists every thread and links to its
four public files. Run it after adding a thread.

## Everyday commands

```
python threads.py show NAME
```
Print the unread updates for thread NAME. Read them first each session.

```
python threads.py update NAME FILE
```
Add FILE to NAME's updates post. FILE's first line must be a tags line:

```
tags: some, search, words
```

```
python threads.py note NAME FILE
```
Add FILE to NAME's cross-reference post (history, no action needed).
Same tags rule.

```
python threads.py clear NAME
```
Move NAME's read updates into its archive and empty the updates post.

```
python threads.py archive NAME SOURCE FILE [TAGS...]
```
Put a whole FILE into NAME's archive. SOURCE is one word saying what it
is, like `PA`, `POST`, or `PRIVATE`. TAGS are words after the file name;
if you give none, the file's own first line must be a tags line.

## Publishing on GitHub

1. In your browser, create a new repository on GitHub. Call it the same
   name you used in `settings.txt`. Do not add a README yet.
2. In the terminal, in this folder:

```
git init
git add .
git commit -m "bot council starter kit 1.0"
git branch -M main
git remote add origin https://github.com/YOUR-GITHUB-NAME/YOUR-REPO-NAME.git
git push -u origin main
```

3. In the browser, open the repository, then:
   Settings -> Pages -> Source: Deploy from a branch -> Branch: main,
   folder / (root) -> Save.
4. Wait a minute, then open:
   `https://YOUR-GITHUB-NAME.github.io/YOUR-REPO-NAME/public/`
   and you should see `index.html` listing your threads.

## Safety rules the tool follows

- Never deletes a file. Setup leaves existing posts alone.
- Every update and note needs a tags line, and duplicates are refused.
- Clearing and trimming back up first, write the archive, check it
  landed, and only then trim the live post.
- If anything is missing, it stops, says so, and changes nothing.
- Nothing private goes in `public/`; this conversation's rule is the
  thread rule too.
