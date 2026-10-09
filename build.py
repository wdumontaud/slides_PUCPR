#!/usr/bin/env python3
"""Assemble index.html from main.json + parts/*.html + theme/ (like `latexmk` for main.tex).

    python build.py            build once
    python build.py --watch    rebuild whenever a part / theme file changes
"""
import json, sys, time
from pathlib import Path
import bib
import math_render

ROOT = Path(__file__).resolve().parent

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>@@title@@</title>
<!-- Computer Modern Sans (beamer default font); needs an internet connection -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/computer-modern@0.1.3/cmu-sans-serif.css">
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


def read(p):
    return (ROOT / p).read_text(encoding="utf-8")


def build():
    cfg = json.loads(read("main.json"))
    parts = "\n".join(f"<!-- ==== {p} ==== -->\n{read(p)}" for p in cfg["parts"])
    if cfg.get("bibliography"):                     # \cite{key} -> numbers, slide footers, References appendix
        parts = bib.process(parts, bib.parse(read(cfg["bibliography"])))
    parts = math_render.process(parts)              # \( inline \) and \[ display \] LaTeX -> KaTeX HTML
    values = dict(
        title=cfg.get("title", "Presentation"),
        css=read("theme/katex/katex.min.css").replace("url(fonts/", "url(theme/katex/fonts/") + "\n" + read("theme/style.css"),
        parts=parts,
        config=json.dumps(cfg, ensure_ascii=False),
        field=read("theme/field.js"),
        engine=read("theme/engine.js"),
    )
    html = TEMPLATE
    for k, v in values.items():
        html = html.replace(f"@@{k}@@", v)
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"index.html built from {len(cfg['parts'])} parts")


def stamp():
    files = [ROOT / "main.json", ROOT / "refs.bib", *(ROOT / "theme").glob("*.*"), *(ROOT / "parts").glob("*.html")]
    return {f: f.stat().st_mtime for f in files if f.exists()}


if __name__ == "__main__":
    build()
    if "--watch" in sys.argv:
        print("watching for changes (Ctrl+C to stop)")
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
