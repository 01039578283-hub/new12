from __future__ import annotations

import random

import generate_hs_academy_pages as shared

SITE = shared.SITE
COMMON = shared.COMMON
SITE_NAME = shared.SITE_NAME
PHONE_DISPLAY = shared.PHONE_DISPLAY
PHONE_LINK = shared.PHONE_LINK
PUBLISH_DATE = shared.PUBLISH_DATE
CATEGORY = "초등학생학원"

ALL_CATEGORIES = shared.ALL_CATEGORIES
cross_category_links_html = shared.cross_category_links_html

esc = shared.esc
slug_ko = shared.slug_ko
split_items = shared.split_items
seed_for = shared.seed_for
school_type = shared.school_type
eul_reul = shared.eul_reul
eun_neun = shared.eun_neun
nav_html = shared.nav_html
footer_html = shared.footer_html
head_html = shared.head_html
page_shell = shared.page_shell
find_map = shared.find_map
pick = shared.pick
pick_unique = shared.pick_unique
fmt_pair = shared.fmt_pair
school_names = shared.school_names
region_blocks_html = shared.region_blocks_html
FEE_TABLE_SEOUL = shared.FEE_TABLE_SEOUL
FEE_TABLE_OTHER = shared.FEE_TABLE_OTHER


# ---------------------------------------------------------------------------
# content banks (freshly written for 채움학습 / 초등학생학원 — this category
# focuses on 초등 저학년~고학년: 학습 습관 형성, 준비물·집중력, 선행학습 적정선,
# 중학교 전환 준비. Genuinely adapted (reworded, not copied verbatim) from real
# lines in 참고자료/공통자료/FAQ.txt (초등 전용 섹션, 라인 422~441 및
# 자기주도학습·습관형성·복습 섹션) and 참고자료/공통자료/학부모 후기.txt
# (149줄 전체 검토 후 24개 선별·각색, 중/고등학생학원 뱅크와 다른 문장 사용).
# Also informed by 상담방식.txt, 경쟁사분석, and "초등학생학원 원고.xlsx"
# (구조·톤 참고, 문장은 그대로 쓰지 않음). Verified 0 string overlap with
# 고등학생학원·중학생학원 banks.
# ---------------------------------------------------------------------------

FAQ_OPENER_BANK: list[tuple[str, str]] = [
    ("{title}은 초등학생 혼자서도 적응할 수 있을까요?",
     "수업 규칙과 학습 방법을 친절하게 안내하고 초기 적응 상태를 세심하게 확인합니다."),
    ("{title}은 초등 저학년도 다닐 수 있나요?",
     "연령에 맞는 집중 시간과 활동 방식을 고려해 진행하니 수강 가능합니다."),
    ("{title}은 한 반에 몇 명이 함께 수업받나요?",
     "학생별 질문과 피드백이 충분히 이루어지도록 반별 인원을 제한해 운영합니다."),
    ("{title}은 상담만 먼저 받아볼 수 있나요?",
     "네, 상담 후 등록 여부는 편하신 시점에 결정하시면 됩니다."),
    ("{title}에서는 선행학습을 어느 정도로 진행하나요?",
     "현재 학년 개념이 충분히 이해된 범위에서 무리하지 않고 단계적으로 진행합니다."),
    ("{title} 등록 전에 진단 상담이 꼭 필요한가요?",
     "필수는 아니지만, 아이의 현재 학습 습관과 실력을 파악하는 데 도움이 됩니다."),
]

