"""Build the browser data bundle and publish the GitHub Pages entry point."""

from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview.html"
INDEX = ROOT / "index.html"
NOJEKYLL = ROOT / ".nojekyll"
DOCS = ROOT / "docs"
DOCS_PREVIEW = DOCS / "preview.html"
DOCS_INDEX = DOCS / "index.html"
DOCS_NOJEKYLL = DOCS / ".nojekyll"

DOCS_INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=preview.html">
<title>XPU-Atlas</title>
<link rel="canonical" href="preview.html">
</head>
<body>
<p><a href="preview.html">Open the XPU-Atlas interactive atlas</a></p>
</body>
</html>
"""


def _docs_mirror(text: str) -> str:
    """Make root-relative links work from /docs/preview.html."""
    def rewrite_attr(match: re.Match[str]) -> str:
        attr, url = match.group(1), match.group(2)
        if url.startswith(("#", "http://", "https://", "mailto:", "data:", "../", "/")):
            return match.group(0)
        return f'{attr}="../{url}"'

    text = re.sub(r'(href|src)="([^"]+)"', rewrite_attr, text)
    return re.sub(r'url\((assets/[^)]+)\)', r'url(../\1)', text)


def main() -> int:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_atlas_data.py")], cwd=ROOT, check=True)
    if not PREVIEW.exists():
        print("preview: preview.html missing", file=sys.stderr)
        return 1
    text = PREVIEW.read_text(encoding="utf-8")
    if "localhost" in text or "127.0.0.1" in text:
        print("preview: preview.html contains a local URL", file=sys.stderr)
        return 1
    shutil.copyfile(PREVIEW, INDEX)
    DOCS.mkdir(exist_ok=True)
    DOCS_PREVIEW.write_text(_docs_mirror(text), encoding="utf-8")
    DOCS_INDEX.write_text(DOCS_INDEX_HTML, encoding="utf-8")
    for marker in (NOJEKYLL, DOCS_NOJEKYLL):
        if not marker.exists():
            marker.write_text("", encoding="utf-8")
    print("preview: wrote index.html, docs/preview.html, docs/index.html, and .nojekyll files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
