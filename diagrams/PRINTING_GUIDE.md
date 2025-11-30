# Diagram Printing Guide

## Overview
All diagram HTML files have been optimized for professional printing with the Stock Portfolio Platform's blue theme (#2563eb).

## Features

### Professional Design
- Blue gradient header matching the login page theme
- Clean, corporate layout suitable for documentation
- Print-optimized styling with proper margins
- Professional footer with document information

### Print-Ready
- Metadata lines removed (Generated, Generator, Source, Back to diagrams)
- Optimized page breaks
- High-quality rendering
- Proper margins (0.5 inch on all sides)

## How to Print

### Individual Diagrams
1. Open any diagram HTML file (e.g., `sequence_buy_order.html`)
2. Press `Ctrl+P` (Windows) or `Cmd+P` (Mac)
3. Recommended settings:
   - Paper: Letter or A4
   - Margins: Default
   - Background graphics: ON (to preserve blue header)
   - Scale: 100%

### Batch Printing
To print all diagrams at once, open each file and print, or use your browser's print preview to save as PDF first.

## Files Generated

- **16 individual diagram pages** - Each with professional header and footer
- **index.html** - Overview page with all diagrams organized by category

## Regenerating Diagrams

If you add new diagrams or need to regenerate:

```bash
python scripts/generate_diagram_htmls.py
```

The script will automatically:
- Scan all markdown files in the diagrams folder
- Remove metadata lines
- Apply professional styling
- Generate print-ready HTML files
