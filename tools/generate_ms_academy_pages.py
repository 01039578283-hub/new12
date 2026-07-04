from __future__ import annotations

import random

import generate_hs_academy_pages as shared

SITE = shared.SITE
COMMON = shared.COMMON
SITE_NAME = shared.SITE_NAME
PHONE_DISPLAY = shared.PHONE_DISPLAY
PHONE_LINK = shared.PHONE_LINK
PUBLISH_DATE = shared.PUBLISH_DATE
CATEGORY = "중학생학원"

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
# content banks (freshly written for 채움학습 / 중학생학원 — this category
# focuses on 중1~중3: 자유학기제, 내신 대비, 초→중 전환, 중→고 전환, 진로,
# 자기주도학습, 오답관리. Genuinely adapted (reworded, not copied verbatim)
# from real lines in 참고자료/공통자료/FAQ.txt (특히 초/중/고 전환 섹션,
# 라인 440~461 및 자기주도학습·오답관리·숙제 섹션) and
# 참고자료/공통자료/학부모 후기.txt (149줄 전체 검토 후 24개 선별·각색).
# Also informed by 상담방식.txt, 경쟁사분석, and "중학생학원 원고.xlsx"
# (구조·톤 참고, 문장은 그대로 쓰지 않음).
# ---------------------------------------------------------------------------

FAQ_OPENER_BANK: list[tuple[str, str]] = [
    ("{title}은 상담을 어떻게 신청하나요?",
     "전화나 문자로 편하게 신청하실 수 있으며, 가능한 상담 시간을 확인한 뒤 개별로 안내해 드립니다."),
    ("{title}은 초등학교 졸업 전부터 상담받을 수 있나요?",
     "네, 중학교 진학 전 기초 개념과 학습 습관을 미리 점검하는 상담도 가능합니다."),
    ("{title}은 소수정예로 운영되나요?",
     "학생별 질문과 피드백이 충분히 이루어질 수 있도록 반별 인원을 제한해 운영합니다."),
    ("{title}은 등록 전에 미리 둘러볼 수 있나요?",
     "사전 예약 후 상담실과 강의실 등 시설을 둘러보실 수 있습니다."),
    ("{title}에서는 선행학습도 가능한가요?",
     "현재 학년 개념이 충분히 정리된 경우에 한해 단계적으로 진행합니다."),
    ("{title} 등록 전에 레벨테스트가 꼭 필요한가요?",
     "필수는 아니지만, 학생의 현재 실력과 학습 공백을 파악하기 위해 진행하는 것을 권해드립니다."),
]

