from __future__ import annotations

import json
import re
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]

IMG_RE = re.compile(r'src="([^"]+)"')
CANON_RE = re.compile(r'<link rel="canonical" href="([^"]+)">')
OGURL_RE = re.compile(r'<meta property="og:url" content="([^"]+)">')
H1_RE = re.compile(r"<h1[ >]")
HREF_RE = re.compile(r'href="([^"]+)"')
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

files = sorted(SITE.glob("**/index.html"))
lines = []


def log(msg):
    lines.append(msg)


expected = {
    SITE / "index.html": "/",
    SITE / "학습가이드" / "index.html": "/학습가이드/",
    SITE / "상담문의" / "index.html": "/상담문의/",
}

for f in files:
    if ".git" in f.parts:
        continue
    text = f.read_text(encoding="utf-8")
    tag = f.relative_to(SITE).as_posix()

    h1c = len(H1_RE.findall(text))
    m = CANON_RE.search(text)
    canon = m.group(1) if m else None
    m = OGURL_RE.search(text)
    og = m.group(1) if m else None
    exp = expected.get(f)

    json_errs = []
    for block in LD_RE.findall(text):
        try:
            json.loads(block)
        except Exception as e:
            json_errs.append(str(e))

    img_bad = []
    for src in IMG_RE.findall(text):
        if src.startswith("http"):
            continue
        resolved = (f.parent / src).resolve()
        if not resolved.exists():
            img_bad.append(src)

    link_bad = []
    for href in HREF_RE.findall(text):
        if href.startswith(("http", "tel:", "sms:", "#")):
            continue
        if href.startswith("/"):
            resolved = (SITE / href.lstrip("/")).resolve()
            if href.endswith("/"):
                resolved = resolved / "index.html"
        else:
            resolved = (f.parent / href).resolve()
            if href.endswith("/"):
                resolved = resolved / "index.html"
        if not resolved.exists():
            link_bad.append(href)

    log(f"{tag}: H1={h1c} canonical={canon}(expect {exp}) og={og} json_err={len(json_errs)} img_bad={img_bad} link_bad={link_bad}")

Path(r"C:\Users\얼짱김종범\AppData\Local\Temp\validate_site12.txt").write_text("\n".join(lines), encoding="utf-8")
print("done")