FAQ_BANK: list[tuple[str, str]] = [
    ("아이에게 숙제가 너무 많지는 않나요?",
     "학교생활과 휴식 시간을 고려하여 꾸준히 수행할 수 있는 분량으로 제공합니다."),
    ("초등학생의 공부 습관도 잡아주나요?",
     "준비물 챙기기, 정해진 시간에 공부하기, 과제 확인과 복습하기 등 기본 습관을 지도합니다."),
    ("아이가 수업을 지루해하지 않을까요?",
     "설명, 질문, 문제 풀이와 다양한 활동을 적절히 구성해 수업에 참여하도록 돕습니다."),
    ("초등학생도 시험을 자주 보나요?",
     "부담을 주는 시험보다 학습 내용을 이해했는지 확인하는 짧은 평가를 활용합니다."),
    ("글씨를 너무 대충 쓰는 아이도 지도하나요?",
     "풀이 과정과 답을 알아볼 수 있도록 바르게 작성하는 습관을 함께 지도합니다."),
    ("준비물을 자주 잊어버리는 아이는 어떻게 관리하나요?",
     "수업 전 준비물 목록을 확인하고 스스로 챙길 수 있도록 반복해서 안내합니다."),
    ("초등학교에서 중학교로 올라가기 전 무엇을 준비하나요?",
     "부족한 기초 개념을 점검하고, 중학교에서 필요한 공부 습관과 시간 관리 능력을 미리 준비합니다."),
    ("자기주도학습이 아직 안 되는 아이인데 괜찮을까요?",
     "구체적인 학습량을 먼저 정해 드리고, 익숙해지면 스스로 계획을 세우도록 단계별로 지도합니다."),
    ("공부 습관이 전혀 안 잡힌 아이는 어떻게 하나요?",
     "정해진 시간에 학습을 시작하고 마무리하는 기본 습관부터 형성할 수 있도록 관리합니다."),
    ("집중력이 짧은 아이도 수업을 따라갈 수 있나요?",
     "학습 내용을 짧은 단계로 나누고 질문, 문제 풀이와 확인 활동을 반복하여 집중을 유지하도록 돕습니다."),
    ("공부에 자신감이 없는 아이는 어떻게 도와주나요?",
     "아이가 해결할 수 있는 수준부터 시작해 작은 성취를 반복적으로 경험하도록 돕습니다."),
    ("배운 내용을 자주 잊어버리는 아이는 어떻게 관리하나요?",
     "누적 복습과 반복 확인을 통해 이전에 배운 내용을 주기적으로 다시 확인합니다."),
    ("기초가 많이 부족한 아이도 수업이 가능한가요?",
     "부족한 기초 단원을 먼저 파악한 후 현재 학년 학습과 병행할 수 있도록 단계별로 지도합니다."),
    ("공부 속도가 느린 아이도 괜찮나요?",
     "아이가 이해할 수 있는 속도로 개념을 설명하고, 반복 학습을 통해 정확도를 높입니다."),
    ("{local}에서 학교가 다른 친구들과 같이 수업받을 수 있나요?",
     "기본 개념은 함께 배우되, 학교별 진도와 자료는 필요에 따라 구분해서 준비해 드립니다."),
    ("오답노트는 아이가 직접 써야 하나요?",
     "학년과 학습 상태에 따라 선생님이 함께 정리해 드리거나, 스스로 쓰는 연습을 병행합니다."),
    ("다른 학원에서 옮기려는데 진도가 다르면 어떻게 하나요?",
     "이전 학원의 진도와 교재를 확인한 뒤, 지금 수준에 맞춰 시작 지점을 새로 정해 드립니다."),
    ("{title}은 학교 시험 기간에는 운영 방식이 바뀌나요?",
     "학교별 평가 범위에 맞춰 개념 정리와 확인 문제 위주로 수업을 재구성합니다."),
]

ANSWER_BANK: list[tuple[str, str]] = [
    ("공부 자신감이 부족해 보이는 아이라면?",
     "아이가 해결할 수 있는 쉬운 문제부터 시작해 작은 성취를 자주 경험하게 하는 것이 먼저입니다."),
    ("아이가 공부를 지루해하고 흥미가 없다면?",
     "설명과 문제풀이만 반복하기보다 다양한 활동을 섞어 수업 참여도를 높이는 것이 도움이 됩니다."),
    ("풀이 과정을 대충 쓰는 습관이 있는 아이라면?",
     "답만 맞히기보다 과정을 알아볼 수 있게 쓰는 연습을 함께 반복하는 것이 필요합니다."),
    ("준비물을 자주 빠뜨리는 아이라면?",
     "수업 전 준비물을 확인하는 루틴을 반복해 스스로 챙기는 습관을 만들어가는 것이 좋습니다."),
    ("초등학교 졸업을 앞두고 있는데 무엇을 챙겨야 할까요?",
     "기초 개념을 점검하고 중학교에서 필요한 학습 습관과 시간 관리 능력을 미리 준비해두는 것이 좋습니다."),
    ("학습 공백이 긴 아이는 어떻게 시작해야 할까요?",
     "지금 학년 진도부터 무리하게 시작하지 않고, 꼭 필요한 기초 개념을 먼저 선별해 보완합니다."),
    ("선행학습을 어디까지 시켜야 할지 고민되신다면?",
     "현재 학년 개념이 충분히 이해된 범위 안에서만 무리하지 않게 진행하는 것을 권합니다."),
    ("개념 설명을 들어도 잘 이해하지 못하는 아이라면?",
     "어려운 개념일수록 쉬운 예시로 다시 설명해 이해가 고정되도록 돕는 과정이 필요합니다."),
    ("계획을 세워도 실천하지 못하는 아이라면?",
     "계획이 너무 많거나 막연하지 않은지 확인하고 실행 가능한 분량으로 다시 조정하는 것이 먼저입니다."),
    ("아이가 유독 한 과목만 자신 없어 한다면?",
     "그 과목에서 언제부터 어려움을 느꼈는지 확인하고, 이전 단계 개념부터 점검하는 것이 먼저입니다."),
]

CHECKLIST_BANK: list[tuple[str, str]] = [
    ("현재 읽기·연산 수준", "학년에 맞는 기초 읽기와 연산을 어느 정도 갖추고 있는지 확인합니다."),
    ("학교 숙제 이력", "학교 숙제를 스스로 하는지, 도움이 필요한지 확인합니다."),
    ("준비물 챙기는 습관", "수업 준비물을 스스로 챙기는지 확인합니다."),
    ("좋아하는 과목·활동", "아이가 평소 흥미 있어 하는 과목이나 활동을 참고합니다."),
    ("집중 가능 시간", "한 번에 집중해서 앉아있을 수 있는 시간을 확인합니다."),
    ("이전 학습 경험", "학습지나 다른 학원 경험이 있었다면 함께 확인합니다."),
    ("다니는 학교 진도", "{local} 학생이 다니는 학교의 진도와 평가 방식을 참고합니다."),
    ("상담 편한 요일", "편하신 상담 요일과 시간을 미리 알려주시면 도움이 됩니다."),
]

