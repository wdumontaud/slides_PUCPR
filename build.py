#!/usr/bin/env python3
"""Assemble the presentation from main.json + parts/*.html + theme/ + assets/ (like `latexmk` for main.tex).

    python build.py                 main.html         working copy, pictures and videos read from assets/
    python build.py --standalone    main_export.html  one file: pictures, videos and fonts are embedded
    python build.py --watch         rebuild main.html on every save (then refresh the browser)
"""
import base64, json, re, sys, time
from pathlib import Path
import bib
import math_render

ROOT = Path(__file__).resolve().parent
DEV_HTML, EXPORT_HTML = ROOT / "main.html", ROOT / "main_export.html"

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>@@title@@</title>
<style>
@@css@@
</style>
</head>
<body>
<div id="stage">
@@parts@@
</div>
<script>window.CONFIG=@@config@@;</script>
<script>
@@field@@
</script>
<script>
@@engine@@
</script>
</body>
</html>
"""

MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".svg": "image/svg+xml",
        ".webm": "video/webm", ".mp4": "video/mp4", ".woff2": "font/woff2"}
ATTR = re.compile(r"""\b((?:src|poster)=)(["'])(assets/[^"']+)\2""")       # <img src="assets/..">, <video poster=..>
CSS_URL = re.compile(r"""url\(\s*(["']?)(assets/[^)"']+)\1\s*\)""")          # background: url(assets/..)
FONT_URL = re.compile(r"""url\(\s*(["']?)(theme/[^)"']+\.woff2)\1\s*\)""")   # @font-face sources
FALLBACK = re.compile(r""",\s*url\([^)]*\)\s*format\(["'](?:woff|truetype)["']\)""")  # only woff2 is shipped
EXTERNAL = re.compile(r"""(?:\bsrc=["']|url\(\s*["']?|<link\b[^>]*\bhref=["'])https?://[^"')\s]+""")


def read(p):
    return (ROOT / p).read_text(encoding="utf-8")


def data_uri(data, mime):
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def svg_bytes(path):
    """An SVG used as a picture cannot load the page's fonts, so the sans font its text needs is put inside the file."""
    text = path.read_text(encoding="utf-8")
    if "CMU Sans" in text:
        faces = [(500, "roman")]
        if re.search(r"bold|font-weight[=:]\s*\"?700", text): faces.append((700, "roman"))
        if "italic" in text: faces.append((500, "italic"))
        css = "".join(
            f'@font-face{{font-family:"CMU Sans Serif";font-style:{style};font-weight:{w};'
            f'src:url({data_uri((ROOT / f"theme/computer-modern/fonts/cmu-sans-serif-{w}-{style}.woff2").read_bytes(), "font/woff2")}) format("woff2")}}'
            for w, style in faces)
        text = re.sub(r"(<svg\b[^>]*>)", lambda m: m.group(1) + f"<style>{css}</style>", text, count=1)
    return text.encode("utf-8")


def resolve(html, export, used, warnings):
    """Point every asset at its file (working copy) or embed it (standalone)."""
    def asset(rel):
        f = ROOT / rel
        if not f.is_file():
            warnings.append(f"missing file: {rel}")
            return rel
        used.add(rel)
        if f.suffix.lower() == ".svg":                 # always embedded: keeps the page's fonts working
            return data_uri(svg_bytes(f), MIME[".svg"])
        if export:
            return data_uri(f.read_bytes(), MIME.get(f.suffix.lower(), "application/octet-stream"))
        return rel

    html = ATTR.sub(lambda m: f"{m.group(1)}{m.group(2)}{asset(m.group(3))}{m.group(2)}", html)
    html = CSS_URL.sub(lambda m: f"url({asset(m.group(2))})", html)
    if export:
        def font(m):
            if not (ROOT / m.group(2)).is_file():
                warnings.append(f"missing font: {m.group(2)}")
                return m.group(0)
            return f"url({data_uri((ROOT / m.group(2)).read_bytes(), 'font/woff2')})"
        html = FONT_URL.sub(font, html)
    for m in EXTERNAL.finditer(html):                  # nothing may load from the internet
        warnings.append("loads from the internet: " + m.group(0)[:90])
    return html


def assemble(export, used, warnings):
    cfg = json.loads(read("main.json"))
    parts = "\n".join(f"<!-- ==== {p} ==== -->\n{read(p)}" for p in cfg["parts"])
    if cfg.get("bibliography"):                     # \cite{key} -> numbers, slide footers, References appendix
        parts = bib.process(parts, bib.parse(read(cfg["bibliography"])))
    parts = math_render.process(parts)              # \( inline \) and \[ display \] LaTeX -> KaTeX HTML
    katex = read("theme/katex/katex.min.css").replace("url(fonts/", "url(theme/katex/fonts/")
    sans = read("theme/computer-modern/cmu-sans-serif.css").replace('url("./fonts/', 'url("theme/computer-modern/fonts/')
    values = dict(
        title=cfg.get("title", "Presentation"),
        css=FALLBACK.sub("", katex) + "\n" + FALLBACK.sub("", sans) + "\n" + read("theme/style.css"),
        parts=parts,
        config=json.dumps(cfg, ensure_ascii=False),
        field=read("theme/field.js"),
        engine=read("theme/engine.js"),
    )
    html = TEMPLATE
    for k, v in values.items():
        html = html.replace(f"@@{k}@@", v)
    return resolve(html, export, used, warnings), len(cfg["parts"])


def build(export=False):
    used, warnings = set(), []
    html, n = assemble(export, used, warnings)
    out = EXPORT_HTML if export else DEV_HTML
    out.write_text(html, encoding="utf-8")
    print(f"{out.name} written from {n} parts ({out.stat().st_size / 1e6:.1f} MB)")
    for w in warnings:
        print("  warning:", w)
    unused = [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "assets").rglob("*"))
              if p.is_file() and not p.name.startswith(".") and p.relative_to(ROOT).as_posix() not in used]
    if unused:
        print("  assets not used by the slides:", ", ".join(unused))


def stamp():
    files = [ROOT / "main.json", ROOT / "refs.bib", *(ROOT / "theme").rglob("*.*"),
             *(ROOT / "parts").glob("*.html"), *(ROOT / "assets").rglob("*.svg")]
    return {f: f.stat().st_mtime for f in files if f.is_file()}


if __name__ == "__main__":
    try:
        build(export="--standalone" in sys.argv)
    except RuntimeError as e:          # e.g. no browser: say what to install, without a traceback
        sys.exit(str(e))
    if "--watch" in sys.argv:
        print("watching parts/, theme/ and assets/*.svg (Ctrl+C to stop)")
        last = stamp()
        while True:
            time.sleep(0.7)
            cur = stamp()
            if cur != last:
                last = cur
                try:
                    build()
                except Exception as e:  # keep watching on errors
                    print("build error:", e)