FAQ_BANK: list[tuple[str, str]] = [
    ("중학교 입학 전에 무엇을 준비해야 하나요?",
     "기초 개념을 점검하고 중학교 학습에 필요한 공부 습관, 문제 풀이와 시간 관리 능력을 준비합니다."),
    ("중학교 내신 대비는 어떻게 진행하나요?",
     "교과서, 학교 프린트, 시험 범위와 출제 경향을 바탕으로 학교별 대비를 진행합니다."),
    ("자유학기제 기간에도 학습관리가 필요한가요?",
     "시험 부담이 적은 이 시기를 활용해 기초를 보완하고 자기주도학습 습관을 형성할 수 있습니다."),
    ("아이가 갑자기 공부를 거부하면 어떻게 하나요?",
     "학습량, 난이도, 관계와 성적 부담 등 원인을 확인하고 실행 가능한 목표부터 다시 설정합니다."),
    ("중학교 첫 시험은 언제부터 준비해야 하나요?",
     "시험 직전에 몰아서 공부하기보다 평소 진도와 복습을 유지하며 범위가 확정되면 집중적으로 대비합니다."),
    ("중학생도 진로 상담을 받을 수 있나요?",
     "학생의 관심 분야와 학습 상황을 바탕으로 과목별 목표와 진로 탐색 방향을 안내합니다."),
    ("아이의 스마트폰 사용도 관리해 주시나요?",
     "수업과 자습 중에는 사용을 제한하고 학습에 방해되지 않는 사용 습관을 지도합니다."),
    ("서술형이 약한 학생은 어떻게 지도하나요?",
     "교과서 핵심 표현과 풀이 과정을 정확히 쓰는 연습을 반복합니다."),
    ("특정 과목만 유난히 어려워하면 어떻게 하나요?",
     "이전 학년의 기초부터 점검하고 현재 학교 진도와 연결되는 필수 내용을 우선 보완합니다."),
    ("고등학교 진학 준비는 언제부터 시작하나요?",
     "중학교 성적과 학습 성향을 확인하면서 학교 선택과 고등 학습 준비를 단계적으로 진행합니다."),
    ("중학생에게 고등 과정 선행이 꼭 필요한가요?",
     "학생의 기초와 학습 여건에 따라 다르며, 무리한 선행보다 현재 과정의 완성도를 먼저 확인합니다."),
    ("혼자서는 계획을 못 세우는 학생인데 괜찮을까요?",
     "처음에는 구체적인 학습량과 방법을 제시하고, 익숙해지면 학생이 스스로 계획을 세우도록 단계적으로 지도합니다."),
    ("{local}에서 다니는 학교가 다른 친구들과 같은 반에서 배우나요?",
     "기본 개념은 함께 배우되, 학교별 시험 범위에 맞춰 자료는 따로 준비해 드립니다."),
    ("오답노트는 따로 준비해야 하나요?",
     "학년과 학습 상태에 따라 별도 노트나 교재 내 오답 표시 방식을 활용합니다."),
    ("숙제량이 많은 편인가요?",
     "학생이 무리하지 않으면서도 학습 효과를 얻을 수 있도록 수준과 일정에 따라 과제량을 조절합니다."),
    ("성적이 계속 오르지 않으면 어떻게 하나요?",
     "개념 부족, 문제 해석, 시간 관리 또는 실수 등 원인을 분석하여 학습 방법을 조정합니다."),
    ("다른 학원에서 옮기려는데 바로 등록할 수 있나요?",
     "이전 학원의 진도와 학습자료를 확인한 후 현재 수준에 맞는 반과 학습계획을 안내해 드립니다."),
    ("{title}은 시험 기간에 수업이 어떻게 달라지나요?",
     "학교별 시험 범위에 맞춰 개념 정리, 예상 문제, 서술형 연습과 실전 테스트를 진행합니다."),
]

ANSWER_BANK: list[tuple[str, str]] = [
    ("중학생 아이가 특정 과목만 유독 어려워한다면?",
     "이전 학년의 기초부터 점검하고, 지금 학교 진도와 연결되는 필수 개념을 먼저 보완하는 것이 순서입니다."),
    ("갑자기 공부 자체를 거부하는 중학생이라면?",
     "학습량이나 난이도, 관계, 성적 부담 중 어떤 것이 원인인지 먼저 확인하고 실행 가능한 목표부터 다시 잡습니다."),
    ("성적이 갑자기 떨어졌다면 무엇부터 확인해야 할까요?",
     "최근 학습량과 시험지를 함께 살펴보고, 취약 단원을 우선적으로 보완하는 계획부터 세웁니다."),
    ("자유학기제 기간을 어떻게 활용하면 좋을까요?",
     "시험 부담이 적은 시기이므로 기초를 보완하고 자기주도학습 습관을 만드는 데 활용하는 것이 좋습니다."),
    ("초등학교 졸업을 앞두고 무엇이 걱정되시나요?",
     "기초 개념 점검과 함께 중학교에서 필요한 학습 습관, 시간 관리 능력을 미리 준비하면 도움이 됩니다."),
    ("중학생인데 벌써 고등학교 준비를 해야 할지 고민되신다면?",
     "무리한 선행보다 지금 과정의 완성도를 먼저 확인하고, 필요한 만큼만 단계적으로 준비하는 것을 권합니다."),
    ("공부에 자신감이 없어 보이는 아이라면?",
     "학생이 해결할 수 있는 수준부터 시작해 작은 성취를 반복 경험하도록 돕는 것이 먼저입니다."),
    ("계획을 세워도 지키지 않는 아이라면?",
     "계획이 지나치게 많거나 막연하지 않은지 확인하고, 실행 가능한 분량으로 다시 조정합니다."),
    ("중학생인데 진로를 벌써 고민해야 할까요?",
     "관심 분야와 현재 학습 상황을 바탕으로 과목별 목표와 진로 탐색 방향을 가볍게 안내해 드립니다."),
    ("다니던 학원을 옮기려는데 진도가 다르면 어떻게 하나요?",
     "이전 학원의 진도와 자료를 확인한 뒤, 지금 수준에 맞는 시작 지점을 새로 잡아드립니다."),
]