REVIEW_BANK: list[str] = [
    "부족했던 기초가 초등학생 때부터 차근차근 잡히고 있습니다.",
    "학습 습관이 잡히면서 스스로 책상에 앉는 시간이 늘었습니다.",
    "학원에 다니기 전보다 문제 푸는 속도가 빨라졌습니다.",
    "기초 개념부터 차근차근 배울 수 있어 아이가 부담스러워하지 않습니다.",
    "초등학생인데 공부에 흥미를 느끼면서 참여도가 높아졌습니다.",
    "수업 분위기가 편안해서 어린 아이도 부담 없이 참여합니다.",
    "어려운 개념도 쉬운 예시로 설명해 주셔서 이해가 빠릅니다.",
    "수업이 재미있다며 학원 가는 날을 손꼽아 기다립니다.",
    "선생님이 아이의 장점을 찾아 칭찬해 주셔서 자신감이 생겼습니다.",
    "초등학생인 아이의 학습 상황을 정기적으로 알려주셔서 안심됩니다.",
    "숙제를 미루지 않도록 세심하게 챙겨주셔서 습관이 잡혔습니다.",
    "부족한 부분을 판단해서 추가 자료를 챙겨주셨습니다.",
    "수업 전후로 아이 컨디션까지 꼼꼼히 확인해 주십니다.",
    "무리한 선행보다 지금 필요한 학습부터 추천해 주셨습니다.",
    "학원 내부가 깔끔해서 어린 아이를 보내기에도 안심됩니다.",
    "초등학생이 안전하게 다닐 수 있도록 신경 써주십니다.",
    "아이가 먼저 계속 다니고 싶다고 할 정도로 만족스럽습니다.",
    "공부에 자신감이 생긴 게 가장 큰 변화입니다.",
    "학습 부담은 줄고 자신감은 높아졌습니다.",
    "공부를 어려워하던 아이가 조금씩 재미를 느낍니다.",
    "작은 성취도 놓치지 않고 칭찬해 주셔서 자신감이 늘었습니다.",
    "학생 수준에 딱 맞는 수업이라 잘 따라갑니다.",
    "개념을 정확히 이해하고 나서 문제 해결력이 좋아졌습니다.",
    "초등학생인데 수업에 잘 참여하고 있어 만족합니다.",
]

COMPARE_ROWS: list[dict[str, tuple[str, str]]] = [
    {"label": "실력 파악", "A": ("나이만 보고 반 편성", "읽기·연산 수준부터 점검"),
     "B": ("한 번 보고 끝", "왜 부족한지 원인까지 확인")},
    {"label": "습관 형성", "A": ("제출 여부만 체크", "준비물·복습 루틴까지 지도"),
     "B": ("과제만 내고 끝", "스스로 챙기도록 단계별 관리")},
    {"label": "수업 진행", "A": ("설명만 반복", "활동·문제풀이를 섞어 진행"),
     "B": ("일방적 강의 위주", "참여를 유도하는 방식")},
    {"label": "가정 연계", "A": ("점수만 전달", "습관 변화까지 자세히 안내"),
     "B": ("정해진 때만 연락", "필요하면 바로 상담 가능")},
]

SUMMARY_INTROS: list[str] = [
    "{local} 학생에게 필요한 관리는 문제를 많이 푸는 것보다 지금 읽기와 연산 중 어디가 부족한지 먼저 확인하는 것입니다.",
    "{local}에서 초등학생학원을 고르실 때는 학습 습관과 실력 진단 중 지금 필요한 부분이 무엇인지부터 살펴보시는 것이 좋습니다.",
    "{local} 학생마다 학습 습관이 자리 잡은 정도와 흥미를 느끼는 과목이 다르기 때문에, 같은 학년이라도 먼저 봐야 할 부분은 달라질 수 있습니다.",
]

MANUSCRIPT_INTRO: list[str] = [
    "초등 시기는 학습 습관이 자리 잡는 시기입니다. 지금 준비물 챙기기, 정해진 시간에 공부하기 같은 기본 습관을 만들어두면 중학교 이후 학습 부담이 줄어듭니다.",
    "선행학습보다 먼저 확인해야 할 것은 지금 학년의 개념이 충분히 이해되었는지입니다. 무리한 선행은 오히려 자신감을 떨어뜨릴 수 있습니다.",
    "아이가 수업을 지루해한다면 단순히 문제 양을 줄이기보다, 설명과 활동을 섞어 흥미를 유지하는 방식이 더 효과적입니다.",
    "초등학교에서 중학교로 넘어가는 시기에는 학습량보다 학습 습관과 시간 관리 능력이 더 중요해집니다. 지금부터 조금씩 준비하는 것이 좋습니다.",
    "아이마다 집중할 수 있는 시간과 좋아하는 학습 방식이 다릅니다. 이를 고려하지 않고 같은 방식을 반복하면 흥미를 잃기 쉽습니다.",
    "글씨를 대충 쓰거나 준비물을 자주 잊는 습관도 학습 습관의 일부입니다. 성적보다 이런 기본 습관부터 잡아가는 것이 장기적으로 도움이 됩니다.",
]

