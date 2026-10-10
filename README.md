# Seminar presentation (HTML)

```
main.json            title, author, ordered list of parts   (≈ main.tex)
parts/*.html         one file per section / group of slides (≈ parts/*.tex)
theme/style.css      look & feel                            (≈ presentation.sty)
theme/engine.js      nav bubbles, TOC, footer, fullscreen, steps, PDF mode
theme/field.js       animated contour-line background
theme/katex/         LaTeX equations, rendered at build time (works offline)
theme/computer-modern/  the sans font of the deck (SIL Open Font License)
assets/              pictures, videos, drawings
refs.bib             bibliography (cite with \cite{key} in the parts)
bib.py               BibTeX support used by build.py
math_render.py       LaTeX math -> KaTeX HTML, at build time
headless.py          the Chrome / Edge used by math_render.py and export_pdf.py
assets/icons/*.svg   drawings (editable in assets/illustrations.pptx)
build.py             assembles main.html and main_export.html from the above
export_pdf.py        main_export.html -> main.pdf (one page per step)
build_all.bat        Windows: runs all three steps (double-click)
```

## Workflow
Double-click `build_all.bat` after each change. It writes:
- `main.html`: working copy, open it in the browser and refresh (F5) after a change;
- `main_export.html`: one self-contained file (fonts, pictures and videos inside), works offline;
- `main.pdf`: one page per step, like the beamer overlays.

Do not edit `main.html` or `main_export.html` by hand: they are regenerated from `parts/`, `theme/` and `assets/`.
The first run installs `playwright` and `pypdf` with pip. The build and the PDF use the Google Chrome or Microsoft Edge already installed.

Without the script: `python build.py` (main.html), `python build.py --standalone` (main_export.html),
`python export_pdf.py` (main.pdf), or `python build.py --watch` to rebuild main.html on each save.

## Writing parts
```html
<!-- section: Physical problem -->          new section: goes in the TOC and the top bar
<!-- subsection: Governing equation -->     optional, TOC only

<section class="slide" data-title="Governing equation">   one slide = one bubble
  ...content...
</section>
```
* A part may contain its own `<style>` and `<script>`.
* `data-layout="free"`: no content wrapper (position things yourself); `data-layout="title"`: title slide.
* Steps inside a slide (like beamer `\pause`): `<section class="slide" data-steps="2">`, then
  `<div data-from="1">` (shown from step 1) or `<div data-until="0">` (shown up to step 0).
  The slide gets `data-step="k"` for CSS and a `step` event for JS; the PDF has one page per step.
* Videos: a video cannot play inside a PDF, so it is a still frame there, at `data-pdf-t="10"` seconds (default 0).
* Drawings (`assets/*.svg`) are embedded as images with the deck's sans font, so their text looks the same everywhere.
* Citations: `\cite{key}` or `\cite{key1,key2}` with keys from `refs.bib` -> numbers in order of first citation,
  a footer with the short references on the slide (disable with `data-footcite="off"` on the section),
  and a "References" appendix at the end with the full entries (click a number to jump to it).
* Drawings: `assets/illustrations.pptx` holds every `assets/icons/*.svg`. In PowerPoint: right-click > Convert to Shape,
  edit, then right-click the group > Save as Picture > SVG over the same file, and rebuild.
* To add a part: create `parts/09-xxx.html` and add it to `main.json`.

## Viewing
`← →` / space / click: navigate · `F`: fullscreen · `Home` / `End` · click a bubble to jump.
Buttons "Fullscreen" and "PDF" appear top right when the mouse moves. The PDF button prints one page per slide;
the complete PDF (one page per step) is made by `build_all.bat`.

## Equations (LaTeX)

In `parts/*.html`, write LaTeX as in a .tex file: inline `\( ... \)`, display `\[ ... \]`.
They are rendered at build time by KaTeX (`theme/katex/`) inside the Chrome or Edge already installed (no Node.js needed).
Shortcuts (`\x`, `\n` bold vectors, `\dd`) are defined in `math_render.py` (`MACROS`).
`\htmlData{from=1}{...}` shows part of an equation from step 1 on.
