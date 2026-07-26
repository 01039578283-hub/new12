from __future__ import annotations

import json
import re
from pathlib import Path


SITE = Path(__file__).resolve().parents[1]
BASE_URL = "https://xn--ru4bz7e9zf0zk.com"


def main() -> None:
    page = SITE / "index.html"
    text = page.read_text(encoding="utf-8")
    pattern = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
    match = pattern.search(text)
    if not match:
        raise RuntimeError("메인 JSON-LD를 찾지 못했습니다")
    data = json.loads(match.group(2))
    graph = data.get("@graph", [])
    item_list = next((item for item in graph if item.get("@id", "").endswith("#main-links")), None)
    if item_list is None:
        raise RuntimeError("메인 링크 ItemList를 찾지 못했습니다")
    entries = item_list.setdefault("itemListElement", [])
    entries = [entry for entry in entries if entry.get("name") != "과목별학원"]
    national_index = next((i for i, entry in enumerate(entries) if entry.get("name") == "전국학원"), len(entries))
    entries.insert(national_index, {
        "@type": "ListItem",
        "position": national_index + 1,
        "name": "과목별학원",
        "url": f"{BASE_URL}/과목별학원/",
    })
    for index, entry in enumerate(entries, 1):
        entry["position"] = index
    item_list["itemListElement"] = entries
    replacement = match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)
    page.write_text(text[:match.start()] + replacement + text[match.end():], encoding="utf-8")
    print("root_schema_updated=1")


if __name__ == "__main__":
    main()
