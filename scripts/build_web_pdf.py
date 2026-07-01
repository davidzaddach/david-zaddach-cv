#!/usr/bin/env python3
"""Build public/David_Zaddach_CV_EN_2026_web.pdf from public/index.html (web design, print layout)."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "public" / "index.html"
HTML_OUT = ROOT / "src" / "David_Zaddach_CV_EN_2026_web.html"
PDF_OUT = ROOT / "public" / "David_Zaddach_CV_EN_2026_web.pdf"

PRINT_CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400..700;1,9..40,400..700&display=swap');

:root {
  --bg: #ffffff;
  --card: #ffffff;
  --text: #1a1a1a;
  --muted: #5c574c;
  --accent: #7a5c1e;
  --accent2: #b08d45;
  --border: #e2dccf;
}

@page {
  size: A4;
  margin: 14mm 14mm 16mm;
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
  font-family: "DM Sans", system-ui, sans-serif;
  font-size: 10.5pt;
  line-height: 1.5;
  color: var(--text);
  background: #ffffff;
}

main {
  max-width: 42rem;
  margin: 0 auto;
}

.hero {
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.15rem 1.2rem;
  margin-bottom: 0.85rem;
}

.hero h1 {
  margin: 0 0 0.3rem;
  font-size: 1.55rem;
  letter-spacing: -0.02em;
  color: var(--accent);
}

.hero .name {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 0.55rem;
}

.hero .c-line {
  margin: 0.15rem 0;
  font-size: 0.88rem;
  color: var(--muted);
}

.hero .c-line a.c-link,
a.employer-link {
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px solid var(--accent2);
}

.cv-section {
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0.9rem 1rem 1rem;
  margin-bottom: 0.75rem;
  break-inside: avoid;
  page-break-inside: avoid;
}

.cv-section.allow-break {
  break-inside: auto;
  page-break-inside: auto;
}

.cv-section h2 {
  margin: 0 0 0.65rem;
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent);
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.35rem;
}

.company {
  font-weight: 700;
  font-size: 0.94rem;
  margin: 0.85rem 0 0.3rem;
  color: var(--text);
}

.company:first-child { margin-top: 0; }

.company.break-before {
  break-before: page;
  page-break-before: always;
  margin-top: 0;
}

.job {
  border: 1px solid var(--border);
  border-radius: 9px;
  margin: 0.4rem 0;
  padding: 0.45rem 0.6rem 0.15rem;
  background: transparent;
  break-inside: avoid;
  page-break-inside: avoid;
}

.job-header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: baseline;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.job-title { flex: 1 1 auto; }

.job-period {
  font-weight: 500;
  font-size: 0.82rem;
  color: var(--muted);
  white-space: nowrap;
}

.bullets {
  margin: 0 0 0.45rem 1rem;
  padding: 0;
}

.bullets li { margin: 0.2rem 0; }

.txt, .pre {
  margin: 0.35rem 0;
}

.pre {
  white-space: pre-wrap;
  font-size: 0.9rem;
  color: var(--muted);
}

footer.page-footer {
  margin-top: 1rem;
  font-size: 0.82rem;
  color: var(--muted);
  text-align: center;
}
"""


def _extract_main(html: str) -> str:
    match = re.search(r"<main>(.*?)</main>", html, re.DOTALL)
    if not match:
        raise SystemExit("Could not find <main> in index.html")
    return match.group(1).strip()


def _to_print_html(main_html: str) -> str:
    html = main_html
    html = re.sub(r"<details class=\"job\" open>", '<div class="job">', html)
    html = re.sub(r"</details>", "</div>", html)
    html = re.sub(
        r"<summary>(.*?)</summary>",
        lambda m: f'<div class="job-header">{m.group(1).strip()}</div>',
        html,
        flags=re.DOTALL,
    )
    html = html.replace(
        '<section id="professional-experience" class="cv-section">',
        '<section id="professional-experience" class="cv-section allow-break">',
    )
    html = html.replace(
        '<div class="company"><a class="employer-link" href="https://www.freenet-group.de/en"',
        '<div class="company break-before"><a class="employer-link" href="https://www.freenet-group.de/en"',
    )
    return html


def _wrap_document(body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>David Zaddach, Curriculum Vitae</title>
<style>{PRINT_CSS}</style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""


def _find_chrome() -> Path:
    candidates = [
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    ]
    for path in candidates:
        if path.is_file():
            return path
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if chrome:
        return Path(chrome)
    raise SystemExit("Chrome/Chromium/Edge required for HTML to PDF export")


def _html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    chrome = _find_chrome()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(chrome),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=15000",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0 or not pdf_path.is_file():
        raise SystemExit(
            "PDF export failed.\n"
            f"Chrome exit code: {result.returncode}\n"
            f"stderr: {result.stderr.strip()}\n"
            f"stdout: {result.stdout.strip()}"
        )


def main() -> None:
    if not INDEX.is_file():
        raise SystemExit(f"Missing source: {INDEX}")

    main_html = _to_print_html(_extract_main(INDEX.read_text(encoding="utf-8")))
    document = _wrap_document(main_html)

    HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text(document, encoding="utf-8")
    _html_to_pdf(HTML_OUT, PDF_OUT)

    print(f"Wrote {HTML_OUT}")
    print(f"Wrote {PDF_OUT}")


if __name__ == "__main__":
    main()
