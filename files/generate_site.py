#!/usr/bin/env python3
"""
generate_site.py
Convert RNAseq_Oui Obsidian markdown -> static HTML site (GitHub Pages ready)
- Copies all result files (CSV, PDF, PNG, log, HTML) into site/files/
- Rewrites ./File/... links -> files/...
Usage: python3 generate_site.py
"""

import os, re, shutil
import markdown
from pathlib import Path

# -- Paths ---------------------------------------------------------------------
# Script lives at: <workspace>/01 Projects/RNAseq_Oui/Daily_Logs/File/generate_site.py
# BASE = 5 levels up = workspace root
BASE      = Path(__file__).resolve().parent.parent.parent.parent.parent
OUT_DIR   = BASE / "RNAseq_Oui_site"
FILES_SRC = BASE / "01 Projects/RNAseq_Oui/Daily_Logs/File"
FILES_DST = OUT_DIR / "files"

PAGES = [
    {
        "id":    "index",
        "title": "RNAseq Oui - Project Overview",
        "src":   BASE / "01 Projects/RNAseq_Oui/RNAseq_Oui.md",
        "out":   "index.html",
        "nav":   "Project Overview",
    },
    {
        "id":    "setup",
        "title": "Setup (2026-04-30)",
        "src":   BASE / "01 Projects/RNAseq_Oui/Daily_Logs/2026-04-30-RNAseq-Oui-Setup.md",
        "out":   "2026-04-30-setup.html",
        "nav":   "2026-04-30  Setup",
    },
    {
        "id":    "qc",
        "title": "FastQC Results (2026-05-01)",
        "src":   BASE / "01 Projects/RNAseq_Oui/Daily_Logs/2026-05-01-RNAseq-Oui-QC-Results.md",
        "out":   "2026-05-01-qc.html",
        "nav":   "2026-05-01  FastQC QC",
    },
    {
        "id":    "hisat2",
        "title": "HISAT2 Mapping (2026-05-01)",
        "src":   BASE / "01 Projects/RNAseq_Oui/Daily_Logs/2026-05-01-RNAseq-Oui-HISAT2-Mapping.md",
        "out":   "2026-05-01-hisat2.html",
        "nav":   "2026-05-01  HISAT2 Mapping",
    },
    {
        "id":    "prepde",
        "title": "prepDE Count Matrix (2026-05-01)",
        "src":   BASE / "01 Projects/RNAseq_Oui/Daily_Logs/2026-05-01-RNAseq-Oui-prepDE.md",
        "out":   "2026-05-01-prepde.html",
        "nav":   "2026-05-01  prepDE",
    },
    {
        "id":    "deseq2",
        "title": "DESeq2 Analysis (2026-05-01)",
        "src":   BASE / "01 Projects/RNAseq_Oui/Daily_Logs/2026-05-01-RNAseq-Oui-DESeq2.md",
        "out":   "2026-05-01-deseq2.html",
        "nav":   "2026-05-01  DESeq2 v1",
    },
    {
        "id":    "deseq2v2",
        "title": "DESeq2 Analysis v2 — ตัด DC3/DN3 (2026-05-01)",
        "src":   BASE / "01 Projects/RNAseq_Oui/Daily_Logs/2026-05-01-RNAseq-Oui-DESeq2-v2.md",
        "out":   "2026-05-01-deseq2-v2.html",
        "nav":   "2026-05-01  DESeq2 v2 (11 samples)",
    },
    {
        "id":    "fastp",
        "title": "fastp Trimming (2026-05-08)",
        "src":   BASE / "01 Projects/RNAseq_Oui/Daily_Logs/2026-05-08-RNAseq-Oui-Fastp.md",
        "out":   "2026-05-08-fastp.html",
        "nav":   "2026-05-08  fastp Trimming",
    },
    {
        "id":    "hisat2v2",
        "title": "HISAT2 Mapping v2 (2026-05-08)",
        "src":   BASE / "01 Projects/RNAseq_Oui/Daily_Logs/2026-05-08-RNAseq-Oui-HISAT2-v2.md",
        "out":   "2026-05-08-hisat2-v2.html",
        "nav":   "2026-05-08  HISAT2 v2 (trimmed)",
    },
    {
        "id":    "deseq2v3",
        "title": "DESeq2 Analysis v3 — Final (2026-05-08)",
        "src":   BASE / "01 Projects/RNAseq_Oui/Daily_Logs/2026-05-08-RNAseq-Oui-DESeq2-v3.md",
        "out":   "2026-05-08-deseq2-v3.html",
        "nav":   "2026-05-08  DESeq2 v3 Final ✓",
    },
]

