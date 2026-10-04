(() => {
  'use strict';
  const form = document.querySelector('.ei-filter');
  if (form) {
    const cards = [...document.querySelectorAll('.ei-card')];
    const normalize = value => value.normalize('NFKC').toLocaleLowerCase('ko-KR').trim();
    const filter = () => {
      const words = normalize(form.elements.query.value).split(/\s+/).filter(Boolean);
      const category = form.elements.category.value;
      const audience = form.elements.audience.value;
      const kind = form.elements.kind.value;
      let visible = 0;
      cards.forEach(card => {
        const targets = card.dataset.audience;
        const audienceMatch = !audience || targets.includes(audience) ||
          (audience.endsWith('학생') && audience !== '학생' && targets.split(' ').includes('학생')) ||
          (audience === '학생' && /학생/.test(targets));
        card.hidden = !((!category || card.dataset.category === category) &&
          (!kind || card.dataset.kind === kind) && audienceMatch &&
          words.every(word => normalize(card.dataset.search).includes(word)));
        if (!card.hidden) visible++;
      });
      document.querySelector('.ei-results').textContent = visible + '편을 찾았습니다 · 전체 ' + cards.length + '편';
      document.querySelector('.ei-empty').hidden = visible !== 0;
    };
    form.addEventListener('submit', event => event.preventDefault());
    form.addEventListener('input', filter);
    form.addEventListener('change', filter);
    form.addEventListener('reset', () => setTimeout(filter, 0));
  }
  const locations = window.CHaeumEducationLocations;
  document.querySelectorAll('.ei-location-form').forEach(locationForm => {
    if (!Array.isArray(locations) || !locations.length) return;
    const section = locationForm.closest('.ei-local');
    const region = locationForm.elements.region, center = locationForm.elements.center, town = locationForm.elements.town;
    const centerLink = section.querySelector('[data-center-link]');
    const townLink = section.querySelector('[data-town-link]');
    const status = section.querySelector('.ei-location-status');
    const option = (value, text) => { const item = document.createElement('option'); item.value = value; item.textContent = text; return item; };
    [...new Set(locations.map(item => item.region))].sort((a,b) => a.localeCompare(b,'ko')).forEach(value => region.append(option(value,value)));
    const townReset = () => {
      town.replaceChildren(option('', '지점을 먼저 선택하세요')); town.disabled = true;
      townLink.href = '/전국학원/'; townLink.textContent = '지역별 학원 안내 보기';
    };
    const centerUpdate = () => {
      townReset();
      const selected = locations.find(item => item.path === center.value && item.region === region.value);
      if (!selected) {
        centerLink.href = '/지점안내/'; centerLink.textContent = '전체 지점 안내 보기';
        status.textContent = '지점을 선택하면 해당 지점과 동네 안내로 연결됩니다.';
        return;
      }
      centerLink.href = selected.path; centerLink.textContent = selected.name + ' 지점 안내 보기';
      town.replaceChildren(option('', '동네를 선택하세요'));
      selected.towns.forEach(item => town.append(option(item.path,item.name)));
      town.disabled = selected.towns.length === 0;
      status.textContent = selected.name + '을 선택했습니다. 동네를 선택하면 해당 안내도 열 수 있습니다.';
    };
    region.addEventListener('change', () => {
      center.replaceChildren(option('', '지점을 선택하세요'));
      locations.filter(item => item.region === region.value).forEach(item => center.append(option(item.path,item.name)));
      center.disabled = !region.value;
      centerUpdate();
    });
    center.addEventListener('change', centerUpdate);
    town.addEventListener('change', () => {
      const selected = locations.find(item => item.path === center.value && item.region === region.value);
      const neighborhood = selected?.towns.find(item => item.path === town.value);
      townLink.href = neighborhood ? neighborhood.path : '/전국학원/';
      townLink.textContent = neighborhood ? neighborhood.name + ' 학원 안내 보기' : '지역별 학원 안내 보기';
      status.textContent = neighborhood ? selected.name + '과 ' + neighborhood.name + ' 안내를 열 수 있습니다.' : '동네를 선택하면 해당 안내로 연결됩니다.';
    });
    locationForm.addEventListener('submit', event => event.preventDefault());
    locationForm.hidden = false;
  });
})();
