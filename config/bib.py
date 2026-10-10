"""Minimal BibTeX support for build.py (numbered citations, like LaTeX with the unsrt style).

In parts/*.html:   ... text\\cite{key} ...   or   \\cite{key1,key2}
  -> superscript number(s), numbered in order of first citation in the whole presentation;
  -> each slide that cites gets a footer with the short references (like beamer \\footcite),
     unless the slide has data-footcite="off" (e.g. a slide that already shows the authors);
  -> a "References" appendix (one or more slides) lists every cited entry in full.
"""
import re, unicodedata

# ---------------------------------------------------------------- parsing
def _fields(body):
    out, i, n = {}, 0, len(body)
    while i < n:
        m = re.compile(r"\s*,?\s*([A-Za-z_-]+)\s*=\s*").match(body, i)
        if not m:
            break
        name, i = m.group(1).lower(), m.end()
        if i < n and body[i] in "{\"":
            close = "}" if body[i] == "{" else "\""
            depth, j = 0, i
            while j < n:
                c = body[j]
                if c == "{": depth += 1
                elif c == "}": depth -= 1
                if (close == "}" and depth == 0 and c == "}") or (close == "\"" and c == "\"" and j > i and depth == 0):
                    break
                j += 1
            out[name], i = body[i + 1:j], j + 1
        else:
            m2 = re.compile(r"[^,]+").match(body, i)
            out[name], i = m2.group(0).strip(), m2.end()
    return out


def parse(text):
    """Return {key: {'type':..., field:value}} from a .bib string (comments starting with % are ignored)."""
    text = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("%"))
    entries = {}
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        start, depth, j = m.end(), 1, m.end()
        while j < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        e = _fields(text[start:j - 1])
        e["type"] = m.group(1).lower()
        entries[m.group(2)] = e
    return entries


# ---------------------------------------------------------------- LaTeX -> text
_ACC = {"'": "\u0301", "`": "\u0300", "^": "\u0302", '"': "\u0308", "~": "\u0303", "c": "\u0327", "v": "\u030c", "=": "\u0304"}

def tex(s):
    s = re.sub(r"\\([`'^\"~=])\s*\{?\\?([A-Za-z])\}?", lambda m: unicodedata.normalize("NFC", ("ı" if m.group(2) == "i" and "\\i" in m.group(0) else m.group(2)) + _ACC[m.group(1)]), s)
    s = re.sub(r"\\([cv])\{([A-Za-z])\}", lambda m: unicodedata.normalize("NFC", m.group(2) + _ACC[m.group(1)]), s)
    s = s.replace("\\i", "ı").replace("\\&", "&amp;").replace("---", "—").replace("--", "–").replace("~", "\u00a0")
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)
    return re.sub(r"\s+", " ", s.replace("{", "").replace("}", "")).strip()


def _names(e):
    return [tex(a.strip()) for a in re.split(r"\s+and\s+", e.get("author", "")) if a.strip()]

def _last(name):
    return name.split(",")[0].strip() if "," in name else name.split()[-1]

def _full(name):            # "Last, F." -> "F. Last"
    if "," in name:
        last, first = [x.strip() for x in name.split(",", 1)]
        return f"{first} {last}"
    return name


def short(e):
    """Footer form: Gosselin et al., “Title”, 2016."""
    a = _names(e)
    who = _last(a[0]) + (" et al." if len(a) > 2 else (" and " + _last(a[1]) if len(a) == 2 else "")) if a else ""
    return f"{who}, “{tex(e.get('title', ''))}”, {e.get('year', '')}."


def full(e):
    """References form: F. Last, F. Last and F. Last, Title, Journal 12 (3) (2016) 1–10. doi"""
    a = [_full(x) for x in _names(e)]
    who = ", ".join(a[:-1]) + " and " + a[-1] if len(a) > 1 else (a[0] if a else "")
    venue = tex(e.get("journal", e.get("booktitle", e.get("publisher", ""))))
    vol = e.get("volume", "") + (f" ({e['number']})" if e.get("number") else "")
    pages = tex(e.get("pages", ""))
    out = f"{who}, {tex(e.get('title', ''))}, <i>{venue}</i>"
    if vol: out += f" {vol}"
    out += f" ({e.get('year', '')})"
    if pages: out += f" {pages}"
    out += "."
    if e.get("doi"):
        out += f' <a href="https://doi.org/{e["doi"]}" target="_blank">doi:{e["doi"]}</a>'
    return out


# ---------------------------------------------------------------- processing of the assembled parts
CITE = re.compile(r"\\cite\{([^}]*)\}")
SECTION = re.compile(r"(<section\b[^>]*class=\"[^\"]*\bslide\b[^>]*>)(.*?)(</section>)", re.S)

def process(html, bib, per_slide=11):
    order = []
    for m in CITE.finditer(html):
        for k in (x.strip() for x in m.group(1).split(",")):
            if k not in order:
                order.append(k)
    missing = [k for k in order if k not in bib]
    if missing:
        print("WARNING: unknown citation key(s):", ", ".join(missing))
    num = {k: i + 1 for i, k in enumerate(order)}

    def cite(m):
        ks = [x.strip() for x in m.group(1).split(",")]
        return '<sup class="cite">' + ",".join(f'<a href="#" data-ref="{num[k]}">{num[k]}</a>' if k in bib else "?" for k in ks) + "</sup>"

    def slide(m):
        head, body, tail = m.groups()
        keys = []
        for c in CITE.finditer(body):
            keys += [k.strip() for k in c.group(1).split(",") if k.strip() in bib and k.strip() not in keys]
        body = CITE.sub(cite, body)
        if keys and 'data-footcite="off"' not in head:
            body += '\n  <div class="refs auto">' + "<br>".join(f"<sup>{num[k]}</sup> {short(bib[k])}" for k in sorted(keys, key=num.get)) + "</div>\n"
        return head + body + tail

    html = SECTION.sub(slide, html)
    if not order:
        return html
    found = [k for k in order if k in bib]
    pages = [found[i:i + per_slide] for i in range(0, len(found), per_slide)]
    refs = "\n<!-- appendix -->\n"
    for n, keys in enumerate(pages):
        title = "References" + (f" ({n + 1}/{len(pages)})" if len(pages) > 1 else "")
        items = "".join(f'<li value="{num[k]}">{full(bib[k])}</li>' for k in keys)
        refs += f'<section class="slide s-refs" data-title="{title}"><ol class="biblio">{items}</ol></section>\n'
    return html + refs