CHECKLIST_BANK: list[tuple[str, str]] = [
    ("최근 시험 결과", "점수뿐 아니라 취약 단원과 오답 원인까지 함께 확인하는 데 필요합니다."),
    ("다니는 학교 시험 범위", "{local} 학생이 재학 중인 학교의 시험 범위와 출제 경향을 참고합니다."),
    ("오답 정리 방식", "지금까지 틀린 문제를 어떻게 다시 봐왔는지 여쭤봅니다."),
    ("자유학기제 여부", "현재 자유학기제 기간인지에 따라 학습 관리 방향이 달라질 수 있습니다."),
    ("다니던 학원·교재", "이전에 사용하던 교재나 학원 진도가 있다면 알려주시면 좋습니다."),
    ("관심 과목·진로", "특별히 관심 있는 과목이나 진로가 있다면 함께 확인합니다."),
    ("연락 가능한 요일", "편하신 상담 요일을 미리 알려주시면 일정 조율이 쉽습니다."),
    ("현재 학습량", "학원, 과외, 학습지 등 지금 어떻게 공부하고 있는지 확인합니다."),
]

REVIEW_BANK: list[str] = [
    "중학교 입학 후 성적이 눈에 띄게 올랐습니다.",
    "오답을 꼼꼼히 관리해 주셔서 같은 실수가 줄었습니다.",
    "서술형 문제에 자신감이 많이 생겼습니다.",
    "중학생이 되고 나서 스스로 부족한 부분을 찾아 공부합니다.",
    "숙제와 학습 진행 상황을 정기적으로 알려주셔서 안심됩니다.",
    "중간·기말 시험 기간엔 확실히 더 집중적으로 챙겨주십니다.",
    "자유학기제 기간을 알차게 활용할 수 있도록 도와주셨습니다.",
    "진로 상담도 편하게 받을 수 있어서 좋았습니다.",
    "중학생인데 생활 습관까지 함께 잡아주셔서 든든합니다.",
    "중학교 진학 후 적응을 걱정했는데 지금은 즐겁게 다니고 있습니다.",
    "진도만 나가지 않고 이해했는지 꼭 확인해 주셔서 안심됩니다.",
    "한때 공부를 거부했던 아이인데 지금은 스스로 앉아서 공부합니다.",
    "유독 어려워하던 과목의 기초부터 다시 잡아주셔서 좋아졌습니다.",
    "선생님과 관계가 좋아 학원 생활에 빨리 적응했습니다.",
    "스마트폰 사용 습관까지 신경 써주셔서 감사했습니다.",
    "중학교 첫 시험을 앞두고 체계적으로 준비해 주셨습니다.",
    "학원에 다니면서 아이와 공부 문제로 다투는 일이 줄었습니다.",
    "오답 노트로 취약한 단원을 반복해서 공부하게 해주십니다.",
    "매일 할 학습량이 정해져 있어서 꾸준히 하고 있습니다.",
    "고등학교 진학까지 미리 방향을 잡아주셔서 든든합니다.",
    "아이 성격을 고려해서 지도 방법을 다르게 해주셨습니다.",
    "인원이 적당해서 개별 지도를 잘 받고 있습니다.",
    "여기서 배운 공부 방법이 다른 과목에도 도움이 됩니다.",
    "학교별 내신 범위에 맞춰 꼼꼼하게 준비해 주셨습니다.",
]

