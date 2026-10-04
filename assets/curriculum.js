/* Progressive filters. Every curriculum link remains available without JavaScript. */
(() => {
  function connect(formSelector, cardSelector, attributes, noun) {
    const form = document.querySelector(formSelector);
    if (!form) return;
    const section = form.closest('section');
    const cards = [...section.querySelectorAll(cardSelector)];
    const count = section.querySelector('.cu-results');
    const empty = section.querySelector('.cu-empty');
    const normalize = value => value.toLocaleLowerCase('ko').replace(/\s+/g, '');
    const render = () => {
      if (form.elements.school) {
        const prefix = {초등:'초', 중등:'중', 고등:'고'}[form.elements.school.value];
        for (const option of form.elements.grade.options) {
          option.disabled = !!(prefix && option.value && !option.value.startsWith(prefix));
          option.hidden = option.disabled;
        }
        if (form.elements.grade.selectedOptions[0]?.disabled) form.elements.grade.value = '';
      }
      const terms = form.elements.query.value.trim().split(/\s+/).filter(Boolean).map(normalize);
      let visible = 0;
      for (const card of cards) {
        const matches = attributes.every(name => !form.elements[name].value || card.dataset[name] === form.elements[name].value);
        card.hidden = !matches || !terms.every(term => normalize(card.dataset.search).includes(term));
        if (!card.hidden) visible++;
      }
      count.textContent = `${visible}개 ${noun} · 전체 ${cards.length}개`;
      empty.hidden = visible > 0;
    };
    const params = new URLSearchParams(location.search);
    for (const name of ['query', ...attributes]) {
      const field = form.elements[name], value = params.get(name);
      if (value && (field.tagName !== 'SELECT' || [...field.options].some(option => option.value === value))) field.value = value;
    }
    form.hidden = false;
    form.addEventListener('submit', event => event.preventDefault());
    form.addEventListener('input', render);
    form.addEventListener('change', render);
    form.addEventListener('reset', () => queueMicrotask(render));
    render();
  }
  connect('.cu-filters', '.cu-card', ['school', 'grade', 'subject'], '학년·과목 안내');
  connect('.cu-choice-filters', '.cu-choice', ['subject', 'kind'], '공통·선택과목 항목');
})();
