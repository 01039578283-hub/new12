from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path

import generate_hs_academy_pages as shared


SITE = Path(__file__).resolve().parents[1]
COMMON = SITE.parent / "참고자료" / "공통자료"
USED_DRAFTS = SITE.parent / "참고자료" / "사용한 원고" / "채움학습.com 추가 원고"
BASE_URL = "https://xn--ru4bz7e9zf0zk.com"
SITE_NAME = "채움학습"
PHONE_DISPLAY = "010-6839-8283"
PHONE_LINK = "01068398283"
PUBLISH_DATE = "2026-07-26"


CONFIGS = {
    "중1수학학원": {
        "zip": "중1 수학학원.zip",
        "label": "중1 수학학원",
        "grade": "중학교 1학년",
        "subject": "수학",
        "school_field": "타깃학교\n(중)",
        "grade_field": "가능학년\n(수학)",
    },
    "중1영어학원": {
        "zip": "중1 영어학원.zip",
        "label": "중1 영어학원",
        "grade": "중학교 1학년",
        "subject": "영어",
        "school_field": "타깃학교\n(중)",
        "grade_field": "가능학년\n(영어)",
    },
    "초6수학학원": {
        "zip": "초6 수학학원.zip",
        "label": "초6 수학학원",
        "grade": "초등학교 6학년",
        "subject": "수학",
        "school_field": "타깃학교\n(초)",
        "grade_field": "가능학년\n(수학)",
    },
    "초6영어학원": {
        "zip": "초6 영어학원.zip",
        "label": "초6 영어학원",
        "grade": "초등학교 6학년",
        "subject": "영어",
        "school_field": "타깃학교\n(초)",
        "grade_field": "가능학년\n(영어)",
    },
}


SECTION_RE = re.compile(r"^\[(페이지타이틀|메타설명|본문|FAQ|학부모후기|JSON-LD 요약)\]\s*$", re.M)
FAQ_RE = re.compile(r"Q\d+[.)]?\s*(.*?)\s*\nA\d+[.)]?\s*(.*?)(?=\n\s*Q\d+[.)]?|\Z)", re.S)


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def has_batchim(value: str) -> bool:
    if not value:
        return False
    code = ord(value[-1])
    return 0xAC00 <= code <= 0xD7A3 and (code - 0xAC00) % 28 != 0


def normalize_particles(value: str) -> str:
    def wa_gwa(match: re.Match[str]) -> str:
        word = match.group(1)
        return word + ("과" if has_batchim(word) else "와") + match.group(3)

    # 원고의 뜻은 유지하고, 명사 뒤 조사만 받침에 맞게 바로잡습니다.
    return re.sub(r"([가-힣]+)(와|과)(\s+(?:관련|함께|비교|연결|같이|달리|더불어))", wa_gwa, value)


