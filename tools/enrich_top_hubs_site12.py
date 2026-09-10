"""Enrich only the 23 national/topic coaching hubs; never regenerate locality copy."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from copy import deepcopy
from datetime import date
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urljoin

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tools/data/hub-guides'
REPORTS = ROOT / 'tools/reports/hub-enrichment'
DOMAIN = 'https://xn--ru4bz7e9zf0zk.com'
CSS = '/assets/hub-guide-v1.css?v=20260910-1'
PHOTOS = [
    ('classroom-desks.webp', 500, 300, '개별 책상과 칸막이가 있는 학습 공간', '개별 학습에 집중할 수 있도록 책상과 칸막이를 배치한 공간 예시'),
    ('classroom-study.webp', 800, 600, '책상에서 교재를 살펴보는 학습 공간', '교재를 펼쳐 문제를 풀고 학습 과정을 점검하는 공간 예시'),
]


def esc(value):
    return html.escape(str(value), quote=True)


def p(value):
    return '<p>' + esc(value) + '</p>'


def fragment(value):
    return BeautifulSoup(value, 'html.parser')


def has_type(node, name):
    types = node.get('@type', [])
    return name in ([types] if isinstance(types, str) else types)


def scoped_subject(subject, stage, grade=None):
    """Show only this school stage, retaining relevant and unscoped conditions."""
    import re

    if not stage:
        return subject
    prefix = stage[0]
    grades = [g for g in subject['grades'] if g.startswith(prefix) and (not grade or g == grade)]
    numbers = sorted({int(g[1:]) for g in grades})
    runs = []
    for number in numbers:
        if runs and number == runs[-1][-1] + 1:
            runs[-1].append(number)
        else:
            runs.append([number])
    grade_summary = ' · '.join(prefix + str(run[0]) + ('~' + prefix + str(run[-1]) if len(run) > 1 else '') for run in runs)
    # The reviewed summary starts with exact grade/range tokens. Remove only
    # those tokens, not grade limits embedded in a condition sentence.
    grade_token = r'(?:초[1-6]|중[1-3]|고[1-3])(?:[~～-](?:초[1-6]|중[1-3]|고[1-3]))?'
    conditions = [part.strip() for part in subject['summary'].split(' · ')
                  if part.strip() and not re.fullmatch(grade_token, part.strip())]
    relevant, unscoped = [], []
    for detail in conditions:
        inherited_scope = set()
        inherited_grades = set()
        for clause in (part.strip(' ,;') for part in re.split(r'[,;]', detail)):
            if not clause:
                continue
            scope = set(re.findall(r'([초중고])(?:[1-6]|등|학생)', clause))
            leading = re.match(r'^([초중고\s]{2,})', clause)
            if leading:
                scope.update(re.findall(r'[초중고]', leading.group(1)))
            for start, end in re.findall(r'([초중고])[1-6]\s*[~～-]\s*([초중고])[1-6]', clause):
                scope.update('초중고'['초중고'.index(start):'초중고'.index(end) + 1])
            explicit_grades = set(re.findall(r'[초중고][1-6]', clause))
            all_grades = ['초'+str(n) for n in range(1,7)] + ['중'+str(n) for n in range(1,4)] + ['고'+str(n) for n in range(1,4)]
            for start, end in re.findall(r'([초중고][1-6])\s*[~～-]\s*([초중고]?[1-6])', clause):
                if len(end) == 1: end = start[0]+end
                if start in all_grades and end in all_grades:
                    explicit_grades.update(all_grades[all_grades.index(start):all_grades.index(end)+1])
            if not explicit_grades and not scope and re.match(r'^(?:파닉스|수행|수능)', clause):
                # A newly stated activity/course condition is independent of
                # the previous comma-delimited exact-grade restriction.
                inherited_grades = set()
                inherited_scope = set()
            if explicit_grades:
                inherited_grades = explicit_grades
            elif scope:
                inherited_grades = set()
            if grade and inherited_grades and grade not in inherited_grades:
                continue
            explicit_scope = set(scope)
            # These are named high-school courses/exams, not a guess based on
            # a student's age. Other unscoped notes remain explicitly labeled.
            if not scope and re.search(r'미적(?:분)?|기하|확통|확률과\s*통계|수능|사탐|모의고사|통합과학|통합사회|현대사회와\s*윤리|[ⅠⅡ]|(?:화학|물리|생명|생물|지구과학)\s*[12]', clause):
                scope.add('고')
            if explicit_scope:
                inherited_scope = explicit_scope
            elif not scope and inherited_scope and not re.search(r'파닉스', clause):
                # A comma does not cancel the preceding grade condition:
                # '고3 사탐과목, 한국사 모두 가능' remains high-school scoped.
                # Phonics is independently stated without a grade in this source.
                # A course-name inference such as 수능 must not scope a later
                # independent 수행 condition to high school.
                scope = set(inherited_scope)
            if scope:
                if prefix in scope:
                    relevant.append(clause)
            else:
                unscoped.append(clause)
    parts = [grade_summary]
    if relevant:
        parts.append('안내 조건: ' + '; '.join(relevant))
    if unscoped:
        parts.append('지점 과목 안내 조건: ' + '; '.join(unscoped))
    return {**subject, 'grades': grades, 'summary': ' · '.join(parts)}


def choose_centers(rel, examples):
    import re
    slug = rel.split('/')[-2]
    if rel in {'전국학원/index.html','과목별학원/index.html'}: slug = '중학생학원'
    grade_match = re.match(r'^(초[3-6]|중[1-3]|고[12])',slug)
    grade = grade_match.group(1) if grade_match else None
    required = ['국어', '영어', '수학'] if '국영수' in slug else ['영어', '수학'] if '영수' in slug else ['영어'] if '영어' in slug else ['수학'] if '수학' in slug else []
    stage = '초등' if slug.startswith('초') else '중등' if slug.startswith('중') else '고등' if slug.startswith('고') else None
    def matches_stage(subject):
        return (not grade or grade in subject['grades']) and (not stage or any(g.startswith(stage[0]) for g in subject['grades']))
    candidates = []
    for original in examples:
        # Source addresses end with a bare single digit whose floor/unit is
        # missing. Preserve the catalog; do not guess a 층/호 suffix in a hub.
        if original['locality'] in {'옥계동', '복산동', '온천동'}:
            continue
        c = deepcopy(original)
        selected = [s for s in c['subjects'] if not required or s['name'] in required]
        if any(not any(s['name'] == name and matches_stage(s) for s in selected) for name in required):
            continue
        if stage and not any(matches_stage(s) for s in selected):
            continue
        if stage:
            selected = [scoped_subject(s, stage, grade) for s in selected if matches_stage(s)]
        if len(required) > 1:
            shared_grades = set.intersection(*(set(s['grades']) for s in selected if s['name'] in required))
            if not shared_grades:
                continue
        path = c['targetPath'] if rel == '과목별학원/index.html' else c.get('targetPaths', {}).get(slug)
        if not path:
            continue
        assert (ROOT / unquote(urlsplit(path).path).strip('/') / 'index.html').is_file(), path
        c['targetPath'] = path
        c['organizationId'] = c.get('categoryOrganizationIds', {}).get(slug, c['organizationId'])
        c['subjects'] = selected
        c['_displayStage'] = grade or stage
        candidates.append(c)
    if not candidates:
        raise ValueError('No verified examples for ' + rel)
    offset = int(hashlib.sha256(rel.encode()).hexdigest()[:8], 16) % len(candidates)
    candidates = candidates[offset:] + candidates[:offset]
    chosen = []
    for c in candidates:
        if c['region'] not in {x['region'] for x in chosen}:
            chosen.append(c)
        if len(chosen) == 3:
            break
    assert len(chosen) == 3, (rel, len(chosen))
    return chosen


def guide_markup(copy):
    cards = ''.join(f'<article class="hub-guide-card"><span class="hub-guide-number">0{i}</span><h3>{esc(s["heading"])}</h3>{"".join(p(t) for t in s["paragraphs"])}</article>' for i, s in enumerate(copy['sections'], 1))
    return f'<section class="hub-guide" data-hub-enrichment="guide" id="hub-learning-guide"><div class="hub-wrap"><div class="hub-guide-heading"><p class="eyebrow">LEARNING CHECK</p><h2>{esc(copy["label"])} 선택 전에 살펴볼 내용</h2></div><div class="hub-guide-grid">{cards}</div></div></section>'


def centers_markup(copy, centers):
    cards = []
    for c in centers:
        subjects = ' / '.join(s['name'] + ': ' + s['summary'] for s in c['subjects'])
        scope_label = (c['_displayStage'] + ' 과목·학년') if c.get('_displayStage') else '안내된 과목·학년'
        cards.append(f'<article class="hub-guide-card hub-center-card"><p class="hub-guide-note">{esc(c["region"])} · {esc(c["locality"])} 안내 연결</p><h3>{esc(c["centerName"])}</h3><dl><dt>주소</dt><dd>{esc(c["address"])}</dd><dt>등록 학원명</dt><dd>{esc(c["registeredAcademyName"])}</dd><dt>등록번호</dt><dd>{esc(c["registrationNumber"])}</dd><dt>{esc(scope_label)}</dt><dd>{esc(subjects)}</dd></dl><a href="{esc(c["targetPath"])}">{esc(c["locality"])} 상세 안내 보기 <span aria-hidden="true">→</span></a></article>')
    return f'<section class="hub-guide" data-hub-enrichment="centers" id="hub-center-examples"><div class="hub-wrap"><div class="hub-guide-heading"><p class="eyebrow">CENTER INFORMATION</p><h2>연결된 지점 정보도 확인하세요</h2><p>아래는 {esc(copy["label"])} 안내에서 살펴볼 수 있는 일부 지점입니다. 동네별 안내 수와 실제 지점 수는 다를 수 있으므로 방문할 곳의 주소와 가능 과목을 확인하세요.</p></div><div class="hub-guide-grid hub-center-grid">{"".join(cards)}</div><p class="hub-guide-note">지점 정보는 일부 예시이며 추천 순위가 아니에요. 표시된 학년 안에서도 현재 개설 여부와 희망 시간을 상담에서 확인해 주세요. 다른 과목의 운영 여부도 지점에 문의할 수 있어요.</p></div></section>'


def after_markup(copy, centers):
    photos = ''.join(f'<figure><img src="/assets/hub-guide/{name}" width="{w}" height="{h}" alt="{esc(copy["label"])} {esc(alt)}" loading="lazy" decoding="async"><figcaption>{esc(caption)}</figcaption></figure>' for name,w,h,alt,caption in PHOTOS)
    return centers_markup(copy, centers) + '<section class="hub-guide" data-hub-enrichment="consultation" id="hub-consultation-guide"><div class="hub-wrap"><div class="hub-guide-heading"><p class="eyebrow">CONSULTATION NOTE</p><h2>지금 필요한 도움을 상담 질문으로 바꿔 보세요</h2><p>궁금한 점을 많이 적기보다 최근 학습에서 멈춘 순간 하나를 골라 보세요. 그 장면에서 필요한 도움과 학생이 직접 해 볼 일을 나누면 상담의 출발점을 잡기 좋아요.</p></div><div class="hub-guide-grid"><article class="hub-guide-card"><h3>어디까지 혼자 했는지</h3><p>시작한 흔적이 있는 문제나 문장을 하나 준비해 주세요. 혼자 한 부분과 설명을 받은 부분에 표시를 달면, 도움을 줄여 가며 다시 확인할 범위를 이야기할 수 있어요.</p></article><article class="hub-guide-card"><h3>복습이 멈추는 이유</h3><p>할 일을 몰라서 못 했는지, 시간이 부족했는지, 시작했지만 어려워서 멈췄는지 나누어 보세요. 실제 생활에서 가능한 공부 시간과 과제의 크기를 함께 조정할 질문이 돼요.</p></article><article class="hub-guide-card"><h3>방문할 지점의 운영 확인</h3><p>주소와 희망 과목·학년을 먼저 대조해 주세요. 상담할 때 수업 요일, 현재 개설 범위, 과제와 피드백 방식, 교습비 및 교재비 포함 여부를 확인하면 선택에 필요한 정보를 정리할 수 있어요.</p></article></div><div class="hub-guide-reading"><a href="/학습가이드/">학습관리 기준 읽기</a><a href="/과목별학원/">과목·학년별 안내 보기</a><a href="/상담문의/">상담 방법 확인하기</a></div></div></section>' + f'<section class="hub-guide" data-hub-enrichment="photos" id="hub-learning-space"><div class="hub-wrap"><div class="hub-guide-heading"><p class="eyebrow">LEARNING SPACE</p><h2>학습 공간 살펴보기</h2><p>와와 학습 공간의 공통 예시입니다. 실제 책상 배치와 시설은 지점별로 다를 수 있습니다.</p></div><div class="hub-guide-gallery">{photos}</div></div></section>'


def update_schema(soup, canonical, copy, centers, qa, modified, rel):
    scripts = soup.select('script[type="application/ld+json"]')
    graphs = []
    for script in scripts:
        data = json.loads(script.get_text())
        graphs.extend(data.get('@graph', [data]) if isinstance(data, dict) else data)
    def absolute(value):
        if isinstance(value, dict): return {k: absolute(v) for k,v in value.items()}
        if isinstance(value, list): return [absolute(v) for v in value]
        if isinstance(value, str) and value.startswith('/'):
            return DOMAIN + value
        return value
    graphs = absolute(graphs)
    replacements = {n['@id']: canonical + '#' + n['@id'].split('#', 1)[1]
                    for n in graphs if '@id' in n and '#' in n['@id']
                    and unquote(n['@id'].split('#')[0]) == unquote(canonical)}
    def normalize(value):
        if isinstance(value, dict): return {k: normalize(v) for k,v in value.items()}
        if isinstance(value, list): return [normalize(v) for v in value]
        return replacements.get(value, value) if isinstance(value, str) else value
    graphs = normalize(graphs)
    # Rebuild managed entities each time: no stale examples, invented opening hours,
    # offers, ratings or reviews. A directory itself is not a class or an article.
    graphs = [n for n in graphs if not any(has_type(n,t) for t in
              ['FAQPage','Article','Service','EducationalOrganization','WebSite'])
              and n.get('@id') != DOMAIN+'/#organization'
              and not str(n.get('@id','')).startswith(canonical+'#hub-')]
    page = next(n for n in graphs if has_type(n,'WebPage') or has_type(n,'CollectionPage'))
    page.update({'@type':['WebPage','CollectionPage'],'url':canonical,
                 'description':copy['description'],'dateModified':modified,
                 'isPartOf':{'@id':DOMAIN+'/#website'},
                 'publisher':{'@id':DOMAIN+'/#organization'}})
    page['about'] = [{'@type':'Thing','name':copy['label']}] + [
        {'@type':'Thing','name':s['heading']} for s in copy['sections']]
    page['mentions'] = [{'@id':c['organizationId']} for c in centers]
    directory = next(n for n in graphs if has_type(n,'ItemList'))
    directory.setdefault('@id', canonical+'#directory')
    for n in graphs:
        if has_type(n,'BreadcrumbList'): n.setdefault('@id', canonical+'#breadcrumb')
    page['mainEntity'] = {'@id':directory['@id']}
    sections = [(x['id'],x.h2.get_text(' ',strip=True))
                for x in soup.select('section[data-hub-enrichment]') if x.get('id') and x.h2]
    page['hasPart'] = [{'@id':canonical+'#'+sid} for sid,_ in sections]+[{'@id':canonical+'#hub-faq'}]
    graphs += [
        {'@type':'WebSite','@id':DOMAIN+'/#website','url':DOMAIN+'/',
         'name':'채움학습.com','publisher':{'@id':DOMAIN+'/#organization'}},
        {'@type':'Organization','@id':DOMAIN+'/#organization',
         'name':'채움학습','url':DOMAIN+'/'}
    ]
    for sid,label in sections:
        graphs.append({'@type':'WebPageElement','@id':canonical+'#'+sid,
            'url':canonical+'#'+sid,'name':label,'isPartOf':{'@id':page['@id']}})
    graphs.append({'@type':'FAQPage','@id':canonical+'#hub-faq',
        'url':canonical+'#hub-questions','isPartOf':{'@id':page['@id']},
        'mainEntity':[{'@type':'Question','name':q['question'],
          'acceptedAnswer':{'@type':'Answer','text':q['answer']}} for q in qa]})
    for c in centers:
        if not any(n.get('@id') == c['organizationId'] for n in graphs):
            graphs.append({'@type':'EducationalOrganization','@id':c['organizationId'],
              'name':c['centerName'],'url':DOMAIN+quote(unquote(urlsplit(c['targetPath']).path),safe='/'),
              'address':c['address']})
    for script in scripts[1:]: script.decompose()
    scripts[0].string = json.dumps({'@context':'https://schema.org','@graph':graphs},
        ensure_ascii=False,separators=(',',':')).replace('</','<\\/')

def update_page(rel, copy, examples, modified):
    path = ROOT / rel
    before = path.read_text(encoding='utf-8')
    soup = BeautifulSoup(before, 'html.parser')
    fixed = (soup.title.get_text(), soup.h1.get_text(), soup.select_one('[rel=canonical]')['href'], soup.select_one('[property="og:url"]')['content'])
    canonical = urljoin(DOMAIN+'/',fixed[2])
    soup.select_one('[rel=canonical]')['href'] = canonical
    soup.select_one('[property="og:url"]')['content'] = urljoin(DOMAIN+'/',fixed[3])
    for old in soup.select('[data-hub-enrichment]'): old.decompose()
    # Replace work-oriented duplicate FAQ and unsourced review-style quotes on
    # the four national hubs with the new fact-bound guide and visible FAQ.
    for old in soup.select('.geo-enhance'): old.decompose()
    soup.body['class'] = list(dict.fromkeys(soup.body.get('class', []) + ['hub-enhanced-page']))
    hero = soup.main.select_one('.page-hero')
    assert hero and hero.h1, rel
    summary = hero.h1.find_next_sibling('p')
    assert summary is not None, rel
    summary.clear(); summary.append(copy['summary'])
    # Retain the published category links, search markup and useful process/CTA.
    directory = next(section for section in soup.main.find_all('section',recursive=False)
                     if section.select('.category-grid,.subject-category-grid,.region-block'))
    if rel == '전국학원/index.html':
        directory.select_one('.section-head .eyebrow').string = '지역별 학습 안내'
        directory.select_one('.section-head h2').string = '학교급을 선택해 가까운 동네 안내를 찾아보세요'
        directory.select_one('.section-head .lead').string = '초등·중등·고등의 현재 학습 단계에 맞는 안내를 골라 보세요. 동네별 페이지에서 연결된 지점과 상담할 내용을 확인할 수 있어요.'
        for item in soup.select('.info-card p'):
            if '고1~고3 전환' in item.get_text():
                item.string = item.get_text().replace('고1~고3 전환', '초·중·고 전환')
    elif rel.startswith('전국학원/'):
        directory.select_one('.section-head .lead').string = '동네나 시·군·구를 검색하거나 아래 지역 버튼을 눌러 상세 학습 안내를 확인하세요.'
    directory['id'] = 'hub-directory'
    if directory.select('.region-block') and not directory.select_one('[data-subject-search]'):
        directory.select_one('.section-head').insert_after(fragment('<div class="hub-directory-search" data-hub-enrichment="search"><label for="hub-search">동네·지역 이름으로 찾기</label><div><input id="hub-search" type="search" placeholder="예: 명일동, 강동구, 서울" aria-label="동네·지역 검색" autocomplete="off"><button type="button" id="hub-search-reset">검색 초기화</button></div><p id="hub-search-result" role="status" aria-live="polite">전체 371개 동네</p></div>'))
        if not soup.select_one('script[src^="/assets/hub-directory-v1.js"]'):
            soup.body.append(soup.new_tag('script',src='/assets/hub-directory-v1.js?v=20260910-1',defer=''))
    jumps = [('hub-directory','지역·분류 찾기'),('hub-learning-guide','학습 선택 기준'),('hub-center-examples','지점 정보'),('hub-consultation-guide','상담 준비'),('hub-learning-space','학습 공간'),('hub-questions','자주 묻는 질문')]
    hero.insert_after(fragment('<nav class="hub-guide-jumps" data-hub-enrichment="navigation" aria-label="이 페이지 빠른 이동"><div class="hub-wrap">'+''.join(f'<a href="#{sid}">{label}</a>' for sid,label in jumps)+'</div></nav>'))
    soup.select_one('.hub-guide-jumps').insert_after(fragment(guide_markup(copy)))
    centers = choose_centers(rel, examples)
    soup.main.append(fragment(after_markup(copy, centers)))
    if rel in {'전국학원/index.html','과목별학원/index.html'}:
        intro = soup.select_one('#hub-center-examples .hub-guide-heading > p:not(.eyebrow)')
        intro.string = '아래는 중학생학원 안내로 연결되는 지점 예시예요. 중등에서 안내된 과목과 학년을 표시했으며, 다른 학교급은 위 분류에서 따로 살펴볼 수 있어요. 동네별 안내 수와 실제 지점 수는 다를 수 있으니 주소도 확인해 주세요.'
    qa = copy['faq'] + [
        {'question':'동네 이름과 실제 방문할 지점은 어떻게 확인하나요?','answer':'여러 동네의 안내가 같은 센터로 연결될 수 있습니다. 관심 동네의 상세 페이지에서 지점명과 주소를 확인하고, 현재 운영 과목·가능 학년·방문 시간을 상담으로 확인하세요.'},
        {'question':'사진과 학습 안내가 모든 지점에 그대로 적용되나요?','answer':'사진은 공통 학습 공간 예시이며 실제 시설과 배치는 지점마다 다릅니다. 학습 점검 방법은 학생의 현재 상태를 살펴보기 위한 안내입니다. 실제 개설 과목·학년·시간표와 교습비, 기록·소통 방식은 해당 지점에서 확인하세요.'},
    ]
    faq_markup = '<section class="hub-guide hub-guide-faq" id="hub-answer" data-hub-enrichment="faq"><div class="hub-wrap" id="hub-questions"><p class="eyebrow">FAQ</p><h2>'+esc(copy['label'])+' 자주 묻는 질문</h2><div id="hub-faq-list">'+''.join(f'<details><summary>{esc(q["question"])}</summary>{p(q["answer"])}</details>' for q in qa)+'</div></div></section>'
    soup.main.append(fragment(faq_markup))
    for attr,key in [('name','description'),('property','og:description'),('name','twitter:description')]:
        meta = soup.find('meta',attrs={attr:key})
        if meta: meta['content'] = copy['description']
    style = next((x for x in soup.select('link[href]') if x['href'].split('?')[0] == CSS.split('?')[0]),None)
    if style: style['href'] = CSS
    else: soup.head.append(soup.new_tag('link',rel='stylesheet',href=CSS))
    if not soup.select_one('link[type="application/rss+xml"]'):
        soup.head.append(soup.new_tag('link',rel='alternate',type='application/rss+xml',title='채움학습 허브 소식',href=DOMAIN+'/rss.xml'))
    update_schema(soup,canonical,copy,centers,qa,modified,rel)
    assert fixed[:2] == (soup.title.get_text(), soup.h1.get_text())
    assert urljoin(DOMAIN+'/',fixed[2]) == soup.select_one('[rel=canonical]')['href']
    assert urljoin(DOMAIN+'/',fixed[3]) == soup.select_one('[property="og:url"]')['content']
    after = str(BeautifulSoup(str(soup),'html.parser'))
    if before != after: path.write_text(after,encoding='utf-8',newline='\n')
    return {'path':rel,'changed':before!=after,'url':canonical,'faq':len(qa),'centerLocalities':[c['locality'] for c in centers],'sha256':hashlib.sha256(after.encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date',default=date.today().isoformat())
    args = parser.parse_args()
    topics = json.loads((DATA/'subject-copy.json').read_text(encoding='utf-8'))
    examples = json.loads((DATA/'center-examples.json').read_text(encoding='utf-8'))
    if isinstance(examples,dict): examples = examples.get('centers',examples.get('examples'))
    assert len(topics) == 23
    REPORTS.mkdir(parents=True,exist_ok=True)
    results = [update_page(rel, copy, examples, args.date) for rel,copy in topics.items()]
    (REPORTS/'generation.json').write_text(json.dumps({'date':args.date,'targets':results},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'targets':len(results),'changed':sum(x['changed'] for x in results),'faq':sum(x['faq'] for x in results)},ensure_ascii=False))


if __name__ == '__main__': main()
