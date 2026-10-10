"""LaTeX math for build.py (math_render.py: not named math.py to avoid shadowing the stdlib module), rendered once at build time with KaTeX (theme/katex, works offline).

In parts/*.html:   inline \\( ... \\)      display \\[ ... \\]
Extras (KaTeX "trust" commands), handy with the step engine:
  \\htmlData{from=1}{...}    part of an equation shown from step 1 (same as data-from on HTML)
  \\htmlClass{hl}{...}       part of an equation highlighted (see .hl in theme/style.css)
Rendered by KaTeX in the headless browser of headless.py (Chrome or Edge): no Node.js needed.
"""
import re
from pathlib import Path

from headless import launch

ROOT = Path(__file__).resolve().parent
MATH = re.compile(r"\\\[(.+?)\\\]|\\\((.+?)\\\)", re.S)

# shortcuts usable in every equation (like \newcommand in a preamble)
MACROS = {
    r"\x": r"\boldsymbol{x}",
    r"\n": r"\boldsymbol{n}",
    r"\dd": r"\mathrm{d}",
}

# runs in the browser page, with katex.min.js from theme/katex: the same KaTeX call as before
JS = """(items) => items.map(([tex, display, macros]) => katex.renderToString(tex, {
  displayMode: display, throwOnError: false, strict: false, trust: true, macros }))"""


SKIP = re.compile(r"(<style\b.*?</style>|<script\b.*?</script>|<!--.*?-->)", re.S)   # never touched


def process(html):
    pieces = SKIP.split(html)                    # odd indices: style / script / comments, kept as they are
    text = "\x00".join(pieces[0::2])
    text = _render(text).split("\x00")
    pieces[0::2] = text
    return "".join(pieces)


def _render(html):
    found = list(MATH.finditer(html))
    if not found:
        return html
    items = [[(m.group(1) if m.group(1) is not None else m.group(2)).strip(), m.group(1) is not None, MACROS] for m in found]
    out = _katex(items)
    for (tex, *_), r in zip(items, out):
        if 'katex-error' in r:
            print("WARNING: KaTeX error in", tex[:60])
    rendered = iter(out)
    return MATH.sub(lambda m: next(rendered), html)


def _katex(items):
    """All the equations of the deck, in one call to KaTeX inside a headless-browser page."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = launch(p)
        page = browser.new_page()
        page.set_content("<!doctype html><html><body></body></html>")
        page.add_script_tag(path=str(ROOT / "theme/katex/katex.min.js"))
        out = page.evaluate(JS, items)
        browser.close()
    return out
