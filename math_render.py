"""LaTeX math for build.py (math_render.py: not named math.py to avoid shadowing the stdlib module), rendered once at build time with KaTeX (theme/katex, works offline).

In parts/*.html:   inline \\( ... \\)      display \\[ ... \\]
Extras (KaTeX "trust" commands), handy with the step engine:
  \\htmlData{from=1}{...}    part of an equation shown from step 1 (same as data-from on HTML)
  \\htmlClass{hl}{...}       part of an equation highlighted (see .hl in theme/style.css)
Needs node on the PATH.
"""
import json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MATH = re.compile(r"\\\[(.+?)\\\]|\\\((.+?)\\\)", re.S)

# shortcuts usable in every equation (like \newcommand in a preamble)
MACROS = {
    r"\x": r"\boldsymbol{x}",
    r"\n": r"\boldsymbol{n}",
    r"\dd": r"\mathrm{d}",
}

JS = r"""
const katex = require(process.argv[1]);
const items = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = items.map(([tex, display, macros]) => katex.renderToString(tex, {
  displayMode: display, throwOnError: false, strict: false, trust: true, macros }));
process.stdout.write(JSON.stringify(out));
"""


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
    res = subprocess.run(["node", "-e", JS, str(ROOT / "theme/katex/katex.min.js")],
                         input=json.dumps(items), capture_output=True, text=True, check=True)
    rendered = iter(json.loads(res.stdout))
    for (tex, *_), r in zip(items, json.loads(res.stdout)):
        if 'katex-error' in r:
            print("WARNING: KaTeX error in", tex[:60])
    return MATH.sub(lambda m: next(rendered), html)
