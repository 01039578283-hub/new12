/* All center names, facts and links are already in the server-delivered HTML. */
(() => {
  'use strict';
  document.querySelectorAll('[data-directory]').forEach(root => {
    const query=root.querySelector('[data-query]'), subject=root.querySelector('[data-subject]'), grade=root.querySelector('[data-grade]');
    const cards=[...root.querySelectorAll('[data-center]')].map(node=>({node,courses:JSON.parse(node.dataset.courses)}));
    const normalize=s=>s.normalize('NFKC').toLocaleLowerCase('ko').replace(/\s+/g,'');
    const update=()=>{
      const terms=query.value.trim().split(/\s+/).filter(Boolean).map(normalize); let n=0;
      for(const {node,courses} of cards){
        const matchingCourse=subject.value ? (courses[subject.value]||[]) : Object.values(courses).flat();
        const match=terms.every(t=>normalize(node.dataset.center).includes(t))&&(!subject.value||matchingCourse.length>0)&&(!grade.value||matchingCourse.includes(grade.value));
        node.hidden=!match;if(match)n++;
      }
      root.querySelector('[data-count]').textContent=`${n}개 지점 · 전체 ${cards.length}개`;
      root.querySelector('[data-empty]').hidden=n!==0;
    };
    query.addEventListener('input',update);subject.addEventListener('change',update);grade.addEventListener('change',update);
    root.querySelector('[data-reset]').addEventListener('click',()=>{query.value='';subject.value='';grade.value='';update();query.focus();});
    update();
  });
  const allowed=new Set(['avpJfW7eIV0','f_skFu40U04','UIXUaBZdNXU']);
  document.querySelectorAll('[data-video]').forEach(card=>{
    const id=card.dataset.video;if(!allowed.has(id))return;
    const stage=card.querySelector('.cd-video-stage'),play=card.querySelector('.cd-play'),stop=card.querySelector('.cd-stop');
    play.addEventListener('click',()=>{
      if(stage.querySelector('iframe'))return;
      const frame=document.createElement('iframe');frame.src=`https://www.youtube-nocookie.com/embed/${id}?rel=0&autoplay=1`;
      frame.title=play.dataset.title;frame.allow='accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; web-share';frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';
      stage.append(frame);play.hidden=true;stop.hidden=false;stop.focus();
    });
    stop.addEventListener('click',()=>{stage.querySelector('iframe')?.remove();play.hidden=false;stop.hidden=true;play.focus();});
  });
  document.addEventListener('keydown',event=>{if(event.key==='Escape'){const menu=document.querySelector('.cd-menu[open]');if(menu){menu.open=false;menu.querySelector('summary').focus();}}});
  document.addEventListener('click',event=>{const menu=document.querySelector('.cd-menu[open]');if(menu&&!menu.contains(event.target))menu.open=false;});
})();
