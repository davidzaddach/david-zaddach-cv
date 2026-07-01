# David Zaddach – CV

Privates Repository für Lebenslauf/CV (DE/EN), Build-Artefakte und die öffentliche Netlify-Site.

**Live:** [https://davidzaddach.netlify.app/](https://davidzaddach.netlify.app/)

## Struktur

| Ordner | Inhalt |
|--------|--------|
| `src/` | Quellen: englische DOCX (Source of Truth), deutsche DOCX, klassisches HTML |
| `public/` | Netlify-Deploy: interaktive `index.html` + Web-PDF + ATS-PDF |
| `archive/` | Referenz (ältere Bewerbung 2021) |
| `scripts/` | Python-Generatoren (später wieder anbinden) |

## Netlify

- **Publish directory:** `public` (siehe `netlify.toml`)
- **Git-Deploy:** Repo als **privates** Remote verbinden, Branch `main` → Production
- **Manuell:** Ordner `public/` per [Netlify Drop](https://app.netlify.com/drop) hochladen

Öffentliche URL für PDF-Link in `cv_netlify_url.txt` pflegen.

## Workflow (aktuell)

1. Inhalt in `src/David_Zaddach_CV_EN_2026.docx` bearbeiten
2. Deutsche Version und HTML/PDF nach Bedarf aktualisieren
3. `public/index.html` pflegen → `python3 scripts/build_web_pdf.py` für Web-PDF; ATS-PDF optional aus DOCX
4. Push → Netlify baut aus `public/`

## Hinweis

Dieses Repo enthält **persönliche Daten**. Nur als **privates** Remote hosten, nicht öffentlich pushen.
