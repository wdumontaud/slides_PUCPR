# Seminar presentation (HTML)

```
build_all.bat        Windows: runs all three steps (double-click)
main.html            working copy (made by the build)
main_export.html     one self-contained file (made by the build, not versioned)
main.pdf             one page per step (made by the build, not versioned)
parts/*.html         one file per section / group of slides (≈ parts/*.tex)
config/              the Python scripts and the deck's settings
  main.json            title, author, ordered list of parts   (≈ main.tex)
  build.py             assembles main.html and main_export.html
  export_pdf.py        main_export.html -> main.pdf (one page per step)
  math_render.py       LaTeX math -> KaTeX HTML, at build time
  headless.py          the Chrome / Edge used by math_render.py and export_pdf.py
  bib.py               BibTeX support used by build.py
theme/style.css      look & feel                            (≈ presentation.sty)
theme/engine.js      nav bubbles, TOC, footer, fullscreen, steps, PDF mode
theme/field.js       animated contour-line background
theme/katex/         LaTeX equations, rendered at build time (works offline)
theme/computer-modern/  the sans font of the deck (SIL Open Font License)
bib/refs.bib         bibliography (cite with \cite{key} in the parts)
assets/              pictures, videos and drawings, one folder per part:
  01-title/ 02-who/ 03-contents/ 04-introduction/ 05-physical/ 06-cosimulation/ 07-conclusion/
  illustrations.pptx   every drawing, one slide per file (editable in PowerPoint)
  who_I_am.pptx        the "who I am" slide in PowerPoint (not read by the build)
```

## Workflow
Double-click `build_all.bat` after each change. It writes:
- `main.html`: working copy, open it in the browser and refresh (F5) after a change;
- `main_export.html`: one self-contained file (fonts, pictures and videos inside), works offline;
- `main.pdf`: one page per step, like the beamer overlays.

Do not edit `main.html` or `main_export.html` by hand: they are regenerated from `parts/`, `theme/` and `assets/`.
The first run installs `playwright` and `pypdf` with pip. The build and the PDF use the Google Chrome or Microsoft Edge already installed.

Without the script: `python config/build.py` (main.html), `python config/build.py --standalone` (main_export.html),
`python config/export_pdf.py` (main.pdf), or `python config/build.py --watch` to rebuild main.html on each save.

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
* Drawings (`assets/**/*.svg`) are embedded as images with the deck's sans font, so their text looks the same everywhere.
  Drawings that change with the steps of a slide (slides 9, 10 and 12) are included inline:
  `<svg class="dom" data-include="assets/05-physical/governing.svg"></svg>`. Their step effects rely on classes inside
  the SVG (`bnd`, `itf`, `nrm`, `wind`, `sunr`, `lw`, `adia`), which a PowerPoint export removes: edit those drawings
  in Inkscape, or keep the classes when exporting.
* Citations: `\cite{key}` or `\cite{key1,key2}` with keys from `bib/refs.bib` -> numbers in order of first citation,
  a footer with the short references on the slide (disable with `data-footcite="off"` on the section),
  and a "References" appendix at the end with the full entries (click a number to jump to it).
* Drawings: `assets/illustrations.pptx` has one slide per drawing file (title = its path). In PowerPoint: right-click >
  Convert to Shape, edit, then right-click the group > Save as Picture > SVG over the same file, and rebuild.
* Figures go in the folder of their part, e.g. `assets/05-physical/`. Pictures that are not drawings (photos, screenshots)
  stay as PNG or JPG in that folder.
* To add a part: create `parts/09-xxx.html`, put its figures in `assets/09-xxx/`, and add it to `config/main.json`.

## Viewing
`← →` / space / click: navigate · `F`: fullscreen · `Home` / `End` · click a bubble to jump.
Buttons "Fullscreen" and "PDF" appear top right when the mouse moves. The PDF button prints one page per slide;
the complete PDF (one page per step) is made by `build_all.bat`.

## Equations (LaTeX)

In `parts/*.html`, write LaTeX as in a .tex file: inline `\( ... \)`, display `\[ ... \]`.
They are rendered at build time by KaTeX (`theme/katex/`) inside the Chrome or Edge already installed (no Node.js needed).
Shortcuts (`\x`, `\n` bold vectors, `\dd`) are defined in `math_render.py` (`MACROS`).
`\htmlData{from=1}{...}` shows part of an equation from step 1 on.
