from __future__ import annotations

"""Strict release audit for the fourteen remaining subject-academy categories.

The audit deliberately uses only the Python standard library.  It validates the
generated release, its raw XLSX inputs, local assets and sitemap as one contract.
The four categories which pre-date this release are outside the content audit;
they can be frozen independently with ``--write-existing-hash-gate`` and checked
later with ``--existing-hash-gate``.
"""

import argparse
import csv
import hashlib
import html
import json
import math
import re
import sys
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET


SITE = Path(__file__).resolve().parents[1]
BASE_URL = "https://xn--ru4bz7e9zf0zk.com"
SUBJECT_ROOT = "과목별학원"
EXPECTED_DETAILS_PER_CATEGORY = 371
EXPECTED_NEW_URLS = 5_208
EXPECTED_SITEMAP_URLS = 7_817
SOURCE_SENTENCE_MIN = 42
JACCARD_LIMIT = 0.75


@dataclass(frozen=True)
class Category:
    slug: str
    source: str
    grade: str
    grade_code: str
    subject: str
    school_level: str

    @property
    def label(self) -> str:
        return re.sub(r"^([초중고]\d)(수학|영어)학원$", r"\1 \2학원", self.slug)


CATEGORIES = (
    Category("초3수학학원", "초3 수학학원 원고.xlsx", "초등학교 3학년", "초3", "수학", "초"),
    Category("초3영어학원", "초3 영어학원.xlsx", "초등학교 3학년", "초3", "영어", "초"),
    Category("초4수학학원", "초4 수학학원 원고.xlsx", "초등학교 4학년", "초4", "수학", "초"),
    Category("초4영어학원", "초4 영어학원 원고.xlsx", "초등학교 4학년", "초4", "영어", "초"),
    Category("초5수학학원", "초5 수학학원 원고.xlsx", "초등학교 5학년", "초5", "수학", "초"),
    Category("초5영어학원", "초5 영어학원 원고.xlsx", "초등학교 5학년", "초5", "영어", "초"),
    Category("중2수학학원", "중2 수학학원 원고.xlsx", "중학교 2학년", "중2", "수학", "중"),
    Category("중2영어학원", "중2 영어학원 원고.xlsx", "중학교 2학년", "중2", "영어", "중"),
    Category("중3수학학원", "중3 수학학원 원고.xlsx", "중학교 3학년", "중3", "수학", "중"),
    Category("중3영어학원", "중3 영어학원 원고.xlsx", "중학교 3학년", "중3", "영어", "중"),
    Category("고1수학학원", "고1 수학학원 원고.xlsx", "고등학교 1학년", "고1", "수학", "고"),
    Category("고1영어학원", "고1 영어학원 원고.xlsx", "고등학교 1학년", "고1", "영어", "고"),
    Category("고2수학학원", "고2 수학학원 원고.xlsx", "고등학교 2학년", "고2", "수학", "고"),
    Category("고2영어학원", "고2 영어학원 원고.xlsx", "고등학교 2학년", "고2", "영어", "고"),
)
EXISTING_CATEGORIES = ("중1수학학원", "중1영어학원", "초6수학학원", "초6영어학원")
ALL_CATEGORY_CARDS = (
    ("초3수학학원", "초3 수학학원"),
    ("초3영어학원", "초3 영어학원"),
    ("초4수학학원", "초4 수학학원"),
    ("초4영어학원", "초4 영어학원"),
    ("초5수학학원", "초5 수학학원"),
    ("초5영어학원", "초5 영어학원"),
    ("초6수학학원", "초6 수학학원"),
    ("초6영어학원", "초6 영어학원"),
    ("중1수학학원", "중1 수학학원"),
    ("중1영어학원", "중1 영어학원"),
    ("중2수학학원", "중2 수학학원"),
    ("중2영어학원", "중2 영어학원"),
    ("중3수학학원", "중3 수학학원"),
    ("중3영어학원", "중3 영어학원"),
    ("고1수학학원", "고1 수학학원"),
    ("고1영어학원", "고1 영어학원"),
    ("고2수학학원", "고2 수학학원"),
    ("고2영어학원", "고2 영어학원"),
)
KNOWN_JOINED_SCHOOLS = {"오현초호매실중": ("오현초", "호매실중")}
REQUIRED_TYPES = {
    "EducationalOrganization", "LocalBusiness", "Article", "Service",
    "FAQPage", "BreadcrumbList", "ItemList",
}
REQUIRED_RELATIONS = {"about", "mentions", "hasPart", "articleSection", "makesOffer"}

JSON_LD_RE = re.compile(
    r"<script\b[^>]*\btype\s*=\s*(['\"])application/ld\+json\1[^>]*>(.*?)</script>",
    re.I | re.S,
)
SENTENCE_RE = re.compile(r"[^.!?。！？\n]+(?:[.!?。！？]+|$)")
WORD_RE = re.compile(r"[가-힣A-Za-z0-9]+")
BAD_VISIBLE = (
    ("와와", re.compile(r"와와")),
    ("placeholder", re.compile(r"\{\{.*?\}\}|\}\}|\[\s*(?:지역|동네|제목|과목|학년)\s*\]|\b(?:TODO|TBD|Lorem ipsum)\b|OO(?:학생|학부모|학원)", re.I)),
    ("spreadsheet_error", re.compile(r"#(?:ERROR!?|REF!?|VALUE!?|N/A|NAME\?)", re.I)),
    ("exaggeration", re.compile(r"(?:성적|등급|점수).{0,12}(?:100\s*%|무조건|반드시|보장)|(?:무조건|반드시).{0,12}(?:상승|향상|합격)|전국\s*1위|최고의\s*학원", re.I)),
)
COPY_REGRESSIONS = (
    ("duplicated signal noun", re.compile(r"시험 점검 점검|풀이 기록 기록")),
    ("double topic marker", re.compile(r"(?:학습 계획은|학습에서는)\s*(?:과제는|주간 점검에서는|오답에는)")),
    ("duplicated consultation timing", re.compile(r"상담을 마친 뒤에는\s*(?:첫 상담에서|상담 뒤에는)")),
    ("dynamic blocked-position misjoin", re.compile(r"의\s*막힌 위치")),
    (
        "dynamic remediation-order misjoin",
        re.compile(r"시험을 준비하며 확인할 사항의 보완 순서|풀이 과정에 남은 학습 흔적의 보완 순서"),
    ),
    ("dynamic change-subject misjoin", re.compile(r"시험을 준비하며 확인할 사항의 변화가")),
    (
        "duplicated process/reference join",
        re.compile(r"이 과정에서\s*[^.!?]{0,120}?과정을 기준으로|확인할 사항[^.!?]{0,120}?함께 확인하면"),
    ),
    (
        "duplicated recheck action",
        re.compile(r"다시 해결하는 과정을 다시 확인|확인할 사항을 다시 확인"),
    ),
)


def compact_space(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def comparable(value: str) -> str:
    return re.sub(r"[^가-힣A-Za-z0-9]", "", compact_space(value)).lower()


def words(value: str) -> list[str]:
    return [item.lower() for item in WORD_RE.findall(compact_space(value))]


def sentences(value: str, minimum: int = SOURCE_SENTENCE_MIN) -> list[str]:
    result: list[str] = []
    for match in SENTENCE_RE.finditer(compact_space(value)):
        item = compact_space(match.group(0))
        key = comparable(item)
        if len(key) >= minimum:
            result.append(key)
    return result


def word_shingles(value: str, size: int) -> set[tuple[str, ...]]:
    tokens = words(value)
    return {tuple(tokens[index:index + size]) for index in range(len(tokens) - size + 1)}


def hashed_word_shingles(value: str, size: int) -> set[int]:
    """Compact in-process representation used only by the large Jaccard matrix."""
    tokens = words(value)
    return {hash(tuple(tokens[index:index + size])) for index in range(len(tokens) - size + 1)}


@dataclass
class Element:
    tag: str
    attrs: dict[str, str]
    text: str
    start: int
    end: int
    in_main: bool

    @property
    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())


