/** Verified center facts and a small, reviewed pilot. No new routes or indexing changes. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {preserveTeacherContent, laterDate} from './teacher-build-preservation.mjs';

const project = path.dirname(fileURLToPath(import.meta.url));
const config = JSON.parse(fs.readFileSync(path.join(project, 'seo-content-improvements.json'), 'utf8'));
const origin = 'https://xn--ru4bz7e9zf0zk.com';
const date = config.reviewedAt;
const nationalCategories = ['고등학생학원', '중학생학원', '초등학생학원'];
const scriptRx = /(<script\b[^>]*type=["']application\/ld\+json["'][^>]*>)([\s\S]*?)(<\/script>)/gi;
const e = value => String(value ?? '').replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
const text = value => value.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
const encoded = value => value.split('/').map(encodeURIComponent).join('/');
const localSlug = value => value.trim().replace(/\s+/g, '').replace(/[\\/:*?"<>|#%&+]/g, '');
const json = value => JSON.stringify(value).replaceAll('<', '\\u003c');
const types = node => [].concat(node?.['@type'] || []);
const link = (url, label, cls = '') => `<a${cls ? ` class="${cls}"` : ''} href="${e(url)}">${e(label)}</a>`;
const outsideLink = (url, label, cls = '') => `<a${cls ? ` class="${cls}"` : ''} href="${e(url)}" target="_blank" rel="noopener">${e(label)}<span class="si-sr-only"> (새 창)</span></a>`;

function visit(value, fn) {
  if (!value || typeof value !== 'object') return;
  if (Array.isArray(value)) { value.forEach(v => visit(v, fn)); return; }
  fn(value); Object.values(value).forEach(v => visit(v, fn));
}

export function sanitizeNational(html, area) {
  let next = html.replace(/<section\b[^>]*>(?:(?!<section\b)[\s\S])*?<\/section>/gi, section =>
    /PARENT REVIEW|class=["']review-grid["']/.test(section) ? '' : section);
  next = next.replace(scriptRx, (all, start, body, end) => {
    const data = JSON.parse(body);
    visit(data, n => {
      for (const key of ['aggregateRating', 'review', 'openingHours', 'openingHoursSpecification']) delete n[key];
      if (Array.isArray(n.hasPart)) n.hasPart = n.hasPart.filter(p => !/학부모 후기|상담 후기/.test(p?.name || ''));
      if (Array.isArray(n.articleSection)) n.articleSection = n.articleSection.filter(p => !/학부모 후기|상담 후기/.test(p));
    });
    return json(data) === body ? all : start + json(data) + end;
  });
  // The workbook records an opening reference, not a verified closing time.
  // Keep this as visible guidance instead of inventing precise schema hours.
  const note = `<p data-verified-hours="20260928"><strong>${e(area.displayName)} 운영 참고:</strong> ${e(area.openingReference)}. ${e(area.weekend)} 방문 시간과 해당 과목의 시간표는 지점에 확인해 주세요.</p>`;
  next = next.replace(/<p data-verified-hours="20260928">[\s\S]*?<\/p>/g, '');
  if (next.includes('id="actual-center"')) {
    next = next.replace(/(<section\b[^>]*\bid="actual-center"[^>]*>[\s\S]*?)(<div class="cd-actions">)/, '$1' + note + '$2');
  }
  if (next !== html) next = next.replace(scriptRx, (all, start, body, end) => {
    const data = JSON.parse(body);
    visit(data, n => { if (types(n).some(t => ['WebPage', 'Article'].includes(t))) n.dateModified = date; });
    return start + json(data) + end;
  });
  return next;
}

export function pilotContent(town, category, html) {
  const c = config.pilots[town], p = c.pages[category], broad = category === '고등학생학원';
  const grade = broad ? null : category.slice(0, 2);
  const highMath = c.subjects['수학'].filter(g => g.startsWith('고'));
  if (grade && !highMath.includes(grade)) throw Error(`Unverified pilot course: ${town} ${grade}`);
  const gradeText = highMath.join('·');
  const title = broad ? `${town} 고등 수학학원·영어학원 | ${c.sourceName} 수강 안내` : `${town} ${grade} 수학학원 | ${c.sourceName} 학년·위치·교습비`;
  const heading = broad ? `${town} 고등 수학·영어학원 안내` : `${town} ${grade} 수학학원 안내`;
  const description = broad
    ? `${town} 고등 수학·영어 수강을 위한 ${c.sourceName}의 과목별 학년·주소·운영 참고와 교습비 자료를 확인하세요.`
    : `${town} ${grade} 수학 수강을 위한 ${c.sourceName}의 학년·위치·교습비 자료와 ${grade === '고1' ? '풀이 기록을 활용한 상담 준비를' : '선택 과목·복습 계획 확인 방법을'} 살펴보세요.`;
  if ([...description].length > 80) throw Error(`Description too long: ${p.key}`);
  const lead = broad
    ? `${c.displayName}의 고등 수학 안내 학년은 ${gradeText}입니다. 영어 등 다른 과목의 학년과 방문 조건도 함께 확인할 수 있습니다.`
    : `${c.displayName}의 수학 안내 학년에 ${grade}이 포함돼 있습니다. 주소와 운영 참고를 확인하고, 학생의 학교 진도·가능한 요일에 맞는 수업을 상담해 보세요.`;
  const mathNote = highMath.includes('고3')
    ? '고3이 안내 학년에 포함돼 있습니다. 선택 과목과 현재 개설 과정, 시간표는 등록 전에 확인해 주세요.'
    : '고3 수학은 안내 학년에 포함돼 있지 않습니다. 별도 과정의 개설 여부는 지점에 확인해 주세요.';
  const courseRows = Object.entries(c.subjects).map(([subject, grades]) => {
    const eligible = grades.filter(g => g.startsWith('고'));
    return `<tr><th scope="row">${e(subject)}</th><td>${e(eligible.join('·') || '개설 학년 문의 필요')}</td></tr>`;
  }).join('');
  const preparations = grade === '고2' ? [
    ['선택 과목과 현재 진도', '학교에서 수강하는 수학 과목명, 교재와 최근 배운 단원을 적어 오세요. 필요한 과목을 해당 지점에서 수강할 수 있는지 먼저 확인합니다.'],
    ['이전 단원과 연결되는 오답', '새 단원이 어려운지, 이전 개념이나 계산에서 막히는지 최근 풀이에 표시해 보세요. 정답뿐 아니라 풀이를 멈춘 위치가 상담 자료가 됩니다.'],
    ['시험 준비와 누적 복습', '학교 시험 일정, 다른 과목의 학습량과 가능한 요일을 함께 적어 오세요. 시험 범위와 이전 오답을 언제 나눠 복습할지 질문해 보세요.']
  ] : grade === '고1' ? [
    ['계산·개념·문제 해석 구분', '최근 시험지나 풀던 교재에서 틀린 문제를 골라 보세요. 계산 실수인지, 개념을 몰랐는지, 문장의 조건을 식으로 옮기기 어려웠는지 표시하면 상담이 구체적입니다.'],
    ['학교 진도와 시작 지점', '최근 배운 단원과 학교의 평가 안내를 준비하세요. 중학교 때부터 남은 공백이 있다면 현재 진도와 함께 살펴볼 수 있도록 질문을 적어 오세요.'],
    ['혼자 다시 풀 수 있는지', '해설을 본 뒤 답을 가리고 다시 푼 흔적을 준비해 보세요. 숙제량과 질문 방법, 오답을 다시 확인하는 주기를 상담에서 확인합니다.']
  ] : [
    ['과목별 학년부터 확인', '수학과 영어의 안내 학년은 같지 않을 수 있습니다. 희망 과목, 현재 학년, 선택 과목을 함께 알려 주세요.'],
    ['학습 자료로 상담 준비', '최근 시험지와 현재 교재, 오답 흔적 중 한두 가지를 준비해 보세요. 계산·개념·문제 해석 중 어디에서 어려운지 이야기하기 좋습니다.'],
    ['시간표와 교습비 비교', '등원 가능한 요일과 학교 일정을 정리해 주세요. 수업 횟수·시간·교재비와 최종 교습비를 같은 조건으로 확인합니다.']
  ];
  const questions = [
    [`${c.sourceName}에서 고등 수학은 몇 학년까지 안내하나요?`, `수학의 고등 안내 학년은 ${gradeText}입니다. ${mathNote}`],
    ['교습비는 어디에서 확인하나요?', `${c.sourceName} 교습비 자료 링크에서 확인할 수 있습니다. 공통 홍보물의 금액과 현재 지점별 금액은 다를 수 있으므로 과목·횟수·시간·교재비를 포함한 최종 금액을 상담에서 확인해 주세요.`],
    ['평일과 주말 방문 시간은 어떻게 확인하나요?', `운영 참고는 ${c.openingReference}입니다. ${c.weekend} 이는 모든 수업의 시작·종료 시간을 뜻하지 않으며 방문 가능 시간과 과목별 시간표는 사전에 확인해 주세요.`]
  ];
  const related = [
    [c.path, `${c.sourceName} 전체 수강 조건·교육비`],
    [`/전국학원/고등학생학원/${town}/`, `${town} 고등 과목별 수강 안내`],
    ...['고1', '고2'].filter(g => highMath.includes(g)).map(g => [`/과목별학원/${g}수학학원/${town}/`, `${town} ${g} 수학 안내`]),
    ...(grade && c.subjects['영어'].includes(grade) ? [[`/과목별학원/${grade}영어학원/${town}/`, `${town} ${grade} 영어 안내`]] : [])
  ].filter(([url]) => url !== p.key);
  const sections = [['enrollment','수강 학년'],['preparation','상담 준비'],['schools','학교 참고'],['fees-hours','시간·교습비'],['visit','위치·이미지'],['questions','질문과 답변'],['related','관련 안내']];
  const media = p.media;
  const img = (m, alt, extra='') => `<img src="${e(m.src)}" alt="${e(alt)}" width="${m.width}" height="${m.height}" loading="lazy" decoding="async" ${extra}>`;
  const parent = broad ? '/전국학원/고등학생학원/' : `/과목별학원/${category}/`;
  const main = `<main id="${e(p.originalMainId || 'main-content')}" class="si-main" data-search-pilot="20260928">
    <section class="si-hero">
      <nav class="si-breadcrumb" aria-label="현재 위치">${link('/', '홈')}<span>/</span>${link(parent, broad ? '고등학생학원' : `${grade} 수학학원`)}<span>/</span><span aria-current="page">${e(town)}</span></nav>
      <p class="si-eyebrow">${e(c.sourceName)} · 고등학생 수강 안내</p><h1>${e(heading)}</h1><p class="si-lead">${e(lead)}</p>
      <dl class="si-facts" id="quick-facts"><div><dt>수학 안내 학년</dt><dd>${e(gradeText)}</dd></div><div><dt>운영 참고</dt><dd>${e(c.openingReference)}</dd></div><div class="si-address"><dt>${e(c.sourceName)} 주소</dt><dd>${e(c.address)}</dd></div></dl>
      <div class="si-actions">${link('tel:010-6839-8283','전화 상담','si-button')}${outsideLink(c.feeLink,'교습비 자료','si-button si-secondary')}${link(encoded(c.path),'지점 상세','si-button si-secondary')}</div>
      <p class="si-small">채움학습 상담 연결 · 실제 반 편성 및 방문 시간은 지점별 확인</p>
    </section>
    <nav class="si-toc" aria-label="이 페이지에서 확인할 내용">${sections.map(([id,label]) => link('#'+id,label)).join('')}</nav>
    <section id="enrollment" class="si-section"><h2>${e(c.sourceName)} 고등 과목별 학년</h2><p>${e(mathNote)}</p><table class="si-table"><caption>지점 안내 자료에 기재된 고등 수강 학년</caption><thead><tr><th scope="col">과목</th><th scope="col">안내 학년</th></tr></thead><tbody>${courseRows}</tbody></table><p class="si-small">현재 개설 과정·선택 과목·잔여 자리·수업 시간은 상담에서 확인해 주세요.</p></section>
    <section id="preparation" class="si-section"><h2>${e(grade ? `${grade} 수학 상담에 준비할 것` : '고등 수학·영어 상담 준비')}</h2><div class="si-preparation">${preparations.map(([h,b],i)=>`<article><span class="si-step">0${i+1}</span><h3>${e(h)}</h3><p>${e(b)}</p></article>`).join('')}</div><p class="si-small">상담 준비를 위한 안내입니다. 진단 방식, 플래너·오답 점검, 학부모 공유 주기는 지점에 확인해 주세요.</p></section>
    <section id="schools" class="si-section"><h2>${e(town)} 학교 참고와 시험 준비</h2><ul class="si-schools">${c.schools.map(s=>`<li>${e(s)}</li>`).join('')}</ul><p>위 학교는 지역 상담을 위한 참고 학교입니다. 학생이 가져온 최신 진도표·평가 안내를 바탕으로 해당 학교와 과목의 수강 가능 여부를 확인해 주세요.</p></section>
    <section id="fees-hours" class="si-section"><h2>운영 참고와 교습비 확인</h2><dl class="si-details"><div><dt>평일</dt><dd>${e(c.openingReference)}</dd></div><div><dt>주말</dt><dd>${e(c.weekend)}</dd></div><div><dt>교습비</dt><dd>${outsideLink(c.feeLink,`${c.sourceName} 교습비 자료 보기`)}<p>과목·수업 횟수·시간·교재비를 포함한 최종 금액을 확인해 주세요. 공통 안내 이미지의 금액과 실제 지점별 금액은 다를 수 있습니다.</p></dd></div><div><dt>등록 정보</dt><dd>${e(c.registeredName)}<br>${e(c.registrationNumber)}</dd></div></dl></section>
    <section id="visit" class="si-section"><h2>${e(c.sourceName)} 찾아가는 길</h2><p class="si-location">${e(c.address)}</p><p>${e(c.locationGuide)}</p><div class="si-actions">${outsideLink(c.mapLink,'네이버 지도에서 위치 보기','si-button si-secondary')}${link(encoded(c.path),`${c.sourceName} 안내 보기`,'si-button si-secondary')}</div>
      ${img(media[0],media[0].alt,'hidden style="display:none"')}
      <details class="si-media-details"><summary>학습코칭 공통 안내 이미지 펼쳐보기</summary><p>공통 프로그램 안내입니다. 해당 지점의 과목·학년·교습비는 위 수강 정보와 지점 상담을 기준으로 확인해 주세요.</p>${img(media[1],`${town} 수학학원 본문`)}</details>
      <figure class="si-map">${img(media[2],`${town} 수학학원 지도`)}<figcaption>${e(c.sourceName)} 위치 안내</figcaption></figure>
    </section>
    <section id="questions" class="si-section"><h2>질문과 답변</h2>${questions.map(([q,a])=>`<details class="si-faq"><summary>${e(q)}</summary><p>${e(a)}</p></details>`).join('')}</section>
    <section id="related" class="si-section"><h2>같은 지역에서 함께 확인하기</h2><div class="si-related">${related.map(([u,l])=>link(encoded(u),l)).join('')}</div></section>
    <p class="si-reviewed">안내 자료 확인·내용 수정 <time datetime="${date}">${date}</time> · 수강 학년과 방문 조건은 변경될 수 있습니다.</p>
  </main>`;
  const url = origin + p.key, centerId = origin + encoded(c.path) + '#center';
  const oldGraphs = [...html.matchAll(scriptRx)].flatMap(m => {const v=JSON.parse(m[2]);return v['@graph'] || [v];});
  const oldArticle = oldGraphs.find(n=>types(n).includes('Article'));
  const oldBreadcrumb = oldGraphs.find(n=>types(n).includes('BreadcrumbList'));
  const primary = origin + media[0].src;
  const nodes = [
    {'@type':'Organization','@id':origin+'/#organization',name:'채움학습',url:origin+'/',contactPoint:{'@type':'ContactPoint',telephone:'010-6839-8283',contactType:'학습 상담'}},
    {'@type':'WebSite','@id':origin+'/#website',url:origin+'/',name:'채움학습',publisher:{'@id':origin+'/#organization'}},
    {'@type':['EducationalOrganization','LocalBusiness'],'@id':centerId,name:c.registeredName,alternateName:c.displayName,url:origin+encoded(c.path),address:{'@type':'PostalAddress',streetAddress:c.address,addressCountry:'KR'},hasMap:c.mapLink},
    {'@type':'ImageObject','@id':url+'#primaryimage',url:primary,caption:media[0].alt},
    {'@type':'WebPage','@id':url+'#webpage',url,name:title,description,inLanguage:'ko-KR',isPartOf:{'@id':origin+'/#website'},about:{'@id':centerId},mainEntity:{'@id':url+'#article'},dateModified:date,primaryImageOfPage:{'@id':url+'#primaryimage'},breadcrumb:{'@id':url+'#breadcrumb'},hasPart:sections.map(([id,label])=>({'@type':'WebPageElement','@id':url+'#'+id,name:label,url:url+'#'+id}))},
    {'@type':'Article','@id':url+'#article',headline:heading,description,abstract:lead,inLanguage:'ko-KR',mainEntityOfPage:{'@id':url+'#webpage'},datePublished:oldArticle?.datePublished || date,dateModified:date,publisher:{'@id':origin+'/#organization'},author:{'@id':origin+'/#organization'},image:primary,articleSection:sections.map(([,label])=>label)},
    {'@type':'FAQPage','@id':url+'#faq',url:url+'#questions',mainEntity:questions.map(([q,a])=>({'@type':'Question',name:q,acceptedAnswer:{'@type':'Answer',text:a}}))},
    {'@type':'ItemList','@id':url+'#related',itemListElement:related.map(([u,l],i)=>({'@type':'ListItem',position:i+1,name:l,url:origin+encoded(u)}))}
  ];
  if (oldBreadcrumb) nodes.push(oldBreadcrumb);
  let next = html.replace(/<main\b[^>]*>[\s\S]*?<\/main>/i,main);
  next = next.replace(/<title>[\s\S]*?<\/title>/i,`<title>${e(title)}</title>`);
  const updates = {'description':description,'og:description':description,'twitter:description':description,'og:title':title,'twitter:title':title};
  const seen = new Set();
  next = next.replace(/<meta\b[^>]*>/gi, tag => {
    const key = tag.match(/(?:name|property)=["']([^"']+)["']/i)?.[1];
    if (!Object.hasOwn(updates,key)) return tag;
    if (seen.has(key)) return ''; seen.add(key);
    return `<meta ${key.startsWith('og:')?'property':'name'}="${key}" content="${e(updates[key])}">`;
  });
  const schemaMarkup = `<script type="application/ld+json">${json({'@context':'https://schema.org','@graph':nodes})}</script>`;
  let schemaPlaced = false;
  next = next.replace(scriptRx, () => {
    if (schemaPlaced) return '';
    schemaPlaced = true;
    return schemaMarkup;
  });
  const missing = Object.entries(updates).filter(([k])=>!seen.has(k)).map(([k,v])=>`<meta ${k.startsWith('og:')?'property':'name'}="${k}" content="${e(v)}">`).join('');
  const stylesheet = html.includes('/assets/search-improvements.css') ? '' : '<link rel="stylesheet" href="/assets/search-improvements.css">';
  next = next.replace('</head>',missing+stylesheet+(schemaPlaced?'':schemaMarkup)+'</head>');
  return {html:next,title,description};
}

export function applyToRoot(root, {check=false, backup, report}={}) {
  const changes = new Map(), descriptions = {};
  const read = rel => fs.readFileSync(path.join(root,rel),'utf8');
  function plan(rel,next) { const before=read(rel); next=preserveTeacherContent(before,next); if (before!==next) changes.set(rel,next); }
  for (const [town,area] of Object.entries(config.areas)) {
    for (const category of nationalCategories) {
      const rel=`전국학원/${category}/${localSlug(town)}/index.html`;
      plan(rel,sanitizeNational(read(rel),area));
    }
  }
  for (const rel of ['전국학원/index.html',...nationalCategories.map(c=>`전국학원/${c}/index.html`)]) {
    plan(rel,read(rel).replaceAll('FAQ, 학부모 후기, 근처 학원페이지','FAQ, 근처 학원페이지'));
  }
  for (const [town,c] of Object.entries(config.pilots)) for (const [category,p] of Object.entries(c.pages)) {
    const rel=p.key.slice(1)+'index.html';
    const result=pilotContent(town,category,changes.get(rel)||read(rel));
    plan(rel,result.html); descriptions[p.key.replace(/\/$/,'')]=result.description;
  }
  if (changes.size) {
    const keys=new Set([...changes.keys()].map(r=>'/'+r.replace(/index\.html$/,'')));
    const sitemap=read('sitemap.xml').replace(/<url>\s*<loc>([^<]+)<\/loc>([\s\S]*?)<\/url>/g,(all,url,rest)=>{
      if (!keys.has(decodeURIComponent(new URL(url).pathname))) return all;
      const modified=laterDate(rest.match(/<lastmod>([^<]*)<\/lastmod>/)?.[1],date);
      return `<url><loc>${url}</loc>${/<lastmod>/.test(rest)?rest.replace(/<lastmod>[^<]*<\/lastmod>/,`<lastmod>${modified}</lastmod>`):`<lastmod>${modified}</lastmod>`+rest}</url>`;
    });
    plan('sitemap.xml',sitemap);
  }
  if (!check) for (const [rel,value] of changes) {
    const file=path.resolve(root,rel);
    if (!file.startsWith(path.resolve(root)+path.sep)) throw Error('Unsafe path');
    if (backup) { const b=path.resolve(backup,rel);if(!fs.existsSync(b)){fs.mkdirSync(path.dirname(b),{recursive:true});fs.copyFileSync(file,b);} }
    fs.writeFileSync(file,value,'utf8');
  }
  const result={check,changed:changes.size,htmlChanged:[...changes.keys()].filter(f=>f.endsWith('.html')).length,paths:[...changes.keys()],descriptions};
  if(report) fs.writeFileSync(report,JSON.stringify(result,null,2));
  return result;
}

if (process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const arg=name=>process.argv.find(a=>a.startsWith(name+'='))?.slice(name.length+1);
  const result=applyToRoot(path.resolve(project,arg('--root')||'.'),{check:process.argv.includes('--check'),backup:arg('--backup'),report:arg('--report')});
  console.log(JSON.stringify({check:result.check,changed:result.changed,htmlChanged:result.htmlChanged,pilotPages:Object.keys(result.descriptions).length}));
  if(result.check&&result.changed)process.exitCode=1;
}
