from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


SITE = Path(__file__).resolve().parents[1]
CATEGORIES = ("중1수학학원", "중1영어학원")
TAG_RE = re.compile(r"<[^>]+>")
DESC_RE = re.compile(r'<meta name="description" content="([^"]+)">')
H2_RE = re.compile(r"<h2(?:\s[^>]*)?>(.*?)</h2>", re.S)
FAQ_RE = re.compile(r'<details class="faq-item">', re.S)
REVIEW_RE = re.compile(r'<article class="review-card">', re.S)
RELATED_RE = re.compile(r'class="subject-related-link"')
COPY_RE = re.compile(r'<section class="section subject-manuscript">(.*?)</section>\s*<section class="section subject-center-card">', re.S)
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def plain(value: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", value)).strip()


def main() -> None:
    for category in CATEGORIES:
        files = sorted((SITE / "과목별학원" / category).glob("*/index.html"))
        desc_lengths: list[int] = []
        copy_lengths: list[int] = []
        h2_counts: list[int] = []
        faq_counts: list[int] = []
        review_counts: list[int] = []
        related_counts: list[int] = []
        school_counts: list[int] = []
        schema_types: Counter[str] = Counter()
        for page in files:
            text = page.read_text(encoding="utf-8")
            desc_lengths.append(len(DESC_RE.search(text).group(1)))
            match = COPY_RE.search(text)
            copy_lengths.append(len(plain(match.group(1))) if match else 0)
            h2_counts.append(len(H2_RE.findall(match.group(1))) if match else 0)
            faq_counts.append(len(FAQ_RE.findall(text)))
            review_counts.append(len(REVIEW_RE.findall(text)))
            related_counts.append(len(RELATED_RE.findall(text)))
            ld = json.loads(LD_RE.search(text).group(1))
            for item in ld.get("@graph", []):
                types = item.get("@type", [])
                types = [types] if isinstance(types, str) else types
                schema_types.update(types)
                if str(item.get("@id", "")).endswith("#schools"):
                    school_counts.append(int(item.get("numberOfItems", 0)))
        def avg(values: list[int]) -> float:
            return round(sum(values) / len(values), 1) if values else 0
        print(f"[{category}] pages={len(files)}")
        print(f" description_len=min{min(desc_lengths)} avg{avg(desc_lengths)} max{max(desc_lengths)}")
        print(f" manuscript_text_len=min{min(copy_lengths)} avg{avg(copy_lengths)} max{max(copy_lengths)}")
        print(f" h2=avg{avg(h2_counts)} faq=avg{avg(faq_counts)} reviews=avg{avg(review_counts)} related=avg{avg(related_counts)}")
        print(f" schools=with_data{sum(1 for x in school_counts if x > 0)}/{len(school_counts)} avg{avg(school_counts)}")
        required = ["EducationalOrganization", "LocalBusiness", "Article", "Service", "FAQPage", "BreadcrumbList", "ItemList"]
        print(" schema=" + ",".join(f"{name}:{schema_types[name]}" for name in required))


if __name__ == "__main__":
    main()
