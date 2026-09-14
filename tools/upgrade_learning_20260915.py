"""Scoped Chaeum overview upgrade, with baseline and intervening-edit guards."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime
from email.utils import format_datetime
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET
import hashlib, html, json, re, subprocess
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'tools/data/learning-upgrade'
REPORT=ROOT/'tools/reports/learning-upgrade'
BASE='f2ae2251f532f938eae05de8160a5910bab77561'
DOMAIN='https://xn--ru4bz7e9zf0zk.com'
DATE='2026-09-15'
CSS='/assets/learning-upgrade.css?v=20260915-1'
CORE={'home':'index.html','coaching':'학습코칭/index.html','guide':'학습가이드/index.html','contact':'상담문의/index.html'}
NAV=[('/','홈'),('/학습코칭/','학습코칭'),('/학습가이드/','학습가이드'),('/과목별학원/','과목별학원'),('/전국학원/','전국학원'),('/상담문의/','상담문의')]

def digest(b):return hashlib.sha256(b).hexdigest()
def raw(rel):
    return subprocess.check_output(['git','show',BASE+':'+rel],cwd=ROOT).decode('utf-8-sig')
def route(rel):return '/' if rel=='index.html' else '/'+rel[:-10]
def esc(v):return html.escape(str(v),quote=True)
def norm(s):return ' '.join(s.split())
def jsontext(v):return json.dumps(v,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
def nav(rel):
    current=route(rel)
    links=''.join(f'<a href="{u}"'+(' class="active" aria-current="page"' if current==u or (u!='/' and current.startswith(u)) else '')+f'>{n}</a>' for u,n in NAV)
    return '<header class="nav-wrap"><nav class="nav" aria-label="주요 메뉴"><a class="brand" href="/"><span class="brand-mark">채</span><span>채움학습</span></a><div class="nav-links">'+links+'</div></nav></header>'
def footer():
    return '<footer class="footer"><div class="shell"><p><strong>채움학습</strong> · 학생의 학습 상태를 살피고, 지역별 학원 정보를 안내합니다.</p><nav class="pl-footer-links" aria-label="하단 메뉴">'+''.join(f'<a href="{u}">{n}</a>' for u,n in NAV)+'</nav></div></footer>'
CTA='<div class="floating-cta" aria-label="빠른 상담 버튼"><a href="tel:010-6839-8283">전화문의</a><a href="sms:01068398283">문자문의</a><a href="/상담문의/">상담문의</a></div>'

TOPIC={
 '초3':('문제를 읽고 시작하는 순간을 살펴요','문장을 끝까지 읽었는지, 모르는 말을 질문했는지부터 함께 확인해 보세요.'),
 '초4':('배운 내용을 자기 말로 연결해 봐요','따라 한 답과 스스로 만든 답을 구분하면 다음 연습의 출발점을 찾기 쉬워요.'),
 '초5':('길어진 과제에서 멈춘 지점을 기록해요','한 번에 끝내기 어려운 과제는 이해·연습·확인의 작은 묶음으로 나누어 보세요.'),
 '초6':('설명을 듣고 혼자 해 보는 간격을 줄여요','다음 학교급을 서두르기 전에 지금 배운 내용을 도움 없이 사용할 수 있는지 확인해 보세요.'),
 '중1':('과목마다 달라진 공부 방식을 정리해요','준비물과 과제 마감을 적고, 학교에서 배운 부분과 혼자 어려웠던 부분을 구분해 보세요.'),
 '중2':('아는 것과 적용하는 것을 따로 확인해요','설명을 이해한 문제를 시간이 지난 뒤 다시 풀어 보면 아직 남은 질문이 드러날 수 있어요.'),
 '중3':('지금의 평가와 다음 공부를 한 계획에 담아요','현재 학교 범위를 마무리하면서 반복해서 막히는 기초를 따로 적어 복습 자리를 남겨 보세요.'),
 '고1':('늘어난 학습량 안에서 보완할 부분을 골라요','실제 수강 과목과 학교 진도를 먼저 적고, 지금 과제를 막는 기초를 우선해서 살펴보세요.'),
 '고2':('풀이 결과와 선택한 근거를 함께 봐요','선택 과목과 평가 범위를 맞춘 뒤 정답뿐 아니라 접근 방법과 사용한 시간을 확인해 보세요.')}
def brief(rel):
    name=rel.split('/')[-2] if '/' in rel else ''
    if rel=='전국학원/index.html':
        title='지역을 찾은 다음, 필요한 도움을 구체적으로 살펴보세요'
        ps=['전국학원은 초등학생·중학생·고등학생 안내를 나누어 제공합니다. 같은 동네라도 연결되는 센터와 수업 조건을 먼저 확인한 뒤 학생에게 필요한 설명과 복습 방식을 비교해 보세요.','브랜드의 학습코칭 흐름을 읽고 최근 과제에서 멈춘 장면을 하나 떠올려 보세요. 방문 상담에서는 진단 뒤 어떤 교재와 연습으로 이어지는지, 다시 확인하는 방식은 무엇인지 질문할 수 있습니다.']
        links=[('/학습코칭/#four-c','진단부터 상담까지 이어지는 4C'),('/상담문의/#ask-center','방문할 센터에 확인할 사항')]
    elif rel=='과목별학원/index.html':
        title='같은 학년이어도, 막히는 과정을 먼저 구분해요'
        ps=['초3부터 고2까지 영어·수학 안내에서 관심 학년을 고를 수 있습니다. 영어는 단어·문장·지문 중 어느 부분이 어려운지, 수학은 개념·조건 읽기·계산 중 어디에서 멈추는지 생각해 보세요.','AI 학습은 진단 결과에 따른 연습을 이해하는 데 참고할 수 있습니다. 프로그램 점수만으로 수업을 정하지 말고, 실제 배운 범위와 학생이 혼자 설명한 내용을 함께 보세요.']
        links=[('/학습코칭/#ai-learning','과목별 AI 학습의 역할'),('/학습가이드/#wrong','다시 볼 문제를 구분하는 방법')]
    elif rel.startswith('전국학원/'):
        stage=name.replace('학생학원','').replace('학원','')
        stagecopy={
         '초등':('스스로 시작하는 작은 경험부터','준비물을 꺼내고 과제를 읽고 마무리하는 세 장면에서 필요한 도움을 관찰해 보세요. 모두 대신해 주기보다 학생이 해 본 부분과 질문한 부분을 구분하는 것이 출발점입니다.','분량을 많이 늘리기 전에 짧은 계획과 재확인을 연결해 보세요. 영어·수학·독서 프로그램의 본사 안내와 실제 센터의 운영 대상은 다를 수 있으므로 수강 가능 여부를 따로 확인합니다.'),
         '중':('학교 공부와 혼자 복습하는 시간을 연결해요','과목별 과제와 평가 일정이 겹칠 때는 공부한 시간만으로 계획을 평가하기 어렵습니다. 아직 설명하지 못한 개념과 혼자 풀어 본 과제를 함께 적어 보세요.','수업에서 받은 설명이 자습에서도 이어지는지 확인할 질문을 준비해 보세요. 진단 결과를 어떤 연습과 상담에 연결하는지 알아보면 학생에게 맞는 관리 방향을 논의하기 좋습니다.'),
         '고등':('과목 선택과 재확인 계획을 함께 점검해요','현재 수강 과목, 학교 진도, 수행 과제의 마감부터 구분해 보세요. 풀이가 오래 걸린 이유가 개념의 빈틈인지, 조건을 해석하는 과정인지 짧게 남겨 두면 상담 자료가 됩니다.','익숙한 문제를 많이 푼 결과와 처음 본 문제에서 근거를 고른 과정은 다릅니다. AI 학습의 결과를 실제 답안과 함께 살펴보고, 다음 복습에서 무엇을 확인할지 정해 보세요.')}
        key='중' if name.startswith('중학생') else stage
        title,*ps=stagecopy[key]
        links=[('/학습코칭/#daily-care','계획·학습·생활 관리 살펴보기'),('/학습가이드/#planner','학교 일정에 맞춰 계획 정리하기')]
    else:
        grade=name[:2];subject='영어' if '영어' in name else '수학'
        title,p=TOPIC[grade]
        title=f'{grade} {subject}, '+title
        subjectp=('단어를 몰랐는지 문장 구조를 읽기 어려웠는지, 답의 근거를 찾지 못했는지 표시해 보세요. 어려움의 원인이 다르면 다시 읽을 내용과 연습도 달라집니다.' if subject=='영어' else '개념을 떠올리지 못한 문제와 조건을 놓친 문제, 계산에서 틀린 문제를 나누어 보세요. 풀이를 다시 적을 때는 왜 그 방법을 선택했는지도 남겨 봅니다.')
        ps=[p+' '+subjectp,f'{grade} {subject} 안내에서 관심 동네를 고른 뒤, 최근 답안과 학교에서 배운 범위를 바탕으로 상담해 보세요. 아래 프로그램 설명은 본사 학습 구성에 대한 안내이며 실제 개설 여부와 이용 조건은 해당 센터에 확인합니다.']
        links=[('/학습코칭/#ai-'+('english' if subject=='영어' else 'math'),f'AI {subject}의 진단과 연습 이해하기'),('/학습가이드/#'+('wrong' if subject=='영어' else 'exam'), '오답을 다음 복습으로 연결하기' if subject=='영어' else '학교 범위에 맞춰 다시 확인하기')]
    markup='<section class="pl-hub-brief" id="coaching-brief"><p class="pl-kicker">학생에게 필요한 학습코칭</p><h2>'+esc(title)+'</h2>'+''.join('<p>'+esc(p)+'</p>' for p in ps)+'<div class="pl-hub-links">'+''.join(f'<a href="{u}">{esc(t)}</a>' for u,t in links)+'</div></section>'
    return markup,title,[DOMAIN+u for u,t in links]

def graph_of(head):
    nodes=[]
    for tag in head.select('script[type="application/ld+json"]'):
        data=json.loads(tag.string or tag.get_text());nodes.extend(data.get('@graph',[data]));tag.decompose()
    return nodes
def append_graph(head,nodes):
    tag=BeautifulSoup('<script type="application/ld+json"></script>','html.parser').script
    tag.string=jsontext({'@context':'https://schema.org','@graph':nodes});head.append(tag)
def faq_markup(rows):
    return '<section class="shell pl-section pl-faq" id="faq"><h2>자주 묻는 질문</h2><div class="pl-faq-list">'+''.join('<details><summary>'+esc(r['q'])+'</summary><p>'+esc(r['a'])+'</p></details>' for r in rows)+'</div></section>'
def placeholders(content):
    regions='<section class="shell pl-section" id="home-regions"><div class="pl-section-head"><p class="pl-kicker">가까운 지역부터</p><h2>학생의 학교급에 맞는 동네 안내</h2><p>동네 페이지에서 연결된 센터의 위치와 수업 조건을 확인하세요.</p></div><div class="pl-grid pl-three">'
    for key,tip in [('초등학생학원','준비·질문·마무리 습관부터'),('중학생학원','학교 과제와 복습의 연결'),('고등학생학원','수강 과목과 공부 우선순위')]:
        regions+=f'<a class="pl-card pl-link-card" href="/전국학원/{key}/"><h3>{key}</h3><p>{tip}</p><span class="pl-link-label">동네별 안내 보기 →</span></a>'
    regions+='</div><a class="pl-text-link" href="/전국학원/">전국학원 전체 안내</a></section>'
    subjects='<div class="pl-subject-grid">'
    for label,grades in [('초등',['초3','초4','초5','초6']),('중등',['중1','중2','중3']),('고등',['고1','고2'])]:
        subjects+=f'<article class="pl-grade-card"><h3>{label}</h3>'+''.join(f'<a href="/과목별학원/{g}{s}학원/">{g} {s}학원 →</a>' for g in grades for s in ['영어','수학'])+'</article>'
    subjects+='</div>'
    videos='<div class="pl-grid pl-three">'
    for id,file,title in [('avpJfW7eIV0','video-student.jpg','학생의 질문에서 시작하는 코칭'),('f_skFu40U04','video-coaching.jpg','공부 과정을 돌아보는 공식 인터뷰'),('UIXUaBZdNXU','video-exam.jpg','자기주도학습을 소개하는 이야기')]:
        videos+=f'<a class="pl-video-card" href="https://www.youtube.com/watch?v={id}" target="_blank" rel="noopener noreferrer"><img src="/assets/official-learning/{file}" alt="{title} 공식 영상" width="480" height="360" loading="lazy" decoding="async"><div class="pl-video-copy"><h3>{title}</h3><span class="pl-link-label">YouTube에서 영상 보기 · 새 창 ↗</span></div></a>'
    videos+='</div>'
    return content.replace('<!-- subject-links -->',subjects).replace('<!-- home-regions -->',regions).replace('<!-- video-cards -->',videos)

def main():
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==BASE
    config=json.loads((DATA/'content.json').read_text('utf-8'))
    old=json.loads((REPORT/'generation.json').read_text('utf-8')) if (REPORT/'generation.json').exists() else {}
    oldhash=old.get('files',{})
    hubs=['전국학원/index.html','과목별학원/index.html']+[p.relative_to(ROOT).as_posix() for root in ['전국학원','과목별학원'] for p in sorted((ROOT/root).glob('*/index.html'))]
    assert len(hubs)==23
    output={};targets=[]
    for rel in [*CORE.values(),*hubs]:
        key=next((k for k,v in CORE.items() if v==rel),None)
        template=raw('index.html' if key=='coaching' else rel)
        head=BeautifulSoup(re.search(r'<head\b[^>]*>(.*?)</head>',template,re.S).group(0),'html.parser').head
        nodes=graph_of(head);url=DOMAIN+route(rel)
        if key:
            meta=config['pages'][key]
            fragment=placeholders((DATA/(key+'.html')).read_text('utf-8'))
            rows=[{'q':r[0],'a':r[1]} if isinstance(r,list) else r for r in config['faq'][key]]
            fragment=fragment.replace('<!-- page-faq -->',faq_markup(rows))
            parsed=BeautifulSoup(fragment,'html.parser')
            assert len(parsed.select('main'))==1 and len(parsed.select('h1'))==1
            h1=parsed.h1.get_text(' ',strip=True)
            head.title.string=meta['title']
            for attr,name,value in [('name','description',meta['description']),('property','og:title',meta['title']),('property','og:description',meta['description']),('property','og:url',url),('name','twitter:title',meta['title']),('name','twitter:description',meta['description'])]:
                tag=head.find('meta',attrs={attr:name})
                if tag:tag['content']=value
            head.find('link',rel='canonical')['href']=url
            if key=='coaching':
                for tag in head.find_all('meta',attrs={'property':'og:image'}):tag['content']=DOMAIN+'/assets/official-learning/brand-learning.png'
            orgs=[n for n in nodes if n.get('@id') in [DOMAIN+'/#organization',DOMAIN+'/#website']]
            for n in orgs:
                if n.get('@id')==DOMAIN+'/#organization':
                    n={'@type':'Organization','@id':DOMAIN+'/#organization','name':'채움학습','url':DOMAIN+'/'}
            nodes=[{'@type':'Organization','@id':DOMAIN+'/#organization','name':'채움학습','url':DOMAIN+'/'},{'@type':'WebSite','@id':DOMAIN+'/#website','name':'채움학습.com','url':DOMAIN+'/','publisher':{'@id':DOMAIN+'/#organization'}}]
            sections=[s for s in parsed.select('section[id]') if s.find(['h2','h3'])]
            nodes.append({'@type':'WebPage','@id':url+'#webpage','url':url,'name':meta['title'],'description':meta['description'],'inLanguage':'ko-KR','isPartOf':{'@id':DOMAIN+'/#website'},'about':[{'@type':'Thing','name':'학습코칭'},{'@type':'Thing','name':'자기주도학습'}],'dateModified':DATE,'hasPart':[{'@id':url+'#'+s['id']} for s in sections]})
            for s in sections:nodes.append({'@type':'WebPageElement','@id':url+'#'+s['id'],'url':url+'#'+s['id'],'name':s.find(['h2','h3']).get_text(' ',strip=True),'isPartOf':{'@id':url+'#webpage'}})
            if key in ('coaching','guide'):
                nodes.append({'@type':'Article','@id':url+'#article','headline':h1,'description':meta['description'],'inLanguage':'ko-KR','mainEntityOfPage':{'@id':url+'#webpage'},'publisher':{'@id':DOMAIN+'/#organization'},'dateModified':DATE,'articleSection':[s.find(['h2','h3']).get_text(' ',strip=True) for s in sections],'mentions':[{'@type':'Thing','name':n} for n in (['4C 학습관리','AI 영어','AI 수학','AI 국어','AI 독서'] if key=='coaching' else ['플래너','복습','오답 정리'])]})
            nodes.append({'@type':'FAQPage','@id':url+'#faq-schema','url':url+'#faq','mainEntity':[{'@type':'Question','name':r['q'],'acceptedAnswer':{'@type':'Answer','text':r['a']}} for r in rows]})
            nodes.append({'@type':'BreadcrumbList','@id':url+'#breadcrumb','itemListElement':[{'@type':'ListItem','position':1,'name':'홈','item':DOMAIN+'/'}]+([] if key=='home' else [{'@type':'ListItem','position':2,'name':dict((v,k) for v,k in NAV)[route(rel)],'item':url}])})
            body='<body class="learning-upgraded"><div class="site-shell">'+nav(rel)+fragment+footer()+CTA+'</div></body>'
        else:
            addition,title,links=brief(rel)
            body=re.search(r'<body\b.*?</body>',template,re.S).group(0)
            body=re.sub(r'<body([^>]*)class="([^"]*)"',r'<body\1class="\2 learning-upgraded"',body,count=1)
            body=re.sub(r'<header\b.*?</header>',lambda m:nav(rel),body,count=1,flags=re.S)
            body=re.sub(r'<footer\b.*?</footer>',lambda m:footer(),body,count=1,flags=re.S)
            body,n=re.subn(r'(<section\b[^>]*class="page-hero"[^>]*>.*?</section>)',lambda m:m.group(0)+addition,body,count=1,flags=re.S)
            assert n==1,rel
            for node in nodes:
                if node.get('@id')==url+'#webpage':
                    node.setdefault('hasPart',[]).append({'@id':url+'#coaching-brief'});node['relatedLink']=links
            nodes.append({'@type':'WebPageElement','@id':url+'#coaching-brief','url':url+'#coaching-brief','name':title,'isPartOf':{'@id':url+'#webpage'}})
        append_graph(head,nodes)
        head.append(BeautifulSoup(f'<link rel="stylesheet" href="{CSS}">','html.parser').link)
        # New root-relative nav and content also require root-relative core assets.
        for tag in head.select('link[href]'):
            href=tag['href']
            if not href.startswith(('/','http')):
                tag['href']='/'+href.replace('../','').removeprefix('./')
        text='<!DOCTYPE html>\n<html lang="ko">'+str(head)+'\n'+body+'\n</html>\n'
        output[rel]=text.encode('utf-8')
        targets.append({'path':rel,'url':url,'kind':key or 'hub'})
    sitemap=raw('sitemap.xml')
    urls={t['url'] for t in targets}
    def update_url(m):
        text=m.group(0);loc=html.unescape(re.search(r'<loc>(.*?)</loc>',text).group(1))
        if DOMAIN+unquote(urlsplit(loc).path) in urls:
            text=re.sub(r'<lastmod>.*?</lastmod>',f'<lastmod>{DATE}</lastmod>',text)
        return text
    sitemap=re.sub(r'<url>.*?</url>',update_url,sitemap,flags=re.S)
    sitemap=sitemap.replace('</urlset>',f'<url><loc>{DOMAIN}/학습코칭/</loc><lastmod>{DATE}</lastmod></url>\n</urlset>')
    output['sitemap.xml']=sitemap.encode('utf-8')
    rss=ET.fromstring(raw('rss.xml'));channel=rss.find('channel')
    generated_at=old.get('generatedAt',datetime.now().astimezone().isoformat())
    stamp=format_datetime(datetime.fromisoformat(generated_at))
    channel.find('lastBuildDate').text=stamp
    # Existing published item dates remain unchanged; only the feed build time
    # and the newly created coaching item receive this generation time.
    item=ET.SubElement(channel,'item')
    for k,v in [('title',config['pages']['coaching']['title']),('link',DOMAIN+'/학습코칭/'),('description',config['pages']['coaching']['description']),('pubDate',stamp),('guid',DOMAIN+'/학습코칭/')]:ET.SubElement(item,k).text=v
    item.find('guid').set('isPermaLink','true');ET.indent(rss)
    output['rss.xml']=ET.tostring(rss,encoding='utf-8',xml_declaration=True)+b'\n'
    llms=raw('llms.txt').replace('## 핵심 페이지','## 핵심 페이지\n\n- 학습코칭: '+DOMAIN+'/학습코칭/')
    llms+='\n## 학습 프로그램 안내\n\n4C 진단·처방·지도·상담과 AI 영어·수학·국어·독서의 구성은 학습코칭 페이지에서 확인할 수 있습니다. 본사 프로그램 소개와 센터별 실제 개설 과목·학년·비용·시간표는 구분합니다.\n'
    output['llms.txt']=llms.encode('utf-8')
    changed=[]
    for rel,data in output.items():
        path=ROOT/rel
        if path.exists():
            existing=path.read_bytes()
            if rel in oldhash:assert digest(existing)==oldhash[rel],('Intervening edit',rel)
            else:assert existing.replace(b'\r\n',b'\n')==raw(rel).encode('utf-8').replace(b'\r\n',b'\n'),('Not baseline',rel)
    for rel,data in output.items():
        path=ROOT/rel;path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists() or path.read_bytes()!=data:path.write_bytes(data);changed.append(rel)
    REPORT.mkdir(parents=True,exist_ok=True)
    report={'baseline':BASE,'date':DATE,'generatedAt':generated_at,'localOnly':True,'targets':targets,'files':{p:digest(b) for p,b in output.items()},'changed':changed}
    (REPORT/'generation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'targetPages':len(targets),'changedFiles':len(changed)},ensure_ascii=False))

if __name__=='__main__':main()
