/* Progressive enhancement: every original directory link remains in the HTML. */
(() => {
  const directory = document.getElementById('hub-directory');
  const input = document.getElementById('hub-search');
  if (!directory || !input) return;
  const reset = document.getElementById('hub-search-reset');
  const status = document.getElementById('hub-search-result');
  const regions = Array.from(directory.querySelectorAll('.region-block'));
  const districts = Array.from(directory.querySelectorAll('.district-block, .subject-district'));
  const links = Array.from(directory.querySelectorAll('.local-button-grid a, .subject-local-grid a'));
  const normalize = text => text.normalize('NFKC').toLocaleLowerCase('ko-KR').replace(/\s+/g, '');
  const records = links.map(link => {
    const region = link.closest('.region-block');
    const district = link.closest('.district-block, .subject-district');
    const label = link.querySelector('strong')?.textContent || link.textContent;
    return { link, region, district, search: normalize([label, district?.querySelector('.district-title, h3')?.textContent || '', region?.querySelector('.region-title h2, .region-title h3')?.textContent || ''].join(' ')) };
  });
  function apply() {
    const query = normalize(input.value.trim());
    let matched = 0;
    records.forEach(record => {
      const show = !query || record.search.includes(query);
      record.link.hidden = !show;
      if (show) matched += 1;
    });
    districts.forEach(district => { district.hidden = !records.some(record => record.district === district && !record.link.hidden); });
    regions.forEach(region => { region.hidden = !records.some(record => record.region === region && !record.link.hidden); });
    directory.querySelectorAll('.region-jump a').forEach(anchor => {
      const target = document.getElementById(decodeURIComponent(anchor.hash.slice(1)));
      anchor.hidden = !!target?.hidden;
    });
    status.textContent = query ? (matched ? `${matched}개 동네를 찾았습니다.` : '검색 결과가 없습니다. 동네 이름을 짧게 입력하거나 검색을 초기화해 보세요.') : `전체 ${records.length}개 동네`;
  }
  input.addEventListener('input', apply);
  reset.addEventListener('click', () => { input.value = ''; apply(); input.focus(); });
  apply();
})();
