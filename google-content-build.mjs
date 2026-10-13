/** Reviewed editorial improvements; keeps URL identities, assets and image markup. */
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseHTML} from './image-order-build.mjs';
const root=path.dirname(fileURLToPath(import.meta.url)),out=path.join(root,'.public-release');
const facts=JSON.parse(fs.readFileSync(path.join(root,'crawl-improvements-data.json'),'utf8'));
const photos=JSON.parse(fs.readFileSync(path.join(root,'branch-thumbnail-data.json'),'utf8'));
const reviewPath=path.join(root,'google-content-review.json');
const date='2026-10-13',photoDate='2026-10-10';
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const decode=s=>s.replaceAll('&amp;','&').replaceAll('&quot;','"').replaceAll('&#39;',"'").replaceAll('&lt;','<').replaceAll('&gt;','>');
const plain=s=>decode(s.replace(/<[^>]*>/g,' ')).replace(/\s+/g,' ').trim();
const norm=s=>s.replaceAll('\r\n','\n');
const sha=s=>createHash('sha256').update(norm(s)).digest('hex');
const cut=(s,n)=>s.slice(n.start,n.end);
const inside=(n,p)=>n.start>p.start&&n.end<=p.end;
const ancestors=n=>{const a=[];for(let p=n.parent;p;p=p.parent)a.push(p);return a;};
function edits(s,list){let last=s.length;for(const e of list.sort((a,b)=>b.start-a.start)){if(e.end>last)throw Error('Overlapping editorial edits');s=s.slice(0,e.start)+e.value+s.slice(e.end);last=e.start;}return s;}
function nodesOf(s){return parseHTML(s);}
const paragraphs=(s,nodes)=>nodes.filter(n=>n.tag==='p'&&ancestors(n).some(x=>x.tag==='main'));
const para=s=>'<p>'+esc(s)+'</p>';

