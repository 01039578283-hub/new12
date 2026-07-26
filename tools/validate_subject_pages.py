from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from itertools import combinations
from pathlib import Path
from urllib.parse import quote


SITE = Path(__file__).resolve().parents[1]
BASE_URL = "https://xn--ru4bz7e9zf0zk.com"
DEFAULT_CATEGORY = "중1수학학원"

CANON_RE = re.compile(r'<link rel="canonical" href="([^"]+)">')
OG_RE = re.compile(r'<meta property="og:url" content="([^"]+)">')
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
DESC_RE = re.compile(r'<meta name="description" content="([^"]+)">')
H1_RE = re.compile(r"<h1(?:\s[^>]*)?>", re.I)
IMG_RE = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"[^>]*>', re.I)
HREF_RE = re.compile(r'href="([^"]+)"')
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
FAQ_RE = re.compile(r'<details class="faq-item"><summary>(.*?)</summary><p>(.*?)</p></details>', re.S)
REVIEW_RE = re.compile(r'<article class="review-card">.*?<p>(.*?)</p></article>', re.S)
COPY_RE = re.compile(r'<article class="subject-copy-card">(.*?)</article>', re.S)
TAG_RE = re.compile(r"<[^>]+>")


def plain(value: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", value)).strip()


def resolve_link(page: Path, value: str) -> Path | None:
    if value.startswith(("http://", "https://", "tel:", "sms:", "mailto:", "#")):
        return None
    if value.startswith("/"):
        target = SITE / value.lstrip("/")
    else:
        target = page.parent / value
    if value.endswith("/"):
        target = target / "index.html"
    return target.resolve()


def shingles(value: str, size: int = 7) -> set[str]:
    chars = re.sub(r"\s+", "", value)
    return {chars[i:i + size] for i in range(max(0, len(chars) - size + 1))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", default=DEFAULT_CATEGORY)
    args = parser.parse_args()
    category = args.category
    root = SITE / "과목별학원" / category
    files = sorted(root.glob("*/index.html"))
    errors: list[str] = []
    warnings: list[str] = []
    titles: list[str] = []
    descriptions: list[str] = []
    bodies: list[tuple[str, set[str]]] = []
    faq_sets: list[str] = []
    review_sets: list[str] = []
    required_types = {"WebPage", "ImageObject", "BreadcrumbList", "EducationalOrganization", "LocalBusiness", "Article", "Service", "FAQPage", "ItemList"}

    if len(files) != 371:
        errors.append(f"local_count={len(files)} expected=371")
    for page in files:
        text = page.read_text(encoding="utf-8")
        slug = page.parent.name
        expected = f"{BASE_URL}/과목별학원/{category}/{slug}/"
        title_m = TITLE_RE.search(text)
        desc_m = DESC_RE.search(text)
        canon_m = CANON_RE.search(text)
        og_m = OG_RE.search(text)
        title = plain(title_m.group(1)) if title_m else ""
        desc = plain(desc_m.group(1)) if desc_m else ""
        titles.append(title)
        descriptions.append(desc)
        if len(H1_RE.findall(text)) != 1:
            errors.append(f"{slug}: h1={len(H1_RE.findall(text))}")
        if not canon_m or canon_m.group(1) != expected:
            errors.append(f"{slug}: canonical={canon_m.group(1) if canon_m else None}")
        if not og_m or og_m.group(1) != expected:
            errors.append(f"{slug}: og:url={og_m.group(1) if og_m else None}")
        if not 65 <= len(desc) <= 115:
            warnings.append(f"{slug}: description_length={len(desc)}")
        if "과목별학원" not in text[text.find('<div class="nav-links">'):text.find("</nav>")]:
            errors.append(f"{slug}: subject_nav_missing")
        if not re.search(r'<section class="section subject-media-section".*?<img class="subject-hidden-representative"', text, re.S):
            errors.append(f"{slug}: hidden_representative_order")

        ld_blocks = LD_RE.findall(text)
        if len(ld_blocks) != 1:
            errors.append(f"{slug}: ld_blocks={len(ld_blocks)}")
            continue
        try:
            ld = json.loads(ld_blocks[0])
        except json.JSONDecodeError as exc:
            errors.append(f"{slug}: json={exc}")
            continue
        found_types: set[str] = set()
        for item in ld.get("@graph", []):
            item_type = item.get("@type", [])
            if isinstance(item_type, str):
                found_types.add(item_type)
            else:
                found_types.update(item_type)
        missing = required_types - found_types
        if missing:
            errors.append(f"{slug}: schema_missing={sorted(missing)}")

        for src in IMG_RE.findall(text):
            if src.startswith("http"):
                continue
            target = SITE / src.lstrip("/") if src.startswith("/") else page.parent / src
            if not target.exists():
                errors.append(f"{slug}: image_missing={src}")
        for href in HREF_RE.findall(text):
            target = resolve_link(page, href)
            if target is not None and not target.exists():
                errors.append(f"{slug}: link_missing={href}")

        copy = " ".join(plain(x) for x in COPY_RE.findall(text))
        bodies.append((slug, shingles(copy)))
        faq_sets.append("|".join(plain(q + a) for q, a in FAQ_RE.findall(text)))
        review_sets.append("|".join(plain(x) for x in REVIEW_RE.findall(text)))

    duplicate_titles = [value for value, count in Counter(titles).items() if count > 1]
    duplicate_desc = [value for value, count in Counter(descriptions).items() if count > 1]
    duplicate_faq = sum(count - 1 for count in Counter(faq_sets).values() if count > 1)
    duplicate_review = sum(count - 1 for count in Counter(review_sets).values() if count > 1)
    if duplicate_titles:
        errors.append(f"duplicate_titles={len(duplicate_titles)}")
    if duplicate_desc:
        warnings.append(f"duplicate_descriptions={len(duplicate_desc)}")
    if duplicate_faq:
        warnings.append(f"duplicate_faq_pages={duplicate_faq}")
    if duplicate_review:
        warnings.append(f"duplicate_review_pages={duplicate_review}")

    high_similarity: list[tuple[str, str, float]] = []
    for (slug_a, a), (slug_b, b) in combinations(bodies, 2):
        if not a or not b:
            continue
        score = len(a & b) / len(a | b)
        if score >= 0.88:
            high_similarity.append((slug_a, slug_b, score))
    high_similarity.sort(key=lambda item: item[2], reverse=True)
    if high_similarity:
        warnings.append(f"body_similarity_ge_0.88={len(high_similarity)} max={high_similarity[0]}")

    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    sitemap_missing = [
        slug for slug, _ in bodies
        if quote(f"/과목별학원/{category}/{slug}/", safe="/") not in sitemap
    ]
    if sitemap_missing:
        errors.append(f"sitemap_missing={len(sitemap_missing)}")

    print(f"pages={len(files)}")
    print(f"unique_titles={len(set(titles))}/{len(titles)}")
    print(f"unique_descriptions={len(set(descriptions))}/{len(descriptions)}")
    print(f"unique_faq_sets={len(set(faq_sets))}/{len(faq_sets)}")
    print(f"unique_review_sets={len(set(review_sets))}/{len(review_sets)}")
    print(f"high_similarity_ge_0.88={len(high_similarity)}")
    print(f"errors={len(errors)} warnings={len(warnings)}")
    for item in errors[:30]:
        print("ERROR", item)
    for item in warnings[:30]:
        print("WARN", item)
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