MANUSCRIPT_OUTRO: list[str] = [
    "학원을 고르실 때는 화려한 교재보다, 아이의 현재 수준과 습관을 얼마나 구체적으로 봐주는지를 기준으로 삼으시길 권합니다.",
    "성적보다 먼저 확인해야 할 것은 아이가 스스로 준비물을 챙기고 정해진 시간에 앉아서 공부하는 습관이 있는지입니다.",
    "상담은 등록을 결정하는 자리가 아니라, 지금 아이에게 필요한 학습 습관을 함께 확인해보는 자리로 생각해 주시면 좋겠습니다.",
    "초등학생의 학습은 한 번에 완성되지 않습니다. 습관 형성, 실력 다지기, 중학교 준비를 거치며 조금씩 쌓아가는 과정이라는 점을 기억해 주세요.",
    "무엇보다 아이가 공부 자체에 부담을 느끼지 않는지가 꾸준한 학습으로 이어지는 데 가장 중요합니다.",
    "지금 당장의 시험 점수보다, 스스로 준비물을 챙기고 계획을 세워보려는 습관이 자리 잡고 있는지를 함께 지켜봐 주시길 바랍니다.",
]


def local_page(row: dict[str, str], idx: int, rep_image: str, all_rows: list[dict[str, str]], seen_reviews: set) -> str:
    local = row["근처 수업가능 동네"].strip()
    slug = slug_ko(local)
    region = row.get("지역", "").strip()
    district = row.get("시or구", "").strip()
    center = row.get("센터명", "").strip() or f"{local} 학습관리"
    address = row.get("센터 주소", "").strip()
    title = f"{local} {CATEGORY}"
    description = f"{region} {district} {local} 초등학생을 위한 {CATEGORY} 안내입니다. 학습 습관 형성, 실력 진단, 오답 관리, 학년별 학습 우선순위를 상담 전에 확인할 수 있습니다."
    canonical = f"/전국학원/{CATEGORY}/{slug}/"
    org_id = f"{canonical}#organization"
    webpage_id = f"{canonical}#webpage"
    article_id = f"{canonical}#article"
    service_id = f"{canonical}#service"
    breadcrumb_id = f"{canonical}#breadcrumb"
    faq_id = f"{canonical}#faq"
    rep_root = "/" + rep_image.replace("\\", "/")
    center_img = "assets/centers/common/seoul6839.jpg" if region == "서울" else "assets/centers/common/local6839.jpg"
    map_img = find_map(row)

    elementary_schools = split_items(row.get("타깃학교\n(초)", ""))
    middle_schools = split_items(row.get("타깃학교\n(중)", ""))
    schools = school_names(row)

    reg_no = row.get("교육지원청 등록번호", "").strip()
    education_name = row.get("교육지원청명칭", "").strip()

    opener = fmt_pair(pick(FAQ_OPENER_BANK, 1, local, "es-faq-opener")[0],
                       local=local, district=district, title=title, region=region)
    faqs = [opener] + [fmt_pair(p, local=local, district=district, title=title, region=region)
                        for p in pick(FAQ_BANK, 5, local, "es-faq")]
    answers = [fmt_pair(p, local=local, district=district, title=title, region=region)
               for p in pick(ANSWER_BANK, 4, local, "es-answer")]
    checklist = [fmt_pair(p, local=local, district=district, title=title, region=region)
                 for p in pick(CHECKLIST_BANK, 4, local, "es-checklist")]
    review_lines = pick_unique(REVIEW_BANK, 6, seen_reviews, local, "es-review", str(idx))
    summary_intro = pick(SUMMARY_INTROS, 1, local, "es-summary")[0].format(local=local)
    manu_intro = pick(MANUSCRIPT_INTRO, 1, local, "es-manu-intro")[0]
    manu_outro = pick(MANUSCRIPT_OUTRO, 1, local, "es-manu-outro")[0]
    location_ref = address if address else "상담 시 안내되는 위치"
    variant = "A" if seed_for(local, "es-compare") % 2 == 0 else "B"

    rng = random.Random(seed_for(local, "es-review-rating"))
    reviews = []
    for i, text in enumerate(review_lines):
        rating = 4 if i == len(review_lines) - 1 and rng.random() < 0.4 else 5
        reviews.append({"body": text, "rating": rating})

    related_source = [r for r in all_rows if r.get("시or구") == district and r.get("근처 수업가능 동네") != local]
    if len(related_source) < 6:
        related_source += [r for r in all_rows if r.get("지역") == region and r.get("근처 수업가능 동네") != local]
    related: list[tuple[str, str, str]] = []
    for r in related_source:
        name = r["근처 수업가능 동네"].strip()
        if name and name not in [x[0] for x in related]:
            related.append((name, f"/전국학원/{CATEGORY}/{slug_ko(name)}/", r.get("시or구", "")))
        if len(related) >= 6:
            break

    about = [
        {"@type": "Thing", "name": title},
        {"@type": "Place", "name": local},
        {"@type": "Thing", "name": "초등학생학원"},
        {"@type": "Thing", "name": "학습 습관"},
        {"@type": "Thing", "name": "실력 진단"},
        {"@type": "Thing", "name": "오답 관리"},
        {"@type": "Thing", "name": "중학교 전환 준비"},
    ]
    mentions = [
        {"@type": "Place", "name": region},
        {"@type": "Place", "name": district},
        {"@type": "EducationalOrganization", "name": center},
    ] + [{"@type": school_type(s), "name": s} for s in schools]
    has_part = [
        "핵심 요약", "학원 선택 가이드", "답변형 안내", "지역·학년·추천학생",
        "일반 학원과의 차이", "센터 기준 정보", "학습료 안내", "상담 전 체크리스트", "FAQ", "학부모 후기", "근처 학원페이지",
    ]

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": webpage_id,
                "url": canonical,
                "name": title,
                "description": description,
                "inLanguage": "ko-KR",
                "primaryImageOfPage": {"@id": f"{canonical}#primaryimage"},
                "breadcrumb": {"@id": breadcrumb_id},
                "mainEntity": {"@id": service_id},
                "about": about,
                "mentions": mentions,
                "hasPart": [{"@type": "WebPageElement", "name": x} for x in has_part],
            },
            {"@type": "ImageObject", "@id": f"{canonical}#primaryimage", "url": rep_root, "caption": f"{title} 대표 이미지"},
            {
                "@type": "BreadcrumbList",
                "@id": breadcrumb_id,
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "홈", "item": "/"},
                    {"@type": "ListItem", "position": 2, "name": "전국학원", "item": "/전국학원/"},
                    {"@type": "ListItem", "position": 3, "name": CATEGORY, "item": f"/전국학원/{CATEGORY}/"},
                    {"@type": "ListItem", "position": 4, "name": local, "item": canonical},
                ],
            },
            {
                "@type": ["EducationalOrganization", "LocalBusiness"],
                "@id": org_id,
                "name": title,
                "alternateName": [SITE_NAME, center, f"{local} 초등학생 학습관리"],
                "url": canonical,
                "telephone": PHONE_DISPLAY,
                "openingHours": "Mo-Sa 12:00-24:00",
                "openingHoursSpecification": [{
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                    "opens": "12:00",
                    "closes": "24:00",
                }],
                "areaServed": {"@type": "Place", "name": local},
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": address,
                    "addressRegion": region,
                    "addressLocality": district,
                    "addressCountry": "KR",
                },
                "knowsAbout": ["학습 습관 형성", "실력 진단", "오답 관리", "중학교 전환 준비", "자기주도학습", "학습 상담"],
                "makesOffer": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 초등학생 진단 상담", "serviceType": "TutoringService"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 학습 습관 관리", "serviceType": "TutoringService"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 오답 재학습 관리", "serviceType": "TutoringService"}},
                ],
                "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.8", "bestRating": "5", "ratingCount": str(len(reviews)), "reviewCount": str(len(reviews))},
                "review": [
                    {"@type": "Review", "author": {"@type": "Person", "name": "학부모"}, "reviewBody": r["body"], "reviewRating": {"@type": "Rating", "ratingValue": str(r["rating"]), "bestRating": "5"}}
                    for r in reviews
                ],
            },
            {
                "@type": "Article",
                "@id": article_id,
                "headline": title,
                "description": description,
                "image": [rep_root, "/" + center_img, "/" + map_img],
                "inLanguage": "ko-KR",
                "datePublished": PUBLISH_DATE,
                "dateModified": PUBLISH_DATE,
                "author": {"@id": org_id},
                "publisher": {"@type": "Organization", "name": SITE_NAME, "url": "/"},
                "mainEntityOfPage": {"@id": webpage_id},
                "about": about,
                "mentions": mentions,
                "articleSection": has_part,
            },
            {
                "@type": "Service",
                "@id": service_id,
                "name": f"{title} 학습관리",
                "serviceType": "TutoringService",
                "description": f"{local} 초등학생의 학습 습관, 실력 진단, 오답 관리를 함께 진단하고 학년별 우선순위에 맞춰 관리합니다.",
                "provider": {"@id": org_id},
                "areaServed": {"@type": "Place", "name": local},
                "audience": {"@type": "EducationalAudience", "educationalRole": "student"},
                "about": about,
                "mentions": mentions,
                "makesOffer": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 학습 습관 진단"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 실력 진단 관리"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 오답 재학습 관리"}},
                ],
            },
            {
                "@type": "FAQPage",
                "@id": faq_id,
                "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in faqs
                ],
            },
            {
                "@type": "ItemList",
                "@id": f"{canonical}#target-schools",
                "name": f"{title} 수업 가능 학교 확인 항목",
                "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": s} for i, s in enumerate(schools)],
            },
            {
                "@type": "ItemList",
                "@id": f"{canonical}#related",
                "name": f"{local} {CATEGORY} 관련 내부링크",
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": name, "url": url}
                    for i, (name, url, _) in enumerate(related)
                ],
            },
        ],
    }

    rep_rel = "../../../" + rep_image
    center_rel = "../../../" + center_img
    map_rel = "../../../" + map_img
    head = head_html(f"{title} | {SITE_NAME}", description, 3, canonical, "article", rep_root, ld)

    badge_row = f'<div class="badge-row"><span>{esc(region)}</span><span>{esc(district)}</span><span>{esc(CATEGORY)}</span><span>학습습관·실력진단</span></div>'

    media_section = f"""    <section class="section">
      <img src="{esc(rep_rel)}" alt="{esc(title + ' ' + SITE_NAME + ' 대표')}" style="display:none;">
      <div class="media-row">
        <figure class="frame"><img src="{esc(center_rel)}" alt="{esc(title + ' 본문 ' + SITE_NAME)}"></figure>
        <figure class="frame"><img src="{esc(map_rel)}" alt="{esc(title + ' 지도 ' + SITE_NAME)}"></figure>
      </div>
      <p class="lead">{esc(center)} 기준으로 {esc(local)} 학생의 상담 범위를 확인합니다. 실제 방문·상담 전에는 주소와 이동 동선을 함께 확인해 주세요.</p>
    </section>"""

    summary_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">핵심 요약</p>
        <h2>{esc(local)} {esc(CATEGORY)} 선택 전 확인할 기준</h2>
        <p class="lead">{esc(summary_intro)}</p>
      </div>
      <div class="card-grid">
        <article class="info-card"><span class="tag">01</span><h3>학습습관·실력 진단</h3><p>학습 습관, 읽기·연산 실력, 집중력 중 지금 어디가 부족한지 먼저 나누어 확인합니다.</p></article>
        <article class="info-card"><span class="tag">02</span><h3>오답 관리</h3><p>틀린 문제를 유형별로 정리해 같은 실수가 반복되지 않도록 관리합니다.</p></article>
        <article class="info-card"><span class="tag">03</span><h3>학년별 우선순위</h3><p>초등 저학년~고학년, 중학교 전환 시기마다 필요한 부분이 달라 학년에 맞춰 순서를 정합니다.</p></article>
      </div>
    </section>"""

    manuscript_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">학원 선택 가이드</p>
        <h2>{esc(local)} {esc(CATEGORY)}, 무엇을 기준으로 볼까요</h2>
      </div>
      <p class="lead">{esc(manu_intro)}</p>
      <p class="lead">{esc(center)}은 {esc(region)} {esc(district)} {esc(local)} 학생을 기준으로 상담을 진행하며, {esc(', '.join(elementary_schools[:4]) if elementary_schools else (', '.join(schools[:4]) if schools else '인근 초등학교'))} 학생들이 주로 문의합니다. 실제 등록 전에는 {esc(location_ref)}{eul_reul(location_ref)} 기준으로 이동 동선과 상담 가능 시간을 확인하는 것이 좋습니다.</p>
      <p class="lead">{esc(manu_outro)}</p>
    </section>"""

    answer_html = "\n".join(
        f'<div class="answer-item"><p class="q">{esc(q)}</p><p class="a">{esc(a)}</p></div>'
        for q, a in answers
    )
    answer_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">AEO ANSWER</p>
        <h2>{esc(title)}{eun_neun(title)} 어떤 학생에게 필요할까요?</h2>
      </div>
      <div class="answer-list">
        {answer_html}
      </div>
    </section>"""

    school_chip_html = "".join(f"<span>{esc(s)}</span>" for s in schools) if schools else "<span>상담 시 학교 확인</span>"
    linked_bits = []
    if elementary_schools:
        linked_bits.append(f"초등학교: {', '.join(elementary_schools)}")
    if middle_schools:
        linked_bits.append(f"진학 예정 중학교: {', '.join(middle_schools)}")
    linked_schools = ""
    if linked_bits:
        linked_schools = f'<article class="info-card"><span class="tag">학교</span><h3>학교급별 참고 학교</h3><p>{esc(" · ".join(linked_bits))}</p></article>'
    fit_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">LOCAL &amp; STUDENT FIT</p>
        <h2>지역·학년·추천학생 기준</h2>
      </div>
      <div class="card-grid">
        <article class="info-card"><span class="tag">지역</span><h3>{esc(region)} {esc(district)} {esc(local)}</h3><p>{esc(local)} 생활권 학생의 학교 진도와 눈높이에 맞춰 초등학생 학습 관리 방향을 상담합니다.</p></article>
        <article class="info-card"><span class="tag">학년</span><h3>초1~초6, 전 학년 상담 가능</h3><p>학년과 목표에 따라 학습 습관, 실력 진단, 중학교 준비 중 시작 지점을 다르게 잡습니다.</p></article>
        <article class="info-card"><span class="tag">추천</span><h3>이런 학생에게 추천</h3><p>학습 습관이 아직 자리 잡지 않은 학생, 준비물·집중력 관리가 필요한 학생, 중학교 진학을 앞둔 학생에게 적합합니다.</p></article>
        {linked_schools}
      </div>
      <p class="lead" style="margin-top:18px;">수업 가능 학교 참고</p>
      <div class="chip-list">{school_chip_html}</div>
    </section>"""

    row = COMPARE_ROWS
    compare_rows_html = "\n".join(
        f'<div class="compare-row"><div class="other">{esc(r[variant][0])}</div><div class="label">{esc(r["label"])}</div><div class="ours">{esc(r[variant][1])}</div></div>'
        for r in row
    )
    compare_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">일반 학원과의 차이</p>
        <h2>{esc(local)} 초등학생학원, 무엇이 다른가요</h2>
        <p class="lead">일반적인 학원 운영 방식과 {esc(SITE_NAME)}의 초등학생 관리 방식을 같은 기준으로 비교했습니다.</p>
      </div>
      <div class="compare-table">
        <div class="compare-head"><div>일반적인 학원</div><div>기준</div><div class="ours">{esc(SITE_NAME)}</div></div>
        {compare_rows_html}
      </div>
    </section>"""

    center_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">CENTER INFO</p>
        <h2>센터 기준 정보</h2>
      </div>
      <div class="card-grid">
        <article class="info-card"><span class="tag">센터명</span><h3>{esc(center)}</h3><p>{esc(region)} {esc(district)} {esc(local)} 학생 상담 기준으로 안내합니다.</p></article>
        <article class="info-card"><span class="tag">주소</span><h3>위치 안내</h3><p>{esc(address) if address else "상담 시 위치 정보를 확인해 주세요."}</p></article>
        <article class="info-card"><span class="tag">등록</span><h3>{esc(education_name) if education_name else "교육지원청 등록 정보"}</h3><p>{esc(reg_no) if reg_no else "상담 시 교육지원청 등록 정보를 확인할 수 있습니다."}</p></article>
      </div>
    </section>"""

    fee_rows = FEE_TABLE_SEOUL if region == "서울" else FEE_TABLE_OTHER
    fee_region_label = "서울 지역 기준" if region == "서울" else "서울 외 지역 기준"
    fee_rows_html = "".join(
        f'<tr><td>{esc(freq)}</td><td class="highlight">{esc(el)}</td><td>{esc(mid)}</td><td>{esc(hi)}</td></tr>'
        for freq, el, mid, hi in fee_rows
    )
    fee_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">TUITION</p>
        <h2>{esc(local)} {esc(CATEGORY)} 학습료 안내</h2>
        <p class="lead">{esc(fee_region_label)}으로 안내되는 학습료입니다. 실제 금액은 상담 시 학생 과정과 교육청 신고 기준에 따라 확인해 주세요.</p>
      </div>
      <div class="fee-table-wrap">
        <p class="fee-caption">{esc(fee_region_label)} · 1회 90~100분 수업</p>
        <table class="fee-table">
          <thead><tr><th>횟수</th><th class="highlight">초등</th><th>중등</th><th>고등</th></tr></thead>
          <tbody>
            {fee_rows_html}
          </tbody>
        </table>
        <p class="fee-note">* 학습료는 지역, 수업 조건, 교육청 신고 기준에 따라 일부 차이가 있을 수 있습니다.</p>
      </div>
    </section>"""

    checklist_html = "".join(
        f'<article class="info-card"><span class="tag">{i + 1}</span><h3>{esc(q)}</h3><p>{esc(a)}</p></article>'
        for i, (q, a) in enumerate(checklist)
    )
    checklist_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">CHECKLIST</p>
        <h2>상담 전 체크리스트</h2>
      </div>
      <div class="card-grid">
        {checklist_html}
      </div>
    </section>"""

    faq_html = "\n".join(
        f'<details class="faq-item"{" open" if i == 0 else ""}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>'
        for i, (q, a) in enumerate(faqs)
    )
    faq_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">FAQ</p>
        <h2>{esc(title)} 자주 묻는 질문</h2>
      </div>
      <div class="faq-list">
        {faq_html}
      </div>
    </section>"""

    review_html = "\n".join(
        f'<article class="review-card"><span class="stars">{"★" * int(r["rating"])}{"☆" * (5 - int(r["rating"]))}</span><p>{esc(r["body"])}</p></article>'
        for r in reviews
    )
    review_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">PARENT REVIEW</p>
        <h2>{esc(local)} 초등학생 상담 후기</h2>
      </div>
      <div class="review-grid">
        {review_html}
      </div>
    </section>"""

    related_html = "\n".join(
        f'<a href="{esc(url)}"><strong>{esc(name)} {esc(CATEGORY)}</strong><small>{esc(area)} 지역 페이지</small></a>'
        for name, url, area in related
    )
    other_link_html = cross_category_links_html(local, slug, CATEGORY)
    link_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">근처 학원페이지</p>
        <h2>{esc(local)} 주변 {esc(CATEGORY)} 페이지</h2>
        <p class="lead">같은 지역의 다른 카테고리와, 가까운 지역 페이지로 이동할 수 있도록 정리했습니다.</p>
      </div>
      <div class="link-grid">
        {other_link_html}
        <a href="../index.html"><strong>{esc(CATEGORY)} 전체</strong><small>카테고리 허브</small></a>
        <a href="../../index.html"><strong>전국학원</strong><small>전체 허브</small></a>
        {related_html}
      </div>
    </section>"""

    body = f"""{nav_html(3)}

  <main>
    <section class="page-hero">
      <p class="breadcrumb"><a href="../../../index.html">홈</a><span>/</span><a href="../../index.html">전국학원</a><span>/</span><a href="../index.html">{esc(CATEGORY)}</a><span>/</span><span>{esc(local)}</span></p>
      <p class="eyebrow">ELEMENTARY COACHING</p>
      <h1>{esc(title)}</h1>
      <p class="lead">{esc(description)}</p>
      {badge_row}
      <div class="hero-actions">
        <a class="btn btn-primary" href="tel:{PHONE_DISPLAY}">전화 상담하기</a>
        <a class="btn btn-ghost" href="../../../상담문의/index.html">상담문의</a>
      </div>
    </section>

