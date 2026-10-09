# Seminar presentation (HTML)

```
main.json            title, author, ordered list of parts   (≈ main.tex)
parts/*.html         one file per section / group of slides (≈ parts/*.tex)
theme/style.css      look & feel                            (≈ presentation.sty)
theme/engine.js      nav bubbles, TOC, footer, fullscreen, PDF mode
theme/field.js       animated contour-line background
assets/              images
build.py             assembles index.html from the above
export_pdf.py        index.html -> PDF
```

## Workflow
```
python build.py --watch      # rebuilds index.html on every save; just refresh the browser
python export_pdf.py         # -> seminar.pdf (needs Chrome or Edge)
```
Open `index.html` directly (double-click), no server needed.

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
  The slide gets `data-step="k"` for CSS and a `step` event for JS; the PDF shows the last step.
* To add a part: create `parts/09-xxx.html` and add it to `main.json`.

## Viewing
`← →` / space / click: navigate · `F`: fullscreen · `Home` / `End` · click a bubble to jump.
Buttons "Fullscreen" and "PDF" appear top right when the mouse moves.
