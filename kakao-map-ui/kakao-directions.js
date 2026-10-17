/* Automatically load just the selected map when it approaches the viewport. */
(()=>{'use strict';
 const sections=[...document.querySelectorAll('.kakao-directions')];
 const safe=(value,pattern)=>{const u=new URL(value,location.href);if(u.origin!==location.origin||!pattern.test(u.pathname))throw Error('Unreviewed map resource');return u.pathname+u.search;};
 const draw=(holder,groups)=>{const list=document.createElement('ul');list.className='kd-traffic';
  for(const group of groups){const row=document.createElement('li'),heading=document.createElement('h3');heading.textContent=group.title;row.append(heading);const items=document.createElement(group.className==='kd-stops'?'ol':'ul');items.className=group.className;
   group.items.forEach((value,index)=>{const li=document.createElement('li');if(group.className==='kd-stops'){const no=document.createElement('span');no.className='kd-stop-number';no.setAttribute('aria-hidden','true');no.textContent=String(index+1);li.append(no);}
    if(typeof value==='string'){const span=document.createElement('span');span.textContent=value;li.append(span);}else{const type=document.createElement('span');type.className='kd-bus-type kd-bus-'+value.type;type.textContent=value.label;const names=document.createElement('span');names.className='kd-bus-numbers';for(const name of value.names){const span=document.createElement('span');span.textContent=name;names.append(span);}li.append(type,names);}items.append(li);});row.append(items);list.append(row);}
  holder.replaceChildren(list);
  if(!groups.length){const note=document.createElement('p');note.textContent='이 약도에는 주변 교통 정보가 등록되어 있지 않습니다.';holder.replaceChildren(note);}
 };
 function load(section){const frame=section.querySelector('iframe'),src=safe(frame.dataset.kakaoSrc,/^\/assets\/kakao-maps\/\d+\/$/);if(frame.dataset.kakaoLoaded===src)return;frame.dataset.kakaoLoaded=src;
  const shell=frame.closest('.kd-map-shell');delete shell.dataset.mapReady;frame.src=src;shell.querySelector('.kd-map-status').textContent='지도 위치를 자동으로 불러옵니다.';
  setTimeout(()=>{if(frame.dataset.kakaoLoaded===src&&!shell.hasAttribute('data-map-ready'))shell.querySelector('.kd-map-status').textContent='카카오맵 연결이 지연되고 있습니다. 아래 주소와 교통 안내를 확인해 주세요.';},12000);
 }
 async function options(section){if(!section.dataset.kakaoOptions||section.dataset.optionsStarted)return;section.dataset.optionsStarted='true';
  try{const response=await fetch(safe(section.dataset.kakaoOptions,/^\/assets\/kakao-options\/[a-f0-9]+\.json$/));if(!response.ok)throw Error('options');const rows=await response.json();const select=section.querySelector('select');
   select.replaceChildren(...rows.map(row=>{const option=document.createElement('option');option.value=row.frame;option.textContent=row.branch;option.dataset.address=row.address;option.dataset.traffic=row.traffic;return option;}));section.dataset.optionsReady='true';
  }catch{delete section.dataset.optionsStarted;section.querySelector('.kd-hub-status').textContent='지점 목록을 불러오지 못했습니다. 기존 지점 목록에서 방문할 지점을 확인해 주세요.';}
 }
 window.addEventListener('message',event=>{if(event.origin!==location.origin||event.data?.type!=='chaeum-kakao-ready')return;
  for(const section of sections){const f=section.querySelector('iframe');if(f.contentWindow===event.source&&new URL(f.dataset.kakaoSrc,location.href).pathname==='/assets/kakao-maps/'+event.data.id+'/')f.closest('.kd-map-shell').dataset.mapReady='true';}
 });
 for(const section of sections){const select=section.querySelector('select');if(!select)continue;
  select.addEventListener('focus',()=>options(section));select.addEventListener('change',async()=>{const item=select.selectedOptions[0];if(!item.dataset.address)return;
   const frame=section.querySelector('iframe');frame.title=item.textContent+' 위치 지도';frame.dataset.kakaoSrc=item.value;load(section);section.querySelector('.kd-address dd').textContent=item.dataset.address;section.querySelector('.kd-hub-status').textContent=item.textContent+'의 위치를 표시합니다.';
   section.dataset.selection=item.value;section.querySelector('.kd-traffic-holder').replaceChildren();
   try{const response=await fetch(safe(item.dataset.traffic,/^\/assets\/kakao-traffic\/\d+\.json$/));if(!response.ok)throw Error('traffic');const data=await response.json();if(section.dataset.selection===item.value)draw(section.querySelector('.kd-traffic-holder'),data);}catch{section.querySelector('.kd-hub-status').textContent+=' 주변 교통 정보를 불러오지 못했습니다.';}
  });
 }
 if('IntersectionObserver'in window){const maps=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){load(e.target);maps.unobserve(e.target);}},{rootMargin:'350px 0px'});const lists=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){options(e.target);lists.unobserve(e.target);}},{rootMargin:'1000px 0px'});sections.forEach(s=>{maps.observe(s);lists.observe(s);});}
 else sections.forEach(s=>{load(s);options(s);});
})();
