#!/usr/bin/env python3
"""Regenerate public/David_Zaddach_CV_EN_2026.pdf from src DOCX (requires Microsoft Word on macOS)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "David_Zaddach_CV_EN_2026.docx"
OUT = ROOT / "public" / "David_Zaddach_CV_EN_2026.pdf"


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Missing source: {SRC}")
    try:
        from docx2pdf import convert
    except ImportError as exc:
        raise SystemExit("Install docx2pdf: python3 -m pip install --user docx2pdf") from exc

    OUT.parent.mkdir(parents=True, exist_ok=True)
    convert(str(SRC), str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
