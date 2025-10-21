# SSID Documentation Diagrams

This directory contains technical diagrams for the SSID project in Mermaid format.

## Files

- `scorecard_flowchart_v1.mmd` - MoSCoW Scorecard Data Flow (v3.2.0 → v4.0)

## Converting to SVG/PNG

### Option 1: Mermaid CLI (Recommended)

```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Convert to SVG
mmdc -i scorecard_flowchart_v1.mmd -o scorecard_flowchart_v1.svg

# Convert to PNG
mmdc -i scorecard_flowchart_v1.mmd -o scorecard_flowchart_v1.png -b transparent
```

### Option 2: Online Tools

1. Visit https://mermaid.live/
2. Paste contents of `.mmd` file
3. Export as SVG or PNG

### Option 3: VS Code Extension

1. Install "Markdown Preview Mermaid Support" extension
2. Open `.mmd` file
3. Preview will render diagram
4. Right-click → Export as SVG

## Viewing in Documentation

GitHub automatically renders Mermaid diagrams in Markdown:

```markdown
\```mermaid
flowchart TB
    A[Start] --> B[End]
\```
```

Or reference the generated SVG:

```markdown
![Scorecard Flow](./diagrams/scorecard_flowchart_v1.svg)
```

## Diagram Conventions

- **Green** (#e1f5e1): Current implemented features (v3.2.0)
- **Blue** (#e3f2fd): Stage 1 features (API)
- **Orange** (#fff3e0): Stage 2 features (AI Self-Healing)
- **Purple** (#f3e5f5): Stage 3 features (Interfederation)
- **Pink** (#fce4ec): Stage 4 features (MCI Analytics)

## Updating Diagrams

1. Edit the `.mmd` file
2. Regenerate SVG/PNG using mermaid-cli
3. Commit both `.mmd` source and generated output
4. Update version number in diagram title if major changes

---

**Version:** 1.0.0
**Last Updated:** 2025-10-17
