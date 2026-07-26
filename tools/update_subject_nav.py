from __future__ import annotations

import re
from pathlib import Path


SITE = Path(__file__).resolve().parents[1]


def relative_prefix(page: Path) -> str:
    depth = len(page.parent.relative_to(SITE).parts)
    return "../" * depth


def update_page(page: Path) -> bool:
    text = page.read_text(encoding="utf-8")
    if "과목별학원" in text[text.find('<div class="nav-links">'):text.find("</nav>")]:
        return False

    prefix = relative_prefix(page)
    link = f'        <a href="{prefix}과목별학원/index.html">과목별학원</a>\n'
    pattern = r'(\s*<a(?: class="active")? href="[^"]*전국학원/index\.html">전국학원</a>)'
    updated, count = re.subn(pattern, "\n" + link + r"\1", text, count=1)
    if not count:
        pattern = r'(\s*<a(?: class="active")? href="[^"]*전국학원/">전국학원</a>)'
        updated, count = re.subn(pattern, "\n" + link + r"\1", text, count=1)
    if not count:
        raise RuntimeError(f"상단 메뉴를 찾지 못했습니다: {page}")
    page.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for page in SITE.glob("**/index.html"):
        if any(part in {".git", ".vercel", "node_modules"} for part in page.parts):
            continue
        changed += int(update_page(page))
    print(f"nav_updated={changed}")


if __name__ == "__main__":
    main()
