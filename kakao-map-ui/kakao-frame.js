/* Keep Kakao imagery, attribution and zoom controls; disable outbound navigation. */
(()=>{'use strict';
 const root=document.querySelector('.root_daum_roughmap');if(!root)return;
 function clean(){
  root.querySelectorAll('.wrap_btn_roadview,.cont,.phone').forEach(n=>n.remove());
  root.querySelectorAll('a').forEach(a=>{for(const name of ['href','target','onclick','title'])a.removeAttribute(name);a.tabIndex=-1;a.querySelectorAll('img[alt]').forEach(i=>{if(/이동|새창/.test(i.alt))i.alt='Kakao 지도';});});
  if(!document.documentElement.dataset.mapReady&&[...root.querySelectorAll('.map img')].some(i=>i.complete&&i.naturalWidth)){
   document.documentElement.dataset.mapReady='true';parent.postMessage({type:'chaeum-kakao-ready',id:root.id.replace('daumRoughmapContainer','')},location.origin);
  }
 }
 let pending=false;const schedule=()=>{if(pending)return;pending=true;requestAnimationFrame(()=>{pending=false;clean();});};
 new MutationObserver(records=>{if(records.some(r=>r.addedNodes.length))schedule();}).observe(root,{subtree:true,childList:true});
 root.addEventListener('load',schedule,true);clean();
 for(const type of ['click','auxclick'])document.addEventListener(type,e=>{if(e.target.closest('a')){e.preventDefault();e.stopImmediatePropagation();}},true);
 document.addEventListener('keydown',e=>{if(['Enter',' '].includes(e.key)&&e.target.closest('a')){e.preventDefault();e.stopImmediatePropagation();}},true);
 let width=document.documentElement.clientWidth;
 window.addEventListener('resize',()=>{const next=document.documentElement.clientWidth;if(next===width)return;width=next;if(window.chaeumMap?.jsMap){const center=window.chaeumMap.jsMap.getCenter();window.chaeumMap.jsMap.relayout();window.chaeumMap.jsMap.setCenter(center);}},{passive:true});
})();
