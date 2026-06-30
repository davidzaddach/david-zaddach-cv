# Build-Skripte

## PDF aus DOCX (macOS + Microsoft Word)

```bash
python3 -m pip install --user docx2pdf
python3 scripts/build_pdf.py
```

Schreibt `public/David_Zaddach_CV_EN_2026.pdf` aus `src/David_Zaddach_CV_EN_2026.docx`.

Die früheren Generatoren (`generate_modern_interactive_cv.py`, `generate_cv_docx.py`, …) lagen in `~/Downloads` und sind nicht mehr auf dem Rechner.

Geplante Wiederanbindung:

- EN DOCX → `public/index.html` (interaktive Version)
- EN DOCX → DE DOCX (Spiegelung)

Bis dahin: Quellen in `src/` bearbeiten, PDF per Skript erzeugen, `public/index.html` bei Bedarf manuell synchron halten.
