# The Librarian — an AI Knowledge Base Starter Kit

Turn a pile of scattered documents into an interlinked, browsable
knowledge base: a private Wikipedia for your company, your research, or
your hobby, maintained by an AI librarian that answers questions from
*your* sources instead of the open internet.

This repo was built for the **20Fathoms Breakfast Lab: Build an AI
Knowledge Base** (Traverse City, MI). It works just as well at home.

## What's actually in the box

Not much, on purpose. The value of this kit is not code. It is a set of
instructions (`AGENTS.md`) that turns a coding agent like Claude Code or
Codex into **The Librarian**: a slightly fussy, extremely useful
character who will:

1. Interview you about what you're building (librarians call this a
   *reference interview*)
2. Propose a structure for your knowledge base and adjust it until you
   approve
3. Process your first document in the open, narrating its editorial
   choices, so you can correct its judgment
4. **Rewrite its own instructions** to match everything you taught it

That last step is the whole point. When onboarding ends, the
instructions in this repo were not written by Anthropic, OpenAI, or the
person who made this kit. They were written by a conversation with you.
You are the designer. The AI is the instrument.

## Quickstart

You need:

- **A paid Claude or ChatGPT subscription** with Claude Code or Codex
  installed and logged in
- **Obsidian** (free, [obsidian.md](https://obsidian.md)) — and if you
  don't have it, the Librarian will offer to install it for you
- **3–5 documents** you'd like to organize (customer notes, strategy
  docs, meeting transcripts, research, SOPs). No documents? The
  `sample-documents/` folder has you covered.

Then:

```
git clone <REPO_URL> my-library
cd my-library
claude        # or: codex
```

And say hi. That's it. The Librarian handles everything from there,
one question at a time. Expect the whole onboarding, from "hello" to
your first real wiki pages, to take about 20 to 30 minutes.

When the Librarian tells you to, open this folder in Obsidian
(**Open folder as vault**, then select this directory). This folder IS
your knowledge base. There is no other setup.

## What success looks like

By the end of onboarding you will have:

- A folder structure designed around *your* material, not a template
- Your first document processed into real, interlinked wiki pages
- A Librarian that knows three services: **bring me documents**,
  **check the shelves**, and **answer from the collection**
- A `Start Here` note in your vault, written by your Librarian, with
  homework for your first real shelving session

The full library takes longer. Plan a follow-up session of an hour or
two to work through your document pile. The Librarian will run it with
you; that's what it's for.

## Repo tour

```
AGENTS.md            The Librarian. Onboarding script now; your custom
                     operating manual after the self-rewrite.
CLAUDE.md            Pointer so Claude Code reads AGENTS.md. Don't edit.
raw/                 Your source documents go here, and stay here,
                     untouched. The permanent collection.
wiki/                The Librarian's work: interlinked Markdown pages.
                     This is what you browse in Obsidian.
tools/health.py      Finds broken links between wiki pages. The
                     Librarian runs it after every shelving session.
tools/youtube_transcript.py
                     Turns a YouTube URL into a transcript in raw/,
                     ready for shelving.
sample-documents/    Three documents from a fictional Traverse City
                     startup, for practice or demos. Delete when you
                     have the real thing.
```

## If your setup fights you

Do not burn your session on a broken install. Everything here is
reproducible at home in about twenty minutes, and the repo will
re-teach you: guiding new users through setup is literally what the
Librarian is for. At the live event, watch a neighbor's screen, mark
this page, and try again after lunch.

Common snags:

- **`claude` or `codex` not found** — the CLI isn't installed or isn't
  on your PATH. Claude Code: see Anthropic's install docs. Codex: see
  OpenAI's. Both take a few minutes.
- **Agent starts but ignores the Librarian** — make sure you launched
  it *inside* this folder (`cd my-library` first). The instructions
  only apply where the instructions live.
- **Onboarding got interrupted** — just relaunch and say hi. The
  Librarian keeps a status line in `AGENTS.md` and will pick up where
  you left off instead of re-introducing itself.
- **Python errors from tools/** — you need Python 3.10+. The transcript
  tool also needs `youtube-transcript-api`; the Librarian will offer to
  install it when first needed.

## Make it yours

This kit is intentionally light so that what you build on top of it is
actually yours. After onboarding, the customization never stops: tell
the Librarian to add a page type, change a processing rule, take on a
new duty. It edits its own manual. That is not a trick. That is the
job.

---

Seeded at 20Fathoms Breakfast Lab, Traverse City, Michigan.
Presented by [Adam Lorton](https://adamlorton.com). The llama is
fictional.
