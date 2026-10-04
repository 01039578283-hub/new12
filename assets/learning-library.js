/* Worksheet text stays in the page: no network or persistent storage APIs. */
(() => {
  'use strict';
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase('ko-KR').replace(/\s+/g, ' ').trim();
  const filters = document.querySelector('[data-guide-filters]');
  if (filters) {
    const query = filters.querySelector('#guide-query');
    const audience = filters.querySelector('#guide-audience');
    const cards = [...document.querySelectorAll('.gl-directory [data-guide]')];
    const sections = [...document.querySelectorAll('[data-category-section]')];
    const buttons = [...filters.querySelectorAll('[data-category-button]')];
    const result = document.querySelector('[data-result-count]');
    const empty = document.querySelector('[data-empty]');
    let category = '';
    const apply = () => {
      const words = normalize(query.value).split(' ').filter(Boolean);
      let count = 0;
      cards.forEach(card => {
        const search = normalize(card.dataset.search);
        const visible = (!category || card.dataset.category === category)
          && (!audience.value || card.dataset.audience.split(' ').includes(audience.value))
          && words.every(word => search.includes(word));
        card.hidden = !visible; if (visible) count += 1;
      });
      sections.forEach(section => {
        const total = [...section.querySelectorAll('[data-guide]')].filter(card => !card.hidden).length;
        section.hidden = total === 0; section.querySelector('[data-category-count]').textContent = `${total}편`;
      });
      buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.categoryButton === category)));
      result.textContent = `전체 48개 중 ${count}개 가이드를 볼 수 있습니다.`; empty.hidden = count !== 0;
    };
    const reset = () => { query.value = ''; audience.value = ''; category = ''; apply(); };
    filters.hidden = false;
    filters.addEventListener('submit', event => event.preventDefault());
    filters.addEventListener('reset', event => { event.preventDefault(); reset(); });
    query.addEventListener('input', apply); audience.addEventListener('change', apply);
    buttons.forEach(button => button.addEventListener('click', () => { category = button.dataset.categoryButton; apply(); }));
    document.querySelector('[data-reset]').addEventListener('click', () => { reset(); query.focus(); });
  }
  document.querySelectorAll('[data-worksheet]').forEach(form => {
    const fields = [...form.querySelectorAll('textarea')];
    const status = form.querySelector('[data-record-status]'); let downloadUrl;
    const removePrintEntries = () => {
      form.querySelectorAll('.gl-print-entry').forEach(entry => entry.remove());
      fields.forEach(field => field.classList.remove('gl-has-print-entry'));
    };
    const preparePrintEntries = () => {
      removePrintEntries();
      fields.forEach(field => {
        const entry = document.createElement('div'); entry.className = 'gl-print-entry';
        entry.textContent = field.value || ' '; field.insertAdjacentElement('afterend', entry);
        field.classList.add('gl-has-print-entry');
      });
    };
    form.querySelectorAll('.gl-enhance').forEach(control => { control.hidden = false; });
    form.addEventListener('submit', event => event.preventDefault());
    form.querySelector('[data-save]').addEventListener('click', () => {
      try {
        const text = [form.dataset.title, '채움학습 · 작성한 활동지', form.dataset.url,
          '작성 내용은 이 페이지에서 파일로 저장한 기록입니다.', '',
          ...fields.flatMap((field, index) => [
            `${index + 1}. ${form.querySelector(`label[for="${field.id}"]`).textContent}`,
            field.value || '(작성하지 않음)', ''
          ])].join('\r\n');
        if (downloadUrl) URL.revokeObjectURL(downloadUrl);
        downloadUrl = URL.createObjectURL(new Blob(['\ufeff', text], {type: 'text/plain;charset=utf-8'}));
        const anchor = document.createElement('a'); anchor.href = downloadUrl; anchor.download = `${form.dataset.slug}-my-record.txt`;
        document.body.append(anchor); anchor.click(); anchor.remove();
        status.textContent = 'TXT 저장을 요청했습니다. 브라우저의 다운로드 목록에서 파일을 확인하세요.';
      } catch { status.textContent = '파일 저장을 시작하지 못했습니다. 내용을 복사하거나 인쇄해 보세요.'; }
    });
    form.querySelector('[data-print]').addEventListener('click', () => {
      preparePrintEntries(); document.body.classList.add('gl-print-worksheet');
      status.textContent = '인쇄 창에서 저장하거나 인쇄하세요.'; window.print();
    });
    form.querySelector('[data-clear]').addEventListener('click', () => {
      fields.forEach(field => { field.value = ''; }); removePrintEntries();
      status.textContent = '활동지 입력을 지웠습니다.'; fields[0].focus();
    });
    window.addEventListener('beforeprint', preparePrintEntries);
    window.addEventListener('afterprint', () => { document.body.classList.remove('gl-print-worksheet'); removePrintEntries(); });
    window.addEventListener('pagehide', () => { if (downloadUrl) URL.revokeObjectURL(downloadUrl); });
  });
})();