STEM_TO_FILE = {Path(p["src"]).stem: p["out"] for p in PAGES}

# -- File extension -> icon + label --------------------------------------------
EXT_META = {
    ".csv":  ("CSV",   "download", "#0ea5e9"),
    ".txt":  ("TXT",   "download", "#64748b"),
    ".log":  ("LOG",   "_blank",   "#64748b"),
    ".html": ("HTML",  "_blank",   "#8b5cf6"),
    ".pdf":  ("PDF",   "_blank",   "#ef4444"),
    ".png":  ("PNG",   "_blank",   "#10b981"),
    ".xls":  ("XLS",   "download", "#22c55e"),
    ".py":   ("PY",    "_blank",   "#f59e0b"),
    ".r":    ("R",     "_blank",   "#3b82f6"),
}

EXT_ICONS = {
    ".csv": "📄", ".txt": "📝", ".log": "📋", ".html": "🌐",
    ".pdf": "📕", ".png": "🖼", ".xls": "📊", ".py": "🐍", ".r": "📊",
}

# -- Markdown converter --------------------------------------------------------
MD = markdown.Markdown(extensions=[
    "tables", "fenced_code", "codehilite", "toc", "nl2br",
], extension_configs={
    "codehilite": {"css_class": "highlight", "guess_lang": False},
})

