#!/usr/bin/env python3
"""Export main_export.html to main.pdf: one PDF page per step, like the overlays of a beamer deck.

    python export_pdf.py                       main_export.html -> main.pdf
    python export_pdf.py talk.html talk.pdf

A slide with data-steps="2" gives 3 pages, so the PDF follows the presentation.
A video cannot play inside a PDF: it appears as a still frame, taken at data-pdf-t seconds (default 0).

Needs Google Chrome or Microsoft Edge, and the Python packages:  pip install playwright pypdf
(set CHROME_PATH to another Chrome or Chromium executable to use it instead).
"""
import io, sys
from pathlib import Path

from headless import launch

ROOT = Path(__file__).resolve().parent

# which slide and step is shown, and whether this page is the last one
STATE = """() => {
  const S = [...document.querySelectorAll('section.slide')];
  const k = S.findIndex(s => s.classList.contains('active')), s = S[k];
  const steps = parseInt(s.dataset.steps) || 0, step = parseInt(s.dataset.step) || 0;
  return {slide: k, step, last: k === S.length - 1 && step >= steps};
}"""

# the videos of the current slide stop on their frame (data-pdf-t, in seconds)
FRAME_VIDEOS = """async () => {
  await Promise.all([...document.querySelectorAll('.slide.active video')].map(v => new Promise(done => {
    v.pause();
    const t = parseFloat(v.dataset.pdfT || '0');
    if (Math.abs(v.currentTime - t) < 0.01) return done();
    v.addEventListener('seeked', () => done(), {once: true});
    v.currentTime = t;
    setTimeout(done, 3000);
  })));
}"""


def main():
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader, PdfWriter

    html = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "main_export.html").resolve()
    out = Path(sys.argv[2] if len(sys.argv) > 2 else ROOT / "main.pdf").resolve()
    if not html.is_file():
        sys.exit(f"{html.name} not found: run  python build.py --standalone  first")
    try:                                                 # fails now, not after a minute of rendering, if a viewer holds it
        if out.exists():
            with out.open("ab"):
                pass
    except OSError as e:
        sys.exit(f"Cannot write {out.name} ({e.strerror or e}).\nClose it in your PDF viewer, then run again.")

    writer = PdfWriter()
    with sync_playwright() as p:
        browser = launch(p)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(html.as_uri() + "?export=1")
        page.wait_for_function("window.__ready === true")
        page.wait_for_timeout(500)                       # let the pictures decode
        pages = 0
        while True:
            page.evaluate(FRAME_VIDEOS)
            page.wait_for_timeout(200)
            state = page.evaluate(STATE)
            pdf = PdfReader(io.BytesIO(page.pdf(width="1280px", height="720px", print_background=True,
                                                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})))
            if len(pdf.pages) > 1:                       # something is taller than the slide: keep page 1, say which
                print(f"\n  warning: slide {state['slide'] + 1}, step {state['step']} overflows its page")
            writer.add_page(pdf.pages[0])
            pages += 1
            print(f"\rpage {pages}", end="", flush=True)
            if state["last"]:
                break
            page.keyboard.press("ArrowRight")            # next step, or next slide: same as a click
            page.wait_for_timeout(700)                   # the CSS transitions last .45 to .6 s
        browser.close()
    print()
    try:
        writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    except (AttributeError, TypeError):                  # older pypdf: bigger file, same pages
        pass
    with out.open("wb") as f:
        writer.write(f)
    print(f"written: {out} ({pages} pages, {out.stat().st_size // 1024} kB)")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:                            # no browser: say what to install, without a traceback
        sys.exit(str(e))
