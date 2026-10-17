/** Add verified branch directions after the existing, reviewed public pipeline. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.dirname(fileURLToPath(import.meta.url));
const sha=b=>createHash('sha256').update(b).digest('hex');
const lf=s=>s.replaceAll('\r\n','\n');
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;');
export function assetsFor(data){
 const files={},urls={};
 for(const file of ['kakao-directions.css','kakao-directions.js','kakao-frame.css','kakao-frame.js']){
  const b=Buffer.from(lf(fs.readFileSync(path.join(root,'kakao-map-ui',file),'utf8'))),[stem,ext]=file.split('.');
  const n=`assets/${stem}.${sha(b).slice(0,12)}.${ext}`;files[n]=b;urls[file]='/'+n;
 }
 const maps={};
 for(const [branch,m] of Object.entries(data.branches)){
  const frame=`<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,follow"><meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests"><title>${esc(branch)} 위치 지도</title><link rel="stylesheet" href="${urls['kakao-frame.css']}"></head><body>
<div id="daumRoughmapContainer${m.timestamp}" class="root_daum_roughmap root_daum_roughmap_landing"></div>
<script charset="UTF-8" class="daum_roughmap_loader_script" src="https://t1.kakaocdn.net/kakaomapweb/roughmap/loader/prod/roughmapLoader.js"></script>
<script>window.chaeumMap=new daum.roughmap.Lander({timestamp:"${m.timestamp}",key:"${m.key}",mapWidth:String(document.documentElement.clientWidth),mapHeight:String(Math.max(240,innerHeight-36))});window.chaeumMap.render();</script>
<script src="${urls['kakao-frame.js']}"></script></body></html>`;
  const frameName=`assets/kakao-maps/${m.timestamp}/index.html`,trafficName=`assets/kakao-traffic/${m.timestamp}.json`;
  files[frameName]=Buffer.from(frame);files[trafficName]=Buffer.from(JSON.stringify(m.groups));
  maps[branch]={...m,branch,frame:'/'+frameName.replace('index.html','')+'?v='+sha(files[frameName]).slice(0,12),traffic:'/'+trafficName+'?v='+sha(files[trafficName]).slice(0,12)};
 }
 const hubs={};
 for(const p of data.pages.filter(p=>p.kind==='hub')){
  const options=p.choices.map(branch=>{const m=maps[branch];return {branch,frame:m.frame,address:m.address,traffic:m.traffic};});
  const b=Buffer.from(JSON.stringify(options)),name='assets/kakao-options/'+sha(b).slice(0,16)+'.json';files[name]=b;hubs[p.file]='/'+name;
 }
 return {files,urls,maps,hubs};
}
function traffic(groups){return groups.length?'<ul class="kd-traffic">'+groups.map(g=>'<li><h3>'+esc(g.title)+'</h3><'+(g.className==='kd-stops'?'ol':'ul')+' class="'+g.className+'">'+g.items.map((v,i)=>'<li>'+(g.className==='kd-stops'?'<span class="kd-stop-number" aria-hidden="true">'+(i+1)+'</span>':'')+(typeof v==='string'?'<span>'+esc(v)+'</span>':'<span class="kd-bus-type kd-bus-'+v.type+'">'+esc(v.label)+'</span><span class="kd-bus-numbers">'+v.names.map(n=>'<span>'+esc(n)+'</span>').join('')+'</span>')+'</li>').join('')+'</'+(g.className==='kd-stops'?'ol':'ul')+'></li>').join('')+'</ul>':'<p>이 약도에는 주변 교통 정보가 등록되어 있지 않습니다.</p>';}
function section(page,data,assets){
 const m=assets.maps[page.kind==='hub'?page.choices[0]:page.branch],hub=page.kind==='hub';
 return `\n<section class="kakao-directions" id="kakao-directions" data-kakao-${hub?'hub':'branch'}="${esc(hub?data.date:m.branch)}"${hub?' data-kakao-options="'+assets.hubs[page.file]+'"':''}><h2>${hub?'지점 위치와 찾아오시는 길':'찾아오시는 길'}</h2><p class="kd-intro">${hub?'방문할 지점을 선택해 지도와 주변 교통편을 확인하세요.':esc(m.branch)+'의 위치와 주변 교통편을 확인하세요.'}</p>${hub?'<label class="kd-hub-label" for="kakao-branch-select">지점 선택</label><select id="kakao-branch-select" class="kd-hub-select" data-kakao-select><option value="'+esc(m.frame)+'">'+esc(m.branch)+'</option></select><p class="kd-hub-status" role="status" aria-live="polite">'+esc(m.branch)+'의 위치를 표시합니다.</p>':''}<div class="kd-map-shell"><div class="kd-map-status" aria-hidden="true">지도 위치를 자동으로 불러옵니다.</div><iframe title="${esc(m.branch)} 위치 지도" data-kakao-src="${esc(m.frame)}" loading="lazy" width="900" height="420" sandbox="allow-scripts allow-same-origin" referrerpolicy="strict-origin-when-cross-origin"></iframe></div><dl class="kd-address"><dt>주소</dt><dd>${esc(m.address)}</dd></dl><div class="kd-traffic-holder">${traffic(m.groups)}</div><p class="kd-source">카카오맵 약도의 위치·교통 정보입니다. 운행 노선과 정류장은 달라질 수 있습니다.</p><noscript><p>${hub?'기존 지점 목록에서 지점별 위치와 교통 정보를 확인해 주세요.':'위 지도 이미지와 주소·교통 안내를 확인해 주세요.'}</p></noscript></section>\n`;
}
export function transform(before,page,data,assets){
 if(before.includes('data-kakao-style='))throw Error('Map already applied: '+page.file);
 let after;const block=section(page,data,assets);
 if(page.kind==='hub'){if((before.match(/<\/main>/g)||[]).length!==1)throw Error('Main mismatch '+page.file);after=before.replace('</main>',block+'</main>');}
 else{
  const figures=[...before.matchAll(/<figure\b[^>]*>[\s\S]*?<\/figure>/g)].filter(m=>/<img\b[^>]*(?:alt=["'][^"']*지도|data-media=["']map["'])/.test(m[0]));
  if(figures.length!==1)throw Error('Map image mismatch '+page.file);const pos=figures[0].index+figures[0][0].length;after=before.slice(0,pos)+block+before.slice(pos);
 }
 after=after.replace('</head>',`<link rel="stylesheet" href="${assets.urls['kakao-directions.css']}" data-kakao-style="${data.date}"><script defer src="${assets.urls['kakao-directions.js']}" data-kakao-script="${data.date}"></script></head>`);
 return after.replace(/("dateModified"\s*:\s*")[^"]*(")/g,'$1'+data.date+'$2');
}
export async function apply(rootOutput,prepare=false,stage=null){
 const data=JSON.parse(fs.readFileSync(path.join(root,'kakao-map-data.json'),'utf8')),assets=assetsFor(data),reviewFile=path.join(root,'kakao-map-review.json');
 const review=prepare?{date:data.date,pages:{},assets:{}}:JSON.parse(fs.readFileSync(reviewFile,'utf8'));
 const output=stage||rootOutput;let changed=0,already=0;
 for(const page of data.pages){
  const file=path.join(rootOutput,page.file),before=fs.readFileSync(file,'utf8'),hash=sha(lf(before));
  if(!prepare&&hash===review.pages[page.file]?.after){already++;continue;}
  if(!prepare&&hash!==review.pages[page.file]?.before)throw Error('Unreviewed map input '+page.file);
  const after=transform(before,page,data,assets),afterHash=sha(lf(after));
  if(prepare)review.pages[page.file]={before:hash,after:afterHash};else if(afterHash!==review.pages[page.file].after)throw Error('Map review drift '+page.file);
  if(stage||!prepare){const dest=path.join(output,page.file);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,after);}changed++;
 }
 for(const [name,bytes] of Object.entries(assets.files)){
  const hash=sha(bytes);if(prepare)review.assets[name]=hash;else if(review.assets[name]!==hash)throw Error('Unreviewed map asset '+name);
  if(stage||!prepare){const dest=path.join(output,name);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,bytes);}
 }
 const sitemapFile=path.join(rootOutput,'sitemap.xml'),before=fs.readFileSync(sitemapFile,'utf8'),routes=new Set(data.pages.map(p=>'/'+p.file.replace(/index\.html$/,'')));
 const after=before.replace(/<url\b[^>]*>[\s\S]*?<\/url>/g,node=>{const loc=node.match(/<loc>(.*?)<\/loc>/)?.[1];return loc&&routes.has(decodeURI(new URL(loc).pathname))?node.replace(/<lastmod>[^<]*<\/lastmod>/,'<lastmod>'+data.date+'</lastmod>'):node;});
 if(prepare)review.sitemap={before:sha(lf(before)),after:sha(lf(after))};else if(![review.sitemap.before,review.sitemap.after].includes(sha(lf(before)))||sha(lf(after))!==review.sitemap.after)throw Error('Sitemap review drift');
 if(stage||!prepare)fs.writeFileSync(path.join(output,'sitemap.xml'),after);
 if(prepare)fs.writeFileSync(reviewFile,JSON.stringify(review,null,2)+'\n');
 console.log(JSON.stringify({mapPages:data.pages.length,changed,already,newAssets:Object.keys(assets.files).length,prepared:prepare,stage:!!stage}));
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))await apply(path.join(root,'.public-release'),process.argv.includes('--prepare'),process.argv.find(x=>x.startsWith('--stage='))?.slice(8)||null);
