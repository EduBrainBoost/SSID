# PDF Export Instructions for Design Documents

This guide explains how to convert Markdown design documents to PDF format for audit-compliant archival.

---

## Prerequisites

### Install Pandoc

**Windows:**
```bash
# Using Chocolatey
choco install pandoc

# Using Scoop
scoop install pandoc

# Or download installer from https://pandoc.org/installing.html
```

**macOS:**
```bash
brew install pandoc
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install pandoc
```

### Install LaTeX (for PDF generation)

**Windows:**
```bash
# MiKTeX (recommended for Windows)
choco install miktex

# Or download from https://miktex.org/download
```

**macOS:**
```bash
# MacTeX
brew install --cask mactex
```

**Linux:**
```bash
# TeX Live
sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra
```

---

## Quick Export

### Basic PDF (Simple)

```bash
# From the design directory
cd 05_documentation/design

# Generate PDF
pandoc roadmap_adaptive_compliance_v4.md \
  -o roadmap_adaptive_compliance_v4.pdf \
  --pdf-engine=pdflatex
```

### Professional PDF (Recommended)

```bash
pandoc roadmap_adaptive_compliance_v4.md \
  -o roadmap_adaptive_compliance_v4.pdf \
  --pdf-engine=pdflatex \
  --toc \
  --toc-depth=3 \
  --number-sections \
  --variable=geometry:margin=1in \
  --variable=fontsize:11pt \
  --variable=documentclass:report \
  --variable=papersize:a4 \
  --highlight-style=tango \
  --metadata title="Adaptive Compliance Intelligence - Roadmap v4.0" \
  --metadata author="SSID Core Team" \
  --metadata date="2025-10-17"
```

### Enterprise PDF (Full Features)

```bash
pandoc roadmap_adaptive_compliance_v4.md \
  -o roadmap_adaptive_compliance_v4.pdf \
  --pdf-engine=xelatex \
  --toc \
  --toc-depth=3 \
  --number-sections \
  --variable=geometry:margin=1in \
  --variable=fontsize:11pt \
  --variable=documentclass:report \
  --variable=papersize:a4 \
  --variable=mainfont:"Arial" \
  --variable=monofont:"Courier New" \
  --highlight-style=tango \
  --metadata title="Adaptive Compliance Intelligence - Roadmap v4.0" \
  --metadata author="SSID Core Team" \
  --metadata date="2025-10-17" \
  --metadata subject="Technical Roadmap" \
  --metadata keywords="MoSCoW, Compliance, SSID, Adaptive Intelligence" \
  --include-in-header=header.tex \
  --include-before-body=cover.tex
```

---

## Advanced Customization

### Custom LaTeX Header (header.tex)

Create `05_documentation/design/header.tex`:

```latex
% Custom LaTeX header for SSID design documents

\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhead[L]{SSID Project}
\fancyhead[C]{Adaptive Compliance Intelligence}
\fancyhead[R]{\thepage}
\fancyfoot[C]{Internal - Technical Roadmap}

\usepackage{listings}
\lstset{
  basicstyle=\ttfamily\small,
  breaklines=true,
  frame=single,
  backgroundcolor=\color{lightgray}
}

\usepackage{hyperref}
\hypersetup{
  colorlinks=true,
  linkcolor=blue,
  urlcolor=blue,
  pdftitle={Adaptive Compliance Intelligence - Roadmap v4.0},
  pdfauthor={SSID Core Team}
}
```

### Cover Page (cover.tex)

Create `05_documentation/design/cover.tex`:

```latex
\begin{titlepage}
  \centering
  \vspace*{2cm}

  {\Huge\bfseries Adaptive Compliance Intelligence\par}
  \vspace{1cm}
  {\Large Roadmap v4.0\par}
  \vspace{2cm}

  {\Large\itshape SSID Core Team\par}
  \vfill

  {\large Document ID: SSID-ROADMAP-ACI-V4.0\par}
  {\large Classification: Internal - Technical Roadmap\par}
  {\large Date: 2025-10-17\par}

  \vfill
\end{titlepage}
```

---

## Batch Export Script

Create `05_documentation/scripts/export_all_pdfs.sh`:

```bash
#!/bin/bash
# Export all design documents to PDF

DESIGN_DIR="05_documentation/design"
PANDOC_OPTS="--pdf-engine=pdflatex --toc --toc-depth=3 --number-sections --variable=geometry:margin=1in --variable=fontsize:11pt --variable=documentclass:report --variable=papersize:a4 --highlight-style=tango"

cd $DESIGN_DIR

for md_file in *.md; do
  if [ "$md_file" != "README.md" ] && [ "$md_file" != "README_PDF_EXPORT.md" ]; then
    pdf_file="${md_file%.md}.pdf"
    echo "Converting $md_file to $pdf_file..."

    pandoc "$md_file" -o "$pdf_file" $PANDOC_OPTS \
      --metadata title="${md_file%.md}" \
      --metadata author="SSID Core Team" \
      --metadata date="$(date +%Y-%m-%d)"

    if [ $? -eq 0 ]; then
      echo "✅ Successfully created $pdf_file"
    else
      echo "❌ Failed to create $pdf_file"
    fi
  fi
done

echo "PDF export complete!"
```

Make executable and run:
```bash
chmod +x 05_documentation/scripts/export_all_pdfs.sh
./05_documentation/scripts/export_all_pdfs.sh
```

---

## Windows PowerShell Script

Create `05_documentation/scripts/export_all_pdfs.ps1`:

