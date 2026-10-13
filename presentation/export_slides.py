"""
Presentation Deck HTML Exporter
================================
Converts presentation_deck.md into an interactive, self-contained HTML slide deck
with keyboard navigation (Left/Right arrow keys) and institutional styling.
"""

import os
import re

def export_slides():
    md_path = 'presentation/presentation_deck.md'
    out_html = 'presentation/index.html'

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by slide
    raw_slides = content.split('---')
    slides = [s.strip() for s in raw_slides if s.strip()]

    html_slides = []
    for idx, slide_md in enumerate(slides):
        lines = slide_md.split('\n')
        slide_title = ""
        slide_body = []
        for line in lines:
            if line.startswith('# '):
                slide_title = line.replace('# ', '').strip()
            elif line.startswith('## '):
                slide_title = line.replace('## ', '').strip()
            elif line.startswith('- '):
                slide_body.append(f"<li>{line[2:].strip()}</li>")
            elif line.strip():
                slide_body.append(f"<p>{line.strip()}</p>")

        body_html = "\n".join(slide_body)
        if slide_body and slide_body[0].startswith('<li>'):
            body_html = f"<ul>{body_html}</ul>"

        html_slides.append(f"""
        <div class="slide {'active' if idx == 0 else ''}" id="slide-{idx}">
          <div class="slide-header">
            <span class="slide-num">SLIDE {idx+1} OF {len(slides)}</span>
            <h2>{slide_title}</h2>
          </div>
          <div class="slide-content">
            {body_html}
          </div>
        </div>
        """)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Securitisation AI Agent - Executive Presentation</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #090e1a;
      --card: #121a2d;
      --border: #1e2c4a;
      --accent: #06b6d4;
      --accent-blue: #2563eb;
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
      justify-content: center;
      align-items: center;
    }}
    .presentation-container {{
      width: 90%;
      max-width: 1100px;
      height: 80vh;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .slide {{
      display: none;
      height: 100%;
      padding: 48px 56px;
      flex-direction: column;
      justify-content: flex-start;
      gap: 28px;
    }}
    .slide.active {{ display: flex; }}
    .slide-num {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      color: var(--accent);
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }}
    .slide-header h2 {{
      font-size: 26px;
      font-weight: 700;
      color: #fff;
      margin-top: 6px;
    }}
    .slide-content {{
      font-size: 15px;
      line-height: 1.7;
      color: #cbd5e1;
      overflow-y: auto;
    }}
    .slide-content ul {{
      padding-left: 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .slide-content strong {{ color: #fff; }}
    .controls {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 32px;
      background: #0b1120;
      border-top: 1px solid var(--border);
      width: 100%;
    }}
    .btn {{
      background: #1e293b;
      color: #fff;
      border: 1px solid var(--border);
      padding: 8px 18px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      font-size: 13px;
      transition: all 0.2s;
    }}
    .btn:hover {{ background: var(--accent-blue); border-color: var(--accent-blue); }}
    .tip {{ font-size: 12px; color: var(--text-muted); }}
  </style>
</head>
<body>
  <div class="presentation-container">
    {''.join(html_slides)}
    <div class="controls">
      <button class="btn" onclick="prevSlide()">◀ Previous</button>
      <span class="tip">Use Left / Right arrow keys to navigate</span>
      <button class="btn" onclick="nextSlide()">Next ▶</button>
    </div>
  </div>

  <script>
    let currentSlide = 0;
    const totalSlides = {len(slides)};
    function showSlide(idx) {{
      document.querySelectorAll('.slide').forEach((s, i) => {{
        s.classList.toggle('active', i === idx);
      }});
      currentSlide = idx;
    }}
    function nextSlide() {{ if (currentSlide < totalSlides - 1) showSlide(currentSlide + 1); }}
    function prevSlide() {{ if (currentSlide > 0) showSlide(currentSlide - 1); }}
    document.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
      if (e.key === 'ArrowLeft') prevSlide();
    }});
  </script>
</body>
</html>
"""
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f" Interactive slides generated: {out_html}")

if __name__ == '__main__':
    export_slides()