class DocumentParser(HTMLParser):
    """Small DOM-like projection, tolerant of class and wrapper variations."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.fragments: list[str] = []
        self.stack: list[tuple[str, dict[str, str], int, bool]] = []
        self.elements: list[Element] = []
        self.images: list[dict[str, str]] = []
        self.inputs: list[dict[str, str]] = []
        self.scripts: list[dict[str, str]] = []
        self.anchors: list[dict[str, str]] = []
        self.metas: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.main_depth = 0
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        values = {str(key).lower(): (value or "") for key, value in attrs}
        in_main = self.main_depth > 0 or tag == "main"
        if tag == "main":
            self.main_depth += 1
        if tag in {"script", "style", "template", "noscript"}:
            self.skip_depth += 1
        if tag == "img":
            self.images.append(values)
        elif tag == "input":
            self.inputs.append(values)
        elif tag == "script":
            self.scripts.append(values)
        elif tag == "a":
            self.anchors.append(values)
        elif tag == "meta":
            self.metas.append(values)
        elif tag == "link":
            self.links.append(values)
        if tag not in self.VOID:
            self.stack.append((tag, values, len(self.fragments), in_main))

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] != tag:
                continue
            opened_tag, attrs, start, in_main = self.stack.pop(index)
            self.elements.append(Element(opened_tag, attrs, compact_space(" ".join(self.fragments[start:])), start, len(self.fragments), in_main))
            break
        if tag == "main" and self.main_depth:
            self.main_depth -= 1
        if tag in {"script", "style", "template", "noscript"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth and data.strip():
            self.fragments.append(data.strip())

    def by_tag(self, tag: str, main_only: bool = False) -> list[Element]:
        return [element for element in self.elements if element.tag == tag and (element.in_main or not main_only)]

    @property
    def main_text(self) -> str:
        mains = self.by_tag("main")
        return compact_space(mains[-1].text if mains else " ".join(self.fragments))


@dataclass
class PageRecord:
    path: Path
    rel: str
    category: str
    locality: str
    canonical: str
    title: str
    description: str
    h1: str
    main_text: str
    paragraphs: list[str] = field(default_factory=list)
    sections: list[str] = field(default_factory=list)
    masked_shingles: set[int] = field(default_factory=set)
    representative: str = ""


class Audit:
    def __init__(self, max_errors: int) -> None:
        self.max_errors = max_errors
        self.errors: list[str] = []
        self.checks = 0
        self.stats: Counter[str] = Counter()

    def require(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            self.errors.append(message)

    def equal(self, actual, expected, message: str) -> None:
        self.require(actual == expected, f"{message}: expected={expected!r} actual={actual!r}")


def one(values: list[str], audit: Audit, rel: str, label: str) -> str:
    audit.equal(len(values), 1, f"{rel}: {label} count")
    return compact_space(values[0]) if len(values) == 1 else ""


def meta_values(parser: DocumentParser, key: str, value: str) -> list[str]:
    return [item.get("content", "") for item in parser.metas if item.get(key, "").lower() == value.lower()]


def schema_types(graph: list[dict]) -> set[str]:
    result: set[str] = set()
    for node in graph:
        node_types = node.get("@type", [])
        result.update([node_types] if isinstance(node_types, str) else node_types)
    return result


def has_type(node: dict, wanted: str) -> bool:
    node_types = node.get("@type", [])
    return wanted in ([node_types] if isinstance(node_types, str) else node_types)


def read_xlsx(path: Path) -> list[list[str]]:
    """Read displayed strings from the first worksheet without an Excel dependency."""
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = [compact_space("".join(item.itertext())) for item in root]
        sheet_names = sorted(
            name for name in archive.namelist()
            if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name)
        )
        if not sheet_names:
            raise ValueError("no worksheet")
        root = ET.fromstring(archive.read(sheet_names[0]))
        rows_by_number: dict[int, list[str]] = {}
        sequential_row = 0
        for row in root.iter():
            if not row.tag.endswith("}row"):
                continue
            sequential_row += 1
            try:
                row_number = int(row.attrib.get("r", sequential_row))
            except ValueError:
                row_number = sequential_row
            values: list[str] = []
            for cell in list(row):
                if not cell.tag.endswith("}c"):
                    continue
                reference = cell.attrib.get("r", "A")
                column = re.match(r"[A-Za-z]+", reference)
                if column and column.group(0).upper() != "A":
                    continue
                cell_type = cell.attrib.get("t", "")
                formula = next((child.text or "" for child in cell if child.tag.endswith("}f")), "")
                raw = "".join(child.text or "" for child in cell.iter() if child.tag.endswith(("}v", "}t")))
                if cell_type == "s" and raw.isdigit():
                    index = int(raw)
                    raw = shared[index] if index < len(shared) else ""
                if formula:
                    # openpyxl(data_only=False), used by the generator, exposes
                    # formula cells with the leading '='.  Mirror that behavior
                    # so the seven neutral-fallback rows are counted identically.
                    raw = "=" + formula
                values.append(compact_space(raw))
            rows_by_number[row_number] = values
        if not rows_by_number:
            return []
        # Preserve intentionally blank source rows: the generator reads A1:A371
        # positionally and treats blanks as neutral fallbacks.
        return [rows_by_number.get(index, []) for index in range(1, max(rows_by_number) + 1)]


def load_sources(
    source_dir: Path, audit: Audit,
) -> tuple[set[str], set[tuple[str, ...]], dict[str, set[int]]]:
    source_sentences: set[str] = set()
    source_shingles: set[tuple[str, ...]] = set()
    fallback_rows: dict[str, set[int]] = defaultdict(set)
    for category in CATEGORIES:
        path = source_dir / category.source
        audit.require(path.is_file(), f"source missing: {path}")
        if not path.is_file():
            continue
        try:
            rows = read_xlsx(path)
        except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
            audit.require(False, f"source unreadable: {path.name}: {exc}")
            continue
        data_rows = rows
        audit.equal(len(data_rows), EXPECTED_DETAILS_PER_CATEGORY, f"{path.name}: source rows")
        # Keep workbook rows as hard document boundaries.  Joining all 371
        # manuscripts would manufacture sentences/shingles across two unrelated
        # source pages and make the reuse test report false positives.
        for row_index, row in enumerate(data_rows):
            chunk = " ".join(row)
            if not chunk.strip() or chunk.lstrip().startswith(("#ERROR", "#REF!", "#VALUE!", "=")):
                fallback_rows[category.slug].add(row_index)
            source_sentences.update(sentences(chunk))
            source_shingles.update(word_shingles(chunk, 12))
    audit.stats["source_sentences"] = len(source_sentences)
    audit.stats["source_12_shingles"] = len(source_shingles)
    fallback_count = sum(len(rows) for rows in fallback_rows.values())
    audit.equal(fallback_count, 7, "source neutral-fallback rows")
    audit.stats["source_fallbacks"] = fallback_count
    return source_sentences, source_shingles, fallback_rows


def normalized_headers(row: dict[str, str]) -> dict[str, str]:
    return {re.sub(r"\s+", "", key or ""): compact_space(value or "") for key, value in row.items()}


def load_center_rows(common_dir: Path, audit: Audit) -> dict[str, dict[str, str]]:
    candidates = sorted(common_dir.glob("*정리.csv"))
    path = next((item for item in candidates if "센터정보" in item.name), None)
    audit.require(path is not None, f"center CSV missing under {common_dir}")
    result: dict[str, dict[str, str]] = {}
    if path is None:
        return result
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for raw in csv.DictReader(handle):
            row = normalized_headers(raw)
            locality = row.get("근처수업가능동네", "")
            if locality:
                result[re.sub(r"\s+", "", locality)] = row
    audit.equal(len(result), EXPECTED_DETAILS_PER_CATEGORY, "center CSV locality rows")
    return result


def split_csv_values(value: str) -> list[str]:
    """Mirror the generator's school/grade normalization contract.

    Some CSV rows use spaces instead of commas.  A multi-word proper name such
    as ``서울 중앙고`` remains one value unless every whitespace token is a
    complete school/grade name.  The one verified run-together source typo is
    expanded explicitly instead of guessed with a general suffix split.
    """
    if "지역내 모든 고등학교 가능" in (value or ""):
        return []
    result: list[str] = []
    school_or_grade = re.compile(
        r"^(?:[가-힣A-Za-z0-9]+(?:초등학교|중학교|고등학교|여중|여고|초|중|고)|[초중고]\d)$"
    )
    for part in re.split(r"[,/·|\n]+", value or ""):
        part = part.strip()
        if not part:
            continue
        if part in KNOWN_JOINED_SCHOOLS:
            result.extend(KNOWN_JOINED_SCHOOLS[part])
            continue
        tokens = part.split()
        if len(tokens) > 1 and all(school_or_grade.fullmatch(token) for token in tokens):
            for token in tokens:
                result.extend(KNOWN_JOINED_SCHOOLS.get(token, (token,)))
        else:
            result.append(part)
    return list(dict.fromkeys(result))


def local_asset(page: Path, value: str) -> Path | None:
    parsed = urlsplit(html.unescape(value))
    if parsed.scheme or parsed.netloc or value.startswith(("#", "tel:", "sms:", "mailto:", "javascript:", "data:")):
        return None
    raw_path = unquote(parsed.path)
    if not raw_path:
        return None
    target = SITE / raw_path.lstrip("/") if raw_path.startswith("/") else page.parent / raw_path
    if raw_path.endswith("/"):
        target /= "index.html"
    return target.resolve()


def nodes_from_ld(text: str, audit: Audit, rel: str) -> list[dict]:
    blocks = JSON_LD_RE.findall(text)
    audit.equal(len(blocks), 1, f"{rel}: JSON-LD blocks")
    if len(blocks) != 1:
        return []
    try:
        payload = json.loads(html.unescape(blocks[0][1]))
    except json.JSONDecodeError as exc:
        audit.require(False, f"{rel}: JSON-LD parse: {exc}")
        return []
    graph = payload.get("@graph", []) if isinstance(payload, dict) else []
    if not graph and isinstance(payload, dict):
        graph = [payload]
    audit.require(all(isinstance(node, dict) for node in graph), f"{rel}: JSON-LD graph nodes must be objects")
    return [node for node in graph if isinstance(node, dict)]


def relation_present(nodes: list[dict], relation: str) -> bool:
    for node in nodes:
        value = node.get(relation)
        if value not in (None, "", [], {}):
            return True
    return False


def script_contract_text(page: Path, source: str) -> str:
    parts: list[str] = []
    for attrs_text, body in re.findall(r"<script\b([^>]*)>(.*?)</script>", source, re.I | re.S):
        if re.search(r"\btype\s*=\s*(['\"])application/ld\+json\1", attrs_text, re.I):
            continue
        parts.append(body)
        src_match = re.search(r"\bsrc\s*=\s*(['\"])(.*?)\1", attrs_text, re.I | re.S)
        if src_match:
            target = local_asset(page, src_match.group(2))
            if target is not None and target.is_file():
                try:
                    parts.append(target.read_text(encoding="utf-8"))
                except UnicodeDecodeError:
                    pass
    return "\n".join(parts)


def selector_candidates(attrs: dict[str, str]) -> set[str]:
    candidates = {
        key for key in attrs
        if key.startswith("data-") and any(term in key for term in ("search", "filter", "local", "reset", "status"))
    }
    if attrs.get("id"):
        candidates.add(attrs["id"])
    candidates.update(
        item for item in attrs.get("class", "").split()
        if any(term in item.lower() for term in ("search", "filter", "reset", "status"))
    )
    return {item for item in candidates if item}


def audit_hub_search(
    page: Path, source: str, parser: DocumentParser, category: Category, audit: Audit,
) -> None:
    rel = page.relative_to(SITE).as_posix()
    search_inputs = [
        attrs for attrs in parser.inputs
        if attrs.get("type", "").lower() == "search"
        or any("search" in (key + " " + value).lower() for key, value in attrs.items())
        or "검색" in attrs.get("aria-label", "")
    ]
    audit.equal(len(search_inputs), 1, f"{rel}: hub search input")

    buttons = parser.by_tag("button", main_only=True)
    reset_buttons = [
        item for item in buttons
        if item.attrs.get("type", "").lower() == "reset"
        or "reset" in " ".join((*item.classes, *item.attrs.keys(), *item.attrs.values())).lower()
        or any(label in item.text for label in ("초기화", "전체 보기", "검색 지우기"))
    ]
    audit.equal(len(reset_buttons), 1, f"{rel}: hub search reset")
    live_elements = [
        item for item in parser.elements
        if item.attrs.get("aria-live", "").lower() in {"polite", "assertive"}
    ]
    audit.equal(len(live_elements), 1, f"{rel}: hub search aria-live")

    detail_pattern = re.compile(rf"^/{re.escape(SUBJECT_ROOT)}/{re.escape(category.slug)}/[^/]+/$")
    local_anchors = [
        item for item in parser.by_tag("a", main_only=True)
        if detail_pattern.fullmatch(urlsplit(item.attrs.get("href", "")).path)
    ]
    audit.equal(len(local_anchors), EXPECTED_DETAILS_PER_CATEGORY, f"{rel}: searchable local anchors")
    common_data_keys: set[str] = set.intersection(*[
        {key for key in item.attrs if key.startswith("data-")}
        for item in local_anchors
    ]) if local_anchors else set()
    searchable_data_keys = {
        key for key in common_data_keys
        if any(term in key.lower() for term in ("search", "filter", "local", "region", "district", "town"))
    }
    for anchor in local_anchors:
        audit.require(bool(compact_space(anchor.text)), f"{rel}: searchable anchor has empty text")

    javascript = script_contract_text(page, source)
    audit.require(bool(javascript.strip()), f"{rel}: hub search script missing")
    link_selectors = [
        selector
        for _quote, selector in re.findall(
            r"querySelectorAll\s*\(\s*(['\"])(.*?)\1", javascript, re.I | re.S,
        )
    ]
    visible_text_search = (
        any(
            ".subject-local-grid" in selector
            and bool(re.search(r"(?:^|[>+~\s])a(?:$|[\s.#:\[])", selector))
            for selector in link_selectors
        )
        and bool(
            re.search(
                r"normalize\s*\(\s*link\.textContent(?:\s*\|\|\s*['\"]{2})?\s*\)"
                r"\s*\.includes\s*\(\s*query\s*\)",
                javascript,
                re.I | re.S,
            )
        )
    )
    data_text_search = bool(searchable_data_keys) and all(
        any(compact_space(anchor.attrs.get(key, "")) for key in searchable_data_keys)
        for anchor in local_anchors
    )
    audit.require(
        data_text_search or visible_text_search,
        f"{rel}: local anchors lack searchable data-* or visible-text script contract",
    )
    if searchable_data_keys and not visible_text_search:
        for anchor in local_anchors:
            audit.require(
                any(compact_space(anchor.attrs.get(key, "")) for key in searchable_data_keys),
                f"{rel}: searchable anchor has empty data text {anchor.attrs.get('href', '')}",
            )

    component_markers: list[set[str]] = []
    if len(search_inputs) == 1:
        component_markers.append(selector_candidates(search_inputs[0]))
    if len(reset_buttons) == 1:
        component_markers.append(selector_candidates(reset_buttons[0].attrs))
    if len(live_elements) == 1:
        component_markers.append(selector_candidates(live_elements[0].attrs))
    if not visible_text_search:
        component_markers.append(searchable_data_keys)
    for index, markers in enumerate(component_markers, 1):
        audit.require(bool(markers), f"{rel}: hub search component {index} lacks selector marker")
        audit.require(any(marker in javascript for marker in markers), f"{rel}: script omits component selector {index}: {sorted(markers)}")
    audit.require(
        bool(re.search(r"addEventListener\s*\(\s*['\"]input['\"]", javascript)),
        f"{rel}: script input-event contract missing",
    )
    audit.require(
        bool(re.search(r"addEventListener\s*\(\s*['\"](?:click|reset)['\"]", javascript)),
        f"{rel}: script reset-event contract missing",
    )
    audit.require(
        bool(re.search(r"\.hidden\s*=|(?:toggle|set|remove)Attribute\s*\(\s*['\"]hidden['\"]", javascript)),
        f"{rel}: script hidden-toggle contract missing",
    )
    audit.require(
        bool(re.search(r"(?:textContent|innerText|aria-live)", javascript)),
        f"{rel}: script live-status update contract missing",
    )


def audit_hidden_css(audit: Audit) -> None:
    path = SITE / "assets" / "site.css"
    audit.require(path.is_file(), "assets/site.css missing")
    if not path.is_file():
        return
    source = path.read_text(encoding="utf-8")
    occurrences = len(re.findall(r"\[hidden\]", source))
    rules = re.findall(r"\[hidden\]\s*\{(.*?)\}", source, re.I | re.S)
    matching = [body for body in rules if re.search(r"display\s*:\s*none\s*!important\s*;?", body, re.I)]
    audit.equal(occurrences, 1, "CSS [hidden] selector occurrences")
    audit.equal(len(matching), 1, "CSS [hidden] display:none!important rules")


def audit_subject_root(audit: Audit) -> None:
    """Validate the pre-existing subject root after its 18-card expansion."""
    page = SITE / SUBJECT_ROOT / "index.html"
    rel = page.relative_to(SITE).as_posix()
    audit.require(page.is_file(), f"{rel}: root page missing")
    if not page.is_file():
        return
    source = page.read_text(encoding="utf-8")
    parser = DocumentParser()
    parser.feed(source)
    expected_url = f"{BASE_URL}/{SUBJECT_ROOT}/"
    title = one([item.text for item in parser.by_tag("title")], audit, rel, "title")
    h1 = one([item.text for item in parser.by_tag("h1", main_only=True)], audit, rel, "H1")
    canonical = one(
        [item.get("href", "") for item in parser.links if "canonical" in item.get("rel", "").lower().split()],
        audit, rel, "canonical",
    )
    og_url = one(meta_values(parser, "property", "og:url"), audit, rel, "og:url")
    audit.equal(title.removesuffix(" | 채움학습"), "과목별학원", f"{rel}: title")
    audit.equal(h1, "과목별학원", f"{rel}: H1")
    audit.equal(canonical, expected_url, f"{rel}: canonical")
    audit.equal(og_url, expected_url, f"{rel}: og:url")

    cards = [item for item in parser.by_tag("a", main_only=True) if "subject-category-card" in item.classes]
    audit.equal(len(cards), len(ALL_CATEGORY_CARDS), f"{rel}: visible category cards")
    actual_cards: list[tuple[str, str]] = []
    for card in cards:
        strongs = [
            item for item in parser.elements
            if item.tag == "strong" and card.start <= item.start <= item.end <= card.end
        ]
        label = compact_space(strongs[0].text) if len(strongs) == 1 else ""
        actual_cards.append((card.attrs.get("href", ""), label))
    expected_cards = [(f"/{SUBJECT_ROOT}/{slug}/", label) for slug, label in ALL_CATEGORY_CARDS]
    audit.require(actual_cards == expected_cards, f"{rel}: visible card order/href/name mismatch")

    nodes = nodes_from_ld(source, audit, rel)
    collection = next((node for node in nodes if has_type(node, "CollectionPage")), None)
    audit.require(collection is not None, f"{rel}: CollectionPage missing")
    expected_list_id = expected_url + "#categories"
    if collection is not None:
        has_part = collection.get("hasPart")
        actual_id = has_part.get("@id", "") if isinstance(has_part, dict) else has_part
        audit.equal(actual_id, expected_list_id, f"{rel}: CollectionPage.hasPart")
    lists = [node for node in nodes if has_type(node, "ItemList") and node.get("@id") == expected_list_id]
    audit.equal(len(lists), 1, f"{rel}: categories ItemList")
    if len(lists) == 1:
        item_list = lists[0]
        audit.equal(item_list.get("numberOfItems"), len(ALL_CATEGORY_CARDS), f"{rel}: ItemList.numberOfItems")
        items = item_list.get("itemListElement", [])
        audit.equal(len(items), len(ALL_CATEGORY_CARDS), f"{rel}: ItemList entries")
        actual_items = [
            (item.get("position"), compact_space(str(item.get("name", ""))), item.get("url", ""))
            for item in items if isinstance(item, dict)
        ]
        expected_items = [
            (position, label, f"{BASE_URL}/{SUBJECT_ROOT}/{slug}/")
            for position, (slug, label) in enumerate(ALL_CATEGORY_CARDS, 1)
        ]
        audit.require(actual_items == expected_items, f"{rel}: ItemList position/name/url mismatch")


def breadcrumb_ok(nodes: list[dict], expected_names: list[str], expected_urls: list[str]) -> bool:
    node = next((item for item in nodes if has_type(item, "BreadcrumbList")), None)
    if not node:
        return False
    items = node.get("itemListElement", [])
    if len(items) != len(expected_names):
        return False
    items = sorted(items, key=lambda item: int(item.get("position", 0)))
    for position, (item, name, url) in enumerate(zip(items, expected_names, expected_urls), 1):
        if item.get("position") != position or compact_space(str(item.get("name", ""))) != name:
            return False
        actual = item.get("item", "")
        if isinstance(actual, dict):
            actual = actual.get("@id", "")
        if actual and str(actual) != url:
            return False
    return True


def relevant_section(parser: DocumentParser, names: tuple[str, ...]) -> list[Element]:
    result: list[Element] = []
    for section in parser.by_tag("section", main_only=True):
        class_text = " ".join(section.classes).lower()
        heading_text = " ".join(
            item.text for item in parser.elements
            if item.tag in {"h2", "h3"} and section.start <= item.start <= item.end <= section.end
        )
        haystack = class_text + " " + heading_text
        if any(name.lower() in haystack for name in names):
            result.append(section)
    return result


def contained_count(parser: DocumentParser, sections: list[Element], tags: set[str], class_term: str = "") -> int:
    candidates = [item for item in parser.elements if item.in_main and item.tag in tags]
    total = 0
    for item in candidates:
        inside = any(section.start <= item.start <= item.end <= section.end for section in sections)
        class_match = class_term and class_term in " ".join(item.classes).lower()
        if inside or class_match:
            total += 1
    return total


def element_inside(element: Element, containers: list[Element]) -> bool:
    return any(container.start <= element.start <= element.end <= container.end for container in containers)


def editorial_sections(parser: DocumentParser) -> list[Element]:
    """Return authored copy while excluding verified center/media facts.

    Center names come from the common CSV and may legitimately contain the old
    operating brand.  The brand-leak gate is meant for rewritten manuscripts,
    FAQs, scenarios and checklists, not those verified fields or Organization
    JSON-LD.  Heading/class matching is intentionally broad so wrapper changes
    do not silently disable the gate.
    """
    result: list[Element] = []
    for section in parser.by_tag("section", main_only=True):
        class_text = " ".join(section.classes).lower()
        if any(term in class_text for term in (
            "subject-center-card", "subject-media-section", "center-facts",
            "location-facts", "subject-related", "related-links",
        )):
            continue
        nested_headings = " ".join(
            item.text for item in parser.elements
            if item.tag in {"h2", "h3"} and section.start <= item.start <= item.end <= section.end
        )
        has_visible_faq = any(
            item.tag == "details"
            and section.start <= item.start <= item.end <= section.end
            and "faq" in " ".join(item.classes).lower()
            for item in parser.elements
        )
        class_authored = any(term in class_text for term in (
            "subject-content", "subject-manuscript", "subject-copy",
            "subject-quick-answer", "subject-checklist", "subject-scenario",
        ))
        heading_authored = any(term in nested_headings for term in (
            "핵심 요약", "핵심 답변", "학습 설계", "추천 학생", "추천학생",
            "체크리스트", "상담 상황", "상황 예시", "자주 묻는 질문", "FAQ",
        ))
        if class_authored or heading_authored or has_visible_faq:
            result.append(section)
    return result


def substantive_paragraphs(parser: DocumentParser) -> list[str]:
    """Paragraph copy only: omit UI labels, leads and verified fact cards."""
    excluded_sections = [
        section for section in parser.by_tag("section", main_only=True)
        if any(term in " ".join(section.classes).lower() for term in (
            "subject-center-card", "subject-media-section", "subject-directory",
        ))
    ]
    structural_classes = {
        "eyebrow", "lead", "tag", "caption", "notice", "subject-service-area-notice",
    }
    result: list[str] = []
    for paragraph in parser.by_tag("p", main_only=True):
        if paragraph.classes & structural_classes or element_inside(paragraph, excluded_sections):
            continue
        value = compact_space(paragraph.text)
        # The contextualized virtual-case disclosure is audited separately.  It
        # is a structural disclosure, rather than editorial body copy.
        if "실제 후기" in value and "가상" in value:
            continue
        if len(comparable(value)) >= 42:
            result.append(value)
    return result


def authored_paragraphs(parser: DocumentParser, sections: list[Element]) -> list[Element]:
    return [
        paragraph for paragraph in parser.by_tag("p", main_only=True)
        if element_inside(paragraph, sections)
    ]


def action_clauses(value: str) -> list[str]:
    """Comparable sentence/long-clause units for body-to-FAQ reuse checks."""
    result: list[str] = []
    for part in re.split(r"[.!?;。！？]+|,\s*", compact_space(value)):
        key = comparable(part)
        if len(key) >= 32:
            result.append(key)
    return result


def audit_authored_copy_regressions(
    parser: DocumentParser, sections: list[Element], rel: str, audit: Audit,
) -> None:
    paragraphs = authored_paragraphs(parser, sections)
    fact_grids = [
        item for item in parser.elements
        if "subject-fact-grid" in item.classes
    ]
    disclosure = lambda value: "실제 후기" in value and "가상" in value
    for paragraph in paragraphs:
        value = compact_space(paragraph.text)
        if (
            not value
            or paragraph.classes & {"eyebrow", "tag"}
            or disclosure(value)
            or element_inside(paragraph, fact_grids)
        ):
            continue
        audit.require(
            bool(re.search(r"(?:[.!?]|다|요)$", value)),
            f"{rel}: authored paragraph has unfinished ending: {value[-40:]}",
        )

    faq_details = [
        item for item in parser.by_tag("details", main_only=True)
        if "faq" in " ".join(item.classes).lower()
    ]
    faq_paragraphs = [item for item in paragraphs if element_inside(item, faq_details)]
    body_paragraphs = [
        item for item in paragraphs
        if not element_inside(item, faq_details)
        and not disclosure(compact_space(item.text))
        and not item.classes & {"eyebrow", "tag"}
    ]
    body_clauses = [clause for item in body_paragraphs for clause in action_clauses(item.text)]
    faq_clauses = [clause for item in faq_paragraphs for clause in action_clauses(item.text)]
    overlaps: set[str] = set()
    for body in body_clauses:
        for faq in faq_clauses:
            shorter, longer = (body, faq) if len(body) <= len(faq) else (faq, body)
            if shorter in longer:
                overlaps.add(shorter)
    audit.require(
        not overlaps,
        f"{rel}: body/FAQ exact core action clauses reused={len(overlaps)}",
    )


def masked_copy(text: str, category: Category, locality: str, title: str) -> str:
    value = compact_space(text)
    replacements = sorted(
        {title, locality, category.slug, category.label, category.grade, category.grade_code, category.subject},
        key=len,
        reverse=True,
    )
    for token in replacements:
        if token:
            value = value.replace(token, " MASK ")
    value = re.sub(r"\b\d+(?:[-.,]\d+)*\b", " NUM ", value)
    return value


def audit_page(
    page: Path,
    category: Category,
    locality: str,
    is_hub: bool,
    source_sentences: set[str],
    source_shingles: set[tuple[str, ...]],
    center_rows: dict[str, dict[str, str]],
    source_fallback: bool,
    audit: Audit,
) -> PageRecord:
    rel = page.relative_to(SITE).as_posix()
    text = page.read_text(encoding="utf-8")
    center_row = center_rows.get(locality, {}) if locality else {}
    display_locality = center_row.get("근처수업가능동네", locality) or locality
    parser = DocumentParser()
    try:
        parser.feed(text)
    except Exception as exc:
        audit.require(False, f"{rel}: HTML parse: {exc}")

    titles = [item.text for item in parser.by_tag("title")]
    h1s = [item.text for item in parser.by_tag("h1", main_only=True)]
    descriptions = meta_values(parser, "name", "description")
    canonicals = [item.get("href", "") for item in parser.links if "canonical" in item.get("rel", "").lower().split()]
    og_urls = meta_values(parser, "property", "og:url")
    title = one(titles, audit, rel, "title")
    h1 = one(h1s, audit, rel, "H1")
    description = one(descriptions, audit, rel, "description")
    canonical = one(canonicals, audit, rel, "canonical")
    og_url = one(og_urls, audit, rel, "og:url")
    expected = f"{BASE_URL}/{SUBJECT_ROOT}/{category.slug}/"
    if not is_hub:
        expected += f"{locality}/"
    audit.equal(canonical, expected, f"{rel}: canonical")
    audit.equal(og_url, expected, f"{rel}: og:url")
    expected_h1 = category.label if is_hub else f"{display_locality} {category.label}"
    audit.equal(h1, expected_h1, f"{rel}: H1 target")
    audit.equal(title.removesuffix(" | 채움학습"), h1, f"{rel}: title/H1")
    audit.require(bool(description), f"{rel}: empty description")

    main_text = parser.main_text
    authored_scope = editorial_sections(parser)
    authored_text = compact_space(" ".join(section.text for section in authored_scope))
    public_text = compact_space(" ".join((title, h1, description, main_text)))
    public_sheet_error = re.compile(r"#(?:ERROR!?|REF!?|VALUE!?|N/A|NAME\?)", re.I)
    audit.require(not public_sheet_error.search(public_text), f"{rel}: spreadsheet error exposed in public text")
    if source_fallback:
        audit.stats["neutral_fallback_pages"] += 1
        audit.require(
            bool(re.search(r"학습|진단|복습|오답|상담", authored_text))
            and not re.search(r"원고\s*오류|수식\s*오류|fallback|spreadsheet", authored_text, re.I),
            f"{rel}: source fallback is not neutral public guidance",
        )
    for label, pattern in BAD_VISIBLE:
        audit.require(not pattern.search(authored_text), f"{rel}: banned authored-copy {label}")
    for label, pattern in COPY_REGRESSIONS:
        audit.require(not pattern.search(authored_text), f"{rel}: authored-copy regression {label}")
    if not is_hub:
        audit_authored_copy_regressions(parser, authored_scope, rel, audit)

    nodes = nodes_from_ld(text, audit, rel)
    found_types = schema_types(nodes)
    audit.require("Review" not in found_types, f"{rel}: Review schema forbidden")
    if is_hub:
        hub_types = {"CollectionPage", "BreadcrumbList", "ItemList"}
        audit.require(hub_types <= found_types, f"{rel}: hub schema missing {sorted(hub_types - found_types)}")
        audit.require(relation_present(nodes, "hasPart"), f"{rel}: hub JSON-LD hasPart missing")
    else:
        audit.require(REQUIRED_TYPES <= found_types, f"{rel}: schema missing {sorted(REQUIRED_TYPES - found_types)}")
        for relation in REQUIRED_RELATIONS:
            audit.require(relation_present(nodes, relation), f"{rel}: JSON-LD relation missing {relation}")
        article = next((node for node in nodes if has_type(node, "Article")), {})
        for relation in ("about", "mentions", "hasPart", "articleSection"):
            audit.require(article.get(relation) not in (None, "", [], {}), f"{rel}: Article.{relation} missing")
        organizations = [node for node in nodes if has_type(node, "EducationalOrganization") or has_type(node, "LocalBusiness")]
        audit.require(any(node.get("makesOffer") not in (None, "", [], {}) for node in organizations), f"{rel}: organization makesOffer missing")

    parent_url = f"{BASE_URL}/{SUBJECT_ROOT}/"
    category_url = f"{parent_url}{category.slug}/"
    expected_names = ["홈", "과목별학원", category.label]
    expected_urls = [f"{BASE_URL}/", parent_url, category_url]
    if not is_hub:
        expected_names.append(f"{display_locality} {category.label}")
        expected_urls.append(expected)
    audit.require(breadcrumb_ok(nodes, expected_names, expected_urls), f"{rel}: JSON-LD breadcrumb chain")
    breadcrumbs = [item for item in parser.elements if item.tag == "nav" and ("breadcrumb" in " ".join(item.classes).lower() or "현재 위치" in item.attrs.get("aria-label", ""))]
    audit.require(bool(breadcrumbs), f"{rel}: visible semantic breadcrumb missing")
    if breadcrumbs:
        audit.require(expected_names[-1] in breadcrumbs[-1].text, f"{rel}: breadcrumb current label")

    if is_hub:
        audit_hub_search(page, text, parser, category, audit)
        item_lists = [node for node in nodes if has_type(node, "ItemList")]
        sizes = [len(node.get("itemListElement", [])) for node in item_lists]
        audit.require(EXPECTED_DETAILS_PER_CATEGORY in sizes, f"{rel}: hub ItemList must contain 371 details; sizes={sizes}")
        detail_pattern = re.compile(rf"^/{re.escape(SUBJECT_ROOT)}/{re.escape(category.slug)}/[^/]+/$")
        local_links = {
            urlsplit(item.get("href", "")).path for item in parser.anchors
            if detail_pattern.fullmatch(urlsplit(item.get("href", "")).path)
        }
        audit.equal(len(local_links), EXPECTED_DETAILS_PER_CATEGORY, f"{rel}: hub unique detail links")
    else:
        faq_nodes = [node for node in nodes if has_type(node, "FAQPage")]
        faq_count = len(faq_nodes[0].get("mainEntity", [])) if faq_nodes else 0
        details = parser.by_tag("details", main_only=True)
        visible_faq = sum(1 for item in details if "faq" in " ".join(item.classes).lower()) or len(details)
        audit.require(faq_count >= 5, f"{rel}: FAQPage questions={faq_count}, expected>=5")
        audit.require(visible_faq >= 5, f"{rel}: visible FAQ items={visible_faq}, expected>=5")
        scenario_sections = relevant_section(parser, ("scenario", "추천 학생", "추천학생", "학습 상황", "상황별", "이런 학생"))
        scenario_cards = contained_count(parser, scenario_sections, {"article", "li"}, "scenario")
        audit.require(bool(scenario_sections), f"{rel}: scenario/recommended-student section missing")
        audit.require(scenario_cards >= 2, f"{rel}: scenario cards={scenario_cards}, expected>=2")
        scenario_disclosures = [
            item.text for item in parser.by_tag("p", main_only=True)
            if element_inside(item, scenario_sections) and "실제 후기" in item.text and "가상" in item.text
        ]
        audit.require(bool(scenario_disclosures), f"{rel}: virtual-scenario disclosure missing")
        audit.require(
            any(display_locality in item or category.label in item or title in item for item in scenario_disclosures),
            f"{rel}: virtual-scenario disclosure lacks page context",
        )
        checklist_sections = relevant_section(parser, ("checklist", "체크리스트", "상담 전", "상담전"))
        checklist_items = contained_count(parser, checklist_sections, {"li"}, "checklist")
        audit.require(bool(checklist_sections), f"{rel}: consultation checklist section missing")
        audit.require(checklist_items >= 3, f"{rel}: checklist items={checklist_items}, expected>=3")

    # Asset-role checks use path and semantic attributes, rather than a single CSS contract.
    representatives = [
        item.get("src", "") for item in parser.images
        if "/assets/representative/" in item.get("src", "")
        or "representative" in item.get("class", "").lower()
        or "대표" in item.get("alt", "")
    ]
    body_images = [item.get("src", "") for item in parser.images if re.search(r"/assets/centers/common/(?:seoul6839|local6839)\.webp(?:[?#].*)?$", item.get("src", ""))]
    map_images = [item.get("src", "") for item in parser.images if "/assets/maps/" in item.get("src", "") or "지도" in item.get("alt", "")]
    if not is_hub:
        audit.equal(len(set(representatives)), 1, f"{rel}: representative image role")
        audit.equal(len(set(body_images)), 1, f"{rel}: common body image role")
        audit.equal(len(set(map_images)), 1, f"{rel}: map image role")
    for attr in [item.get("src", "") for item in parser.images] + [item.get("href", "") for item in parser.anchors] + [item.get("href", "") for item in parser.links]:
        target = local_asset(page, attr)
        if target is not None:
            try:
                target.relative_to(SITE.resolve())
                inside = True
            except ValueError:
                inside = False
            audit.require(inside and target.exists() and target.is_file(), f"{rel}: broken/outside href/src {attr}")

    paragraph_values = substantive_paragraphs(parser)
    section_values = [compact_space(item.text) for item in parser.by_tag("section", main_only=True) if len(comparable(item.text)) >= 120]
    page_sentences = sentences(main_text)
    authored_sentences = sentences(authored_text)
    duplicates = [key for key, count in Counter(page_sentences).items() if count > 1]
    audit.require(not duplicates, f"{rel}: within-page duplicate substantive sentences={len(duplicates)}")
    if not is_hub:
        exact_reuse = set(authored_sentences) & source_sentences
        source_12_reuse = word_shingles(authored_text, 12) & source_shingles
        audit.require(not exact_reuse, f"{rel}: raw-source exact sentences reused={len(exact_reuse)}")
        audit.require(not source_12_reuse, f"{rel}: raw-source 12-word shingles reused={len(source_12_reuse)}")

        row = center_row
        audit.require(bool(row), f"{rel}: locality missing from center CSV")
        school_field = f"타깃학교({category.school_level})"
        grade_field = f"가능학년({category.subject})"
        schools = split_csv_values(row.get(school_field, ""))
        grades = split_csv_values(row.get(grade_field, ""))
        if schools:
            for school in schools:
                audit.require(school in main_text, f"{rel}: CSV school omitted {school}")
        else:
            audit.require(bool(re.search(r"학교.{0,35}(?:상담|확인)|(?:상담|확인).{0,35}학교", main_text)), f"{rel}: empty CSV school consultation branch missing")
        if category.grade_code in grades:
            audit.require(category.grade_code in main_text or category.grade in main_text, f"{rel}: CSV grade omitted {category.grade_code}")
        else:
            audit.require(bool(re.search(r"학년.{0,35}(?:상담|확인)|(?:상담|확인).{0,35}학년", main_text)), f"{rel}: unavailable CSV grade consultation branch missing")

    masked = masked_copy(authored_text, category, display_locality, title)
    return PageRecord(
        path=page, rel=rel, category=category.slug, locality=locality,
        canonical=canonical, title=title, description=description, h1=h1,
        main_text=main_text, paragraphs=paragraph_values, sections=section_values,
        masked_shingles=hashed_word_shingles(masked, 5),
        representative=representatives[0] if representatives else "",
    )


def audit_exact_uniqueness(records: list[PageRecord], audit: Audit) -> None:
    for label, values in (
        ("title", [record.title for record in records]),
        ("H1", [record.h1 for record in records]),
        ("canonical", [record.canonical for record in records]),
        ("description", [record.description for record in records]),
        ("document", [comparable(record.main_text) for record in records]),
        ("paragraph", [comparable(value) for record in records for value in record.paragraphs]),
        ("section", [comparable(value) for record in records for value in record.sections]),
    ):
        counts = Counter(value for value in values if value)
        duplicates = {value: count for value, count in counts.items() if count > 1}
        audit.require(not duplicates, f"global exact duplicate {label}s={len(duplicates)} occurrences={sum(duplicates.values())}")
        audit.stats[f"unique_{label}"] = len(counts)


def audit_representative_permutations(records: list[PageRecord], audit: Audit) -> None:
    details = [record for record in records if record.locality]
    entries: dict[str, list[tuple[str, str, bool]]] = defaultdict(list)
    for category in CATEGORIES:
        category_records = [record for record in details if record.category == category.slug]
        reps = [urlsplit(record.representative).path for record in category_records]
        audit.equal(len(set(reps)), EXPECTED_DETAILS_PER_CATEGORY, f"{category.slug}: representative permutation")
    for record in details:
        entries[record.locality].append((record.category, urlsplit(record.representative).path, True))

    expected_localities = set(entries)
    for category in EXISTING_CATEGORIES:
        root = SITE / SUBJECT_ROOT / category
        pages = sorted(root.glob("*/index.html")) if root.exists() else []
        audit.equal(len(pages), EXPECTED_DETAILS_PER_CATEGORY, f"{category}: protected representative pages")
        actual_localities = {page.parent.name for page in pages}
        audit.require(actual_localities == expected_localities, f"{category}: protected locality set mismatch")
        for page in pages:
            source = page.read_text(encoding="utf-8")
            parser = DocumentParser()
            parser.feed(source)
            representatives = [
                item.get("src", "") for item in parser.images
                if "/assets/representative/" in item.get("src", "")
                or "representative" in item.get("class", "").lower()
                or "대표" in item.get("alt", "")
            ]
            unique = list(dict.fromkeys(urlsplit(value).path for value in representatives if value))
            rel = page.relative_to(SITE).as_posix()
            audit.equal(len(unique), 1, f"{rel}: protected representative role")
            entries[page.parent.name].append((category, unique[0] if len(unique) == 1 else "", False))

    expected_existing_collision_localities = {
        "역북동", "흥덕마을", "부평동", "호암동", "봉방동", "화봉동", "선암동",
    }
    path_existing_collisions: list[tuple[str, str, str]] = []
    sha_existing_collisions: list[tuple[str, str, str]] = []
    path_new_collisions: list[tuple[str, str, str]] = []
    sha_new_collisions: list[tuple[str, str, str]] = []
    sha_cache: dict[str, str] = {}
    for locality, locality_entries in sorted(entries.items()):
        audit.equal(len(locality_entries), len(ALL_CATEGORY_CARDS), f"{locality}: all-category representative entries")
        for category, rep, _ in locality_entries:
            audit.require(rep.startswith("/assets/representative/"), f"{locality}/{category}: representative path {rep}")
            asset = SITE / unquote(rep).lstrip("/")
            audit.require(asset.is_file(), f"{locality}/{category}: representative asset missing {rep}")
            if asset.is_file() and rep not in sha_cache:
                sha_cache[rep] = hashlib.sha256(asset.read_bytes()).hexdigest()
        for left in range(len(locality_entries)):
            left_category, left_path, left_new = locality_entries[left]
            for right in range(left + 1, len(locality_entries)):
                right_category, right_path, right_new = locality_entries[right]
                if left_path == right_path:
                    target = path_new_collisions if left_new or right_new else path_existing_collisions
                    target.append((locality, left_category, right_category))
                left_sha = sha_cache.get(left_path, "")
                right_sha = sha_cache.get(right_path, "")
                if left_sha and left_sha == right_sha:
                    target = sha_new_collisions if left_new or right_new else sha_existing_collisions
                    target.append((locality, left_category, right_category))

    audit.require(not path_new_collisions, f"new representative path collisions={path_new_collisions[:10]}")
    audit.require(not sha_new_collisions, f"new representative SHA collisions={sha_new_collisions[:10]}")
    audit.equal(len(path_existing_collisions), 7, "protected-only representative path collision pairs")
    audit.equal(len(sha_existing_collisions), 7, "protected-only representative SHA collision pairs")
    audit.require(
        {item[0] for item in path_existing_collisions} == expected_existing_collision_localities,
        f"protected-only path collision localities={sorted({item[0] for item in path_existing_collisions})}",
    )
    audit.require(
        {item[0] for item in sha_existing_collisions} == expected_existing_collision_localities,
        f"protected-only SHA collision localities={sorted({item[0] for item in sha_existing_collisions})}",
    )
    audit.stats["representative_protected_path_collisions"] = len(path_existing_collisions)
    audit.stats["representative_protected_sha_collisions"] = len(sha_existing_collisions)


def audit_jaccard(records: list[PageRecord], audit: Audit) -> None:
    """Exact threshold search using the standard Jaccard prefix-filter guarantee."""
    sets = [record.masked_shingles for record in records if record.locality]
    names = [record.rel for record in records if record.locality]
    frequencies = Counter(token for token_set in sets for token in token_set)
    inverted: dict[int, list[int]] = defaultdict(list)
    evaluated: set[tuple[int, int]] = set()
    violations: list[tuple[float, str, str]] = []
    max_examined = (0.0, "", "")
    order_cache: list[list[int]] = []
    for token_set in sets:
        order_cache.append(sorted(token_set, key=lambda token: (frequencies[token], token)))
    for right, ordered in enumerate(order_cache):
        size_right = len(sets[right])
        prefix_length = max(0, size_right - math.ceil(JACCARD_LIMIT * size_right) + 1)
        candidates: set[int] = set()
        for token in ordered[:prefix_length]:
            candidates.update(inverted[token])
        for left in candidates:
            pair = (left, right)
            if pair in evaluated:
                continue
            evaluated.add(pair)
            size_left = len(sets[left])
            if not size_left or not size_right or min(size_left, size_right) / max(size_left, size_right) < JACCARD_LIMIT:
                continue
            intersection = len(sets[left] & sets[right])
            score = intersection / (size_left + size_right - intersection)
            if score > max_examined[0]:
                max_examined = (score, names[left], names[right])
            if score >= JACCARD_LIMIT:
                violations.append((score, names[left], names[right]))
        for token in ordered[:prefix_length]:
            inverted[token].append(right)
    violations.sort(reverse=True)
    audit.require(not violations, f"masked 5-word Jaccard >= {JACCARD_LIMIT}: {violations[:5]}")
    audit.stats["jaccard_candidate_pairs"] = len(evaluated)
    print(f"masked_5word_jaccard_limit={JACCARD_LIMIT:.2f} max_examined={max_examined[0]:.6f} pair={max_examined[1:]} candidates={len(evaluated)}")


def audit_sitemap(records: list[PageRecord], audit: Audit) -> None:
    path = SITE / "sitemap.xml"
    audit.require(path.is_file(), "sitemap.xml missing")
    if not path.is_file():
        return
    try:
        root = ET.parse(path).getroot()
        locs = [
            unquote(compact_space(node.text or ""))
            for node in root.iter()
            if node.tag.endswith("}loc") or node.tag == "loc"
        ]
    except ET.ParseError as exc:
        audit.require(False, f"sitemap.xml parse: {exc}")
        return
    audit.equal(len(locs), EXPECTED_SITEMAP_URLS, "sitemap total URLs")
    audit.equal(len(set(locs)), EXPECTED_SITEMAP_URLS, "sitemap unique URLs")
    expected_new = {record.canonical for record in records}
    audit.equal(len(expected_new), EXPECTED_NEW_URLS, "new canonical set")
    new_prefixes = tuple(f"{BASE_URL}/{SUBJECT_ROOT}/{category.slug}/" for category in CATEGORIES)
    actual_new = {url for url in locs if url.startswith(new_prefixes)}
    audit.equal(len(actual_new), EXPECTED_NEW_URLS, "sitemap new-scope URLs")
    audit.require(expected_new == actual_new, f"sitemap new-scope mismatch missing={len(expected_new - actual_new)} extra={len(actual_new - expected_new)}")


def hash_existing_scope() -> dict[str, str]:
    result: dict[str, str] = {}
    for category in EXISTING_CATEGORIES:
        root = SITE / SUBJECT_ROOT / category
        if not root.exists():
            continue
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            rel = path.relative_to(SITE).as_posix()
            result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def write_hash_gate(path: Path) -> None:
    payload = {
        "algorithm": "sha256",
        "scope": list(EXISTING_CATEGORIES),
        "files": hash_existing_scope(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote_existing_hash_gate={path} files={len(payload['files'])}")


def check_hash_gate(path: Path, audit: Audit) -> None:
    audit.require(path.is_file(), f"existing hash gate missing: {path}")
    if not path.is_file():
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("manifest must be an object")
        if payload.get("algorithm") != "sha256":
            raise ValueError("algorithm must be sha256")
        if set(payload.get("scope", [])) != set(EXISTING_CATEGORIES):
            raise ValueError(f"scope must be exactly {list(EXISTING_CATEGORIES)!r}")
        expected = payload.get("files")
        if not isinstance(expected, dict) or not expected:
            raise ValueError("files must be a non-empty object")
        allowed_prefixes = tuple(f"{SUBJECT_ROOT}/{category}/" for category in EXISTING_CATEGORIES)
        outside = [key for key in expected if not isinstance(key, str) or not key.startswith(allowed_prefixes)]
        if outside:
            raise ValueError(f"files outside protected scope: {outside[:3]!r}")
        invalid_hashes = [value for value in expected.values() if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)]
        if invalid_hashes:
            raise ValueError("files contains invalid SHA-256 values")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        audit.require(False, f"existing hash gate unreadable: {exc}")
        return
    actual = hash_existing_scope()
    missing = set(expected) - set(actual)
    extra = set(actual) - set(expected)
    changed = {key for key in set(expected) & set(actual) if expected[key] != actual[key]}
    audit.require(not missing and not extra and not changed, f"existing hash gate mismatch missing={len(missing)} extra={len(extra)} changed={len(changed)}")
    for category in EXISTING_CATEGORIES:
        prefix = f"{SUBJECT_ROOT}/{category}/"
        html_files = [key for key in actual if key.startswith(prefix) and key.endswith(".html")]
        audit.equal(len(html_files), EXPECTED_DETAILS_PER_CATEGORY + 1, f"existing hash scope {category} HTML files")
    audit.stats["existing_hash_files"] = len(actual)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=Path.home() / "Desktop" / "새 폴더")
    parser.add_argument("--common-dir", type=Path, default=SITE.parent / "참고자료" / "공통자료")
    parser.add_argument("--existing-hash-gate", type=Path, help="JSON SHA-256 baseline to verify for the four existing categories")
    parser.add_argument("--write-existing-hash-gate", type=Path, help="write a JSON SHA-256 baseline for the four existing categories")
    parser.add_argument("--max-errors", type=int, default=100)
    args = parser.parse_args()

    if args.write_existing_hash_gate:
        write_hash_gate(args.write_existing_hash_gate.resolve())
        return 0
    if not args.existing_hash_gate:
        parser.error("release audit requires --existing-hash-gate; create it separately with --write-existing-hash-gate")
    audit = Audit(max_errors=max(1, args.max_errors))
    check_hash_gate(args.existing_hash_gate.resolve(), audit)

    source_sentences, source_shingles, fallback_rows = load_sources(args.source_dir.resolve(), audit)
    center_rows = load_center_rows(args.common_dir.resolve(), audit)
    ordered_localities = list(center_rows)
    fallback_pages = {
        (category_slug, ordered_localities[row_index])
        for category_slug, row_indexes in fallback_rows.items()
        for row_index in row_indexes
        if row_index < len(ordered_localities)
    }
    audit.equal(len(fallback_pages), 7, "mapped neutral-fallback pages")
    audit_hidden_css(audit)
    audit_subject_root(audit)
    records: list[PageRecord] = []
    for category in CATEGORIES:
        root = SITE / SUBJECT_ROOT / category.slug
        hub = root / "index.html"
        detail_pages = sorted(root.glob("*/index.html")) if root.exists() else []
        audit.require(hub.is_file(), f"{category.slug}: hub missing")
        audit.equal(len(detail_pages), EXPECTED_DETAILS_PER_CATEGORY, f"{category.slug}: detail pages")
        if hub.is_file():
            records.append(audit_page(hub, category, "", True, source_sentences, source_shingles, center_rows, False, audit))
        for page in detail_pages:
            locality = page.parent.name
            records.append(audit_page(
                page, category, locality, False, source_sentences, source_shingles,
                center_rows, (category.slug, locality) in fallback_pages, audit,
            ))

    audit.equal(len(records), EXPECTED_NEW_URLS, "new page records")
    audit.equal(audit.stats["neutral_fallback_pages"], 7, "neutral fallback output pages")
    audit_exact_uniqueness(records, audit)
    audit_representative_permutations(records, audit)
    audit_jaccard(records, audit)
    audit_sitemap(records, audit)

    print(f"categories={len(CATEGORIES)} hubs={sum(not item.locality for item in records)} details={sum(bool(item.locality) for item in records)}")
    print(" ".join(f"{key}={value}" for key, value in sorted(audit.stats.items())))
    print(f"checks={audit.checks} errors={len(audit.errors)}")
    for error in audit.errors[:audit.max_errors]:
        print("ERROR", error)
    if len(audit.errors) > audit.max_errors:
        print(f"ERROR ... {len(audit.errors) - audit.max_errors} more")
    return 1 if audit.errors else 0


if __name__ == "__main__":
    sys.exit(main())