COMPARE_ROWS: list[dict[str, tuple[str, str]]] = [
    {"label": "학습 진단", "A": ("학년만 보고 반 편성", "단원 이해도부터 확인"),
     "B": ("레벨만 확인하고 끝", "막힌 이유까지 구체적으로 확인")},
    {"label": "내신 대비", "A": ("공통 자료만 사용", "학교별 시험 범위에 맞춰 준비"),
     "B": ("일괄 진도만 나감", "학교 프린트까지 반영해 대비")},
    {"label": "학습 습관", "A": ("숙제 확인만 함", "자기주도학습으로 이어지게 지도"),
     "B": ("과제만 내주고 끝", "계획·실행 여부까지 관리")},
    {"label": "학부모 안내", "A": ("성적만 통보", "학습 태도·진로까지 안내"),
     "B": ("정해진 주기로만 연락", "궁금할 때 편하게 문의 가능")},
]

SUMMARY_INTROS: list[str] = [
    "{local} 학생에게 필요한 관리는 문제를 많이 푸는 것보다 지금 어느 단원, 어느 과목에서 막히는지 먼저 확인하는 것입니다.",
    "{local}에서 중학생학원을 고르실 때는 내신 대비와 학습 습관 중 지금 필요한 부분이 무엇인지부터 살펴보시는 것이 좋습니다.",
    "{local} 학생마다 중1~중3 학년별 고민(적응, 내신, 고등 준비)이 다르기 때문에, 같은 학년이라도 먼저 봐야 할 부분은 달라질 수 있습니다.",
]

MANUSCRIPT_INTRO: list[str] = [
    "중학교는 초등학교와 달리 과목별 내신 시험이 본격적으로 시작되는 시기입니다. 지금 학습 습관을 잡아두지 않으면 고등학교에서 부담이 더 커질 수 있습니다.",
    "자유학기제처럼 시험 부담이 적은 시기는 오히려 기초를 다지고 자기주도학습 습관을 만들 수 있는 좋은 기회입니다.",
    "특정 과목만 유독 어려워하는 학생일수록 지금 학년의 문제만 보지 않고, 이전 학년의 기초부터 점검하는 것이 먼저입니다.",
    "중학교 첫 시험은 범위와 방식이 초등학교와 크게 다릅니다. 미리 시험 형태에 익숙해지는 것이 첫 성적을 좌우할 수 있습니다.",
    "중3이 되면 고등학교 진학 준비와 내신 관리를 동시에 고민하게 됩니다. 무리한 선행보다 지금 과정의 완성도를 먼저 확인하는 것이 중요합니다.",
    "같은 실수를 반복하는 학생일수록 오답을 다시 채점하는 데서 끝내지 않고, 왜 틀렸는지 원인을 나누어 확인하는 과정이 필요합니다.",
]

MANUSCRIPT_OUTRO: list[str] = [
    "학원을 고르실 때는 화려한 커리큘럼보다, 아이의 현재 이해도와 학습 습관을 얼마나 구체적으로 봐주는지를 기준으로 삼으시길 권합니다.",
    "성적보다 먼저 확인해야 할 것은 아이가 스스로 계획을 세우고 실행해 보려는 습관이 자리 잡고 있는지입니다.",
    "상담은 등록을 결정하는 자리가 아니라, 지금 아이에게 필요한 학습 방향을 함께 정리해보는 자리로 생각해 주시면 좋겠습니다.",
    "중학생의 학습은 한 번에 완성되지 않습니다. 적응, 내신, 고등 준비를 거치며 조금씩 쌓아가는 과정이라는 점을 기억해 주세요.",
    "무엇보다 아이가 지금의 변화(중학교 진학, 첫 시험)에 압도되지 않는지가 꾸준한 학습으로 이어지는 데 중요합니다.",
    "지금 당장의 시험 점수보다, 스스로 오답을 정리해 보려는 습관이 자리 잡고 있는지를 함께 지켜봐 주시길 바랍니다.",
]


