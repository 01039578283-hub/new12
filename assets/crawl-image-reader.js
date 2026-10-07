/* Progressive enhancement: visible images and their original URLs work without JavaScript. */
(() => {
 'use strict';
 const dialog=document.querySelector('[data-crawl-reader]');
 if(!dialog||typeof dialog.showModal!=='function')return;
 const image=dialog.querySelector('img'),title=dialog.querySelector('[data-reader-title]'),zoom=dialog.querySelector('input'),close=dialog.querySelector('button');
 let opener=null,base=0;
 const resize=()=>{if(base)image.style.width=Math.round(base*Number(zoom.value)/100)+'px';};
 document.addEventListener('click',e=>{
  const link=e.target.closest('a[data-readable-image]');
  if(!link||e.button!==0||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;
  e.preventDefault();opener=link;title.textContent=link.dataset.readerTitle||'이미지 원본';image.alt=link.querySelector('img')?.alt||title.textContent;
  zoom.value='100';base=0;image.removeAttribute('style');image.src=link.href;
  dialog.showModal();close.focus();
 });
 image.addEventListener('load',()=>{base=Math.min(image.naturalWidth,dialog.querySelector('[data-reader-body]').clientWidth-24);resize();});
 zoom.addEventListener('input',resize);
 close.addEventListener('click',()=>dialog.close());
 dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
 dialog.addEventListener('close',()=>{image.removeAttribute('src');image.removeAttribute('style');opener?.focus();opener=null;base=0;});
})();