def convert_md(text):
    MD.reset()

    # 1. Obsidian [[wikilinks]] -> HTML anchor
    def replace_wikilink(m):
        stem  = m.group(1).replace(".md", "")
        label = m.group(2) if m.group(2) else stem
        target = STEM_TO_FILE.get(stem, "#")
        return '<a href="' + target + '">' + label + '</a>'
    text = re.sub(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', replace_wikilink, text)

    # 2. ./File/... links -> files/...
    def replace_file_link(m):
        label = m.group(1)
        path  = m.group(2)
        href  = "files/" + path
        return '[' + label + '](' + href + ')'
    text = re.sub(r'\[([^\]]+)\]\(\.\/File\/([^\)]+)\)', replace_file_link, text)

    # 3. Convert to HTML
    html = MD.convert(text)

    # 4. Post-process <a> tags for file links - add icons and badges
    def enhance_link(m):
        attrs = m.group(1)
        label = m.group(2)
        href_m = re.search(r'href="([^"]+)"', attrs)
        if not href_m:
            return m.group(0)
        href = href_m.group(1)
        ext  = Path(href).suffix.lower()
        if ext in EXT_META and "files/" in href:
            badge, target, color = EXT_META[ext]
            icon = EXT_ICONS.get(ext, "🔗")
            t_attr = 'target="' + target + '"' if target != "download" else "download"
            return (
                '<a href="' + href + '" ' + t_attr + ' class="file-link" style="--badge-color:' + color + '">'
                + icon + ' ' + label + ' <span class="file-badge">' + badge + '</span>'
                + '</a>'
            )
        return m.group(0)
    html = re.sub(r'<a([^>]*)>([^<]+)</a>', enhance_link, html)

    return html

# -- CSS -----------------------------------------------------------------------
CSS = """
:root {
  --bg:#f8f9fa; --sidebar-bg:#1e293b; --sidebar-text:#cbd5e1;
  --sidebar-active:#38bdf8; --sidebar-hover:#334155;
  --accent:#0ea5e9; --accent2:#6366f1; --text:#1e293b;
  --muted:#64748b; --border:#e2e8f0; --code-bg:#f1f5f9; --card:#ffffff;
  --badge-color:#0ea5e9;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);
  color:var(--text);display:flex;min-height:100vh;font-size:15px}

#sidebar{width:260px;min-height:100vh;background:var(--sidebar-bg);
  color:var(--sidebar-text);position:sticky;top:0;height:100vh;
  overflow-y:auto;flex-shrink:0}
#sidebar .brand{padding:20px 18px 16px;border-bottom:1px solid #334155;
  font-size:13px;font-weight:700;color:var(--sidebar-active);
  letter-spacing:.05em;text-transform:uppercase}
#sidebar .brand span{display:block;font-size:11px;color:var(--muted);
  font-weight:400;text-transform:none;margin-top:2px}
#sidebar nav{padding:10px 0}
#sidebar nav .section-label{padding:14px 18px 4px;font-size:10px;
  font-weight:700;text-transform:uppercase;color:#475569;letter-spacing:.08em}
#sidebar nav a{display:block;padding:8px 18px;color:var(--sidebar-text);
  text-decoration:none;font-size:13px;border-left:3px solid transparent;
  transition:all .15s}
#sidebar nav a:hover{background:var(--sidebar-hover);color:#fff}
#sidebar nav a.active{background:var(--sidebar-hover);color:var(--sidebar-active);
  border-left-color:var(--sidebar-active);font-weight:600}

#main{flex:1;padding:36px 48px;max-width:980px}
#main h1{font-size:2em;font-weight:800;margin-bottom:6px;line-height:1.2}
#main h2{font-size:1.35em;font-weight:700;margin:32px 0 12px;
  padding-bottom:6px;border-bottom:2px solid var(--border)}
#main h3{font-size:1.1em;font-weight:700;margin:24px 0 10px;color:var(--accent2)}
#main p{line-height:1.75;margin-bottom:12px;color:#334155}
#main a{color:var(--accent);text-decoration:none}
#main a:hover{text-decoration:underline}
#main ul,#main ol{padding-left:22px;margin-bottom:12px}
#main li{line-height:1.75;margin-bottom:3px}
#main strong{color:var(--text);font-weight:700}
#main hr{border:none;border-top:1px solid var(--border);margin:28px 0}

#main table{border-collapse:collapse;width:100%;margin:16px 0;
  font-size:.9em;border-radius:8px;overflow:hidden;
  box-shadow:0 1px 4px rgba(0,0,0,.08)}
#main th{background:var(--sidebar-bg);color:#e2e8f0;padding:10px 14px;
  text-align:left;font-weight:600;font-size:.85em}
#main td{padding:9px 14px;border-bottom:1px solid var(--border)}
#main tr:last-child td{border-bottom:none}
#main tr:nth-child(even) td{background:#f8fafc}
#main tr:hover td{background:#f0f9ff}

#main code{background:var(--code-bg);padding:2px 6px;border-radius:4px;
  font-size:.88em;font-family:'Cascadia Code','Fira Code',monospace;color:#be185d}
#main pre{background:#1e293b;border-radius:8px;padding:18px;
  overflow-x:auto;margin:16px 0}
#main pre code{background:none;color:#e2e8f0;padding:0;
  font-size:.85em;line-height:1.6}
.highlight{background:#1e293b!important;border-radius:8px;
  padding:18px!important;margin:16px 0;overflow-x:auto}
.highlight pre{background:none;padding:0;margin:0;border-radius:0}
.highlight code{background:none;color:#e2e8f0;padding:0;font-size:.85em}

a.file-link{
  display:inline-flex;align-items:center;gap:6px;
  background:#f0f9ff;border:1px solid #bae6fd;
  padding:3px 10px;border-radius:6px;font-size:.85em;
  color:#0369a1;text-decoration:none;transition:all .15s;
  white-space:nowrap;
}
a.file-link:hover{background:#e0f2fe;border-color:#38bdf8;
  color:#0284c7;text-decoration:none}
.file-badge{background:var(--badge-color);color:#fff;font-size:.7em;
  font-weight:700;padding:1px 6px;border-radius:4px;
  letter-spacing:.05em;text-transform:uppercase}

.meta-bar{display:flex;align-items:center;gap:12px;
  padding:10px 16px;background:var(--card);border:1px solid var(--border);
  border-radius:8px;margin-bottom:28px;font-size:.85em;color:var(--muted)}
.badge{display:inline-block;padding:2px 10px;border-radius:999px;
  font-size:.78em;font-weight:700;text-transform:uppercase;letter-spacing:.05em}
.badge-done{background:#dcfce7;color:#166534}
.badge-wip{background:#fef9c3;color:#713f12}

footer{margin-top:60px;padding-top:20px;border-top:1px solid var(--border);
  font-size:.8em;color:var(--muted);text-align:center}

@media(max-width:768px){
  body{flex-direction:column}
  #sidebar{width:100%;min-height:auto;height:auto;position:static}
  #main{padding:20px}
}
"""

# -- Nav builder ---------------------------------------------------------------
def build_nav(active_id):
    parts = []
    parts.append('<div class="section-label">Project</div>')
    p = PAGES[0]
    cls = "active" if p["id"] == active_id else ""
    parts.append('<a href="' + p["out"] + '" class="' + cls + '">' + p["nav"] + '</a>')
    parts.append('<div class="section-label">Daily Logs</div>')
    for p in PAGES[1:]:
        cls = "active" if p["id"] == active_id else ""
        parts.append('<a href="' + p["out"] + '" class="' + cls + '">' + p["nav"] + '</a>')
    return "".join(parts)

# -- Page wrapper --------------------------------------------------------------
def wrap_html(page, body_html):
    status_m = re.search(r'\*\*Status:\*\*\s*([\w ]+)', body_html)
    status   = status_m.group(1).strip() if status_m else ""
    badge = ""
    if "Done" in status:
        badge = '<span class="badge badge-done">Done</span>'
    elif "Progress" in status:
        badge = '<span class="badge badge-wip">In Progress</span>'

    badge_part = "<span>·</span>" + badge if badge else ""

    return (
        "<!DOCTYPE html>\n"
        '<html lang="th">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">\n'
        "<title>" + page["title"] + " | RNAseq Oui</title>\n"
        "<style>" + CSS + "</style>\n"
        "</head>\n"
        "<body>\n"
        '<div id="sidebar">\n'
        '  <div class="brand">RNAseq Oui Lab Notebook\n'
        '    <span>Wanchana 2026</span>\n'
        '  </div>\n'
        "  <nav>" + build_nav(page["id"]) + "</nav>\n"
        "</div>\n"
        '<div id="main">\n'
        '  <div class="meta-bar">\n'
        "    <span>RNAseq Oui</span><span>·</span>\n"
        "    <span>IRGSP-1.0 (Oryza sativa)</span>\n"
        "    <span>·</span><span>13 samples</span>\n"
        "    " + badge_part + "\n"
        "  </div>\n"
        "  " + body_html + "\n"
        "  <footer>RNAseq Oui Lab Notebook · Wanchana 2026</footer>\n"
        "</div>\n"
        "</body>\n"
        "</html>"
    )

# -- Copy result files ---------------------------------------------------------
SKIP_EXTS  = {'.rdata', '.rhistory', '.zip'}
SKIP_NAMES = {'.RData', '.Rhistory'}

def copy_files():
    copied = skipped = 0
    for item in FILES_SRC.rglob('*'):
        if not item.is_file():
            continue
        if item.name in SKIP_NAMES or item.suffix.lower() in SKIP_EXTS:
            skipped += 1
            continue
        rel  = item.relative_to(FILES_SRC)
        dest = FILES_DST / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dest)
        copied += 1
    return copied, skipped

