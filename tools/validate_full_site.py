from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


SITE = Path(__file__).resolve().parents[1]
H1_RE = re.compile(r"<h1(?:\s[^>]*)?>", re.I)
CANON_RE = re.compile(r'<link rel="canonical" href="([^"]+)">')
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
IMG_RE = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"', re.I)
HREF_RE = re.compile(r'href="([^"]+)"')


def main() -> None:
    files = [
        p for p in SITE.glob("**/index.html")
        if not any(part in {".git", ".vercel", "node_modules"} for part in p.parts)
    ]
    errors: list[str] = []
    canonicals: list[str] = []
    nav_count = 0
    for page in files:
        text = page.read_text(encoding="utf-8")
        tag = page.relative_to(SITE).as_posix()
        h1_count = len(H1_RE.findall(text))
        if h1_count != 1:
            errors.append(f"{tag}: h1={h1_count}")
        canon = CANON_RE.search(text)
        if not canon:
            errors.append(f"{tag}: canonical_missing")
        else:
            canonicals.append(canon.group(1))
        if "과목별학원" in text[text.find('<div class="nav-links">'):text.find("</nav>")]:
            nav_count += 1
        else:
            errors.append(f"{tag}: subject_nav_missing")
        for block in LD_RE.findall(text):
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"{tag}: json={exc}")
        for src in IMG_RE.findall(text):
            if src.startswith(("http://", "https://", "data:")):
                continue
            target = SITE / src.lstrip("/") if src.startswith("/") else page.parent / src
            if not target.resolve().exists():
                errors.append(f"{tag}: image_missing={src}")
        for href in HREF_RE.findall(text):
            if href.startswith(("http://", "https://", "tel:", "sms:", "mailto:", "#", "javascript:")):
                continue
            target = SITE / href.lstrip("/") if href.startswith("/") else page.parent / href
            if href.endswith("/"):
                target = target / "index.html"
            if not target.resolve().exists():
                errors.append(f"{tag}: link_missing={href}")
    duplicates = [url for url, count in Counter(canonicals).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate_canonical={len(duplicates)}")
    print(f"site_pages={len(files)} subject_nav={nav_count}/{len(files)} unique_canonical={len(set(canonicals))}/{len(canonicals)} errors={len(errors)}")
    for error in errors[:50]:
        print("ERROR", error)
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
