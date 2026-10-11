# Seminar presentation (HTML)

```
build_all.bat        Windows: runs all three steps (double-click)
main.html            working copy (made by the build)
main_export.html     one self-contained file (made by the build, not versioned)
main.pdf             one page per step (made by the build, not versioned)
parts/<section>/NN-name.html   one folder per section, one file per slide (≈ \input of a .tex per frame)
config/              the Python scripts and the deck's settings
  main.json            title, author, ordered list of the section folders   (≈ main.tex)
  build.py             assembles main.html and main_export.html
  export_pdf.py        main_export.html -> main.pdf (one page per step)
  math_render.py       LaTeX math -> KaTeX HTML, at build time
  headless.py          the Chrome / Edge used by math_render.py and export_pdf.py
  bib.py               BibTeX support used by build.py
  make_band.py         straightens band 1 of the street-canyon frame -> assets/04-introduction/band1.jpg (run by hand, needs Pillow)
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

## Where is my slide?
```
parts/04-introduction/01-context.html     <- slide 4
parts/04-introduction/02-why-optimise.html
parts/05-physical/00-style.html           <- CSS shared by the slides of the section (no slide)
parts/05-physical/02-governing.html
```
One file = one slide, with its own `<style>` (rules prefixed by the class of the slide, e.g. `.ctx ...`) and, if needed, its own `<script>`.
The files of a folder are read in name order, so `03-` before `04-`: renaming a file moves the slide. The first file of a folder starts with
`<!-- section: Name -->`. `config/main.json` lists the folders; a new file in a folder is picked up by the next build.
In the browser, **I** shows the file of the slide on screen (`data-src` in the inspector), and the address `main.html#12` opens slide 12 (F5 keeps it).

VS Code (settings in `.vscode/`): `Ctrl+P` + a few letters of the file name (`gov` -> `02-governing.html`) opens a slide;
`Ctrl+Shift+B` starts `build.py --watch` (rebuilds `main.html` at each save, then F5 in the browser);
`Ctrl+Shift+F` ignores the generated `main.html`; typing `slide` + Tab in a new file gives the skeleton of a slide;
the formatter is off for HTML (it would reflow the SVG); `Ctrl+K Z`/split editor: the slide on the left, the browser on the right.

## Writing parts
```html
<!-- section: Physical problem -->          new section: goes in the TOC and the top bar
<!-- subsection: Governing equation -->     optional, TOC only

<section class="slide" data-title="Governing equation">   one slide = one bubble
  ...content...
</section>
```
* A file may contain its own `<style>` and `<script>` (the `<script>` right after its `<section>`: `document.currentScript.previousElementSibling` is the slide).
* `data-layout="free"`: no content wrapper (position things yourself); `data-layout="title"`: title slide.
* Steps inside a slide (like beamer `\pause`): `<section class="slide" data-steps="2">`, then
  `<div data-from="1">` (shown from step 1) or `<div data-until="0">` (shown up to step 0).
  The slide gets `data-step="k"` for CSS and a `step` event for JS; the PDF has one page per step.
* Videos: a video cannot play inside a PDF, so it is a still frame there, at `data-pdf-t="10"` seconds (default 0).
* Drawings (`assets/**/*.svg`) use the deck's sans font, so their text looks the same everywhere.
* Drawings that change with the steps of a slide (slides 9, 10 and 12) are stacked: one complete drawing per step,
  each in its own file (`governing-*.svg`, `external-*.svg`, `internal-*.svg`), shown with `data-from` / `data-until`
  as on the radiation slide: `<svg data-until="0" data-include="assets/05-physical/governing-boundaries-faint.svg"></svg>`
  inside a `<div class="fig layers">`. No step effect depends on a class inside the file, so a PowerPoint export keeps them.
  Each file is one slide of `illustrations.pptx`. Keep the transparent frame of each file
  (the rectangle with no fill): it fixes the size of the drawing, so that the steps line up.
* Slide 5 (why optimise): the three before/after schemas are `assets/04-introduction/why-topology.svg`, `why-shape.svg`, `why-both.svg`
  (slides 24 to 26 of `illustrations.pptx`), shown one after the other with `data-from` on their `<figure>`.
* Slide 7 (state of the art) is a timeline: one lane per scale (material, wall, building), x = year, one dot per article
  (`parts/04-introduction/04-state-of-the-art.html`). Step 0 draws it (a year cursor, the dots appear at their date), steps 1 to 3 look at one
  scale (the other lanes fade, pictures and a comment appear below), step 4 shows the gap and the aim. To add or move an article, copy a
  `<div class="pp ...">`: `--yr` is its year, class `p` / `t` / `s` its type (parameters, topology, shape), `u` / `d` puts the label above or below.
  The dashed boxes are pictures still to add: save the figure in `assets/04-introduction/` (the name is written in the box) and replace
  the `<div class="slot">` of the box by an `<img>` like the one of Bruggi.
* Slide 4 (context) turns band 1 of the façade into a block of wall, cuts it along A and turns it to face us (CSS 3D, steps 2 and 3).
  It ends on the 2D section `assets/04-introduction/section.svg`, which is also the cut face of the block while it turns: the file is
  included twice, so the build gives the ids of the second copy a suffix. The façade of the block is `band1.jpg`, made by
  `config/make_band.py` from the frame of the video. The labels of step 2 are placed on the 3D pose of the block: if the pose changes
  in the CSS of the part, place them again.
* Citations: `\cite{key}` or `\cite{key1,key2}` with keys from `bib/refs.bib` -> numbers in order of first citation,
  a footer with the short references on the slide (disable with `data-footcite="off"` on the section),
  and a "References" appendix at the end with the full entries (click a number to jump to it).
* Drawings: `assets/illustrations.pptx` has one slide per drawing file (title = its path). In PowerPoint: right-click >
  Convert to Shape, edit, then right-click the group > Save as Picture > SVG over the same file, and rebuild.
* Figures go in the folder of their part, e.g. `assets/05-physical/`. Pictures that are not drawings (photos, screenshots)
  stay as PNG or JPG in that folder.
* To add a section: create the folder `parts/09-xxx/` with its slide files, put its figures in `assets/09-xxx/`, and add the folder to `config/main.json`.
To add a slide: create `parts/<section>/NN-name.html` (the snippet `slide`).

## Viewing
`← →` / space / click: navigate · `F`: fullscreen · `Home` / `End` · click a bubble to jump.
Buttons "Fullscreen" and "PDF" appear top right when the mouse moves. The PDF button prints one page per slide;
the complete PDF (one page per step) is made by `build_all.bat`.

## Equations (LaTeX)

In `parts/*.html`, write LaTeX as in a .tex file: inline `\( ... \)`, display `\[ ... \]`.
They are rendered at build time by KaTeX (`theme/katex/`) inside the Chrome or Edge already installed (no Node.js needed).
Shortcuts (`\x`, `\n` bold vectors, `\dd`) are defined in `math_render.py` (`MACROS`).
`\htmlData{from=1}{...}` shows part of an equation from step 1 on.
