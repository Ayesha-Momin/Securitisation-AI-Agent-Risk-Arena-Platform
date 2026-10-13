"""
Master Technical Report HTML / Printable Exporter
=================================================
Converts master_technical_report.md into an executive, printable HTML report
with pagination, financial table formatting, and institutional header/footer.
"""

import os

def export_report():
    md_path = 'reports/master_technical_report.md'
    out_html = 'reports/483553A_Master_Technical_Report.html'

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Simple Markdown-to-HTML parser for structured sections
    lines = md_text.split('\n')
    html_lines = []
    in_table = False
    in_code = False
    code_block = []

    for line in lines:
        if line.startswith('```'):
            if in_code:
                in_code = False
                html_lines.append(f"<pre><code>{'<br>'.join(code_block)}</code></pre>")
                code_block = []
            else:
                in_code = True
            continue

        if in_code:
            code_block.append(line.replace('<', '&lt;').replace('>', '&gt;'))
            continue

        if line.startswith('|') and '|' in line[1:]:
            if not in_table:
                in_table = True
                html_lines.append("<div class='table-container'><table class='report-table'>")
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if all(set(p) <= {'-', ':', ' '} for p in parts if p):
                continue # delimiter row
            row_tag = "th" if ("Key Risk Indicator" in line or "User Role" in line or "Commercial Stream" in line or "Structural Dimension" in line or "Rubric Disqualifier" in line) else "td"
            cells = "".join(f"<{row_tag}>{p}</{row_tag}>" for p in parts)
            html_lines.append(f"<tr>{cells}</tr>")
            continue
        else:
            if in_table:
                in_table = False
                html_lines.append("</table></div>")

        if line.startswith('# '):
            html_lines.append(f"<h1 class='report-h1'>{line[2:].strip()}</h1>")
        elif line.startswith('## '):
            html_lines.append(f"<h2 class='report-h2'>{line[3:].strip()}</h2>")
        elif line.startswith('### '):
            html_lines.append(f"<h3 class='report-h3'>{line[4:].strip()}</h3>")
        elif line.startswith('- '):
            html_lines.append(f"<li>{line[2:].strip()}</li>")
        elif line.startswith('---'):
            html_lines.append("<hr class='divider'>")
        elif line.strip():
            # bold text conversion
            txt = line.strip()
            # replace **bold** with <strong>bold</strong>
            import re
            txt = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', txt)
            html_lines.append(f"<p>{txt}</p>")

    if in_table:
        html_lines.append("</table></div>")

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>483553A - Securitisation AI Agent Master Technical Report</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    @media print {{
      body {{ font-size: 11pt; }}
      .no-print {{ display: none; }}
      .divider {{ page-break-after: always; }}
    }}
    body {{
      font-family: 'Inter', sans-serif;
      color: #1e293b;
      background: #f8fafc;
      margin: 0;
      padding: 40px;
      line-height: 1.6;
    }}
    .document-page {{
      max-width: 900px;
      margin: 0 auto;
      background: #ffffff;
      padding: 60px 80px;
      border: 1px solid #e2e8f0;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
      border-radius: 8px;
    }}
    .report-h1 {{ font-size: 26px; color: #0f172a; border-bottom: 2px solid #0f172a; padding-bottom: 8px; margin-top: 32px; }}
    .report-h2 {{ font-size: 20px; color: #1e3a8a; margin-top: 28px; }}
    .report-h3 {{ font-size: 16px; color: #334155; margin-top: 20px; }}
    p {{ margin-bottom: 12px; color: #334155; }}
    li {{ margin-left: 20px; margin-bottom: 6px; color: #334155; }}
    .divider {{ border: 0; border-top: 1px solid #cbd5e1; margin: 32px 0; }}
    .table-container {{ overflow-x: auto; margin: 20px 0; }}
    .report-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    .report-table th {{ background: #1e3a8a; color: #ffffff; padding: 10px 12px; text-align: left; }}
    .report-table td {{ padding: 9px 12px; border-bottom: 1px solid #e2e8f0; }}
    .report-table tr:nth-child(even) {{ background: #f8fafc; }}
    pre {{ background: #0f172a; color: #e2e8f0; padding: 16px; border-radius: 6px; overflow-x: auto; font-family: 'JetBrains Mono', monospace; font-size: 11px; margin: 16px 0; }}
    .print-btn {{
      position: fixed; top: 20px; right: 20px;
      background: #1e3a8a; color: #fff; border: 0;
      padding: 10px 20px; border-radius: 6px; font-weight: 600; cursor: pointer;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
  </style>
</head>
<body>
  <button class="print-btn no-print" onclick="window.print()">🖨️ Print / Save as PDF</button>
  <div class="document-page">
    {''.join(html_lines)}
  </div>
</body>
</html>
"""
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f" Master Technical Report HTML/PDF printable version generated: {out_html}")

if __name__ == '__main__':
    export_report()