function answer(q,c){
 const confirmation=c?c.key+'의 실제 개설 과정과 지도 방식은 상담에서 확인하세요.':'실제 개설 과정과 지도 방식은 지점에서 확인하세요.';
 if(/시험 기간.*운영/.test(q))return '학교의 시험 일정과 범위표를 준비해 추가 수업 여부, 질문 가능한 시간, 결석 보완, 추가 비용을 각각 확인하세요. 평소 운영 안내만으로 시험 기간의 시간표를 확정할 수는 없습니다.';
 if(/고3.*성적/.test(q))return '남은 평가 일정과 최근 답안에서 스스로 해결한 문항을 먼저 구분하세요. 단기간에 바꿀 수 있는 실수와 개념 보완이 필요한 부분을 나눠 목표를 정합니다. 일정 기간의 성적 향상을 보장할 수는 없습니다.';
 if(/고2.*선행/.test(q))return '현재 단원의 기본 문제를 혼자 풀고 이유를 설명할 수 있는지 먼저 확인하세요. 학교 평가가 가까우면 현재 범위의 빈틈을 정리하고, 선행은 필요한 이전 개념과 학습 가능한 시간을 확인한 뒤 범위를 정하세요.';
 if(/내신.*수능.*시간/.test(q))return '학교 평가일까지 남은 날과 모의평가에서 반복해 틀린 내용을 각각 적어 보세요. 겹치는 개념은 함께 복습하고 학교별 범위와 낯선 문항 연습은 구분해 계획합니다. 고정된 시간 비율보다 실행 기록을 보고 조정하세요.';
 if(/내신.*수능.*함께/.test(q))return '학교 교과서·평가 범위와 모의평가 답안을 함께 가져가 공통 개념과 별도 연습이 필요한 문항을 구분해 보세요. '+confirmation;
 if(/선행학습도 가능한가요/.test(q))return '선행 과정을 실제로 개설하는지와 가능한 학년·과목은 '+(c?c.key:'해당 지점')+'에 먼저 확인하세요. 현재 교재에서 혼자 푼 답안과 어려웠던 단원을 준비하고, 선행 범위·복습 시간·다시 확인하는 방법을 구분해 질문하세요.';
 if(/중학생.*선행/.test(q))return '고등 과정을 먼저 배웠는지보다 현재 중학교 단원의 개념과 풀이 이유를 설명할 수 있는지 확인하세요. 막히는 이전 개념이 있다면 보완하고, 선행 여부는 학교 진도·학습 시간·학생의 이해를 함께 보고 정하세요.';
 if(/성적이 낮게/.test(q))return '진단 점수만으로 학생의 능력이나 수강 과정을 결정하지 마세요. 틀린 문항 중 읽기·개념·계산·표현에서 막힌 부분을 나누고, 도움 뒤 다시 해결할 수 있는 과제부터 출발점을 확인하세요.';
 if(/모의고사 성적/.test(q))return '최근 답안 두세 회에서 단원, 실수 유형, 시간 부족으로 남긴 문항을 비교하세요. 시험마다 난이도가 다를 수 있으므로 점수 변화와 같은 개념에서의 반복 오류를 따로 기록하는 것이 좋습니다.';
 if(/공부는 하는데 성적/.test(q))return '공부한 시간과 혼자 다시 풀 수 있는 문제를 나누어 확인하세요. 해설을 읽은 문제를 가리고 재풀이한 기록, 과제를 끝내는 데 든 시간과 반복 오류를 가져오면 필요한 연습을 구체적으로 질문할 수 있습니다.';
 if(/오답노트/.test(q))return '별도 노트를 새로 사기보다 기존 교재나 종이에 문제 위치, 막힌 이유, 고친 풀이와 다시 확인할 날짜를 남겨 보세요. 지점에서 요구하는 기록 양식이나 준비물이 있는지는 방문 전에 확인하세요.';
 if(/문과.*이과/.test(q))return '문과·이과라는 구분만으로 학습 범위를 정하지 마세요. 학생이 실제 이수하는 과목, 학교 평가 범위와 진로에 필요한 과목을 적어 상담하세요. '+confirmation;
 if(/준비물을 자주/.test(q))return '다음 날 필요한 물건을 학교 안내와 대조해 짧은 목록으로 만들고, 가방을 챙길 때 학생이 직접 확인하게 해 보세요. 빠진 항목과 확인한 시간을 기록하면 어느 단계에서 도움이 필요한지 찾기 쉽습니다.';
 if(/자유학기/.test(q))return '학교의 현재 수업과 활동 안내를 확인하고 읽기·계산 등 기본 과제와 수행 과정의 기록을 이어가세요. 지필평가 일정만으로 공부를 정하기보다 배운 내용을 설명하고 다시 확인하는 시간을 확보하는 것이 좋습니다.';
 if(/중학교 첫 시험/.test(q))return '학교가 공지한 평가 일정과 범위를 먼저 확인하세요. 날짜를 정해 일괄적으로 시작하기보다 현재 단원의 이해, 수행평가 마감, 스스로 공부할 수 있는 시간을 바탕으로 복습과 재확인 일정을 나누세요.';
 if(/중학교 입학|초등학교에서 중학교/.test(q))return '현재 교과서의 읽기와 계산 과제에서 혼자 설명할 수 있는 부분을 확인하고, 준비물·과제·마감일을 스스로 적는 연습을 해 보세요. 입학할 학교의 실제 교육과정과 생활 안내가 나오면 그 자료에 맞춰 준비 범위를 조정하세요.';
 if(/고등학교 진학/.test(q))return '현재 학교의 진로·진학 안내와 다음 학교의 공식 교육과정 자료를 확인하세요. 중학교 과제에서 남은 개념의 빈틈, 과목 선택에 관한 질문, 주간 학습 시간을 정리해 두면 이후 계획을 구체화할 수 있습니다.';
 if(/고1.*준비/.test(q))return '학교에서 실제 이수하는 공통·선택과목과 현재 교과서를 확인하세요. 새 단원을 배우며 막힌 이전 개념을 따로 기록하고, 학교 과제·평가 일정과 혼자 복습할 시간을 한 주 계획에 함께 적어 보세요.';
 if(/상담.*준비/.test(q))return '최근 답안 한두 장과 학교 평가 안내, 현재 교재를 준비하세요. 혼자 해결한 부분과 도움받은 부분을 표시하고 가능한 요일·시간을 적어 오면 '+(c?c.key+'에서 ':'')+'수강 조건과 필요한 도움을 함께 확인하기 쉽습니다.';
 return null;
}

