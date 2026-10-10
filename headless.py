"""The headless browser of the build (KaTeX, math_render.py) and of the PDF export (export_pdf.py).

It is the Chrome or Edge already installed on the computer (else Playwright's Chromium).
Needs the Python package playwright:  pip install playwright
Set CHROME_PATH to use another Chrome or Chromium executable.
"""
import os, sys


def launch(p):
    """p: a running sync_playwright() instance. Returns a browser or exits with a message."""
    if os.environ.get("CHROME_PATH"):
        try:
            return p.chromium.launch(executable_path=os.environ["CHROME_PATH"])
        except Exception as e:
            sys.exit(f"CHROME_PATH is not usable: {os.environ['CHROME_PATH']}\n{str(e).splitlines()[0]}")
    error = ""
    for channel in ("chrome", "msedge", None):          # installed Chrome, then Edge, then Playwright's Chromium
        try:
            return p.chromium.launch(channel=channel)
        except Exception as e:
            error = str(e).splitlines()[0] if str(e) else error
    sys.exit("No Chrome, Edge or Chromium found: install Google Chrome (or Microsoft Edge), "
             "or run  python -m playwright install chromium\n" + error)