def clean_text(value: str) -> str:
    value = value.replace("\ufeff", "").replace("내신성적와", "내신성적과")
    value = normalize_particles(value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def split_values(value: str) -> list[str]:
    values = [x.strip() for x in re.split(r"[,/\n·]+", value or "") if x.strip()]
    return list(dict.fromkeys(values))


def slug_local(value: str) -> str:
    return re.sub(r"\s+", "", value.strip())


def trim_description(value: str, fallback: str) -> str:
    text = re.sub(r"\s+", " ", clean_text(value)) or fallback
    if len(text) <= 110:
        return text
    clipped = text[:106]
    for stop in (". ", "다. ", "요. "):
        pos = clipped.rfind(stop)
        if pos >= 72:
            return clipped[: pos + len(stop.strip())].strip()
    return clipped.rstrip(" ,·") + "…"


def absolute(path: str) -> str:
    return BASE_URL + (path if path.startswith("/") else "/" + path)


def parse_sections(raw: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(raw))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        sections[match.group(1)] = clean_text(raw[match.end():end])
    required = {"페이지타이틀", "메타설명", "본문", "FAQ", "학부모후기", "JSON-LD 요약"}
    missing = required - sections.keys()
    if missing:
        raise ValueError(f"원고 구역 누락: {sorted(missing)}")
    return sections


def decode_zip_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp949"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("unknown", data, 0, 1, "지원하는 인코딩이 아닙니다")


def load_manuscripts(zip_path: Path, category_label: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    with zipfile.ZipFile(zip_path) as archive:
        for name in archive.namelist():
            if not name.lower().endswith(".txt") or name.endswith("/"):
                continue
            sections = parse_sections(decode_zip_text(archive.read(name)))
            title = sections["페이지타이틀"].strip()
            local = re.sub(rf"\s*{re.escape(category_label)}\s*$", "", title).strip()
            if not local:
                raise ValueError(f"동네명을 찾을 수 없습니다: {name}")
            key = slug_local(local)
            if key in result:
                raise ValueError(f"중복 동네 원고: {local}")
            sections["동네"] = local
            sections["파일"] = name
            result[key] = sections
    return result


def load_centers() -> list[dict[str, str]]:
    with (COMMON / "센터정보 정리.csv").open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def parse_body(body: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    chunks = re.split(r"^##\s+", clean_text(body), flags=re.M)
    intro = [p.strip() for p in chunks[0].split("\n\n") if p.strip()]
    sections: list[tuple[str, list[str]]] = []
    for chunk in chunks[1:]:
        lines = chunk.splitlines()
        heading = lines[0].strip().strip("# ")
        paragraphs = [p.strip() for p in "\n".join(lines[1:]).split("\n\n") if p.strip()]
        if heading:
            sections.append((heading, paragraphs))
    return intro, sections


def parse_faq(value: str) -> list[tuple[str, str]]:
    pairs = [(clean_text(q), clean_text(a)) for q, a in FAQ_RE.findall(value)]
    if len(pairs) < 3:
        raise ValueError(f"FAQ를 3개 이상 해석하지 못했습니다: {value[:120]}")
    return pairs


def parse_reviews(value: str) -> list[str]:
    result = []
    for paragraph in re.split(r"\n\s*\n", clean_text(value)):
        paragraph = re.sub(r"^.*?학부모\s*후기\s*예시\s*\d+\s*:\s*", "", paragraph.strip())
        if paragraph:
            result.append(paragraph)
    return result


def representative_images() -> list[Path]:
    files = sorted(p for p in (SITE / "assets" / "representative").iterdir() if p.is_file())
    if not files:
        raise FileNotFoundError("assets/representative 대표이미지가 없습니다")
    return files


def pick_representative(images: list[Path], local: str, category: str) -> str:
    digest = hashlib.sha256(f"{category}|{local}|6839".encode()).digest()
    index = int.from_bytes(digest[:4], "big") % len(images)
    return "/assets/representative/" + images[index].name


def find_map(row: dict[str, str]) -> str:
    rel = shared.find_map(row)
    return "/" + rel.replace("\\", "/").lstrip("/")


def fee_link(row: dict[str, str]) -> str:
    value = row.get("센터 교습비", "").strip()
    match = re.search(r"https?://[^\s\"'<>]+", value)
    if not match:
        return ""
    return match.group(0)


def head_html(title: str, description: str, canonical: str, image: str, graph: list[dict]) -> str:
    payload = {"@context": "https://schema.org", "@graph": graph}
    return f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} | {SITE_NAME}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{esc(canonical)}">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{esc(title)} | {SITE_NAME}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(absolute(image))}">
  <link rel="alternate" type="text/plain" href="{BASE_URL}/llms.txt" title="LLM 안내">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&amp;family=Noto+Serif+KR:wght@500;600;700;800&amp;display=swap" rel="stylesheet">
  <link rel="icon" type="image/png" href="/assets/favicon.png">
  <link rel="apple-touch-icon" href="/assets/favicon.png">
  <link rel="stylesheet" href="/assets/site.css">
  <script type="application/ld+json">{json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")}</script>
</head>'''


def nav(active: str) -> str:
    links = [
        ("홈", "/"),
        ("학습가이드", "/학습가이드/"),
        ("상담문의", "/상담문의/"),
        ("과목별학원", "/과목별학원/"),
        ("전국학원", "/전국학원/"),
    ]
    items = "\n".join(
        f'        <a{" class=\"active\"" if name == active else ""} href="{href}">{name}</a>'
        for name, href in links
    )
    return f'''  <header class="nav-wrap">
    <nav class="nav" aria-label="주요 메뉴">
      <a class="brand" href="/"><span class="brand-mark">채</span><span>{SITE_NAME}</span></a>
      <div class="nav-links">
{items}
      </div>
    </nav>
  </header>'''


def footer() -> str:
    return f'''  <footer class="footer">
    <p><strong>{SITE_NAME}</strong> · 학습 코칭 · 상담은 전화·문자로 편하게 문의해주세요.</p>
  </footer>
  <div class="floating-cta" aria-label="빠른 상담 버튼">
    <a href="tel:{PHONE_DISPLAY}">전화문의</a>
    <a href="sms:{PHONE_LINK}">문자문의</a>
    <a href="/상담문의/">상담문의</a>
  </div>'''


def shell(head: str, body: str) -> str:
    return f'''{head}
<body>
<div class="site-shell">
{body}
</div>
</body>
</html>
'''


def body_html(intro: list[str], sections: list[tuple[str, list[str]]]) -> str:
    intro_html = "".join(f"<p>{esc(p)}</p>" for p in intro)
    cards = []
    for index, (heading, paragraphs) in enumerate(sections, 1):
        cards.append(
            f'<article class="subject-copy-card"><span class="subject-copy-index">{index:02d}</span>'
            f'<h2>{esc(heading)}</h2>{"".join(f"<p>{esc(p)}</p>" for p in paragraphs)}</article>'
        )
    return f'<div class="subject-intro">{intro_html}</div><div class="subject-copy-grid">{"".join(cards)}</div>'


def local_page(
    row: dict[str, str], manuscript: dict[str, str], config: dict[str, str], category: str,
    rep_images: list[Path], ordered_rows: list[dict[str, str]],
) -> str:
    local = row["근처 수업가능 동네"].strip()
    slug = slug_local(local)
    title = manuscript["페이지타이틀"].strip()
    region = row.get("지역", "").strip()
    district = row.get("시or구", "").strip()
    center = row.get("센터명", "").strip() or f"{local} 학습코칭센터"
    address = row.get("센터 주소", "").strip()
    location = row.get("위치안내", "").strip()
    schools = split_values(row.get(config["school_field"], ""))
    grade_range = row.get(config["grade_field"], "").strip()
    reg_office = row.get("교육지원청명칭", "").strip()
    reg_number = row.get("교육지원청 등록번호", "").strip()
    description = trim_description(
        manuscript["메타설명"],
        f"{region} {district} {local} {config['grade']} {config['subject']} 학습에서 확인할 진단·내신·오답 관리 기준을 정리했습니다.",
    )
    summary = trim_description(manuscript["JSON-LD 요약"], description)
    summary = re.sub(r"정보성\s*원고이다\.?$", "정보성 학습 안내입니다.", summary)
    intro, body_sections = parse_body(manuscript["본문"])
    faqs = parse_faq(manuscript["FAQ"])
    reviews = parse_reviews(manuscript["학부모후기"])
    path = f"/과목별학원/{category}/{slug}/"
    canonical = absolute(path)
    rep = pick_representative(rep_images, local, category)
    center_image = "/assets/centers/common/seoul6839.webp" if region == "서울" else "/assets/centers/common/local6839.webp"
    map_image = find_map(row)
    fee = fee_link(row)

    nearby: list[str] = []
    pools = [
        [r for r in ordered_rows if r.get("지역", "").strip() == region and r.get("시or구", "").strip() == district],
        [r for r in ordered_rows if r.get("지역", "").strip() == region],
        ordered_rows,
    ]
    for pool in pools:
        ranked = sorted(
            pool,
            key=lambda r: hashlib.sha256(f"{local}|{r['근처 수업가능 동네']}|nearby".encode()).hexdigest(),
        )
        for other in ranked:
            other_local = other["근처 수업가능 동네"].strip()
            if other_local != local and other_local not in nearby:
                nearby.append(other_local)
            if len(nearby) == 4:
                break
        if len(nearby) == 4:
            break

    related = [
        (f"{category} 전체 지역", f"/과목별학원/{category}/", "지역별 목록으로 돌아가기"),
        (f"{local} 지역 학원", f"/전국학원/중학생학원/{slug}/", "같은 동네 학습관리 확인"),
    ] + [(f"{name} {config['label']}", f"/과목별학원/{category}/{slug_local(name)}/", "가까운 지역 안내") for name in nearby]
    related = [item for item in related if (SITE / item[1].strip("/") / "index.html").exists() or item[1].startswith(f"/과목별학원/{category}/")]

    org_id = canonical + "#organization"
    page_id = canonical + "#webpage"
    article_id = canonical + "#article"
    service_id = canonical + "#service"
    faq_id = canonical + "#faq"
    breadcrumb_id = canonical + "#breadcrumb"
    school_items = [
        {"@type": "ListItem", "position": i + 1, "name": school}
        for i, school in enumerate(schools)
    ]
    offer = {
        "@type": "Offer",
        "url": canonical,
        "itemOffered": {
            "@type": "Service",
            "name": f"{title} 학습 상담",
            "serviceType": "TutoringService",
        },
    }
    org: dict = {
        "@type": ["EducationalOrganization", "LocalBusiness"],
        "@id": org_id,
        "name": center,
        "alternateName": [SITE_NAME, title],
        "url": canonical,
        "telephone": PHONE_DISPLAY,
        "image": [absolute(rep), absolute(center_image), absolute(map_image)],
        "address": {"@type": "PostalAddress", "streetAddress": address, "addressCountry": "KR"},
        "areaServed": [{"@type": "AdministrativeArea", "name": value} for value in (region, district, local) if value],
        "knowsAbout": [title, config["grade"], config["subject"], "내신 관리", "오답 재학습", "학습 플래너"],
        "makesOffer": [offer],
    }
    if reg_office or reg_number:
        org["identifier"] = " · ".join(x for x in (reg_office, reg_number) if x)

    graph = [
        {
            "@type": "WebPage", "@id": page_id, "url": canonical, "name": title,
            "description": description, "inLanguage": "ko-KR", "about": {"@id": org_id},
            "mentions": [config["grade"], config["subject"], local, *schools],
            "primaryImageOfPage": {"@type": "ImageObject", "url": absolute(rep)},
            "breadcrumb": {"@id": breadcrumb_id},
            "mainEntity": {"@id": article_id},
            "hasPart": [{"@id": article_id}, {"@id": service_id}, {"@id": faq_id}],
        },
        {"@type": "ImageObject", "@id": canonical + "#primaryimage", "url": absolute(rep), "caption": f"{title} {SITE_NAME} 대표"},
        {
            "@type": "BreadcrumbList", "@id": breadcrumb_id,
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "홈", "item": BASE_URL + "/"},
                {"@type": "ListItem", "position": 2, "name": "과목별학원", "item": absolute("/과목별학원/")},
                {"@type": "ListItem", "position": 3, "name": config["label"], "item": absolute(f"/과목별학원/{category}/")},
                {"@type": "ListItem", "position": 4, "name": title, "item": canonical},
            ],
        },
        org,
        {
            "@type": "Article", "@id": article_id, "mainEntityOfPage": {"@id": page_id},
            "headline": title, "name": title, "description": summary,
            "image": [absolute(rep), absolute(center_image), absolute(map_image)],
            "datePublished": PUBLISH_DATE, "dateModified": PUBLISH_DATE,
            "author": {"@id": org_id}, "publisher": {"@id": org_id}, "inLanguage": "ko-KR",
            "articleSection": [heading for heading, _ in body_sections],
            "about": [title, config["grade"], config["subject"], "학습 진단", "오답 관리"],
            "mentions": [local, district, region, *schools],
        },
        {
            "@type": "Service", "@id": service_id, "name": f"{title} 학습관리",
            "serviceType": "TutoringService", "provider": {"@id": org_id},
            "description": summary, "areaServed": {"@type": "Place", "name": local},
            "audience": {"@type": "EducationalAudience", "educationalRole": "student", "audienceType": config["grade"]},
            "about": [config["subject"], "내신 대비", "개념 점검"],
            "mentions": ["학습 플래너", "오답 재학습", *schools], "makesOffer": [offer],
        },
        {
            "@type": "FAQPage", "@id": faq_id,
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs],
        },
        {
            "@type": "ItemList", "@id": canonical + "#schools", "name": f"{local} 수업 가능 학교 참고",
            "numberOfItems": len(school_items), "itemListElement": school_items,
        },
        {
            "@type": "ItemList", "@id": canonical + "#related", "name": f"{local} 관련 학원 페이지",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": name, "url": absolute(url)} for i, (name, url, _) in enumerate(related)],
        },
    ]

    school_html = "".join(f"<li>{esc(school)}</li>" for school in schools) or "<li>상담 시 재학 학교와 진도를 확인합니다.</li>"
    fee_html = f'<a class="btn btn-ghost" href="{esc(fee)}" target="_blank" rel="noopener">센터 교습비 확인</a>' if fee else ""
    faq_html = "".join(f'<details class="faq-item"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faqs)
    review_html = "".join(f'<article class="review-card"><span class="review-label">상담 참고 사례 {i}</span><p>{esc(review)}</p></article>' for i, review in enumerate(reviews, 1))
    link_html = "".join(f'<a class="subject-related-link" href="{url}"><strong>{esc(name)}</strong><small>{esc(note)}</small></a>' for name, url, note in related)
    registration = " · ".join(x for x in (reg_office, reg_number) if x)

    body = f'''{nav("과목별학원")}
  <main>
    <section class="page-hero subject-local-hero">
      <p class="breadcrumb"><a href="/">홈</a><span>/</span><a href="/과목별학원/">과목별학원</a><span>/</span><a href="/과목별학원/{category}/">{esc(config['label'])}</a><span>/</span><span>{esc(title)}</span></p>
      <p class="eyebrow">LOCAL SUBJECT ACADEMY</p>
      <h1>{esc(title)}</h1>
      <p class="lead">{esc(description)}</p>
      <div class="hero-actions"><a class="btn btn-primary" href="tel:{PHONE_DISPLAY}">학습 상담하기</a>{fee_html}</div>
    </section>

    <section class="section subject-media-section" aria-label="{esc(title)} 이미지 안내">
      <img class="subject-hidden-representative" src="{esc(rep)}" alt="{esc(title)} {SITE_NAME} 대표" style="display:none;">
      <div class="media-row">
        <figure class="frame"><img src="{center_image}" alt="{esc(title)} {SITE_NAME} 본문" width="1200" height="900" fetchpriority="high"><figcaption>{esc(local)} 학습관리 안내</figcaption></figure>
        <figure class="frame"><img src="{map_image}" alt="{esc(title)} {SITE_NAME} 지도" width="1200" height="900" loading="lazy"><figcaption>{esc(center)} 위치 안내</figcaption></figure>
      </div>
    </section>

    <section class="section subject-answer-summary">
      <div class="section-head"><p class="eyebrow">핵심 답변</p><h2>{esc(title)}을 찾을 때 무엇부터 확인해야 할까요?</h2><p class="lead">{esc(description)}</p></div>
      <div class="subject-fact-grid">
        <article><span>대상</span><strong>{esc(config['grade'])}</strong><p>{esc(grade_range or '학생별 진도 확인 후 안내')}</p></article>
        <article><span>과목</span><strong>{esc(config['subject'])}</strong><p>개념·내신·오답 흐름 점검</p></article>
        <article><span>지역</span><strong>{esc(local)}</strong><p>{esc(' · '.join(x for x in (region, district) if x))}</p></article>
      </div>
    </section>

    <section class="section subject-manuscript">
      <div class="section-head"><p class="eyebrow">학습 안내</p><h2>{esc(title)} 학습 설계</h2></div>
      {body_html(intro, body_sections)}
    </section>

    <section class="section subject-center-card">
      <div class="section-head"><p class="eyebrow">센터 정보</p><h2>{esc(center)}</h2><p class="lead">제공된 센터 자료를 기준으로 정리했습니다.</p></div>
      <dl class="subject-center-facts">
        <div><dt>주소</dt><dd>{esc(address or '상담 시 안내')}</dd></div>
        <div><dt>위치 안내</dt><dd>{esc(location or '상담 시 상세 안내')}</dd></div>
        <div><dt>수업 가능 학교</dt><dd><ul>{school_html}</ul></dd></div>
        <div><dt>등록 정보</dt><dd>{esc(registration or '센터별 등록 정보는 상담 시 확인')}</dd></div>
      </dl>
      {fee_html}
    </section>

    <section class="section">
      <div class="section-head"><p class="eyebrow">FAQ</p><h2>{esc(title)} 자주 묻는 질문</h2><p class="lead">상담 전에 자주 확인하는 내용을 학년과 과목 기준으로 정리했습니다.</p></div>
      <div class="faq-list">{faq_html}</div>
    </section>

    <section class="section">
      <div class="section-head"><p class="eyebrow">상담 참고 사례</p><h2>{esc(local)} 학부모가 궁금해한 학습 상황</h2><p class="lead">아래 내용은 상담 상황을 이해하기 위한 참고 예시이며, 학생별 학습 과정과 결과는 다를 수 있습니다.</p></div>
      <div class="review-grid subject-review-grid">{review_html}</div>
    </section>

    <section class="section">
      <div class="section-head"><p class="eyebrow">내부 안내</p><h2>{esc(local)}에서 함께 확인할 페이지</h2></div>
      <div class="subject-related-grid">{link_html}</div>
    </section>
  </main>
{footer()}'''
    return shell(head_html(title, description, canonical, rep, graph), body)


def region_directory(rows: list[dict[str, str]], category: str, config: dict[str, str]) -> str:
    grouped: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[row.get("지역", "기타").strip() or "기타"][row.get("시or구", "기타").strip() or "기타"].append(row)
    jump = "".join(f'<a href="#region-{i}">{esc(region)}</a>' for i, region in enumerate(grouped))
    blocks = []
    for region_index, (region, districts) in enumerate(grouped.items()):
        district_html = []
        for district, district_rows in districts.items():
            links = "".join(
                f'<a href="/과목별학원/{category}/{slug_local(r["근처 수업가능 동네"])}/"><strong>{esc(r["근처 수업가능 동네"])}</strong><small>{esc(config["label"])}</small></a>'
                for r in district_rows
            )
            district_html.append(f'<section class="subject-district"><h3>{esc(district)} <small>{len(district_rows)}곳</small></h3><div class="subject-local-grid">{links}</div></section>')
        blocks.append(f'<section class="region-block" id="region-{region_index}"><div class="region-title"><h2>{esc(region)}</h2><span>{sum(len(v) for v in districts.values())}개 지역</span></div>{"".join(district_html)}</section>')
    return f'<nav class="region-jump" aria-label="광역 지역 바로가기">{jump}</nav>{"".join(blocks)}'


def category_page(rows: list[dict[str, str]], category: str, config: dict[str, str]) -> None:
    path = f"/과목별학원/{category}/"
    canonical = absolute(path)
    title = config["label"]
    description = f"전국 371개 동네의 {title} 학습 안내를 지역별로 정리했습니다. {config['grade']} {config['subject']} 진단, 내신 관리, 오답 재학습 기준을 확인할 수 있습니다."
    item_list = [
        {"@type": "ListItem", "position": i + 1, "name": f"{r['근처 수업가능 동네']} {title}", "url": absolute(f"{path}{slug_local(r['근처 수업가능 동네'])}/")}
        for i, r in enumerate(rows)
    ]
    graph = [
        {"@type": "CollectionPage", "@id": canonical + "#webpage", "url": canonical, "name": title, "description": description, "inLanguage": "ko-KR", "hasPart": {"@id": canonical + "#regions"}},
        {"@type": "BreadcrumbList", "@id": canonical + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "과목별학원", "item": absolute("/과목별학원/")},
            {"@type": "ListItem", "position": 3, "name": title, "item": canonical},
        ]},
        {"@type": "ItemList", "@id": canonical + "#regions", "name": f"{title} 지역 목록", "numberOfItems": len(item_list), "itemListElement": item_list},
    ]
    body = f'''{nav("과목별학원")}
  <main>
    <section class="page-hero">
      <p class="breadcrumb"><a href="/">홈</a><span>/</span><a href="/과목별학원/">과목별학원</a><span>/</span><span>{esc(title)}</span></p>
      <p class="eyebrow">SUBJECT ACADEMY DIRECTORY</p><h1>{esc(title)}</h1><p class="lead">{esc(description)}</p>
      <div class="subject-count"><strong>{len(rows)}</strong><span>지역별 학습 안내</span></div>
    </section>
    <section class="section subject-directory"><div class="section-head"><p class="eyebrow">지역 찾기</p><h2>광역 지역과 시·군·구 순서로 찾기</h2><p class="lead">먼저 광역 지역을 고른 뒤 시·군·구별 동네 버튼을 확인할 수 있습니다.</p></div>{region_directory(rows, category, config)}</section>
  </main>
{footer()}'''
    out = SITE / "과목별학원" / category / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(shell(head_html(title, description, canonical, "/assets/generated/coaching-center-hero-v2.png", graph), body), encoding="utf-8")


def subject_root() -> None:
    category_dirs = sorted(p for p in (SITE / "과목별학원").iterdir() if p.is_dir() and (p / "index.html").exists())
    categories = [p.name for p in category_dirs]
    cards = "".join(
        f'<a class="subject-category-card" href="/과목별학원/{name}/"><span>{i:02d}</span><strong>{esc(CONFIGS.get(name, {}).get("label", name))}</strong><small>371개 지역별 안내 보기</small></a>'
        for i, name in enumerate(categories, 1)
    )
    canonical = absolute("/과목별학원/")
    description = "학년과 과목 기준으로 지역별 학습 안내를 찾는 채움학습 과목별학원 허브입니다. 학생 상황에 맞는 진단·내신·오답 관리 정보를 확인하세요."
    graph = [
        {"@type": "CollectionPage", "@id": canonical + "#webpage", "url": canonical, "name": "과목별학원", "description": description, "inLanguage": "ko-KR", "hasPart": {"@id": canonical + "#categories"}},
        {"@type": "BreadcrumbList", "@id": canonical + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "과목별학원", "item": canonical},
        ]},
        {"@type": "ItemList", "@id": canonical + "#categories", "name": "과목별학원 카테고리", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": CONFIGS.get(name, {}).get("label", name), "url": absolute(f"/과목별학원/{name}/")}
            for i, name in enumerate(categories)
        ]},
    ]
    body = f'''{nav("과목별학원")}
  <main>
    <section class="page-hero"><p class="breadcrumb"><a href="/">홈</a><span>/</span><span>과목별학원</span></p><p class="eyebrow">SUBJECT ACADEMY HUB</p><h1>과목별학원</h1><p class="lead">{esc(description)}</p></section>
    <section class="section"><div class="section-head"><p class="eyebrow">학년·과목 선택</p><h2>필요한 학습 안내부터 확인하세요</h2><p class="lead">학년과 과목을 선택한 뒤, 광역 지역과 시·군·구 순서로 가까운 동네의 학습 안내를 찾을 수 있습니다.</p></div><div class="subject-category-grid">{cards}</div></section>
    <section class="section"><div class="section-head"><p class="eyebrow">채움학습 관리 기준</p><h2>과목 이름보다 학생이 막힌 지점을 먼저 봅니다</h2></div><div class="card-grid"><article class="info-card"><span class="tag">01</span><h3>현재 상태 진단</h3><p>최근 시험과 오답에서 개념, 계산, 적용 중 어디에서 흐름이 끊기는지 확인합니다.</p></article><article class="info-card"><span class="tag">02</span><h3>학년별 우선순위</h3><p>학교 진도와 시험 일정을 함께 보고 복습과 내신 준비의 순서를 정합니다.</p></article><article class="info-card"><span class="tag">03</span><h3>기록 기반 재학습</h3><p>틀린 이유와 다시 풀 시점을 기록해 같은 실수가 반복되지 않도록 관리합니다.</p></article></div></section>
  </main>
{footer()}'''
    out = SITE / "과목별학원" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(shell(head_html("과목별학원", description, canonical, "/assets/generated/coaching-center-hero-v2.png", graph), body), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", default="중1수학학원", choices=sorted(CONFIGS))
    args = parser.parse_args()
    category = args.category
    config = CONFIGS[category]
    zip_path = USED_DRAFTS / config["zip"]
    if not zip_path.exists():
        raise FileNotFoundError(zip_path)
    rows = load_centers()
    manuscripts = load_manuscripts(zip_path, config["label"])
    row_keys = {slug_local(row["근처 수업가능 동네"]): row for row in rows}
    missing_drafts = sorted(set(row_keys) - set(manuscripts))
    unknown_drafts = sorted(set(manuscripts) - set(row_keys))
    if missing_drafts or unknown_drafts:
        raise RuntimeError(f"센터/원고 불일치 missing={missing_drafts[:8]} unknown={unknown_drafts[:8]}")
    if len(rows) != 371 or len(manuscripts) != 371:
        raise RuntimeError(f"371개가 아닙니다: centers={len(rows)} drafts={len(manuscripts)}")
    reps = representative_images()
    category_page(rows, category, config)
    for row in rows:
        slug = slug_local(row["근처 수업가능 동네"])
        out = SITE / "과목별학원" / category / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(local_page(row, manuscripts[slug], config, category, reps, rows), encoding="utf-8")
    subject_root()
    print(f"generated category={category} local_pages={len(rows)} source={zip_path.name}")


if __name__ == "__main__":
    main()
