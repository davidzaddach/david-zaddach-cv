#!/usr/bin/env python3
"""Build web-styled CV PDFs from public/index.html (print layout)."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "public" / "index.html"

PRINT_CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400..700;1,9..40,400..700&display=swap');

:root {
  --bg: #ffffff;
  --card: #f6f4ef;
  --card-inner: #ffffff;
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
  background: var(--bg);
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

main {
  max-width: 42rem;
  margin: 0 auto;
}

.hero {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.15rem 1.2rem;
  margin-bottom: 0.85rem;
  -webkit-box-decoration-break: clone;
  box-decoration-break: clone;
}

.hero h1 {
  margin: 0 0 0.3rem;
  font-size: 1.55rem;
  letter-spacing: -0.02em;
  color: #7a5c1e;
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
  color: #7a5c1e;
  text-decoration: none;
  border-bottom: 1px solid var(--accent2);
}

.cv-section {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0.9rem 1rem 1rem;
  margin-bottom: 0.75rem;
  break-inside: avoid;
  page-break-inside: avoid;
  overflow: hidden;
  -webkit-box-decoration-break: clone;
  box-decoration-break: clone;
}

.cv-section.allow-break {
  break-inside: auto;
  page-break-inside: auto;
  -webkit-box-decoration-break: clone;
  box-decoration-break: clone;
}

.cv-section.avoid-break-before {
  break-before: avoid;
  page-break-before: avoid;
}

.cv-section.break-before {
  break-before: page;
  page-break-before: always;
  margin-top: 0;
}

.cv-section h2 {
  margin: 0 0 0.65rem;
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #7a5c1e;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.35rem;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

.profile-headline {
  margin: 0 0 0.55rem;
  font-size: 0.88rem;
  font-weight: 600;
  line-height: 1.45;
  color: #7a5c1e;
}
.hero .profile-headline {
  margin: 0 0 0.75rem;
  font-size: 0.92rem;
  color: #7a5c1e;
}
.expertise-tags {
  display: flex;
  flex-wrap: wrap;
  gap: .35rem;
  list-style: none;
  margin: 0;
  padding: 0;
}
.expertise-tags li {
  font-size: .78rem;
  padding: .22rem .5rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--card-inner);
  color: var(--muted);
}
.bullet-label { font-weight: 600; color: var(--text); }

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
  background: var(--card-inner);
  break-inside: avoid;
  page-break-inside: avoid;
  overflow: hidden;
  -webkit-box-decoration-break: clone;
  box-decoration-break: clone;
}

.cv-section.allow-break .job {
  break-inside: auto;
  page-break-inside: auto;
  -webkit-box-decoration-break: clone;
  box-decoration-break: clone;
}

.job.break-before {
  break-before: page;
  page-break-before: always;
  margin-top: 0;
}

.job.no-split {
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
  margin-top: 0.25rem;
  font-size: 0.78rem;
  color: var(--muted);
  text-align: center;
  break-before: avoid;
  page-break-before: avoid;
}

#education,
#certifications-selection,
#languages {
  padding: 0.65rem 0.85rem 0.7rem;
  margin-bottom: 0.4rem;
}

#education h2,
#certifications-selection h2,
#languages h2 {
  margin-bottom: 0.4rem;
  padding-bottom: 0.2rem;
}

#education .job {
  margin: 0.15rem 0;
  padding: 0.25rem 0.45rem 0.05rem;
}

#certifications-selection .bullets,
#languages .bullets {
  margin-bottom: 0.2rem;
}

#languages .page-footer {
  margin: 0.35rem 0 0;
  font-size: 0.78rem;
  color: var(--muted);
  text-align: center;
}
"""

SKILLS_BLOCK = """<ul class="bullets">
<li>Executive product &amp; technology leadership</li>
<li>Portfolio strategy, prioritisation &amp; multi-year roadmaps</li>
<li>P&amp;L ownership, budgeting &amp; vendor governance</li>
<li>B2B platform scaling (music / copyright / data)</li>
<li>Stakeholder &amp; board-level communication</li>
<li>Music publishing, licensing &amp; copyright operations</li>
<li>AI strategy and applied expertise (LLMs, agentic systems, human-in-the-loop)</li>
<li>Agentic coding and AI-assisted software delivery</li>
</ul>"""

