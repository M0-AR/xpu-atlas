import re
from pathlib import Path

from xpu_atlas.io_utils import ROOT

PREVIEW = ROOT / "preview.html"
INDEX = ROOT / "index.html"
DOCS_PREVIEW = ROOT / "docs" / "preview.html"
DOCS_INDEX = ROOT / "docs" / "index.html"
DATA = ROOT / "assets" / "atlas-data.js"


def test_pages_entry_points_exist():
    assert PREVIEW.exists()
    assert INDEX.exists()
    assert INDEX.read_bytes() == PREVIEW.read_bytes()
    assert DOCS_PREVIEW.exists()
    assert DOCS_INDEX.exists()
    assert (ROOT / ".nojekyll").exists()
    assert (ROOT / "docs" / ".nojekyll").exists()


def test_docs_preview_mirror_uses_parent_assets():
    text = DOCS_PREVIEW.read_text(encoding="utf-8")
    assert 'src="../assets/atlas-data.js"' in text
    assert 'src="assets/' not in text
    assert 'href="docs/' not in text
    assert 'href="../README.md"' in text
    assert "url=preview.html" in DOCS_INDEX.read_text(encoding="utf-8")


def test_preview_bundle_and_sections():
    assert DATA.exists()
    bundle = DATA.read_text(encoding="utf-8")
    assert "window.XPU_DATA" in bundle
    text = PREVIEW.read_text(encoding="utf-8")
    for section in ("demo", "findings", "atlas", "explorer", "learn", "quiz", "lab"):
        assert f'id="{section}"' in text
    for control in (
        "claim-search",
        "claim-rows",
        "quiz-form",
        "path-label",
        "theme-toggle",
        "demo-tabs",
        "demo-viewport",
        "demo-launch-btn",
        "lab-canvas",
        "lab-start-btn",
        "lab-answers",
        "lab-voice",
    ):
        assert f'id="{control}"' in text
    assert "?embed=1" in text
    assert "prefers-reduced-motion" in text
    assert (ROOT / "assets" / "vendor" / "three.module.min.js").exists()
    assert (ROOT / "assets" / "vendor" / "three.core.min.js").exists()


def test_preview_has_no_local_or_placeholder_urls():
    text = PREVIEW.read_text(encoding="utf-8")
    assert "localhost" not in text
    assert "127.0.0.1" not in text
    assert "example.org" not in text


def test_preview_local_assets_exist():
    text = PREVIEW.read_text(encoding="utf-8")
    refs = set(re.findall(r'(?:src|href)="(assets/[^"]+)"', text))
    refs.update(re.findall(r"url\((assets/[^)]+)\)", text))
    assert refs
    missing = [ref for ref in sorted(refs) if not (ROOT / ref).exists()]
    assert not missing, missing

    docs_text = DOCS_PREVIEW.read_text(encoding="utf-8")
    docs_refs = set(re.findall(r'(?:src|href)="(\.\./assets/[^"]+)"', docs_text))
    docs_refs.update(re.findall(r"url\((\.\./assets/[^)]+)\)", docs_text))
    assert docs_refs
    missing = [ref for ref in sorted(docs_refs) if not (DOCS_PREVIEW.parent / ref).resolve().exists()]
    assert not missing, missing
