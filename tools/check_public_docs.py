"""Check relative Markdown and HTML asset links against the public worktree.

Offline by design: external URLs and anchors are not checked. Git's ignore rules
keep local-only material out of the link graph, including during local edits.
"""
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_ASSET = re.compile(r'(?:src|srcset|href)="([^"\s]+)"')


def main() -> int:
    paths = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT
    ).decode().split("\0")
    public = {ROOT / path for path in paths if path}
    failures = []
    checked = 0
    for document in sorted(public):
        if document.suffix != ".md" or not document.is_file():
            continue
        # Ignore code examples; only check actual documentation links.
        content = re.sub(r"(?ms)^```.*?^```[^\n]*", "", document.read_text(encoding="utf-8"))
        links = MARKDOWN_LINK.findall(content) + HTML_ASSET.findall(content)
        for link in links:
            parsed = urlsplit(link.strip("<>"))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (document.parent / unquote(parsed.path)).resolve()
            checked += 1
            if target in public and target.is_file():
                continue
            if target.is_dir() and any(path.is_relative_to(target) for path in public):
                continue
            failures.append(f"{document.relative_to(ROOT)}: missing or non-public target: {link}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"Checked {checked} relative public documentation links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
