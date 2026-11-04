"""Build the browser data bundle and publish the GitHub Pages entry point."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview.html"
INDEX = ROOT / "index.html"
NOJEKYLL = ROOT / ".nojekyll"


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
    if not NOJEKYLL.exists():
        NOJEKYLL.write_text("", encoding="utf-8")
    print(f"preview: wrote {INDEX.relative_to(ROOT)} and .nojekyll")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
