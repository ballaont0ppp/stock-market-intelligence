#!/usr/bin/env python3
"""
Generate individual HTML files for each Mermaid diagram.
This script reads all .md files in the diagrams directory and creates
separate HTML files with embedded Mermaid rendering.
"""

import os
import re
from pathlib import Path


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Stock Portfolio Platform</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: white;
            color: #111827;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            padding: 40px 60px;
            border-bottom: 4px solid #1e40af;
        }}
        
        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .company-name {{
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            opacity: 0.9;
            margin-bottom: 8px;
        }}
        
        h1 {{
            font-size: 32px;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }}
        
        .diagram-type {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 12px;
            letter-spacing: 0.5px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 60px;
        }}
        
        .diagram-container {{
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            padding: 40px;
            margin: 0;
            overflow-x: auto;
        }}
        
        .footer {{
            margin-top: 60px;
            padding-top: 30px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            color: #6b7280;
            font-size: 13px;
        }}
        
        .footer-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .footer-left {{
            text-align: left;
        }}
        
        .footer-right {{
            text-align: right;
        }}
        
        .footer strong {{
            color: #2563eb;
            font-weight: 600;
        }}
        
        /* Print styles */
        @media print {{
            body {{
                background: white;
            }}
            
            .header {{
                background: #2563eb;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            
            .container {{
                padding: 40px 20px;
            }}
            
            .diagram-container {{
                border: 2px solid #e5e7eb;
                page-break-inside: avoid;
            }}
            
            .footer {{
                page-break-before: avoid;
            }}
        }}
        
        @page {{
            margin: 0.5in;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="company-name">Stock Portfolio Platform</div>
            <h1>{title}</h1>
            <span class="diagram-type">{category} Diagram</span>
        </div>
    </div>
    
    <div class="container">
        <div class="diagram-container">
            <pre class="mermaid">
{mermaid_code}
            </pre>
        </div>
        
        <div class="footer">
            <div class="footer-content">
                <div class="footer-left">
                    <strong>Stock Portfolio Platform</strong><br>
                    System Architecture Documentation
                </div>
                <div class="footer-right">
                    Document: <strong>{title}</strong><br>
                    Page 1 of 1
                </div>
            </div>
        </div>
    </div>
    
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'neutral',
            securityLevel: 'loose',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }}
        }});
    </script>
</body>
</html>
"""


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Portfolio Platform - System Diagrams</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f9fafb;
            color: #111827;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
            border-bottom: 4px solid #1e40af;
        }}
        
        .header h1 {{
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 12px;
            letter-spacing: -1px;
        }}
        
        .header p {{
            font-size: 18px;
            opacity: 0.95;
            max-width: 700px;
            margin: 0 auto;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 60px 40px;
        }}
        
        .section-title {{
            font-size: 24px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 24px;
            padding-bottom: 12px;
            border-bottom: 3px solid #2563eb;
        }}
        
        .diagram-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 24px;
            margin-bottom: 48px;
        }}
        
        .diagram-card {{
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            padding: 24px;
            transition: all 0.2s ease;
            cursor: pointer;
        }}
        
        .diagram-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(37, 99, 235, 0.15);
            border-color: #2563eb;
        }}
        
        .diagram-card h3 {{
            font-size: 18px;
            font-weight: 600;
            color: #111827;
            margin-bottom: 12px;
        }}
        
        .diagram-card a {{
            color: #2563eb;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        
        .diagram-card a:hover {{
            color: #1d4ed8;
        }}
        
        .diagram-card a::after {{
            content: '→';
            font-size: 16px;
            transition: transform 0.2s ease;
        }}
        
        .diagram-card:hover a::after {{
            transform: translateX(4px);
        }}
        
        .category {{
            display: inline-block;
            background: #dbeafe;
            color: #1e40af;
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 12px;
            letter-spacing: 0.5px;
        }}
        
        .stats {{
            display: flex;
            gap: 40px;
            justify-content: center;
            margin-top: 40px;
            padding: 30px;
            background: white;
            border-radius: 8px;
            border: 2px solid #e5e7eb;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 36px;
            font-weight: 700;
            color: #2563eb;
            display: block;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #6b7280;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .footer {{
            text-align: center;
            padding: 40px;
            color: #6b7280;
            font-size: 14px;
            border-top: 2px solid #e5e7eb;
            margin-top: 60px;
        }}
        
        .footer strong {{
            color: #2563eb;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>System Architecture Diagrams</h1>
        <p>Comprehensive visual documentation of the Stock Portfolio Platform</p>
    </div>
    
    <div class="container">
{diagram_sections}
        
        <div class="stats">
            <div class="stat">
                <span class="stat-number">{total_diagrams}</span>
                <span class="stat-label">Total Diagrams</span>
            </div>
            <div class="stat">
                <span class="stat-number">{category_count}</span>
                <span class="stat-label">Categories</span>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <strong>Stock Portfolio Platform</strong> - System Architecture Documentation<br>
        Generated for professional documentation and printing
    </div>
</body>
</html>
"""


