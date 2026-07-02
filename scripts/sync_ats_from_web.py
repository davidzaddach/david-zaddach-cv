#!/usr/bin/env python3
"""Sync src/David_Zaddach_CV_EN_2026.html (ATS) from public/index.html content."""

from __future__ import annotations

import html
import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "public" / "index.html"
DOCX = ROOT / "src" / "David_Zaddach_CV_EN_2026.docx"
ATS_HTML = ROOT / "src" / "David_Zaddach_CV_EN_2026.html"

BMG_BULLET = (
    "End-to-end ownership of the technology product portfolio, investment and roadmap, "
    "and measurable value aligned with enterprise priorities"
)

ATS_CSS = """
    :root { --accent: #5f5226; --body: #262626; --muted: #5f5a52; }
    * { box-sizing: border-box; }
    body { font-family: Arial, Helvetica, sans-serif; font-size: 11pt; line-height: 1.45; color: var(--body); max-width: 52rem; margin: 0 auto; padding: 1.5rem 1.25rem 3rem; }
    h1 { color: var(--accent); font-size: 1.55rem; margin: 0 0 0.35rem; font-weight: 700; border-bottom: 2px solid #c4b89e; padding-bottom: 0.35rem; }
    .name { font-size: 1.2rem; font-weight: 700; margin: 0.75rem 0 0.25rem; }
    .contact p { margin: 0.15rem 0; font-size: 10pt; }
    h2 { color: var(--accent); font-size: 1.05rem; margin: 1.35rem 0 0.5rem; border-bottom: 1px solid #d8d0bc; padding-bottom: 0.2rem; }
    .profile-headline { margin: 0 0 0.55rem; font-size: 10pt; font-weight: 700; line-height: 1.4; color: var(--accent); }
    .profile-target { margin: 0 0 0.55rem; font-size: 10pt; font-weight: 700; line-height: 1.4; color: var(--body); }
    h3 { font-size: 0.98rem; margin: 1rem 0 0.35rem; color: #303030; font-weight: 700; }
    .role { display: flex; justify-content: space-between; gap: 1rem; font-weight: 700; font-size: 10.5pt; margin: 0.35rem 0 0.15rem; }
    .role .period { font-weight: 400; font-style: italic; color: var(--muted); white-space: nowrap; }
    ul { margin: 0.2rem 0 0.6rem 1.1rem; padding: 0; }
    li { margin: 0.2rem 0; }
    .footer { margin-top: 2rem; font-size: 9pt; color: #666; }
    @media print { body { max-width: 100%; } }
"""


def _text(node: Tag | NavigableString | None) -> str:
    if node is None:
        return ""
    text = node.get_text(" ", strip=True)
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r",\s+", ", ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def _sanitize_bullet(text: str) -> str:
    if "technology product portfolio" in text and "+" in text:
        return BMG_BULLET
    return text


def _render_list(ul: Tag | None, parts: list[str]) -> None:
    if ul is None:
        return
    parts.append("<ul>")
    for li in ul.find_all("li", recursive=False):
        parts.append(f"<li>{html.escape(_sanitize_bullet(_text(li)))}</li>")
    parts.append("</ul>")


def _render_job(details: Tag, parts: list[str]) -> None:
    summary = details.find("summary")
    if summary is None:
        return
    title = summary.find(class_="job-title")
    period = summary.find(class_="job-period")
    parts.append(
        f'<div class="role"><span>{html.escape(_text(title))}</span>'
        f'<span class="period">{html.escape(_text(period))}</span></div>'
    )
    _render_list(details.find("ul", class_="bullets"), parts)