SKILLS_BLOCK_MUSIC = """<ul class="bullets">
<li>Music publishing, licensing &amp; copyright operations</li>
<li>Royalties, sync &amp; rights platform modernisation</li>
<li>B2B platform scaling in music &amp; media</li>
<li>Executive product &amp; technology leadership</li>
<li>Portfolio strategy, prioritisation &amp; multi-year roadmaps</li>
<li>P&amp;L ownership, budgeting &amp; vendor governance</li>
<li>Stakeholder management across labels, societies &amp; partners</li>
<li>AI strategy for music catalogue, metadata &amp; operations</li>
</ul>"""


@dataclass(frozen=True)
class PdfVariant:
    name: str
    html_out: Path
    pdf_out: Path
    transform: Callable[[str], str]


def _extract_main(html: str) -> str:
    match = re.search(r"<main>(.*?)</main>", html, re.DOTALL)
    if not match:
        raise SystemExit("Could not find <main> in index.html")
    return match.group(1).strip()


def _apply_music_variant(main_html: str) -> str:
    html = main_html
    html = html.replace(
        "<p class=\"profile-headline\">Senior Director / Head of Product (Technology) | Enterprise platforms in music, copyright &amp; data</p>",
        "<p class=\"profile-headline\">Senior Director / Head of Product (Technology) | Music publishing, royalties &amp; rights technology</p>",
    )
    html = html.replace(
        "<p class=\"profile-target\">Target role: Chief Product Officer, VP Product or Head of Technology Products in music, media &amp; enterprise platforms</p>",
        "<p class=\"profile-target\">Target role: VP Product, Head of Technology or CPO at music companies, publishers, labels &amp; rights organisations</p>",
    )
    html = html.replace(
        "<p class=\"txt\">Senior product and technology leader who aligns business, engineering and partners in complex rights and data environments. Background in hands-on content and technical operations, with progression into portfolio-level leadership. Focused on modernising enterprise platforms, AI-ready architecture and measurable business outcomes.</p>",
        "<p class=\"txt\">Product and technology leader across music publishing, copyright and royalties — from hands-on music content operations to portfolio leadership at BMG. Deep domain knowledge in licensing, metadata, royalty platforms and B2B music tech; focused on modernising rights infrastructure and measurable outcomes for labels and publishers.</p>",
    )
    html = html.replace(SKILLS_BLOCK, SKILLS_BLOCK_MUSIC)
    html = html.replace(
        "<h2>Further experience</h2>",
        "<h2>Music industry &amp; creative background</h2>",
    )
    html = html.replace(
        "<li>Own portfolio of 50+ technology products and ~€40M IT budget; investment, roadmap and outcomes aligned with enterprise priorities</li>",
        "<li>Own portfolio of 50+ technology products across royalties, copyright, sync and publishing workflows and ~€40M IT budget; investment, roadmap and outcomes aligned with music business priorities</li>",
    )
    html = html.replace(
        "<li>Led decommissioning of legacy monolithic copyright and royalties platform (iMaestro); delivered sync pitching tool, microservices, headless architecture and APIs for AI transformation</li>",
        "<li>Led decommissioning of legacy monolithic copyright and royalties platform (iMaestro); delivered sync pitching tool, microservices and APIs to modernise music publishing and royalty operations</li>",
    )
    html = html.replace(
        "<li>Built content operations, CMS workflows and partner onboarding; introduced Scrum and scaled music as a core mobile content category.</li>",
        "<li>Built music content operations, CMS workflows and label partner onboarding; introduced Scrum and scaled full-track music as a core mobile content category.</li>",
    )
    html = html.replace(
        "<li>Ongoing music production; selected projects with artists such as ",
        "<li>Active music producer and label entrepreneur; ongoing projects with artists such as ",
    )
    return html


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
        '<section id="profile" class="cv-section">',
        '<section id="profile" class="cv-section allow-break">',
    )
    html = html.replace(
        '<section id="core-expertise" class="cv-section">',
        '<section id="core-expertise" class="cv-section allow-break">',
    )
    html = html.replace(
        '<section id="skills-knowledge" class="cv-section">',
        '<section id="skills-knowledge" class="cv-section allow-break">',
    )
    html = html.replace(
        '<section id="professional-experience" class="cv-section">',
        '<section id="professional-experience" class="cv-section allow-break avoid-break-before">',
    )
    html = html.replace(
        '<section id="music-creative" class="cv-section">',
        '<section id="music-creative" class="cv-section allow-break">',
    )
    html = html.replace(
        '<section id="further-experience" class="cv-section">',
        '<section id="further-experience" class="cv-section allow-break">',
    )
    html = html.replace(
        '<section id="education-additional" class="cv-section">',
        '<section id="education-additional" class="cv-section allow-break">',
    )
    html = html.replace(
        '<section id="education" class="cv-section">',
        '<section id="education" class="cv-section allow-break">',
    )
    html = html.replace(
        '<section id="certifications-selection" class="cv-section">',
        '<section id="certifications-selection" class="cv-section allow-break">',
    )
    html = html.replace(
        '<section id="languages" class="cv-section">',
        '<section id="languages" class="cv-section allow-break avoid-break-before">',
    )
    # Web PDF only: omit French to keep Languages on page 3 (3-page layout).
    html = re.sub(r"\s*<li>French: basic</li>", "", html)
    # Keep footer on the same page as Languages.
    html = re.sub(
        r'(<section id="languages" class="cv-section allow-break avoid-break-before">.*?</ul>)\s*</section>\s*<footer class="page-footer">([^<]*)</footer>',
        r'\1<p class="page-footer">\2</p></section>',
        html,
        flags=re.DOTALL,
    )
    html = html.replace(
        '<div class="job"><div class="job-header"><span class="job-title">Internships and early industry roles',
        '<div class="job no-split"><div class="job-header"><span class="job-title">Internships and early industry roles',
    )
    return html