```powershell
# Export all design documents to PDF (Windows)

$DesignDir = "05_documentation\design"
$PandocOpts = "--pdf-engine=pdflatex --toc --toc-depth=3 --number-sections --variable=geometry:margin=1in --variable=fontsize:11pt --variable=documentclass:report --variable=papersize:a4 --highlight-style=tango"

Set-Location $DesignDir

Get-ChildItem -Filter *.md | Where-Object { $_.Name -notmatch "README" } | ForEach-Object {
    $MdFile = $_.Name
    $PdfFile = $MdFile -replace ".md$", ".pdf"

    Write-Host "Converting $MdFile to $PdfFile..."

    $Title = $MdFile -replace ".md$", ""
    $Date = Get-Date -Format "yyyy-MM-dd"

    pandoc $MdFile -o $PdfFile $PandocOpts.Split(" ") `
        --metadata title="$Title" `
        --metadata author="SSID Core Team" `
        --metadata date="$Date"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Successfully created $PdfFile" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create $PdfFile" -ForegroundColor Red
    }
}

Write-Host "PDF export complete!"
```

Run in PowerShell:
```powershell
.\05_documentation\scripts\export_all_pdfs.ps1
```

---

## Troubleshooting

### Issue: "pdflatex not found"

**Solution:** Install LaTeX distribution (MiKTeX/MacTeX/TeX Live)

### Issue: Missing fonts

**Solution:** Use `--pdf-engine=xelatex` instead of `pdflatex` for better font support

### Issue: Unicode characters not rendering

**Solution:** Switch to XeLaTeX:
```bash
pandoc input.md -o output.pdf --pdf-engine=xelatex
```

### Issue: Code blocks cut off

**Solution:** Add `--variable=geometry:margin=0.75in` to reduce margins

### Issue: Images not embedded

**Solution:** Ensure image paths are relative and images exist:
```bash
pandoc input.md -o output.pdf --resource-path=.:./images
```

---

## CI/CD Integration

### GitHub Actions Workflow

Add to `.github/workflows/export_docs_pdf.yml`:

```yaml
name: Export Design Docs to PDF

on:
  push:
    paths:
      - '05_documentation/design/*.md'
  workflow_dispatch:

jobs:
  export-pdf:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Install Pandoc
        run: |
          sudo apt-get update
          sudo apt-get install -y pandoc texlive-latex-base texlive-fonts-recommended texlive-latex-extra

      - name: Export PDFs
        run: |
          cd 05_documentation/design
          for md in *.md; do
            if [[ "$md" != "README"* ]]; then
              pdf="${md%.md}.pdf"
              pandoc "$md" -o "$pdf" \
                --pdf-engine=pdflatex \
                --toc --toc-depth=3 --number-sections \
                --variable=geometry:margin=1in \
                --variable=fontsize:11pt \
                --metadata title="${md%.md}" \
                --metadata author="SSID Core Team" \
                --metadata date="$(date +%Y-%m-%d)"
            fi
          done

      - name: Upload PDF Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: design-docs-pdf
          path: 05_documentation/design/*.pdf
          retention-days: 90

      - name: Commit PDFs to Repository
        run: |
          git config --local user.email "ci@ssid-project.local"
          git config --local user.name "CI PDF Export"
          git add 05_documentation/design/*.pdf
          git diff --staged --quiet || git commit -m "docs: Update design document PDFs [skip ci]"
          git push
```

---

## Quality Checklist

Before finalizing PDF exports:

- [ ] All headings numbered correctly
- [ ] Table of contents generated
- [ ] Code blocks formatted properly
- [ ] Images embedded and visible
- [ ] Links functional (blue and underlined)
- [ ] Metadata (title, author, date) correct
- [ ] Page numbers present
- [ ] No text cutoff at page boundaries
- [ ] File size reasonable (<10MB for docs)
- [ ] PDF version compatible (PDF/A for archival)

---

## Archival-Grade PDF (PDF/A)

For long-term archival compliance:

```bash
pandoc roadmap_adaptive_compliance_v4.md \
  -o roadmap_adaptive_compliance_v4.pdf \
  --pdf-engine=xelatex \
  --toc --toc-depth=3 --number-sections \
  --variable=geometry:margin=1in \
  --variable=fontsize:11pt \
  --variable=documentclass:report \
  --metadata title="Adaptive Compliance Intelligence - Roadmap v4.0" \
  --metadata author="SSID Core Team" \
  --metadata date="2025-10-17" \
  --metadata subject="Technical Roadmap" \
  --metadata keywords="MoSCoW, Compliance, SSID"

# Convert to PDF/A using Ghostscript
gs -dPDFA=3 -dBATCH -dNOPAUSE \
  -sColorConversionStrategy=UseDeviceIndependentColor \
  -sDEVICE=pdfwrite \
  -dPDFACompatibilityPolicy=1 \
  -sOutputFile=roadmap_adaptive_compliance_v4_PDFA.pdf \
  roadmap_adaptive_compliance_v4.pdf
```

---

## File Naming Convention

```
<document_name>_v<version>.pdf

Examples:
- roadmap_adaptive_compliance_v4.0.pdf
- ci_moscow_gate_integration_v1.0.pdf
- sot_enforcement_report_v3.2.0.pdf
```

---

## Next Steps

1. Generate PDF for `roadmap_adaptive_compliance_v4.md`
2. Review PDF output for quality
3. Archive PDF in `05_documentation/design/` (committed to repo)
4. Optionally upload to SharePoint/Confluence for broader access
5. Update document register with PDF location

---

**Version:** 1.0.0
**Last Updated:** 2025-10-17
**Maintained By:** SSID Documentation Team
