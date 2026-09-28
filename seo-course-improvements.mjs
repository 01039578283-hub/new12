/** Source-bounded course notices and reviewed branch layouts. No route or index changes. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const project = path.dirname(fileURLToPath(import.meta.url));
const config = JSON.parse(fs.readFileSync(path.join(project, 'seo-course-improvements.json'), 'utf8'));
const origin = 'https://xn--ru4bz7e9zf0zk.com';
const scriptRx = /(<script\b[^>]*type=["']application\/ld\+json["'][^>]*>)([\s\S]*?)(<\/script>)/gi;
const escape = value => String(value ?? '').replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const plain = value => value.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
const encode = value => value.split('/').map(encodeURIComponent).join('/');
const json = value => JSON.stringify(value).replaceAll('<','\\u003c');
const types = value => [].concat(value?.['@type'] || []);
const link = (url,label) => `<a class="cd-button cd-secondary" href="${escape(url)}">${escape(label)}</a>`;
const gradeText = grades => ['초','중','고'].flatMap(stage => {
  const ns=grades.filter(g=>g.startsWith(stage)).map(g=>+g[1]).sort((a,b)=>a-b);
  if(!ns.length)return [];
  if(ns.at(-1)-ns[0]+1===ns.length)return stage+ns[0]+(ns.length>1?'~'+stage+ns.at(-1):'');
  return ns.map(n=>stage+n).join('·');
}).join(' · ');

function walk(value, fn) {
  if (!value || typeof value !== 'object') return;
  if (Array.isArray(value)) { value.forEach(v=>walk(v,fn)); return; }
  fn(value); Object.values(value).forEach(v=>walk(v,fn));
}
function withMetadata(html, description, transform) {
  let next=html.replace(/<meta\b[^>]*>/gi,tag=>{
    const key=tag.match(/(?:name|property)=["']([^"']+)["']/i)?.[1];
    return ['description','og:description','twitter:description'].includes(key)
      ? `<meta ${key.startsWith('og:')?'property':'name'}="${key}" content="${escape(description)}">` : tag;
  });
  next=next.replace(scriptRx,(all,start,body,end)=>{
    const data=JSON.parse(body);
    if(transform)transform(data);
    walk(data,n=>{
      if(types(n).some(t=>['WebPage','Article'].includes(t))){n.description=description;n.dateModified=config.reviewedAt;}
    });
    return start+json(data)+end;
  });
  if(!next.includes('/assets/course-improvements.css'))next=next.replace('</head>','<link rel="stylesheet" href="/assets/course-improvements.css"></head>');
  return next;
}

export function courseContent(html, p) {
  // Reviewed math pages are owned by the subsequent math-specific build step.
  if(html.includes('data-math-review="20260929"'))return html;
  const centerId=origin+encode(p.branchPath)+'#center';
  const answer=p.guidance;
  const notice=`<section class="cd-section cd-local-callout ci-course-notice" id="actual-center" aria-labelledby="actual-center-title" data-course-review="20260928"><div class="cd-section-heading"><p class="ci-label">${escape(p.grade+' '+p.subject)} · ${escape(p.status)}</p><h2 id="actual-center-title">${escape(p.centerName)} 수강 전 확인</h2></div><p class="ci-guidance">${escape(answer)}</p><dl class="ci-facts"><div><dt>상담 지점 주소</dt><dd>${escape(p.address)}</dd></div><div><dt>운영 참고</dt><dd>${escape(p.openingReference)} · 방문 시간 별도 확인</dd></div></dl><div class="cd-actions">${link(encode(p.branchPath),p.centerName+' 수강 조건')}${link(p.feeLink,'지점 교습비 자료')}${link(p.mapLink,'지도 확인')}</div><p class="ci-small">아래 학습 내용은 상담 준비를 위한 안내입니다. 수업 장소·시간표·접수 가능 여부를 확인한 뒤 방문해 주세요.</p></section>`;
  let next=html.replace(/<section\b[^>]*\bid="actual-center"[^>]*>[\s\S]*?<\/section>/, '');
  if(next===html)throw Error('Missing actual-center block: '+p.town+' '+p.grade+p.subject);
  // Keep the page's teaching guidance, but do not present conflicting grade lists as availability.
  next=next.replace(/<p\b[^>]*>[\s\S]*?<\/p>/g, paragraph=>{
    const value=plain(paragraph);
    if(/가능\s*학년|수업 가능 학년/.test(value))return `<p>${escape(answer)}</p>`;
    return paragraph;
  });
  next=next.replace(/<summary>([^<]*)가능 학년([^<]*)<\/summary>/g,`<summary>${escape(p.centerName+'의 '+p.grade+' '+p.subject+' 수강 전 무엇을 확인하나요?')}</summary>`);
  // Insert immediately after the page hero, before the long common illustration.
  next=next.replace(/(<main\b[^>]*>[\s\S]*?<section\b[^>]*>[\s\S]*?<\/section>)/, '$1'+notice);
  next=next.replace(/<main\b([^>]*)>/, (all,attrs)=>attrs.includes('data-course-review')?all:`<main${attrs} data-course-review="20260928">`);
  return withMetadata(next,p.description,data=>{
    const nodes=data['@graph'] || [data];
    const oldCenters=new Set(nodes.filter(n=>types(n).some(t=>['LocalBusiness','EducationalOrganization'].includes(t))).map(n=>n['@id']));
    const services=new Set(nodes.filter(n=>types(n).includes('Service')).map(n=>n['@id']));
    if(data['@graph'])data['@graph']=nodes.filter(n=>!types(n).some(t=>['Service','Offer'].includes(t)));
    walk(data,n=>{
      if(oldCenters.has(n['@id']) || services.has(n['@id']))n['@id']=centerId;
      for(const key of ['offers','makesOffer','hasOfferCatalog','eligibleCustomerType'])delete n[key];
      if(types(n).some(t=>['LocalBusiness','EducationalOrganization'].includes(t))){
        n.name=p.registeredName;n.url=origin+encode(p.branchPath);
        n.address={'@type':'PostalAddress',streetAddress:p.address,addressCountry:'KR'};
        delete n.openingHours;delete n.openingHoursSpecification;
      }
      if(types(n).includes('Question') && /가능\s*학년/.test(n.name || '')){
        n.name=p.centerName+'의 '+p.grade+' '+p.subject+' 수강 전 무엇을 확인하나요?';
        n.acceptedAnswer.text=answer;
      }
      if(types(n).includes('Answer') && /가능\s*학년/.test(n.text || ''))n.text=answer;
    });
  });
}

export function branchContent(html, c) {
  if(html.includes('data-branch-review="20260928"'))return html;
  let main=html.match(/<main\b[^>]*>[\s\S]*?<\/main>/)?.[0];
  if(!main)throw Error('Missing branch main: '+c.sourceName);
  const take=id=>{
    const rx=new RegExp(`<section\\b[^>]*\\bid="${id}"[^>]*>[\\s\\S]*?<\\/section>`);
    const block=main.match(rx)?.[0];if(!block)throw Error('Missing '+id+': '+c.sourceName);
    main=main.replace(block,'');return block;
  };
  const courses=take('courses'), facts=take('center-facts'), fees=take('fees');
  let media=take('center-images'),photos=take('learning-space');
  const hidden=main.match(/<img\b[^>]*\bhidden\b[^>]*>/)?.[0];
  if(!hidden)throw Error('Missing representative: '+c.sourceName);
  main=main.replace(hidden,'');
  const figures=[...media.matchAll(/<figure\b[^>]*>[\s\S]*?<\/figure>/g)].map(m=>m[0]);
  if(figures.length!==2)throw Error('Unexpected branch media: '+c.sourceName);
  const banner=figures[0].replace(/<figcaption>[\s\S]*?<\/figcaption>/,'<figcaption>학습코칭 공통 프로그램 참고 이미지</figcaption>');
  media=media.replace(figures[0],`<details class="ci-common-media"><summary>학습코칭 공통 안내 이미지 펼쳐보기</summary><p>공통 프로그램 안내입니다. 이 지점의 수강 학년·교습비·방문 조건은 위 안내와 지점 상담을 기준으로 확인해 주세요.</p>${banner}</details>`);
  media=media.replace(figures[1],figures[1].replace(/<figure[^>]*>/,'<figure class="ci-map">'));
  media=media.replace('학습 안내와 찾아가는 위치','찾아가는 위치와 공통 안내');
  const centerPhotos=c.photoMode==='center';
  if(centerPhotos){
    photos=photos.replace(/(<h2\b[^>]*>)[^<]*<\/h2>/,`$1${escape(c.sourceName)} 제공 사진</h2>`);
    let imageIndex=0,captionIndex=0;
    photos=photos.replace(/<img\b[^>]*>/g,tag=>tag.replace(/alt="[^"]*"/,`alt="${escape(c.sourceName)} 제공 사진 ${++imageIndex}"`));
    photos=photos.replace(/<figcaption>[\s\S]*?<\/figcaption>/g,()=>`<figcaption>${escape(c.sourceName)} 제공 사진 ${++captionIndex}</figcaption>`);
    photos=photos.replace('<div class="cd-gallery">','<p class="ci-small">제공된 지점 사진입니다. 촬영 이후 시설과 좌석 배치가 달라질 수 있으니 현재 공간은 방문 전에 확인해 주세요.</p><div class="cd-gallery">');
  }else{
    photos=photos.replace('공부하는 공간 살펴보기','공통 학습 공간 참고 사진').replaceAll('학습 공간 살펴보기','공통 학습 공간 예시').replace(/alt="학습 공간 안내 (\d+)"/g,'alt="공통 학습 공간 참고 사진 $1"');
    photos=photos.replace('<div class="cd-gallery">','<p class="ci-small">아래는 공용 참고 사진입니다. '+escape(c.sourceName)+'의 실제 공간 사진은 아니며, 시설과 좌석 구성은 방문 전에 확인해 주세요.</p><div class="cd-gallery">');
  }
  const expanded=c.layoutVersion===2;
  const gradeSummary=subject=>escape(gradeText(c.subjects[subject]) || '수강 학년 확인 필요');
  const gradeLabel=expanded?'자료상 안내 학년':'안내 학년';
  const notes=expanded?`<div class="ci-branch-conditions" aria-label="수강 전 확인사항"><p class="ci-small">자료에 안내된 학년입니다. 현재 개설 과목·접수 가능 여부와 방문 시간은 지점 상담에서 확인해 주세요.</p>${c.pendingReconciliation?'<p>일부 과목·학년은 안내 자료 간 차이가 있어 수강 조건을 먼저 확인해야 합니다.</p>':''}${(c.courseNotes || []).map(note=>`<p>${escape(note)}</p>`).join('')}</div>`:'';
  const quick=`<dl class="ci-branch-quick"><div><dt>수학 ${gradeLabel}</dt><dd>${gradeSummary('수학')}</dd></div><div><dt>영어 ${gradeLabel}</dt><dd>${gradeSummary('영어')}</dd></div><div><dt>운영 참고</dt><dd>${escape(c.openingReference)}</dd></div><div><dt>주말</dt><dd>${escape(c.weekend)}</dd></div></dl>${notes}`;
  main=main.replace(/(<section class="cd-hero">[\s\S]*?)(<div class="cd-actions">)/,'$1'+quick+'$2');
  main=main.replace('<a href="#fees" class="cd-button cd-secondary">교육비 확인</a>',link(c.feeLink,'지점 교습비 자료')+link('#fees','교육비 확인'));
  const nav=[['courses','수강 학년'],['center-facts','기본정보'],['fees','교육비'],['center-images','위치·공통 안내'],['learning-space',centerPhotos?'지점 제공 사진':'공통 참고 사진'],['school-context','학교 참고'],['prepare','상담 준비'],['faq','질문과 답변']];
  if(main.includes('id="neighborhood-guides"'))nav.push(['neighborhood-guides','동네별 안내']);
  const toc=`<nav class="cd-toc" aria-label="페이지 목차">${nav.map(([id,label])=>`<a href="#${id}">${escape(label)}</a>`).join('')}</nav>`;
  main=main.replace(/<nav class="cd-toc"[\s\S]*?<\/nav>/,toc+courses+facts+fees+hidden+media+photos);
  main=main.replace('<main id="main" class="cd-main">','<main id="main" class="cd-main ci-branch" data-branch-review="20260928">');
  main=main.replace(/<time datetime="[^"]+">[^<]*<\/time>/g,`<time datetime="${config.reviewedAt}">${config.reviewedAt}</time>`);
  return withMetadata(html.replace(/<main\b[^>]*>[\s\S]*?<\/main>/,main),c.description);
}

export function applyToRoot(root,{check=false,backup,report}={}) {
  const changes=new Map();
  function plan(rel,next){if(fs.readFileSync(path.join(root,rel),'utf8')!==next)changes.set(rel,next);}
  for(const [key,p] of Object.entries(config.pages)){
    const rel=key.slice(1)+'index.html';plan(rel,courseContent(fs.readFileSync(path.join(root,rel),'utf8'),p));
  }
  for(const [key,c] of Object.entries(config.branches)){
    const rel=key.slice(1)+'index.html';plan(rel,branchContent(fs.readFileSync(path.join(root,rel),'utf8'),c));
  }
  if(changes.size){
    const keys=new Set([...changes.keys()].map(r=>'/'+r.replace(/index\.html$/,'')));
    const sitemap=fs.readFileSync(path.join(root,'sitemap.xml'),'utf8').replace(/<url>\s*<loc>([^<]+)<\/loc>([\s\S]*?)<\/url>/g,(all,url,rest)=>{
      if(!keys.has(decodeURIComponent(new URL(url).pathname)))return all;
      return `<url><loc>${url}</loc>${/<lastmod>/.test(rest)?rest.replace(/<lastmod>[^<]*<\/lastmod>/,`<lastmod>${config.reviewedAt}</lastmod>`):`<lastmod>${config.reviewedAt}</lastmod>`+rest}</url>`;
    });plan('sitemap.xml',sitemap);
  }
  if(!check)for(const [rel,value] of changes){
    const file=path.resolve(root,rel);if(!file.startsWith(path.resolve(root)+path.sep))throw Error('Unsafe path');
    if(backup){const dest=path.resolve(backup,rel);if(!fs.existsSync(dest)){fs.mkdirSync(path.dirname(dest),{recursive:true});fs.copyFileSync(file,dest);}}
    fs.writeFileSync(file,value,'utf8');
  }
  const result={check,changed:changes.size,htmlChanged:[...changes.keys()].filter(p=>p.endsWith('.html')).length,paths:[...changes.keys()]};
  if(report)fs.writeFileSync(report,JSON.stringify(result,null,2));
  return result;
}
if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const arg=name=>process.argv.find(a=>a.startsWith(name+'='))?.slice(name.length+1);
  const r=applyToRoot(path.resolve(project,arg('--root')||'.'),{check:process.argv.includes('--check'),backup:arg('--backup'),report:arg('--report')});
  console.log(JSON.stringify({check:r.check,changed:r.changed,htmlChanged:r.htmlChanged}));
  if(r.check&&r.changed)process.exitCode=1;
}
