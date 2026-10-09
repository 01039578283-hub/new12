/** Select verified, visible branch photographs without moving existing media. */
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseHTML} from './image-order-build.mjs';

const root=path.dirname(fileURLToPath(import.meta.url));
const output=path.join(root,'.public-release');
const data=JSON.parse(fs.readFileSync(path.join(root,'branch-thumbnail-data.json'),'utf8'));
const sha=s=>createHash('sha256').update(s).digest('hex');
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');
const ancestors=n=>{const a=[];for(let p=n.parent;p;p=p.parent)a.push(p);return a;};
const attr=(tag,key,value)=>{
 const rx=new RegExp('\\s'+key+'(?:\\s*=\\s*(?:"[^"]*"|\'[^\']*\'|[^\\s>]+))?','i');
 const a=' '+key+'="'+esc(value)+'"';
 return rx.test(tag)?tag.replace(rx,a):tag.replace(/\s*\/?>$/,a+'>');
};
const replace=(s,edits)=>{
 edits.sort((a,b)=>b.start-a.start);let edge=s.length;
 for(const e of edits){if(e.end>edge)throw Error('Overlapping thumbnail edits');s=s.slice(0,e.start)+e.value+s.slice(e.end);edge=e.start;}
 return s;
};
const imageAsset=src=>decodeURIComponent(new URL(src,data.origin).pathname).slice(1);
function schemaImages(obj,url,row){
 if(Array.isArray(obj)){obj.forEach(v=>schemaImages(v,url,row));return;}
 if(!obj||typeof obj!=='object')return;
 const types=[obj['@type']].flat();
 if(types.some(t=>['WebPage','Article','BlogPosting'].includes(t))){
  if(obj.primaryImageOfPage!==undefined&&!obj.primaryImageOfPage?.['@id'])obj.primaryImageOfPage={'@type':'ImageObject',url,contentUrl:url,width:row.width,height:row.height,caption:row.caption};
  if(obj.image!==undefined)obj.image=url;
 }
 if(row.photoType!=='common-reference'&&types.some(t=>['LocalBusiness','EducationalOrganization'].includes(t))&&obj.image!==undefined){
  const originals=[obj.image].flat().filter(v=>typeof v==='string'&&row.branchImageAssets.includes(imageAsset(v))&&imageAsset(v)!==imageAsset(url));
  obj.image=Array.isArray(obj.image)?[url,...originals]:url;
 }
 // Linked primary ImageObjects are page media. Organization logos remain untouched.
 if(types.includes('ImageObject')&&/#primaryimage$/i.test(obj['@id']||'')){
  obj.url=url;obj.contentUrl=url;obj.width=row.width;obj.height=row.height;obj.caption=row.caption;
 }
 for(const [k,v] of Object.entries(obj))if(k!=='logo')schemaImages(v,url,row);
}
const style='<style data-branch-thumbnail="v1">.branch-photo-bottom{margin:40px auto 0;padding:24px 0;width:calc(100% - 36px);max-width:960px}.branch-photo-bottom h2{font-size:1.5rem;margin:0 0 12px}.branch-photo-bottom figure{margin:20px 0 0}.branch-photo-bottom [data-branch-photo]{display:block;width:100%;height:auto;max-width:100%;object-fit:contain}.branch-photo-bottom figcaption{margin-top:10px;font-size:.95rem;line-height:1.6}.branch-photo-bottom p{line-height:1.7}.branch-photo-bottom a{display:block;color:inherit}.branch-photo-bottom a:focus-visible{outline:3px solid #277953;outline-offset:4px}</style>';
const report={targetPages:data.targetPages,completed:0,held:data.held.length,existingPhotos:0,addedBottomPhotos:0,removedHiddenElements:0,unfolded:0};
for(const [name,row] of Object.entries(data.pages)){
 const file=path.resolve(output,name);if(!file.startsWith(output+path.sep))throw Error('Unsafe thumbnail page');
 const before=fs.readFileSync(file,'utf8');
 if(sha(before.replaceAll('\r\n','\n'))!==row.beforeShaLF)throw Error('Unreviewed page change: '+name);
 const image=path.resolve(output,imageAsset(row.src));
 if(!image.startsWith(output+path.sep)||sha(fs.readFileSync(image))!==row.imageSha256)throw Error('Unverified image: '+name);
 if(!(row.width>150&&row.height>150&&row.bytes>=5000&&row.width/row.height<=3))throw Error('Invalid image criteria: '+name);
 const nodes=parseHTML(before),head=nodes.find(n=>n.tag==='head'),main=nodes.find(n=>n.tag==='main');
 if(!head||!main)throw Error('Missing page document structure: '+name);
 const patch=[];const visibleURL=new URL(row.src,data.origin).href;
 const common=row.photoType==='common-reference';
 // Only previously inventoried hidden representative elements are removed.
 const hidden=nodes.filter(n=>n.tag==='img'&&ancestors(n).includes(main)&&(Object.hasOwn(n.attrs,'hidden')||/display\s*:\s*none/i.test(n.attrs.style||''))&&(n.attrs['data-media-role']==='representative'||/\/representative\//.test(n.attrs.src||'')));
 if(hidden.length!==row.hiddenCount)throw Error('Hidden representative inventory changed: '+name);
 for(const n of hidden)patch.push({start:n.start,end:n.end,value:''});
 report.removedHiddenElements+=hidden.length;
 const existing=nodes.filter(n=>n.tag==='img'&&ancestors(n).includes(main)&&imageAsset(n.attrs.src||'/')===imageAsset(row.src));
 if(row.existing){
  if(existing.length!==1)throw Error('Existing branch photograph is absent or duplicated: '+name);
  const n=existing[0];let tag=before.slice(n.start,n.end);
  const markers=common?{'data-common-photo':'reference'}:{'data-branch-photo':row.center};
  for(const [k,v] of Object.entries({'src':row.src,'alt':row.caption,'width':row.width,'height':row.height,'loading':n.attrs.loading||'lazy','decoding':'async',...markers,'data-page-image':'primary'}))tag=attr(tag,k,v);
  tag=attr(tag,'style',(n.attrs.style||'').replace(/(?:^|;)\s*(?:aspect-ratio|object-fit|height|max-height)\s*:[^;]*/gi,'')+';aspect-ratio:'+row.width+'/'+row.height+';height:auto;max-height:none;object-fit:contain;');
  patch.push({start:n.start,end:n.end,value:tag});report.existingPhotos++;
  const figure=ancestors(n).find(x=>x.tag==='figure'),caption=figure?.children.find(x=>x.tag==='figcaption');
  if(caption)patch.push({start:caption.openEnd,end:caption.closeStart,value:esc(row.caption)});
  const gates=ancestors(n).filter(x=>x.tag==='details');
  for(const gate of gates){
   patch.push({start:gate.start,end:gate.openEnd,value:before.slice(gate.start,gate.openEnd).replace(/^<details\b/i,'<div').replace(/\sopen(?:="[^"]*")?/i,'')});
   patch.push({start:gate.closeStart,end:gate.end,value:'</div>'});
   for(const child of gate.children.filter(x=>x.tag==='summary'))patch.push({start:child.start,end:child.end,value:''});
   report.unfolded++;
  }
  if(ancestors(n).some(x=>Object.hasOwn(x.attrs,'hidden')||/display\s*:\s*none/i.test(x.attrs.style||'')))throw Error('Unreviewed hidden gallery: '+name);
 }else{
  if(existing.length)throw Error('Refusing a duplicate branch photograph: '+name);
  const heading=common?'공용 학습 공간 참고 사진':row.center+' 제공 사진';
  const explanation=common?'공용사진을 활용한 학습 공간 참고 이미지입니다. 해당 지점의 실제 공간 사진은 아닙니다. 실제 시설과 좌석 구성은 지점 방문 상담에서 확인해 주세요.':'제공받은 지점 사진입니다. 촬영 이후 공간 모습은 달라질 수 있습니다.';
  const marker=common?'data-common-photo="reference"':'data-branch-photo="'+esc(row.center)+'"';
  const body='<section class="branch-photo-bottom" id="branch-photo" aria-labelledby="branch-photo-title"><h2 id="branch-photo-title">'+esc(heading)+'</h2><p>'+esc(explanation)+'</p><figure><a href="'+esc(row.src)+'" aria-label="'+esc(row.caption+' 원본 열기')+'"><img src="'+esc(row.src)+'" alt="'+esc(row.caption)+'" width="'+row.width+'" height="'+row.height+'" loading="lazy" decoding="async" '+marker+' data-page-image="primary"></a><figcaption>'+esc(row.caption)+'</figcaption></figure></section>';
  patch.push({start:main.closeStart,end:main.closeStart,value:body});report.addedBottomPhotos++;
 }
 // Remove all image metadata before inserting one consistent set in the initial head.
 const imageMeta=nodes.filter(n=>n.tag==='meta'&&ancestors(n).includes(head)&&(/^(og:image(?::.*)?|twitter:image(?::.*)?)$/i.test(n.attrs.property||'')||/^(og:image(?::.*)?|twitter:image(?::.*)?)$/i.test(n.attrs.name||'')));
 for(const n of imageMeta)patch.push({start:n.start,end:n.end,value:''});
 const meta='<meta property="og:image" content="'+esc(visibleURL)+'"><meta property="og:image:secure_url" content="'+esc(visibleURL)+'"><meta property="og:image:type" content="'+row.mime+'"><meta property="og:image:width" content="'+row.width+'"><meta property="og:image:height" content="'+row.height+'"><meta property="og:image:alt" content="'+esc(row.caption)+'"><meta name="twitter:image" content="'+esc(visibleURL)+'"><meta name="twitter:image:alt" content="'+esc(row.caption)+'">';
 const photoStyle=common?style.replace('data-branch-thumbnail','data-common-thumbnail').replace('[data-branch-photo]','[data-common-photo]'):style;
 patch.push({start:head.closeStart,end:head.closeStart,value:meta+(row.existing?'':photoStyle)});
 for(const match of before.matchAll(/<script\b[^>]*\btype=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script\s*>/gi)){
  const raw=match[1],start=match.index+match[0].indexOf('>')+1,end=start+raw.length,o=JSON.parse(raw);schemaImages(o,visibleURL,row);
  const value=JSON.stringify(o).replaceAll('<','\\u003c');
  if(value!==raw)patch.push({start,end,value});
 }
 fs.writeFileSync(file,replace(before,patch));report.completed++;
}
console.log(JSON.stringify(report));
