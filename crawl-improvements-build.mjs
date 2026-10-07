/** Scoped improvements run after the seven existing, reviewed build stages. */
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseHTML} from './image-order-build.mjs';
const root=path.dirname(fileURLToPath(import.meta.url)),out=path.join(root,'.public-release');
const data=JSON.parse(fs.readFileSync(path.join(root,'crawl-improvements-data.json'),'utf8'));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'release-public-manifest.json'),'utf8'));
const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const decode=s=>(s||'').replaceAll('&amp;','&').replaceAll('&quot;','"').replaceAll('&#39;',"'").replaceAll('&lt;','<').replaceAll('&gt;','>');
const plain=s=>decode(s.replace(/<[^>]*>/g,' ')).replace(/\s+/g,' ').trim();
const sha=b=>createHash('sha256').update(b).digest('hex');
const url=n=>'/'+n.replace(/index\.html$/,'');
const slice=(s,n)=>s.slice(n.start,n.end);
const ancestors=n=>{const a=[];for(let p=n.parent;p;p=p.parent)a.push(p);return a;};
function edits(s,rows){let last=s.length;for(const e of rows.sort((a,b)=>b.start-a.start)){if(e.end>last)throw Error('Overlapping edits');s=s.slice(0,e.start)+e.value+s.slice(e.end);last=e.start;}return s;}
function replace(s,node,value){return s.slice(0,node.start)+value+s.slice(node.end);}
const a=(label,href)=>'<a href="'+esc(href.startsWith('/')?href.replaceAll('+','%2B'):href)+'">'+esc(label)+'</a>';
const p=s=>'<p>'+esc(s)+'</p>';
const sec=(id,title,body,cls='')=>'<section class="crawl-facts '+cls+'" id="'+id+'" aria-labelledby="'+id+'-title"><h2 id="'+id+'-title">'+esc(title)+'</h2>'+body+'</section>';
const actions=links=>'<div class="crawl-actions">'+links.map(([t,u])=>a(t,u)).join('')+'</div>';
function gradeText(grades){const groups=[];for(const stage of ['초','중','고']){const ns=grades.filter(g=>g.startsWith(stage)).map(g=>Number(g.slice(1))).sort((a,b)=>a-b);if(!ns.length)continue;let first=ns[0],prev=first;for(const n of [...ns.slice(1),99]){if(n!==prev+1){groups.push(stage+first+(first!==prev?'~'+stage+prev:''));first=n;}prev=n;}}return groups.join(' · ');}
function stageOf(name){return /고등학생학원|\/고등\/|\/고[123]/.test(name)?'고':/중학생학원|\/중등\/|\/중[123]/.test(name)?'중':/초등학생학원|\/초등\/|\/초[1-6]/.test(name)?'초':'';}
function courseRows(c,stage=''){return Object.entries(c.subjects).map(([subject,grades])=>[subject,stage?grades.filter(g=>g.startsWith(stage)):grades]).filter(([,g])=>g.length);}
function courseList(c,stage=''){const rows=courseRows(c,stage);return rows.length?'<ul class="crawl-course-list">'+rows.map(([s,g])=>'<li><strong>'+esc(s)+'</strong> '+esc(gradeText(g))+'</li>').join('')+'</ul>':'<p>이 학교급의 과목·학년 범위는 제공된 자료에서 확인되지 않아 지점에 문의해야 합니다.</p>';}
function facts(c,stage=''){
 return p(c.registeredName+'의 안내 주소는 '+c.address+'입니다.')+'<dl><dt>주소</dt><dd>'+esc(c.address)+'</dd><dt>찾아오는 길</dt><dd>'+esc(c.locationGuide)+'</dd><dt>등록 정보</dt><dd>'+esc(c.registrationNumber)+'</dd><dt>상담 연결</dt><dd>'+a('010-6839-8283','tel:010-6839-8283')+' · 채움학습 상담</dd></dl><h3>자료에 안내된 '+(stage?{'초':'초등','중':'중등','고':'고등'}[stage]+' ':'')+'과목과 학년</h3>'+courseList(c,stage)+c.courseNotes.map(p).join('')+p('자료에 적힌 학년 범위와 현재 개설·접수 가능 여부는 다를 수 있습니다. 시간표·교재·최종 교습비와 방문 가능 시간은 지점에서 확인하세요.')+actions([[c.key+' 전체 수강 안내',c.path],['지점 교습비 자료',c.feeLink],['네이버 지도에서 주소 확인',c.mapLink]]);
}
function schools(c,name){
 const stage=stageOf(name),area=c.schoolAreas.find(x=>name.includes(x.neighborhood))||{schools:c.schools};
 const label={'초':'초등학교','중':'중학교','고':'고등학교'}[stage];
 const rows=Object.entries(area.schools).filter(([s])=>!label||s===label);const names=[...new Set(rows.flatMap(([,ns])=>ns))];
 return (names.length?p('자료에 기재된 학교 참고: '+names.join(' · ')+'.'):'')+p('학교 이름보다 학생이 가져온 최신 자료를 먼저 확인하세요. 교과서의 과목·출판사·현재 단원, 학교 프린트와 평가 안내에서 실제 범위와 제출일을 표시합니다.')+'<ol><li>최근 답안에서 혼자 해결한 부분과 도움받은 부분을 구분합니다.</li><li>'+esc(stage==='고'?'실제 선택 과목과 내신·모의평가 일정을 대조해 마감이 가까운 과제와 누적 개념 보완을 나눕니다.':stage==='중'?'시험 범위·수행평가 기준과 최근 오답을 대조해 개념 확인, 풀이 연습, 답안 표현을 나눕니다.':'읽기·계산 등 현재 단원의 과제를 살펴보고 설명을 들은 뒤 혼자 수행할 수 있는 범위를 확인합니다.')+'</li><li>'+esc(c.key)+' 상담에서는 이 자료를 어떤 진도와 복습 과제로 연결할지 질문하고, 답변을 날짜와 함께 남깁니다.</li></ol>'+p('학교 목록은 학교별 개설 수업·제휴·재학생 수강 실적을 뜻하지 않습니다. 학교별 지도 범위와 자료 제공은 별도로 확인하세요.');
}
function teacherSummary(c){const list=c.teachers.slice(0,3);return list.length?p('제공된 '+c.key+' 소개에는 '+list.map(t=>t.name+' 선생님('+t.approach+')').join(', ')+'의 학습 방식이 기재되어 있습니다.')+p('소개글의 지도 방향을 읽고 최근 답안에서 필요한 도움과 비교해 보세요. 현재 담당 과목·학년과 배정은 지점에 확인하세요.'):'';}
function faqAdvice(q,c){
 if(/성적|늦지|향상|따라/.test(q))return '최근 답안과 남은 일정으로 우선 보완할 과제를 좁혀 보세요. 현재 이해와 실제 수행 기록을 비교해 시작 범위를 정하며, 특정 기간의 성적 향상을 약속하는 의미는 아닙니다.';
 if(/준비/.test(q))return '학교의 최신 평가 안내, 현재 교재의 막힌 부분과 최근 답안을 준비해 보세요. 혼자 해결한 부분과 도움받은 부분을 표시하고 실제로 공부할 수 있는 요일·시간을 적으면 상담에 도움이 됩니다.';
 if(/기간|시간 배분|선행|내신.*수능|시험.*운영/.test(q))return '학교의 평가 범위와 일정, 누적된 개념의 빈틈을 함께 적고 지금 할 과제와 다음에 할 과제를 나누세요. '+c.key+'의 시험 기간 시간표·추가 수업·개별 진도와 피드백 방식은 상담에서 확인해야 합니다.';
 return null;
}
function faqRows(s){const rows=[];for(const m of s.matchAll(/<script\b[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gi)){let graph;try{graph=JSON.parse(m[1])['@graph']||[];}catch{continue;}for(const item of graph)if(item['@type']==='FAQPage')for(const q of item.mainEntity||[])rows.push([q.name,q.acceptedAnswer?.text||'']);}return rows;}
const stats={pages:0,changed:0,semanticChanged:0,normalizedLinks:0,mergedResourcePanels:0,mergedCenterPanels:0,schoolPanels:0,teacherSummaries:0,faqConsolidations:0,dimensions:0,imageZoom:0,optimizedImages:0,reservedImageAreas:0,changedPaths:[],semanticPaths:[],errors:[]};
const css='/assets/crawl-improvements.css',js='/assets/crawl-image-reader.js';
function normalizeHref(href,pagePath){
 if(!href||href.startsWith('#')||/^(?:mailto|tel|sms|javascript|data):/.test(href))return href;
 let u;try{u=new URL(decode(href),data.origin+pagePath);}catch{return href;}
 if(u.origin!==data.origin)return href;
 let raw;try{raw=decodeURIComponent(u.pathname);}catch{return href;}
 if(raw.endsWith('/index.html'))raw=raw.slice(0,-10);
 if(data.knownPages[raw])return encodeURI(raw).replaceAll('+','%2B')+u.search+u.hash;
 return href;
}
function reserveImageAreas(source,name){
 const images=source.replace(/<img\b[^>]*>/gi,tag=>{
  const n=parseHTML(tag)[0];if(!['body','map'].includes(n.attrs['data-media-role']))return tag;
  const w=Number(n.attrs.width),h=Number(n.attrs.height);if(!w||!h)throw Error('Missing reserved image size');
  const ratio='aspect-ratio:'+w+'/'+h+';';stats.reservedImageAreas++;
  if(n.attrs.style){const old=n.attrs.style.replace(/aspect-ratio\s*:[^;]*(?:;|$)/gi,'');return tag.replace(/\bstyle="[^"]*"/i,'style="'+esc(old+(old&&!old.endsWith(';')?';':'')+ratio)+'"');}
  return tag.replace(/(\s*\/?>)$/,' style="'+ratio+'"$1');
 });
 const c=data.centers[data.pageCenter[name]];
 if(!c)return images;
 return images.replace(/(<a\b[^>]*data-readable-image="map"[^>]*>[\s\S]*?<\/a>)<p class="crawl-image-note"(?: data-map-context="verified")?>[\s\S]*?<\/p>/g,(m,anchor)=>{
  const combined=anchor.includes('/maps/byeolnaedong.jpg')?' 원본 지도에는 별내점과 별가람점 안내가 함께 있습니다. 이 페이지의 연결 지점명과 주소를 기준으로 확인하세요.':'';
  return anchor+'<p class="crawl-image-note" data-map-context="verified">'+esc(c.key+' 안내 주소: '+c.address+'.')+' 채움학습 상담 연결: '+a('010-6839-8283','tel:010-6839-8283')+'. '+esc('지도를 누르면 원본 크기로 확대할 수 있습니다.'+combined)+'</p>';
 });
}
function transform(source,name){
 let s=source,semantic=false;const pagePath=url(name),center=data.centers[data.pageCenter[name]],family=name.split('/')[0];
 s=s.replace(/(<a\b[^>]*\bhref=")([^"]*)(")/gi,(m,start,href,end)=>{const h=normalizeHref(href,pagePath);if(h!==href){stats.normalizedLinks++;semantic=true;return start+esc(h)+end;}return m;});
 let nodes=parseHTML(s),cu=nodes.find(n=>n.tag==='section'&&n.attrs.id==='curriculum-connection'),ei=nodes.find(n=>n.tag==='section'&&n.attrs.id==='education-info-links');
 if(cu&&ei){
  const inner=n=>'<div id="'+n.attrs.id+'">'+s.slice(n.openEnd,n.closeStart).replace(/<h2\b/gi,'<h3').replace(/<\/h2>/gi,'</h3>')+'</div>';
  const panel='<section class="crawl-resources" id="study-resources" aria-labelledby="study-resources-title"><h2 id="study-resources-title">공부 순서와 실천 방법을 함께 살펴보세요</h2><div class="crawl-resource-grid">'+inner(cu)+inner(ei)+'</div></section>';
  s=edits(s,[{start:cu.start,end:cu.end,value:cu.start<ei.start?panel:''},{start:ei.start,end:ei.end,value:ei.start<cu.start?panel:''}]);stats.mergedResourcePanels++;semantic=true;
 }
 if(center){
  nodes=parseHTML(s);const tc=nodes.find(n=>n.tag==='section'&&n.attrs.id==='teacher-connection');
  if(tc&&center.teachers.length){let content=slice(s,tc);const paras=parseHTML(content).filter(n=>n.tag==='p');content=edits(content,paras.map((n,i)=>({start:n.start,end:n.end,value:i===0?teacherSummary(center):''})));s=replace(s,tc,content);stats.teacherSummaries++;semantic=true;}
  nodes=parseHTML(s);const school=nodes.find(n=>n.tag==='section'&&n.attrs.id==='school-context');
  if(school){s=replace(s,school,s.slice(school.start,school.closeStart)+'<div class="crawl-school">'+schools(center,name)+'</div>'+s.slice(school.closeStart,school.end));stats.schoolPanels++;semantic=true;}
  if(family==='전국학원'&&name.split('/').length===4){
   const stage=stageOf(name),rows=faqRows(s);nodes=parseHTML(s);const direct=nodes.filter(n=>n.tag==='section'&&n.parent?.tag==='main');
   const aeo=direct.find(n=>plain(slice(s,n)).startsWith('AEO ANSWER'));
   if(aeo){const markup=slice(s,aeo),ps=parseHTML(markup).filter(n=>n.tag==='p');for(let i=0;i<ps.length;i++){const q=plain(slice(markup,ps[i]));if(q.startsWith('Q.'))rows.push([q.slice(2).trim(),ps[i+1]?plain(slice(markup,ps[i+1])):'']);}}
   const actual=nodes.find(n=>n.tag==='section'&&n.attrs.id==='actual-center'),oldcenter=direct.find(n=>plain(slice(s,n)).startsWith('CENTER INFO')),fit=direct.find(n=>plain(slice(s,n)).startsWith('LOCAL & STUDENT FIT')),comparison=direct.find(n=>plain(slice(s,n)).startsWith('일반 학원과의 차이')),faq=direct.find(n=>plain(slice(s,n)).startsWith('FAQ'));
   const patch=[];
   if(actual){patch.push({start:actual.start,end:actual.end,value:''});const hero=direct[0];patch.push({start:hero.end,end:hero.end,value:sec('local-center-facts',center.key+' 위치와 수강 조건',facts(center,stage))});stats.mergedCenterPanels++;}
   if(oldcenter)patch.push({start:oldcenter.start,end:oldcenter.end,value:''});
   if(fit)patch.push({start:fit.start,end:fit.end,value:sec('local-school-context','학교 자료로 준비하는 상담',schools(center,name))});
   if(comparison)patch.push({start:comparison.start,end:comparison.end,value:sec('class-comparison','수업 설명을 비교할 때 확인할 네 가지','<ol><li>진단: 최근 답안의 어느 부분을 보고 시작 범위를 정하나요?</li><li>설명과 질문: 혼자 시도한 풀이와 도움받은 풀이를 어떻게 구분하나요?</li><li>복습: 다시 풀어볼 과제와 확인 날짜를 어떻게 정하나요?</li><li>소통: 학교 일정과 미완료 과제를 어떤 기록으로 함께 확인하나요?</li></ol>'+p('수업 방식의 차이를 확인하는 질문입니다. 특정 학원의 운영이 더 우수하다는 뜻이 아니며 실제 제공 방식은 지점 상담에서 확인하세요.'))});
   if(aeo)patch.push({start:aeo.start,end:aeo.end,value:''});
   if(faq){const unique=[...new Map(rows.map(([q,ans])=>[q,[q,faqAdvice(q,center)||ans]])).values()],h1=nodes.find(n=>n.tag==='h1');patch.push({start:faq.start,end:faq.end,value:sec('local-faq',plain(slice(s,h1))+' 상담 질문','<div class="crawl-faq">'+unique.map(([q,ans])=>'<details><summary>'+esc(q)+'</summary>'+p(ans)+'</details>').join('')+'</div>')});stats.faqConsolidations++;}
   s=edits(s,patch);semantic=true;
   nodes=parseHTML(s);const unverified=nodes.filter(n=>n.tag==='p'&&ancestors(n).some(p=>p.tag==='main')&&/학생들이 주로 문의합니다/.test(plain(slice(s,n))));
   s=edits(s,unverified.map(n=>({start:n.start,end:n.end,value:p(center.key+'의 실제 주소와 자료상 수강 범위를 먼저 확인하세요. 학교별 상담에는 최신 평가 안내와 학생의 최근 답안을 함께 준비하고, 현재 지도 범위는 지점에 문의하세요.')})));
  }
  if(family==='과목별학원'&&name.split('/').length===4){
   nodes=parseHTML(s);const duplicate=nodes.find(n=>n.tag==='section'&&(n.attrs.class||'').includes('subject-center-card')),actual=nodes.find(n=>n.tag==='section'&&n.attrs.id==='actual-center');
   if(duplicate&&actual){const replacement=s.slice(actual.start,actual.closeStart)+'<p class="crawl-image-note">등록 학원명: '+esc(center.registeredName)+' · '+esc(center.registrationNumber)+'</p>'+p(center.locationGuide)+s.slice(actual.closeStart,actual.end);s=edits(s,[{start:actual.start,end:actual.end,value:replacement},{start:duplicate.start,end:duplicate.end,value:''}]);stats.mergedCenterPanels++;semantic=true;}
  }
 }
 if(name==='index.html'){
  nodes=parseHTML(s);const regions=nodes.find(n=>n.tag==='section'&&n.attrs.id==='home-regions');
  if(regions){const rs=[...new Set(Object.values(data.centers).map(c=>c.region))].filter(r=>data.knownPages['/지점안내/'+r+'/']);s=replace(s,regions,s.slice(regions.start,regions.closeStart)+'<h3>지역별 지점 목록 바로가기</h3>'+actions(rs.map(r=>[r+' 지점 목록','/지점안내/'+r+'/']))+s.slice(regions.closeStart,regions.end));semantic=true;}
 }
 s=s.replace(/(<a\b[^>]*\bhref=")([^"]*)(")/gi,(m,start,href,end)=>{const h=normalizeHref(href,pagePath);return h===href?m:start+esc(h)+end;});
 // Add intrinsic dimensions without resampling any image.
 s=s.replace(/<img\b[^>]*>/gi,tag=>{const n=parseHTML(tag)[0];const src=n.attrs.src;if(!src)return tag;let asset;try{asset=decodeURIComponent(new URL(src,data.origin+pagePath).pathname).slice(1);}catch{return tag;}const im=data.images[asset];if(!im)return tag;for(const [k,v] of [['width',im.width],['height',im.height]])if(Number(n.attrs[k])!==v){const rx=new RegExp('\\s'+k+'="[^"]*"','i');tag=n.attrs[k]?tag.replace(rx,' '+k+'="'+v+'"'):tag.replace(/\s*\/?>$/,' '+k+'="'+v+'">');stats.dimensions++;}if(!n.attrs.decoding)tag=tag.replace(/\s*\/?>$/,' decoding="async">');if(!n.attrs.loading&&['body','map'].includes(n.attrs['data-media-role']))tag=tag.replace(/\s*\/?>$/,' loading="lazy">');return tag;});
 nodes=parseHTML(s);const zoomEdits=[];
 for(const n of nodes.filter(n=>n.tag==='img'&&ancestors(n).some(x=>x.tag==='main')&&!n.attrs.hidden)){
  const role=n.attrs['data-media-role'];if(!['body','map'].includes(role))continue;
  const oldAnchor=ancestors(n).find(x=>x.tag==='a');if(oldAnchor)continue;
  const picture=n.parent?.tag==='picture'?n.parent:n;const title=role==='map'?'지도 확대':'본문 안내 확대';
  const original=new URL(decode(n.attrs.src),data.origin+pagePath),asset=decodeURIComponent(original.pathname).slice(1);if(manifest.files[asset])original.searchParams.set('v',manifest.files[asset].slice(0,12));const originalHref=original.pathname.replaceAll('+','%2B')+original.search;
  zoomEdits.push({start:picture.start,end:picture.end,value:'<a class="crawl-image-link" href="'+esc(originalHref)+'" data-readable-image="'+role+'" data-reader-title="'+title+'" aria-label="'+esc(n.attrs.alt+' · 원본 확대')+'">'+slice(s,picture)+'</a><p class="crawl-image-note">이미지를 누르면 원본 크기로 확대할 수 있습니다.</p>'});stats.imageZoom++;semantic=true;
 }
 if(zoomEdits.length){s=edits(s,zoomEdits);s=s.replace(/<\/body>/i,'<dialog class="crawl-reader" data-crawl-reader aria-labelledby="crawl-reader-title"><div class="crawl-reader-bar"><strong id="crawl-reader-title" data-reader-title>이미지 원본</strong><label class="crawl-reader-zoom">확대 <input type="range" min="100" max="400" value="100" step="25" aria-label="이미지 확대 비율"></label><button type="button">닫기</button></div><p class="crawl-reader-help">확대한 뒤 가로·세로로 이동해 읽어보세요. Esc 키로 닫을 수 있습니다.</p><div class="crawl-reader-body" data-reader-body><img alt=""></div></dialog><script defer src="'+js+'"></script>$&');}
 // Lossless alternatives retain every pixel; the original remains the fallback.
 nodes=parseHTML(s);const optimal=[];
 for(const n of nodes.filter(n=>n.tag==='img'&&n.attrs.src&&n.parent?.tag!=='picture')){let asset;try{asset=decodeURIComponent(new URL(n.attrs.src,data.origin+pagePath).pathname).slice(1);}catch{continue;}const im=data.optimizedImages[asset];if(im){optimal.push({start:n.start,end:n.end,value:'<picture data-lossless-original="'+esc('/'+asset)+'"><source type="image/webp" srcset="'+im.src+'">'+slice(s,n)+'</picture>'});stats.optimizedImages++;}}
 s=edits(s,optimal);
 // Content hashes in resource URLs avoid stale browser caches after an edit.
 s=s.replace(/<(?:img|source|script|link)\b[^>]*>/gi,tag=>tag.replace(/\b(src|srcset|href)="([^"]*)"/gi,(m,key,value)=>{
  if(key==='href'&&!/rel="(?:stylesheet|icon)"/i.test(tag))return m;
  const part=val=>{const match=val.trim().match(/^(\S+)(\s+\d+[wx])?$/);if(!match)return val;let u;try{u=new URL(decode(match[1]),data.origin+pagePath);}catch{return val;}if(u.origin!==data.origin)return val;const asset=decodeURIComponent(u.pathname).slice(1),hash=manifest.files[asset];if(!hash)return val;u.searchParams.set('v',hash.slice(0,12));return u.pathname+u.search+(match[2]||'');};
  const next=key==='srcset'?value.split(',').map(part).join(', '):part(value);return next===value?m:key+'="'+esc(next)+'"';
 }));
 if(s!==source){s=s.replace(/<\/head>/i,'<link rel="stylesheet" href="'+css+'?v='+manifest.files[css.slice(1)].slice(0,12)+'">$&');}
 // Refresh only modified pages; publication dates and canonical identities remain intact.
 if(semantic){
  s=s.replace(/<script\b[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gi,(tag,raw)=>{
   const doc=JSON.parse(raw);let graph=doc['@graph'];if(!graph)return tag;
   const faqNodes=parseHTML(s).filter(n=>n.tag==='details'&&ancestors(n).some(x=>['faq','local-faq','hub-answer'].includes(x.attrs.id)));
   for(const obj of graph){if(['WebPage','CollectionPage','Article'].some(t=>Array.isArray(obj['@type'])?obj['@type'].includes(t):obj['@type']===t))obj.dateModified=data.date;
    if(obj['@type']==='FAQPage'&&name.startsWith('전국학원/')&&faqNodes.length){obj.mainEntity=faqNodes.map(n=>{const chunk=slice(s,n),ns=parseHTML(chunk),summary=ns.find(x=>x.tag==='summary'),paras=ns.filter(x=>x.tag==='p');return {'@type':'Question','name':plain(slice(chunk,summary)),'acceptedAnswer':{'@type':'Answer','text':paras.map(x=>plain(slice(chunk,x))).join(' ')}};});}
   }
   return tag.replace(raw,JSON.stringify(doc).replaceAll('<','\\u003c'));
  });
  s=s.replace(/(<meta\b[^>]*property="article:modified_time"[^>]*content=")[^"]*(")/gi,(m,a,b)=>a+data.date+b);
 }
 return {html:reserveImageAreas(s,name),semantic};
}
let cursor=0;const names=Object.keys(manifest.files).filter(n=>n.endsWith('index.html'));const changed=new Set();
if(process.argv.includes('--reserve-only')){
 await Promise.all(Array.from({length:12},async()=>{while(cursor<names.length){const name=names[cursor++],file=path.join(out,name),before=await fs.promises.readFile(file,'utf8'),after=reserveImageAreas(before,name);if(after!==before)await fs.promises.writeFile(file,after);}}));
 const report=JSON.parse(fs.readFileSync(path.join(root,'crawl-improvements-report.json'),'utf8'));report.reservedImageAreas=stats.reservedImageAreas;fs.writeFileSync(path.join(root,'crawl-improvements-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({mode:'reserve-only',pages:names.length,reservedImageAreas:stats.reservedImageAreas}));process.exit(0);
}
await Promise.all(Array.from({length:12},async()=>{while(cursor<names.length){const name=names[cursor++];const file=path.join(out,name),before=await fs.promises.readFile(file,'utf8');const result=transform(before,name);stats.pages++;if(result.html!==before){await fs.promises.writeFile(file,result.html);stats.changed++;stats.changedPaths.push(url(name));changed.add(url(name));}if(result.semantic){stats.semanticChanged++;stats.semanticPaths.push(url(name));}}}));
const semantic=new Set(stats.semanticPaths),sm=path.join(out,'sitemap.xml');let xml=fs.readFileSync(sm,'utf8');xml=xml.replace(/<url>([\s\S]*?)<\/url>/g,(tag,content)=>{const loc=decode(content.match(/<loc>([\s\S]*?)<\/loc>/)?.[1]||'');let p;try{p=decodeURIComponent(new URL(loc).pathname);}catch{return tag;}if(!semantic.has(p))return tag;return tag.includes('<lastmod>')?tag.replace(/<lastmod>[^<]*<\/lastmod>/,'<lastmod>'+data.date+'</lastmod>'):tag.replace('</url>','<lastmod>'+data.date+'</lastmod></url>');});fs.writeFileSync(sm,xml);
// RSS is a feed of published articles. All other landing pages remain in the full sitemap.
const rssFile=path.join(out,'rss.xml');let rss=fs.readFileSync(rssFile,'utf8');let rssArticles=0,rssOtherItems=0;
rss=rss.replace(/<lastBuildDate>[^<]*<\/lastBuildDate>/,'<lastBuildDate>'+new Date(data.rssUpdatedAt).toUTCString()+'</lastBuildDate>').replace('<title>채움학습 학습·지점 안내</title>','<title>채움학습 교육정보·학습가이드</title>').replace('<description>학습코칭과 실제 지점의 수강 조건을 안내합니다.</description>','<description>학생과 학부모가 활용할 수 있는 교육정보와 공부 방법을 안내합니다.</description>');
rss=rss.replace(/<rss\b([^>]*)>/,'<rss$1 xmlns:content="http://purl.org/rss/1.0/modules/content/">');
rss=rss.replace(/<item>([\s\S]*?)<\/item>/g,(tag,body)=>{const link=decode(body.match(/<link>([\s\S]*?)<\/link>/)?.[1]||'');let p;try{p=decodeURIComponent(new URL(link).pathname);}catch{return tag;}if(!/^\/(교육정보|학습가이드)\/[^/]+\/$/.test(p)){rssOtherItems++;return '';}
 const name=p.slice(1)+'index.html',source=fs.readFileSync(path.join(out,name),'utf8'),main=parseHTML(source).find(n=>n.tag==='main');
 if(!main)throw Error('RSS article has no main: '+name);let content=source.slice(main.openEnd,main.closeStart).replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,'').replace(/<form\b[^>]*>[\s\S]*?<\/form>/gi,'');content=content.replace(/\b(href|src|srcset)="([^"]*)"/gi,(m,k,v)=>{const absolute=value=>{try{return new URL(decode(value),data.origin+p).href;}catch{return value;}};const value=k==='srcset'?v.split(',').map(part=>part.trim().replace(/^(\S+)/,u=>absolute(u))).join(', '):absolute(v);return k+'="'+esc(value)+'"';});rssArticles++;
 return tag.replace('</item>','<content:encoded><![CDATA['+content.replaceAll(']]>',']]]]><![CDATA[>')+']]></content:encoded></item>');
});
if(rssArticles!==108||Buffer.byteLength(rss)>=10*1024*1024)throw Error('Invalid full-article RSS');fs.writeFileSync(rssFile,rss);stats.rss={articles:rssArticles,landingPagesMovedToSitemapOnly:rssOtherItems,bytes:Buffer.byteLength(rss)};
stats.changedPaths.sort();stats.semanticPaths.sort();fs.writeFileSync(path.join(root,'crawl-improvements-report.json'),JSON.stringify(stats,null,2)+'\n');console.log(JSON.stringify({...stats,changedPaths:undefined,semanticPaths:undefined}));
