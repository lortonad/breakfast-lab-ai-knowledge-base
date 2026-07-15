#!/usr/bin/env python3
"""Wiki health check: report broken wikilinks in wiki/.

The Librarian runs this after every ingestion. Exit code 0 means the
shelves are sound; exit code 1 means something needs attention.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
WIKI_DIR = REPO_ROOT / "wiki"

# Matches [[Target]], [[Target|Alias]], [[Target#Heading]] — captures Target.
WIKILINK_RE = re.compile(r"\[\[([^\]\[]+?)\]\]")


def collect_markdown_pages(wiki_dir: Path) -> list[Path]:
    return sorted(wiki_dir.rglob("*.md"))


def link_target(raw_link: str) -> str:
    """Reduce a wikilink body to its page target (drop alias and heading)."""
    target = raw_link.split("|", 1)[0].split("#", 1)[0].strip()
    # Obsidian links may include a path; only the final segment names the page.
    return target.split("/")[-1]


def validate_wikilinks(pages: list[Path]) -> list[tuple[str, str]]:
    """Return (relative_path, link) pairs whose target page does not exist."""
    known = {p.stem.lower() for p in pages}
    broken: list[tuple[str, str]] = []
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        for match in WIKILINK_RE.finditer(text):
            target = link_target(match.group(1))
            if target and target.lower() not in known:
                broken.append((str(page.relative_to(REPO_ROOT)), match.group(1)))
    return broken


def main() -> int:
    if not WIKI_DIR.exists():
        print("wiki/ does not exist")
        return 1

    pages = collect_markdown_pages(WIKI_DIR)
    if not pages:
        print("wiki/ exists but holds no pages yet. Empty shelves are healthy shelves.")
        return 0

    broken = validate_wikilinks(pages)
    if not broken:
        print(f"Checked {len(pages)} pages. No broken wikilinks found.")
        return 0

    print("Broken wikilinks:")
    for rel_path, link in broken:
        print(f"- {rel_path}: [[{link}]]")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
