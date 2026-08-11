# Build-Skripte

## Inhalt synchron halten (Web → ATS)

```bash
# 1. Inhalt in public/index.html pflegen
python3 scripts/sync_ats_from_web.py   # → src HTML + DOCX-Bullet-Fix
python3 scripts/build_web_pdf.py       # → Web-PDF (default + music industry variant)
python3 scripts/build_web_pdf.py --variant music   # → music variant only
python3 scripts/build_pdf.py           # → ATS-PDF (Word, macOS)
```

`sync_ats_from_web.py` erzeugt `src/David_Zaddach_CV_EN_2026.html` aus der Web-CV (eine Spalte, Standard-Überschriften, ATS-saubere Bullets).

## Web-PDF (Design wie Netlify-Seite)

```bash
python3 scripts/build_web_pdf.py
```

Liest `public/index.html`, erzeugt:

- `src/David_Zaddach_CV_EN_2026_web.html` und `public/David_Zaddach_CV_EN_2026_web.pdf` (Standard)
- `src/David_Zaddach_CV_EN_2026_web_music.html` und `public/David_Zaddach_CV_EN_2026_web_music.pdf` (Musikbranche)

Mit `--variant default|music|all` (Standard: `all`). Chrome/Edge headless.

Nach Änderungen an `public/index.html` das Skript für die Web-PDF laufen lassen. Der Download-Button auf Netlify verweist auf die Web-PDF.

## ATS-PDF aus DOCX (macOS + Microsoft Word)

```bash
python3 -m pip install --user docx2pdf
python3 scripts/build_pdf.py
```

Schreibt `public/David_Zaddach_CV_EN_2026.pdf` aus `src/David_Zaddach_CV_EN_2026.docx` (einfaches Layout für Bewerbungsportale).

## Dateien

| Datei | Zweck |
|-------|--------|
| `public/David_Zaddach_CV_MusicTech_Executive.pdf` | Music-Tech Executive CV — Haupt-Download (`/cv.pdf`, `/cv-musictech.pdf`) |
| `public/David_Zaddach_CV_EN_2026_web.pdf` | Design-PDF — Web-Layout (`/cv-web.pdf`) |
| `public/David_Zaddach_CV_EN_2026.pdf` | ATS/Word-Version (`/cv-ats.pdf`) |

Geplante Wiederanbindung:

- EN DOCX → `public/index.html` (interaktive Version)
- EN DOCX → DE DOCX (Spiegelung)

Bis dahin: Inhalt in `public/index.html` pflegen, Web-PDF per Skript bauen, ATS-PDF aus DOCX bei Bedarf.