def _wrap_document(body: str, title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{PRINT_CSS}</style>
</head><body>
<main>
{body}
</main>
</body></html>
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


def _build_variant(source_main: str, variant: PdfVariant) -> None:
    main_html = variant.transform(source_main)
    document = _wrap_document(
        _to_print_html(main_html),
        f"David Zaddach, Curriculum Vitae ({variant.name})",
    )
    variant.html_out.parent.mkdir(parents=True, exist_ok=True)
    variant.html_out.write_text(document, encoding="utf-8")
    _html_to_pdf(variant.html_out, variant.pdf_out)
    print(f"Wrote {variant.html_out}")
    print(f"Wrote {variant.pdf_out}")


def _variants() -> dict[str, PdfVariant]:
    return {
        "default": PdfVariant(
            name="default",
            html_out=ROOT / "src" / "David_Zaddach_CV_EN_2026_web.html",
            pdf_out=ROOT / "public" / "David_Zaddach_CV_EN_2026_web.pdf",
            transform=lambda html: html,
        ),
        "music": PdfVariant(
            name="music",
            html_out=ROOT / "src" / "David_Zaddach_CV_EN_2026_web_music.html",
            pdf_out=ROOT / "public" / "David_Zaddach_CV_EN_2026_web_music.pdf",
            transform=_apply_music_variant,
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build web-styled CV PDF(s) from index.html")
    parser.add_argument(
        "--variant",
        choices=("default", "music", "all"),
        default="all",
        help="PDF variant to build (default: all)",
    )
    args = parser.parse_args()

    if not INDEX.is_file():
        raise SystemExit(f"Missing source: {INDEX}")

    source_main = _extract_main(INDEX.read_text(encoding="utf-8"))
    available = _variants()

    names = list(available) if args.variant == "all" else [args.variant]
    for name in names:
        _build_variant(source_main, available[name])


if __name__ == "__main__":
    main()
