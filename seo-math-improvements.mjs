/** Source-backed summaries and accessible media for existing high-school math routes. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {preserveTeacherContent, laterDate} from './teacher-build-preservation.mjs';
const project=path.dirname(fileURLToPath(import.meta.url));
const config=JSON.parse(fs.readFileSync(path.join(project,'seo-math-improvements.json'),'utf8'));
const origin='https://xn--ru4bz7e9zf0zk.com';
const esc=v=>String(v??'').replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const plain=s=>s.replace(/<[^>]*>/g,' ').replace(/\s+/g,' ').trim();
const encoded=s=>s.split('/').map(encodeURIComponent).join('/');
const types=n=>[].concat(n?.['@type']||[]);
const scriptRx=/(<script\b[^>]*type=["']application\/ld\+json["'][^>]*>)([\s\S]*?)(<\/script>)/gi;
const availability=/가능\s*학년|수업 가능 학년/;
const question=/가능\s*학년|수강 전 무엇을 확인하나요/;
const link=(href,label)=>`<a href="${esc(href)}">${esc(label)}</a>`;
function walk(v,fn){if(!v||typeof v!=='object')return;if(Array.isArray(v)){v.forEach(n=>walk(n,fn));return;}fn(v);Object.values(v).forEach(n=>walk(n,fn));}
function sizeImage(tag){
 const src=tag.match(/\bsrc="([^"]+)"/)?.[1],m=config.images[src];
 if(!m)throw Error('Unrecorded image: '+src);
 let next=tag.replace(/\s(?:width|height|fetchpriority|loading|decoding)="[^"]*"/g,'');
 return next.replace(/>$/,` width="${m.width}" height="${m.height}" loading="lazy" decoding="async">`);
}
export function mathContent(html,p){
 const c=config.centers[p.centerPath],centerId=origin+encoded(p.centerPath)+'#center';
 let main=html.match(/<main\b[^>]*>[\s\S]*?<\/main>/)?.[0];
 if(!main)throw Error('Missing main');
 const noticeRx=/<section\b[^>]*\bid="actual-center"[^>]*>[\s\S]*?<\/section>/;
 if(!noticeRx.test(main))throw Error('Missing center: '+p.town);
 main=main.replace(noticeRx,'');
 main=main.replace(/<p\b[^>]*>[\s\S]*?<\/p>/g,s=>availability.test(plain(s))?`<p>${esc(p.answer)}</p>`:s);
  main=main.replace(/<summary>([^<]*)<\/summary>/g,(all,s)=>question.test(s)?`<summary>${esc(p.question)}</summary>`:all);
  // Previously reviewed answers may no longer contain the old availability phrase.
  main=main.replace(/<details\b[^>]*>[\s\S]*?<\/details>/g,block=>{
   const label=block.match(/<summary>([\s\S]*?)<\/summary>/)?.[1]||'';
   return question.test(plain(label))?block.replace(/<p\b[^>]*>[\s\S]*?<\/p>/,`<p>${esc(p.answer)}</p>`):block;
  });
 const status=p.priorNotice?'수강 조건 확인':p.listedInSource?'자료상 안내 학년 포함':'개설 여부 확인 필요';
 const notice=`<section class="mi-center" id="actual-center" aria-labelledby="actual-center-title"><p class="mi-label">${esc(p.grade)} 수학 · ${status}</p><h2 id="actual-center-title">${esc(c.sourceName)} 수강 안내</h2><p class="mi-guidance">${esc(p.guidance)}</p>${p.notes.map(n=>`<p class="mi-condition">${esc(n)}</p>`).join('')}<dl><div><dt>실제 지점 주소</dt><dd>${esc(c.address)}</dd></div><div><dt>운영 참고</dt><dd>${esc(c.openingReference)} · 방문 시간 별도 확인</dd></div></dl><div class="mi-actions">${link(encoded(p.centerPath),c.sourceName+' 지점안내')}${link(c.feeLink,'지점 교습비 자료')}${link(c.mapLink,'네이버 지도')}${link('#math-visit','위치 이미지')}</div><p class="mi-small">아래 학습 제안은 상담 준비를 위한 안내입니다. 실제 개설 과목·시간표·접수 여부는 지점에 확인해 주세요.</p></section>`;
 main=main.replace(/(<section\b[^>]*subject-local-hero[^>]*>[\s\S]*?<\/section>)/,'$1'+notice);
 if(!main.includes('class="mi-toc"'))main=main.replace(/<nav\b[^>]*subject-page-toc[^>]*>[\s\S]*?<\/nav>/,s=>`<details class="mi-toc"><summary>학습 내용 목차 펼치기</summary>${s}</details>`);
 const mediaRx=/<section\b[^>]*subject-media-section[^>]*>[\s\S]*?<\/section>/;
 const oldMedia=main.match(mediaRx)?.[0];
 if(!oldMedia)throw Error('Missing media: '+p.town);
 const hidden=oldMedia.match(/<img\b[^>]*subject-hidden-representative[^>]*>/)?.[0];
 const figures=[...oldMedia.matchAll(/<figure\b[^>]*>[\s\S]*?<\/figure>/g)].map(m=>m[0]);
 if(!hidden||figures.length!==2)throw Error('Unexpected media: '+p.town);
 const body=figures[0].replace(/<figcaption>[\s\S]*?<\/figcaption>/,'<figcaption>학습코칭 공통 프로그램 참고 이미지</figcaption>');
 const media=`<section class="section subject-media-section mi-media" id="math-visit" aria-labelledby="math-visit-title"><h2 id="math-visit-title">${esc(c.sourceName)} 위치와 공통 안내</h2>${hidden}<details class="mi-common-media"><summary>학습코칭 공통 안내 이미지 펼쳐보기</summary><p>공통 프로그램 참고 이미지입니다. 현재 지점별 수강 조건과 교습비는 위 안내와 지점 상담에서 확인해 주세요.</p>${body}</details>${figures[1].replace(/<figure\b[^>]*>/,'<figure class="frame mi-map">')}</section>`.replace(/<img\b[^>]*>/g,sizeImage);
 main=main.replace(mediaRx,'');
 main=main.replace(/<p class="mi-reviewed">[\s\S]*?<\/p>/g,'');
 main=main.replace('</main>',media+`<p class="mi-reviewed">안내 자료 확인·내용 수정 <time datetime="${config.reviewedAt}">${config.reviewedAt}</time> · 현재 수강 조건은 지점에 확인해 주세요.</p></main>`);
 main=main.replace(/<main\b[^>]*>/,tag=>{
  if(!tag.includes('class='))tag=tag.replace('>',' class="mi-page">');
  else if(!/\bmi-page\b/.test(tag))tag=tag.replace(/class="([^"]*)"/,'class="$1 mi-page"');
  return tag.includes('data-math-review')?tag:tag.replace('>',' data-math-review="20260929">');
 });
 let next=html.replace(/<main\b[^>]*>[\s\S]*?<\/main>/,main);
 next=next.replace(/<meta\b[^>]*>/g,tag=>{
  const key=tag.match(/(?:name|property)="([^"]*)"/)?.[1];
  return ['description','og:description','twitter:description'].includes(key)?`<meta ${key.startsWith('og:')?'property':'name'}="${key}" content="${esc(p.description)}">`:tag;
 });
 next=next.replace(scriptRx,(all,start,body,end)=>{
  const data=JSON.parse(body),nodes=data['@graph']||[data];
  const ids=new Set(nodes.filter(n=>types(n).some(t=>['LocalBusiness','EducationalOrganization','Service'].includes(t))).map(n=>n['@id']).filter(Boolean));
  if(data['@graph'])data['@graph']=nodes.filter(n=>!types(n).some(t=>['Service','Offer'].includes(t)));
  walk(data,n=>{
   if(ids.has(n['@id']))n['@id']=centerId;
   for(const k of ['offers','makesOffer','hasOfferCatalog','eligibleCustomerType'])delete n[k];
   if(types(n).some(t=>['EducationalOrganization','LocalBusiness'].includes(t))){n.name=c.registeredName;n.url=origin+encoded(p.centerPath);n.address={'@type':'PostalAddress',streetAddress:c.address,addressCountry:'KR'};delete n.openingHours;delete n.openingHoursSpecification;}
   if(types(n).some(t=>['WebPage','Article'].includes(t))){n.description=p.description;n.dateModified=config.reviewedAt;}
   if(types(n).includes('Question')&&question.test(n.name||'')){n.name=p.question;n.acceptedAnswer.text=p.answer;}
   if(types(n).includes('Answer')&&availability.test(n.text||''))n.text=p.answer;
  });
  return start+JSON.stringify(data).replaceAll('<','\\u003c')+end;
 });
 if(!next.includes('/assets/math-improvements.css'))next=next.replace('</head>','<link rel="stylesheet" href="/assets/math-improvements.css"></head>');
 return next;
}
export function applyToRoot(root,{check=false,backup,report,only}={}){
 const changes=new Map();
 for(const [key,p] of Object.entries(config.pages)){
  if(only&&!only.includes(key))continue;
  const rel=key.slice(1)+'index.html',s=fs.readFileSync(path.join(root,rel),'utf8'),next=preserveTeacherContent(s,mathContent(s,p));
  if(next!==s)changes.set(rel,next);
 }
 if(changes.size){
  const keys=new Set([...changes.keys()].map(r=>'/'+r.replace(/index\.html$/,'')));
  const old=fs.readFileSync(path.join(root,'sitemap.xml'),'utf8');
  const next=old.replace(/<url>\s*<loc>([^<]+)<\/loc>([\s\S]*?)<\/url>/g,(all,url,rest)=>keys.has(decodeURIComponent(new URL(url).pathname))?`<url><loc>${url}</loc>${rest.replace(/<lastmod>([^<]*)<\/lastmod>/,(_,current)=>`<lastmod>${laterDate(current,config.reviewedAt)}</lastmod>`)}</url>`:all);
  if(next!==old)changes.set('sitemap.xml',next);
 }
 if(!check)for(const [rel,s] of changes){
  const file=path.resolve(root,rel);if(!file.startsWith(path.resolve(root)+path.sep))throw Error('Unsafe path');
  if(backup){const b=path.resolve(backup,rel);if(!fs.existsSync(b)){fs.mkdirSync(path.dirname(b),{recursive:true});fs.copyFileSync(file,b);}}
  fs.writeFileSync(file,s,'utf8');
 }
 const result={check,changed:changes.size,htmlChanged:[...changes.keys()].filter(p=>p.endsWith('.html')).length,paths:[...changes.keys()]};
 if(report)fs.writeFileSync(report,JSON.stringify(result,null,2));
 return result;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const arg=name=>process.argv.find(a=>a.startsWith(name+'='))?.slice(name.length+1);
 const r=applyToRoot(path.resolve(project,arg('--root')||'.'),{check:process.argv.includes('--check'),backup:arg('--backup'),report:arg('--report')});
 console.log(JSON.stringify({check:r.check,changed:r.changed,htmlChanged:r.htmlChanged}));if(r.check&&r.changed)process.exitCode=1;
}