# -- Main ----------------------------------------------------------------------
OUT_DIR.mkdir(exist_ok=True)
FILES_DST.mkdir(parents=True, exist_ok=True)

# 1. Copy result files
print("Copying result files...")
copied, skipped = copy_files()
print("  Copied: " + str(copied) + " files  |  Skipped: " + str(skipped) + " files")

# 2. Generate HTML pages
print("\nGenerating HTML pages...")
for page in PAGES:
    src = Path(page["src"])
    if not src.exists():
        print("  [SKIP] Not found: " + src.name)
        continue
    text = src.read_text(encoding="utf-8")
    body = convert_md(text)
    html = wrap_html(page, body)
    out  = OUT_DIR / page["out"]
    out.write_text(html, encoding="utf-8")
    size = out.stat().st_size // 1024
    print("  [OK] " + page["out"] + "  (" + str(size) + " KB)")

# 3. .nojekyll for GitHub Pages
(OUT_DIR / ".nojekyll").touch()

# 4. Summary
html_files  = list(OUT_DIR.glob("*.html"))
all_files   = [f for f in OUT_DIR.rglob("*") if f.is_file()]
print("\nSite ready: " + str(OUT_DIR))
print("  HTML pages : " + str(len(html_files)))
print("  Total files: " + str(len(all_files)))
print("\nTop-level contents:")
for f in sorted(OUT_DIR.iterdir()):
    if f.is_dir():
        n = len(list(f.rglob('*')))
        print("  [dir]  " + f.name + "/  (" + str(n) + " items)")
    elif not f.name.startswith('.'):
        print("  [file] " + f.name)