def extract_mermaid_code(content):
    """Extract Mermaid code from markdown content and remove metadata lines."""
    # Match mermaid code blocks
    pattern = r'```mermaid\s*\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if not matches:
        return None
    
    mermaid_code = matches[0]
    
    # Remove metadata lines (Generated, Generator, Source, Back to diagrams)
    lines = mermaid_code.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip lines that contain metadata
        if any(keyword in line for keyword in ['Generated:', 'Generator:', 'Source:', 'Back to diagrams']):
            continue
        # Skip lines that are just dashes (separators after metadata)
        if line.strip() and not line.strip().replace('-', ''):
            continue
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def extract_title_from_filename(filename):
    """Convert filename to readable title."""
    name = filename.replace('.md', '').replace('_', ' ').replace('-', ' ')
    return ' '.join(word.capitalize() for word in name.split())


def extract_description(content):
    """Extract description from markdown content (text before first code block)."""
    # Get text before first code block
    parts = content.split('```', 1)
    if len(parts) > 1:
        desc = parts[0].strip()
        # Remove markdown headers
        desc = re.sub(r'^#+\s+.*$', '', desc, flags=re.MULTILINE).strip()
        if desc:
            return f'<div class="description">{desc}</div>'
    return ''


def categorize_diagram(filename):
    """Categorize diagram by type."""
    if 'architecture' in filename or 'component' in filename or 'package' in filename:
        return 'Architecture'
    elif 'sequence' in filename:
        return 'Sequence'
    elif 'class' in filename:
        return 'Class'
    elif 'er' in filename or 'database' in filename:
        return 'Database'
    elif 'dfd' in filename:
        return 'Data Flow'
    elif 'state' in filename:
        return 'State'
    elif 'use_case' in filename:
        return 'Use Case'
    else:
        return 'Other'


def generate_html_files():
    """Generate individual HTML files for each diagram."""
    diagrams_dir = Path('diagrams')
    
    if not diagrams_dir.exists():
        print(f"Error: {diagrams_dir} directory not found")
        return
    
    # Find all markdown files
    md_files = list(diagrams_dir.glob('*.md'))
    
    # Filter out non-diagram files
    exclude_files = {'README.md', 'GENERATION_SUMMARY.md', 'DIAGRAMS_GENERATION_SUMMARY.md'}
    md_files = [f for f in md_files if f.name not in exclude_files]
    
    generated_files = []
    
    for md_file in md_files:
        print(f"Processing {md_file.name}...")
        
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract Mermaid code
        mermaid_code = extract_mermaid_code(content)
        
        if not mermaid_code:
            print(f"  ⚠️  No Mermaid code found in {md_file.name}, skipping...")
            continue
        
        # Generate title and category
        title = extract_title_from_filename(md_file.name)
        category = categorize_diagram(md_file.name)
        
        # Generate HTML
        html_content = HTML_TEMPLATE.format(
            title=title,
            category=category,
            mermaid_code=mermaid_code
        )
        
        # Write HTML file
        html_filename = md_file.stem + '.html'
        html_path = diagrams_dir / html_filename
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        generated_files.append({
            'filename': html_filename,
            'title': title,
            'category': category
        })
        
        print(f"  ✓ Generated {html_filename}")
    
    # Generate index page with sections by category
    print("\nGenerating index page...")
    
    # Group diagrams by category
    categories = {}
    for file_info in generated_files:
        cat = file_info['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(file_info)
    
    # Sort categories
    category_order = ['Architecture', 'Database', 'Class', 'Sequence', 'Data Flow', 'State', 'Use Case', 'Other']
    sorted_categories = sorted(categories.keys(), key=lambda x: category_order.index(x) if x in category_order else 999)
    
    # Build sections
    sections = []
    for category in sorted_categories:
        files = sorted(categories[category], key=lambda x: x['title'])
        
        cards = []
        for file_info in files:
            card = f"""            <div class="diagram-card" onclick="window.location.href='{file_info['filename']}'">
                <h3>{file_info['title']}</h3>
                <a href="{file_info['filename']}">View Diagram</a>
                <span class="category">{file_info['category']}</span>
            </div>"""
            cards.append(card)
        
        section = f"""        <div class="section">
            <h2 class="section-title">{category} Diagrams</h2>
            <div class="diagram-grid">
{chr(10).join(cards)}
            </div>
        </div>
"""
        sections.append(section)
    
    index_html = INDEX_TEMPLATE.format(
        diagram_sections='\n'.join(sections),
        total_diagrams=len(generated_files),
        category_count=len(categories)
    )
    
    index_path = diagrams_dir / 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"  ✓ Generated index.html")
    
    print(f"\n✅ Successfully generated {len(generated_files)} diagram HTML files!")
    print(f"📂 Open diagrams/index.html to view all diagrams")


if __name__ == '__main__':
    generate_html_files()