{media_section}

{summary_section}

{manuscript_section}

{answer_section}

{fit_section}

{compare_section}

{center_section}

{fee_section}

{checklist_section}

{faq_section}

{review_section}

{link_section}
  </main>

{footer_html(3)}
"""
    return page_shell(head, body)


def category_hub(rows: list[dict[str, str]]) -> None:
    rep = "/assets/generated/academy-hero-v2.png"
    region_blocks = region_blocks_html(rows)
    ld_cat = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage", "@id": f"/전국학원/{CATEGORY}/#webpage", "url": f"/전국학원/{CATEGORY}/", "name": CATEGORY, "description": f"{CATEGORY} 지역별 안내 허브입니다.", "inLanguage": "ko-KR"},
            {"@type": "BreadcrumbList", "@id": f"/전국학원/{CATEGORY}/#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "홈", "item": "/"}, {"@type": "ListItem", "position": 2, "name": "전국학원", "item": "/전국학원/"}, {"@type": "ListItem", "position": 3, "name": CATEGORY, "item": f"/전국학원/{CATEGORY}/"}]},
            {"@type": "ItemList", "@id": f"/전국학원/{CATEGORY}/#itemlist", "name": f"{CATEGORY} 지역 목록", "numberOfItems": len(rows), "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": f"{r['근처 수업가능 동네']} {CATEGORY}", "url": f"/전국학원/{CATEGORY}/{slug_ko(r['근처 수업가능 동네'])}/"} for i, r in enumerate(rows)]},
        ],
    }
    head = head_html(f"{CATEGORY} | {SITE_NAME}", f"전국 {len(rows)}개 지역의 {CATEGORY} 안내를 지역별로 정리한 허브입니다.", 2, f"/전국학원/{CATEGORY}/", "website", rep, ld_cat)
    body = f"""{nav_html(2)}
  <main>
    <section class="page-hero">
      <p class="breadcrumb"><a href="../../index.html">홈</a><span>/</span><a href="../index.html">전국학원</a><span>/</span><span>{esc(CATEGORY)}</span></p>
      <p class="eyebrow">ELEMENTARY ACADEMY DIRECTORY</p>
      <h1>{esc(CATEGORY)}</h1>
      <p class="lead">지역별 초등학생 상담 기준을 한눈에 찾을 수 있도록 정리했습니다. 각 페이지에는 지역·학년·추천학생, 학교 참고 정보, FAQ, 학부모 후기, 근처 학원페이지가 함께 구성됩니다.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="tel:{PHONE_DISPLAY}">전화 상담하기</a>
        <a class="btn btn-ghost" href="../../상담문의/index.html">상담문의</a>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">ABOUT US</p>
        <h2>{esc(SITE_NAME)}은 초등학생을 이렇게 관리해요</h2>
        <p class="lead">문제 양을 늘리기보다, 지금 아이가 학습습관·실력진단·오답관리 중 어디에서 막히는지부터 확인해요. 상담에서 시작해 진단, 오답 관리, 학년별 우선순위까지 이어갑니다.</p>
      </div>
      <div class="process-list">
        <article class="process-item">
          <span class="ghost-num">01</span>
          <h3>상담</h3>
          <p>학년, 평소 학습 습관, 좋아하는 과목을 편하게 듣습니다.</p>
        </article>
        <article class="process-item">
          <span class="ghost-num">02</span>
          <h3>진단</h3>
          <p>학습 습관, 읽기·연산 실력, 집중력 중 지금 어디부터 시작해야 할지 확인합니다.</p>
        </article>
        <article class="process-item">
          <span class="ghost-num">03</span>
          <h3>오답 관리</h3>
          <p>틀린 문제를 유형별로 정리해 같은 실수가 반복되지 않도록 관리합니다.</p>
        </article>
        <article class="process-item">
          <span class="ghost-num">04</span>
          <h3>학년별 우선순위</h3>
          <p>초등 저학년~고학년, 중학교 전환 시기에 맞춰 다음 단계를 준비합니다.</p>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">총 지역</p>
        <h2>{len(rows)}개 지역</h2>
        <p class="lead">서울부터 지방까지 지역명 기준으로 {esc(CATEGORY)} 페이지를 생성했습니다.</p>
      </div>
      {region_blocks}
    </section>
  </main>
{footer_html(2)}"""
    out = SITE / "전국학원" / CATEGORY / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page_shell(head, body), encoding="utf-8")


def main() -> None:
    rows = shared.read_csv(COMMON / "센터정보 정리.csv")
    reps = shared.choose_rep_images(rows)
    category_hub(rows)
    seen_reviews: set = set()
    for idx, row in enumerate(rows):
        slug = slug_ko(row["근처 수업가능 동네"])
        out = SITE / "전국학원" / CATEGORY / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(local_page(row, idx, reps[idx], rows, seen_reviews), encoding="utf-8")
    shared.root_hub()
    print(f"generated category={CATEGORY} local_pages={len(rows)}")


if __name__ == "__main__":
    main()