def _convert_main(main: Tag) -> str:
    parts: list[str] = []

    hero = main.find("header", class_="hero")
    if hero:
        parts.append(f"<h1>{html.escape(_text(hero.find('h1')))}</h1>")
        parts.append(f'<p class="name">{html.escape(_text(hero.find(class_="name")))}</p>')
        for line in hero.find_all("p", class_="c-line"):
            parts.append(f'<div class="contact"><p>{html.escape(_text(line))}</p></div>')

    for section in main.find_all("section", class_="cv-section"):
        h2 = section.find("h2")
        if h2:
            parts.append(f"<h2>{html.escape(_text(h2))}</h2>")

        section_id = section.get("id", "")
        if section_id == "personal-details":
            pre = section.find("p", class_="pre")
            if pre:
                parts.append(f'<p style="white-space:pre-wrap">{html.escape(pre.get_text())}</p>')
            continue
        if section_id == "profile":
            lead = section.find("p", class_="profile-headline")
            target = section.find("p", class_="profile-target")
            txt = section.find("p", class_="txt")
            if lead:
                parts.append(
                    f'<p class="profile-headline">{html.escape(_text(lead))}</p>'
                )
            if target:
                parts.append(
                    f'<p class="profile-target">{html.escape(_text(target))}</p>'
                )
            if txt:
                parts.append(f"<p>{html.escape(_text(txt))}</p>")
            continue
        if section_id in {"skills-knowledge", "certifications-selection", "languages"}:
            _render_list(section.find("ul", class_="bullets"), parts)
            continue

        for child in section.children:
            if not isinstance(child, Tag):
                continue
            if child.name == "div" and "company" in child.get("class", []):
                parts.append(f"<h3>{html.escape(_text(child))}</h3>")
            elif child.name == "details" and "job" in child.get("class", []):
                _render_job(child, parts)

    footer = main.find("footer", class_="page-footer")
    if footer:
        parts.append(f'<p class="footer">{html.escape(_text(footer))}</p>')

    return "\n".join(parts)


def _wrap_html(body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>David Zaddach, Curriculum Vitae</title>
<style>{ATS_CSS}
</style>
</head><body>
{body}
</body></html>
"""


def _sync_docx_fixes() -> None:
    from docx import Document
    from docx.shared import RGBColor

    if not DOCX.is_file():
        raise SystemExit(f"Missing source: {DOCX}")

    section_headings = {
        "Profile",
        "Skills & knowledge",
        "Professional experience",
        "Further experience",
        "Education",
        "Certifications (selection)",
        "Languages",
    }
    accent = RGBColor(0x5F, 0x52, 0x26)

    doc = Document(str(DOCX))
    changed = 0
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text in section_headings:
            paragraph.text = text
            run = paragraph.runs[0]
            run.bold = True
            run.font.color.rgb = accent
            changed += 1
        if "technology product portfolio" in paragraph.text and "+" in paragraph.text:
            paragraph.text = BMG_BULLET
            changed += 1
        if paragraph.text.strip().startswith("Senior Product Owner Business Services"):
            if not paragraph.paragraph_format.page_break_before:
                paragraph.paragraph_format.page_break_before = True
                changed += 1
        if paragraph.text.strip().startswith("Internships and early industry roles"):
            if not paragraph.paragraph_format.page_break_before:
                paragraph.paragraph_format.page_break_before = True
                changed += 1
            # Remove duplicate inline page breaks (page_break_before is enough).
            w_ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            for br in list(paragraph._element.findall(f".//{w_ns}br")):
                if br.get(f"{w_ns}type") == "page":
                    br.getparent().remove(br)
                    changed += 1
    doc.save(str(DOCX))
    print(f"Updated DOCX paragraphs: {changed}")


def main() -> None:
    if not INDEX.is_file():
        raise SystemExit(f"Missing source: {INDEX}")

    soup = BeautifulSoup(INDEX.read_text(encoding="utf-8"), "html.parser")
    main = soup.find("main")
    if main is None:
        raise SystemExit("Could not find <main> in index.html")

    ATS_HTML.write_text(_wrap_html(_convert_main(main)), encoding="utf-8")
    print(f"Wrote {ATS_HTML}")
    _sync_docx_fixes()


if __name__ == "__main__":
    main()
