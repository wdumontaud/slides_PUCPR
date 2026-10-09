#!/usr/bin/env python3
"""Export the presentation to PDF (one 16:9 page per slide) with headless Chrome / Edge.

    python export_pdf.py                 -> seminar.pdf
    python export_pdf.py my_talk.pdf

Needs Chrome, Chromium or Edge installed, and an internet connection (for the Computer Modern font).
The animated contour backgrounds are exported as a still frame.
"""
import os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]


def find_browser():
    for c in CANDIDATES:
        p = c if os.path.isabs(c) and os.path.exists(c) else shutil.which(c)
        if p:
            return p
    sys.exit("No Chrome / Edge found: open index.html, press the 'PDF' button and choose 'Save as PDF'.")


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "seminar.pdf").resolve()
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
    url = (ROOT / "index.html").as_uri() + "?print=1"
    with tempfile.TemporaryDirectory() as profile:
        cmd = [find_browser(), "--headless=new", "--disable-gpu-sandbox", "--use-angle=swiftshader",
               "--enable-unsafe-swiftshader", "--hide-scrollbars", f"--user-data-dir={profile}",
               "--no-pdf-header-footer", "--virtual-time-budget=15000",
               f"--print-to-pdf={out}", url]
        subprocess.run(cmd, check=True, timeout=120)
    print("written:", out, f"({out.stat().st_size // 1024} kB)")


if __name__ == "__main__":
    main()
