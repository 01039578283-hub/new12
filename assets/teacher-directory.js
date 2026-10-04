(() => {
  'use strict';
  const form = document.querySelector('[data-teacher-search]');
  if (!form) return;
  const query = form.querySelector('#teacher-query');
  const region = form.querySelector('#teacher-region');
  const focus = form.querySelector('#teacher-focus');
  const cards = [...document.querySelectorAll('[data-teacher-branch]')];
  const count = document.querySelector('[data-teacher-count]');
  const empty = document.querySelector('[data-teacher-empty]');
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase('ko-KR').replace(/\s+/g, ' ').trim();
  const apply = () => {
    const words = normalize(query.value).split(' ').filter(Boolean);
    let shown = 0;
    cards.forEach(card => {
      const visible = (!region.value || card.dataset.region === region.value)
        && (!focus.value || card.dataset.focus.split('|').includes(focus.value))
        && words.every(word => normalize(card.dataset.search).includes(word));
      card.hidden = !visible;
      if (visible) shown += 1;
    });
    count.textContent = `전체 ${cards.length}개 지점 중 ${shown}개 지점의 소개를 볼 수 있습니다.`;
    empty.hidden = shown !== 0;
  };
  form.hidden = false;
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('reset', event => {
    event.preventDefault(); query.value = ''; region.value = ''; focus.value = ''; apply(); query.focus();
  });
  query.addEventListener('input', apply);
  region.addEventListener('change', apply);
  focus.addEventListener('change', apply);
  apply();
})();