// Preserve old bookmark URLs after the media section received its descriptive ID.
export function repairMediaAnchors(s,name){
 if(!name.startsWith('과목별학원/'))return {html:s,count:0};
 const ids=new Set([...s.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]));
 const missing=[...new Set([...s.matchAll(/<a\b[^>]*href="#(subject-section-\d+)"[^>]*>[\s\S]*?<\/a>/g)].filter(m=>!ids.has(m[1])).map(m=>{
  if(!/class="subject-page-toc-text"[^>]*>와와학습코칭센터 /.test(m[0]))throw Error('Unclear missing media anchor: '+name);
  return m[1];
 }))];
 if(!missing.length)return {html:s,count:0};
 const target=/<section\b[^>]*\bclass="[^"]*\bsubject-media-section\b[^"]*"[^>]*>/g;
 if([...s.matchAll(target)].length!==1)throw Error('Missing unique media destination: '+name);
 return {html:s.replace(target,tag=>tag+missing.map(id=>'<span id="'+id+'"></span>').join('')),count:missing.length};
}

export function transform(input,name){
 let s=input,counts={},changedFAQ=new Map();
 const count=k=>counts[k]=(counts[k]||0)+1;
 const parts=name.split('/'),family=parts[0],c=facts.centers[facts.pageCenter[name]];
 const landing=['과목별학원','전국학원','지점안내'].includes(family)&&parts.length>=4;
 // Put existing, image-free branch facts before supplementary reading.
 if(landing){
  let nodes=nodesOf(s),resources=nodes.find(n=>n.attrs.id==='study-resources'),main=nodes.find(n=>n.tag==='main');
  if(resources&&main){
   const ids=family==='지점안내'?['center-facts','courses']:['actual-center','local-center-facts','enrollment'];
   const blocks=ids.map(id=>nodes.find(n=>n.attrs.id===id)).filter(n=>n&&n.start>resources.start&&n.parent===main&&!/<img\b/i.test(cut(s,n)));
   if(blocks.length){s=edits(s,[{start:resources.start,end:resources.start,value:blocks.map(n=>cut(s,n)).join('')},...blocks.map(n=>({start:n.start,end:n.end,value:''}))]);count('branchFactsFirst');}
  }
  // Keep every existing resource destination, remove repeated introductory labels.
  nodes=nodesOf(s);resources=nodes.find(n=>n.attrs.id==='study-resources');
  if(resources){
   const sections=['curriculum-connection','education-info-links'].map(id=>nodes.find(n=>n.attrs.id===id&&inside(n,resources)));
   if(sections.every(Boolean)){
    const body=sections.map((n,i)=>{const links=nodes.filter(a=>a.tag==='a'&&inside(a,n)).map(a=>cut(s,a));return '<div id="'+n.attrs.id+'"><h3 id="'+n.attrs.id+'-title">'+(i?'함께 읽을 공부 방법':'학년·과목별 공부 순서')+'</h3>'+(i?'':para('학교 교과서와 현재 진도에 맞춰 필요한 과제를 골라 보세요.'))+'<div class="'+(i?'ei-actions':'cu-actions')+'">'+links.join('')+'</div></div>';}).join('');
    s=edits(s,[{start:resources.start,end:resources.end,value:'<section class="crawl-resources" id="study-resources" aria-labelledby="study-resources-title"><h2 id="study-resources-title">관련 공부 자료</h2><div class="crawl-resource-grid">'+body+'</div></section>'}]);count('compactResources');
   }
  }
 }
 // Subject pages retain one full conditions block. Other subjects stay on the branch page.
 if(family==='과목별학원'&&parts.length===4&&c){
  let nodes=nodesOf(s),actual=nodes.find(n=>n.attrs.id==='actual-center'),patch=[];
  for(const n of paragraphs(s,nodes)){
   const text=plain(cut(s,n)),inFAQ=ancestors(n).some(x=>x.tag==='details');
   if(text.startsWith(c.key+'의 자료상 ')&&!inFAQ&&(!actual||!inside(n,actual))){patch.push({start:n.start,end:n.end,value:''});count('duplicateConditions');}
   else if(c.courseNotes.includes(text)&&actual&&inside(n,actual)){
    const subject=parts[1].includes('수학')?'수학':'영어';
    if(!text.includes(subject)&&!nodes.some(a=>a.tag==='a'&&inside(a,n))){patch.push({start:n.start,end:n.end,value:''});count('unrelatedCourseNotes');}
   }
  }
  if(patch.length)s=edits(s,patch);
 }
 // Added school lists are redundant only when every name already exists in that same section.
 if(c){
  const nodes=nodesOf(s),patch=[];
  for(const n of paragraphs(s,nodes)){
   const text=plain(cut(s,n));if(!text.startsWith('자료에 기재된 학교 참고: '))continue;
   const section=ancestors(n).find(x=>x.tag==='section');if(!section)continue;
   const names=text.slice('자료에 기재된 학교 참고: '.length).replace(/\.$/,'').split(' · '),before=plain(s.slice(section.start,n.start));
   if(names.length&&names.every(x=>before.includes(x))){patch.push({start:n.start,end:n.end,value:''});count('duplicateSchoolList');}
  }
  if(patch.length)s=edits(s,patch);
 }
 // Preserve FAQ questions, improve answers which repeated a different question or the main body.
 {
  const nodes=nodesOf(s),ps=paragraphs(s,nodes),frequency=new Map();for(const p of ps){const text=plain(cut(s,p));frequency.set(text,(frequency.get(text)||0)+1);}
  const issue=nodes.find(n=>n.attrs.id==='learning-issue'),patch=[];
  for(const d of nodes.filter(n=>n.tag==='details'&&ancestors(n).some(x=>x.tag==='main'))){
   const qn=d.children.find(n=>n.tag==='summary');if(!qn)continue;const q=plain(cut(s,qn)).replace(/\s*[+−–]\s*$/,'');
   const answerPs=ps.filter(n=>inside(n,d));if(answerPs.length!==1)continue;
   const n=answerPs[0],old=plain(cut(s,n));let next=null;
   if(family==='전국학원'&&((frequency.get(old)||0)>1||/수강 조건은/.test(old)))next=answer(q,c);
   if(family==='지점안내'&&issue&&(frequency.get(old)||0)>1&&/무엇부터 확인/.test(q)){
    const h=nodes.find(n=>n.tag==='h2'&&inside(n,issue)),topic=h?plain(cut(s,h)).split(':')[0]:'';
    next=(topic?'위의 '+topic+' 점검에서 ':'최근 과제에서 ')+'학생에게 해당하는 장면을 고르고, 시도한 답안과 막힌 부분을 준비하세요. 비교 질문에 대한 지점의 답변을 적은 뒤 실제 수강 학년·과목과 방문 조건을 확인하세요.';
   }
   if(family==='학습커리큘럼'&&/순서대로 학교 진도/.test(q)&&(frequency.get(old)||0)>1)next='학교별 단원 순서나 이수 학기를 확정하는 표는 아닙니다. 현재 교과서·시간표·평가 안내를 기준으로 필요한 부분을 골라 활용하세요. 교육과정 적용 범위와 주의사항은 위의 학습 범위 안내에서 확인할 수 있습니다.';
   if(family==='과목별학원'&&c&&old.startsWith(c.key+'의 자료상 ')){
    const g=parts[1].match(/^(초[3-6]|중[1-3]|고[1-2])(수학|영어)학원$/);
    if(g){const supported=(c.subjects[g[2]]||[]).includes(g[1]);next=c.key+' 자료의 '+g[2]+' 안내 학년에 '+g[1]+(supported?' 과정이 포함돼 있습니다.':' 과정이 포함돼 있지 않습니다.')+' 현재 개설 과정·잔여 자리·교재와 수업 시간은 지점에 확인하세요. 전체 과목의 조건은 지점 상세 안내에서 볼 수 있습니다.';}
   }
   if(next&&next!==old){patch.push({start:n.start,end:n.end,value:para(next)});changedFAQ.set(q,next);count('focusedFaqAnswers');if(/선행학습도 가능한가요/.test(q))count('specificAdvanceAvailabilityAnswers');}
  }
  if(patch.length)s=edits(s,patch);
 }
 // Repeated non-FAQ prose is removed only when an earlier copy remains; links/media/IDs are protected.
 {
  const nodes=nodesOf(s),seen=new Set(),patch=[];
  for(const n of paragraphs(s,nodes)){
   if(ancestors(n).some(x=>x.tag==='details'))continue;
   const text=plain(cut(s,n));if(text.length<60)continue;
   if(seen.has(text)&&!n.attrs.id&&!/<(?:a|img|input)\b/.test(cut(s,n))){patch.push({start:n.start,end:n.end,value:''});count('duplicateBodyParagraphs');}else seen.add(text);
  }
  if(patch.length)s=edits(s,patch);
 }
 // Existing branch and curriculum links give more useful next steps than distant-region suggestions.
 if(family==='과목별학원'&&parts.length===4&&c){
  const nodes=nodesOf(s),links=nodes.filter(n=>n.tag==='a'&&plain(cut(s,n)).includes('다른 지역 안내'));
  const local=parts[2],course=parts[1],g=course.match(/^(초[3-6]|중[1-3]|고[1-2])(수학|영어)학원$/);
  if(g&&links.length){
   const year=Number(g[1].slice(1)),prefix=g[1][0],adjacent=[year-1,year+1].filter(y=>prefix==='초'?y>=3&&y<=6:prefix==='중'?y>=1&&y<=3:y>=1&&y<=2);
   const candidates=[{href:c.path,title:c.key+' 전체 수강 안내',label:'실제 지점 조건'},...adjacent.map(y=>({href:'/과목별학원/'+prefix+y+g[2]+'학원/'+local+'/',title:local+' '+prefix+y+' '+g[2]+' 안내',label:'같은 동네의 학습 단계'})),{href:'/학습커리큘럼/'+g[1]+'/'+g[2]+'/',title:g[1]+' '+g[2]+' 공부 순서',label:'관련 학습 준비'}];
   const patch=[];for(let i=0;i<links.length;i++){const n=links[i],dest=candidates[i%candidates.length];if(!facts.knownPages[dest.href])continue;
    const open=s.slice(n.start,n.openEnd).replace(/\bhref="[^"]*"/,'href="'+esc(encodeURI(dest.href))+'"');
    patch.push({start:n.start,end:n.end,value:open+'<strong>'+esc(dest.title)+'</strong><small>'+esc(dest.label)+'</small></a>'});count('relevantNextSteps');}
   if(patch.length)s=edits(s,patch);
  }
 }
 const repaired=repairMediaAnchors(s,name);s=repaired.html;
 if(repaired.count)counts.repairedMediaAnchors=repaired.count;
 const editorialChanged=s!==input;
 const modified=editorialChanged?date:photos.pages[name]?photoDate:null;
 if(modified){
  s=s.replace(/<script\b[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi,(tag,raw)=>{
   const doc=JSON.parse(raw);let touched=false;
   function walk(x){if(Array.isArray(x)){x.forEach(walk);return;}if(!x||typeof x!=='object')return;
    const types=Array.isArray(x['@type'])?x['@type']:[x['@type']];
    if(types.some(t=>['WebPage','CollectionPage','Article'].includes(t))){if(x.dateModified!==modified){x.dateModified=modified;touched=true;}}
    if(types.includes('FAQPage'))for(const q of x.mainEntity||[]){if(changedFAQ.has(q.name)&&q.acceptedAnswer){q.acceptedAnswer.text=changedFAQ.get(q.name);touched=true;}}
    Object.values(x).forEach(walk);
   }walk(doc);return touched?tag.replace(raw,JSON.stringify(doc).replaceAll('<','\\u003c')):tag;
  });
  s=s.replace(/(<meta\b[^>]*property="article:modified_time"[^>]*content=")[^"]*(")/gi,(_,a,b)=>a+modified+b);
 }
 return {html:s,modified,editorialChanged,counts};
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
const prepare=process.argv.includes('--prepare'),check=process.argv.includes('--check');
const materialize=prepare&&process.argv.includes('--materialize');
if(materialize&&check)throw Error('Cannot materialize in check mode');
const reportArg=process.argv.find(a=>a.startsWith('--report='));
const outputReport=reportArg?path.resolve(reportArg.slice(9)):null;
const names=Object.keys(JSON.parse(fs.readFileSync(path.join(root,'release-public-manifest.json'),'utf8')).files).filter(n=>n.endsWith('index.html')).sort();
const review=prepare?{version:1,reviewedAt:date,baselineCommit:'9f0128434109a915350d5b1c5b1f18eafa5d2ed1',pages:{}}:JSON.parse(fs.readFileSync(reviewPath,'utf8'));
const report={checked:0,changed:0,editorial:0,dateOnly:0,counts:{},pages:[],unchanged:0};
const modifiedPaths=new Map();
for(const name of names){
 const file=path.join(out,name),before=fs.readFileSync(file,'utf8'),entry=review.pages[name];report.checked++;
 if(report.checked%2000===0)console.log('Editorial pages checked: '+report.checked);
 if(!prepare&&entry&&sha(before)===entry.after){modifiedPaths.set('/'+name.replace(/index\.html$/,''),entry.modified);report.unchanged++;continue;}
 if(!prepare&&entry&&sha(before)!==entry.before)throw Error('Unreviewed page input: '+name);
 const result=transform(before,name);
 if(result.html===before){if(entry)throw Error('Reviewed change not reproduced: '+name);report.unchanged++;continue;}
 if(prepare)review.pages[name]={before:sha(before),after:sha(result.html),modified:result.modified,editorial:result.editorialChanged,counts:result.counts};
 else if(!entry||sha(result.html)!==entry.after)throw Error('Unreviewed output: '+name);
 // Images, their order, source URLs and surrounding media wrappers remain untouched.
 const media=s=>(s.match(/<(?:img|source)\b[^>]*>/gi)||[]);
 if(JSON.stringify(media(before))!==JSON.stringify(media(result.html)))throw Error('Image preservation failed: '+name);
 const identity=s=>(s.match(/<link\b[^>]*rel="canonical"[^>]*>|<title>[\s\S]*?<\/title>|<meta\b[^>]*(?:name="robots"|name="description"|property="og:image"|name="twitter:image")[^>]*>/gi)||[]);
 if(JSON.stringify(identity(before))!==JSON.stringify(identity(result.html)))throw Error('Page identity changed: '+name);
 modifiedPaths.set('/'+name.replace(/index\.html$/,''),result.modified);report.changed++;report[result.editorialChanged?'editorial':'dateOnly']++;
 for(const [k,v] of Object.entries(result.counts))report.counts[k]=(report.counts[k]||0)+v;
 report.pages.push({name,...(prepare?review.pages[name]:entry)});
 if((!prepare&&!check)||materialize)fs.writeFileSync(file,result.html);
}
const sm=path.join(out,'sitemap.xml'),beforeSM=fs.readFileSync(sm,'utf8');
const afterSM=beforeSM.replace(/<url>([\s\S]*?)<\/url>/g,(tag,body)=>{const loc=decode(body.match(/<loc>([^<]+)<\/loc>/)?.[1]||'');let p;try{p=decodeURIComponent(new URL(loc).pathname);}catch{return tag;}const d=modifiedPaths.get(p);return d?tag.replace(/<lastmod>[^<]*<\/lastmod>/,'<lastmod>'+d+'</lastmod>'):tag;});
// RSS contains full article bodies: sync only articles actually changed, preserving publication dates.
const rssFile=path.join(out,'rss.xml'),beforeRSS=fs.readFileSync(rssFile,'utf8');let rssChanged=0;
const afterRSS=beforeRSS.replace(/<item>([\s\S]*?)<\/item>/g,(tag,body)=>{const link=decode(body.match(/<link>([^<]+)<\/link>/)?.[1]||'');let p;try{p=decodeURIComponent(new URL(link).pathname);}catch{return tag;}const entry=review.pages[p.slice(1)+'index.html'];if(!entry?.editorial)return tag;
 // Educational articles are only touched if reviewed body edits were necessary.
 const file=path.join(out,p.slice(1),'index.html'),raw=fs.readFileSync(file,'utf8'),source=sha(raw)===entry.after?raw:transform(raw,p.slice(1)+'index.html').html;
 const main=nodesOf(source).find(n=>n.tag==='main');let content=source.slice(main.openEnd,main.closeStart).replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,'').replace(/<form\b[^>]*>[\s\S]*?<\/form>/gi,'');
 content=content.replace(/\b(href|src|srcset)="([^"]*)"/gi,(m,k,v)=>{const absolute=x=>{try{return new URL(decode(x),facts.origin+p).href;}catch{return x;}};return k+'="'+esc(k==='srcset'?v.split(',').map(x=>x.trim().replace(/^(\S+)/,absolute)).join(', '):absolute(v))+'"';});
 rssChanged++;return tag.replace(/<content:encoded>[\s\S]*?<\/content:encoded>/,'<content:encoded><![CDATA['+content.replaceAll(']]>',']]]]><![CDATA[>')+']]></content:encoded>');});
if(prepare){review.sitemap={before:sha(beforeSM),after:sha(afterSM)};review.rss={before:sha(beforeRSS),after:sha(afterRSS)};fs.writeFileSync(reviewPath,JSON.stringify(review,null,2)+'\n');if(materialize){fs.writeFileSync(sm,afterSM);if(beforeRSS!==afterRSS)fs.writeFileSync(rssFile,afterRSS);}}
else{if(![review.sitemap.before,review.sitemap.after].includes(sha(beforeSM))||sha(afterSM)!==review.sitemap.after)throw Error('Sitemap not reviewed');if(![review.rss.before,review.rss.after].includes(sha(beforeRSS))||sha(afterRSS)!==review.rss.after)throw Error('RSS not reviewed');if(!check){fs.writeFileSync(sm,afterSM);if(beforeRSS!==afterRSS)fs.writeFileSync(rssFile,afterRSS);}}
report.rssArticlesSynced=rssChanged;report.sitemapChanged=beforeSM!==afterSM;
if(outputReport)fs.writeFileSync(outputReport,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({...report,pages:undefined,mode:prepare?'prepare':check?'check':'apply'}));
}
