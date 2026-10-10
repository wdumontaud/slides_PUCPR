"""The headless browser of the build (KaTeX, math_render.py) and of the PDF export (export_pdf.py).

It is the Chrome or Edge already installed on the computer (else Playwright's Chromium).
Needs the Python package playwright:  pip install playwright
Set CHROME_PATH to use another Chrome or Chromium executable.
"""
import os


def launch(p):
    """p: a running sync_playwright() instance. Raises RuntimeError, with the browser's own message, if none starts."""
    if os.environ.get("CHROME_PATH"):
        path = os.environ["CHROME_PATH"]
        try:
            return p.chromium.launch(executable_path=path)
        except Exception as e:
            raise RuntimeError(f"CHROME_PATH={path} does not start a browser:\n{e}") from None
    errors = []
    for channel in ("chrome", "msedge", None):          # installed Chrome, then Edge, then Playwright's Chromium
        try:
            return p.chromium.launch(channel=channel)
        except Exception as e:
            errors.append(f"[{channel or 'Playwright Chromium'}] {e}")
    raise RuntimeError(
        "No browser could start (tried Google Chrome, Microsoft Edge, Playwright's Chromium).\n"
        "If Chrome or Edge is installed, its own start-up error is below. Otherwise install Google Chrome, "
        "or run  python -m playwright install chromium\n\n" + "\n\n".join(errors))