def local_page(row: dict[str, str], idx: int, rep_image: str, all_rows: list[dict[str, str]], seen_reviews: set) -> str:
    local = row["근처 수업가능 동네"].strip()
    slug = slug_ko(local)
    region = row.get("지역", "").strip()
    district = row.get("시or구", "").strip()
    center = row.get("센터명", "").strip() or f"{local} 학습관리"
    address = row.get("센터 주소", "").strip()
    title = f"{local} {CATEGORY}"
    description = f"{region} {district} {local} 중학생을 위한 {CATEGORY} 안내입니다. 내신 대비, 자기주도학습 진단, 오답 관리, 학년별 학습 우선순위를 상담 전에 확인할 수 있습니다."
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

    opener = fmt_pair(pick(FAQ_OPENER_BANK, 1, local, "ms-faq-opener")[0],
                       local=local, district=district, title=title, region=region)
    faqs = [opener] + [fmt_pair(p, local=local, district=district, title=title, region=region)
                        for p in pick(FAQ_BANK, 5, local, "ms-faq")]
    answers = [fmt_pair(p, local=local, district=district, title=title, region=region)
               for p in pick(ANSWER_BANK, 4, local, "ms-answer")]
    checklist = [fmt_pair(p, local=local, district=district, title=title, region=region)
                 for p in pick(CHECKLIST_BANK, 4, local, "ms-checklist")]
    review_lines = pick_unique(REVIEW_BANK, 6, seen_reviews, local, "ms-review", str(idx))
    summary_intro = pick(SUMMARY_INTROS, 1, local, "ms-summary")[0].format(local=local)
    manu_intro = pick(MANUSCRIPT_INTRO, 1, local, "ms-manu-intro")[0]
    manu_outro = pick(MANUSCRIPT_OUTRO, 1, local, "ms-manu-outro")[0]
    location_ref = address if address else "상담 시 안내되는 위치"
    variant = "A" if seed_for(local, "ms-compare") % 2 == 0 else "B"

    rng = random.Random(seed_for(local, "ms-review-rating"))
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
        {"@type": "Thing", "name": "중학생학원"},
        {"@type": "Thing", "name": "내신 대비"},
        {"@type": "Thing", "name": "자기주도학습"},
        {"@type": "Thing", "name": "오답 관리"},
        {"@type": "Thing", "name": "진로 탐색"},
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
                "alternateName": [SITE_NAME, center, f"{local} 중학생 학습관리"],
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
                "knowsAbout": ["내신 대비", "자유학기제 학습관리", "자기주도학습", "오답 관리", "진로 탐색", "학습 상담"],
                "makesOffer": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 중학생 진단 상담", "serviceType": "TutoringService"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 내신 대비 관리", "serviceType": "TutoringService"}},
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
                "description": f"{local} 중학생의 내신, 학습 습관, 진로, 오답을 함께 진단하고 학년별 우선순위에 맞춰 관리합니다.",
                "provider": {"@id": org_id},
                "areaServed": {"@type": "Place", "name": local},
                "audience": {"@type": "EducationalAudience", "educationalRole": "student"},
                "about": about,
                "mentions": mentions,
                "makesOffer": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 내신 대비 관리"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 자기주도학습 관리"}},
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

    badge_row = f'<div class="badge-row"><span>{esc(region)}</span><span>{esc(district)}</span><span>{esc(CATEGORY)}</span><span>내신·자기주도학습</span></div>'

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
        <article class="info-card"><span class="tag">01</span><h3>내신·학습습관 진단</h3><p>내신 대비, 자기주도학습, 오답관리 중 지금 어디가 부족한지 먼저 나누어 확인합니다.</p></article>
        <article class="info-card"><span class="tag">02</span><h3>오답 관리</h3><p>틀린 문제를 유형별로 정리해 같은 실수가 반복되지 않도록 관리합니다.</p></article>
        <article class="info-card"><span class="tag">03</span><h3>학년별 우선순위</h3><p>중1~중3 전환 시기마다 필요한 부분이 달라 학년에 맞춰 순서를 정합니다.</p></article>
      </div>
    </section>"""

    manuscript_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">학원 선택 가이드</p>
        <h2>{esc(local)} {esc(CATEGORY)}, 무엇을 기준으로 볼까요</h2>
      </div>
      <p class="lead">{esc(manu_intro)}</p>
      <p class="lead">{esc(center)}은 {esc(region)} {esc(district)} {esc(local)} 학생을 기준으로 상담을 진행하며, {esc(', '.join(middle_schools[:4]) if middle_schools else (', '.join(schools[:4]) if schools else '인근 중학교'))} 학생들이 주로 문의합니다. 실제 등록 전에는 {esc(location_ref)}{eul_reul(location_ref)} 기준으로 이동 동선과 상담 가능 시간을 확인하는 것이 좋습니다.</p>
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
        linked_bits.append(f"진학 전 초등학교: {', '.join(elementary_schools)}")
    if middle_schools:
        linked_bits.append(f"중학교: {', '.join(middle_schools)}")
    linked_schools = ""
    if linked_bits:
        linked_schools = f'<article class="info-card"><span class="tag">학교</span><h3>학교급별 참고 학교</h3><p>{esc(" · ".join(linked_bits))}</p></article>'
    fit_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">LOCAL &amp; STUDENT FIT</p>
        <h2>지역·학년·추천학생 기준</h2>
      </div>
      <div class="card-grid">
        <article class="info-card"><span class="tag">지역</span><h3>{esc(region)} {esc(district)} {esc(local)}</h3><p>{esc(local)} 생활권 학생의 학교 진도와 눈높이에 맞춰 중학생 학습 관리 방향을 상담합니다.</p></article>
        <article class="info-card"><span class="tag">학년</span><h3>중1~중3, 전 학년 상담 가능</h3><p>학년과 목표에 따라 적응, 내신, 고등 준비 중 시작 지점을 다르게 잡습니다.</p></article>
        <article class="info-card"><span class="tag">추천</span><h3>이런 학생에게 추천</h3><p>중학교 첫 시험이 걱정되는 학생, 특정 과목만 유독 어려운 학생, 자기주도학습 습관이 약한 학생에게 적합합니다.</p></article>
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
        <h2>{esc(local)} 중학생학원, 무엇이 다른가요</h2>
        <p class="lead">일반적인 학원 운영 방식과 {esc(SITE_NAME)}의 중학생 관리 방식을 같은 기준으로 비교했습니다.</p>
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
        f'<tr><td>{esc(freq)}</td><td>{esc(el)}</td><td class="highlight">{esc(mid)}</td><td>{esc(hi)}</td></tr>'
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
          <thead><tr><th>횟수</th><th>초등</th><th class="highlight">중등</th><th>고등</th></tr></thead>
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
        <h2>{esc(local)} 중학생 상담 후기</h2>
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
      <p class="eyebrow">MIDDLE SCHOOL COACHING</p>
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
    rep = "/assets/generated/site6-hero.png"
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
      <p class="eyebrow">MIDDLE SCHOOL ACADEMY DIRECTORY</p>
      <h1>{esc(CATEGORY)}</h1>
      <p class="lead">지역별 중학생 상담 기준을 한눈에 찾을 수 있도록 정리했습니다. 각 페이지에는 지역·학년·추천학생, 학교 참고 정보, FAQ, 학부모 후기, 근처 학원페이지가 함께 구성됩니다.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="tel:{PHONE_DISPLAY}">전화 상담하기</a>
        <a class="btn btn-ghost" href="../../상담문의/index.html">상담문의</a>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">ABOUT US</p>
        <h2>{esc(SITE_NAME)}은 중학생을 이렇게 관리해요</h2>
        <p class="lead">문제 양을 늘리기보다, 지금 학생이 내신·학습습관·오답관리 중 어디에서 막히는지부터 확인해요. 상담에서 시작해 진단, 오답 관리, 학년별 우선순위까지 이어갑니다.</p>
      </div>
      <div class="process-list">
        <article class="process-item">
          <span class="ghost-num">01</span>
          <h3>상담</h3>
          <p>학년, 최근 성적, 학교 생활을 편하게 듣습니다.</p>
        </article>
        <article class="process-item">
          <span class="ghost-num">02</span>
          <h3>진단</h3>
          <p>내신, 학습 습관, 진로 중 지금 어디부터 시작해야 할지 확인합니다.</p>
        </article>
        <article class="process-item">
          <span class="ghost-num">03</span>
          <h3>오답 관리</h3>
          <p>틀린 문제를 유형별로 정리해 같은 실수가 반복되지 않도록 관리합니다.</p>
        </article>
        <article class="process-item">
          <span class="ghost-num">04</span>
          <h3>학년별 우선순위</h3>
          <p>중1~중3 전환 시기에 맞춰 다음 단계를 준비합니다.</p>
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
