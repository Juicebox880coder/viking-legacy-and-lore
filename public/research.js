/* Search stays local. Query parameters make a selection bookmarkable. */
for (const index of document.querySelectorAll('[data-research-index]')) {
  const form = index.querySelector('.research-filters');
  const fields = [...form.querySelectorAll('input, select')];
  const cards = [...index.querySelectorAll('[data-research-item]')];
  const count = index.querySelector('.research-count');
  const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const searchable = new Map(cards.map(card => [card, normalize(card.textContent)]));
  function readURL() {
    const params = new URLSearchParams(location.search);
    for (const field of fields) {
      const value = params.get(field.name) || '';
      field.value = field.tagName === 'SELECT' && ![...field.options].some(o => o.value === value) ? '' : value;
    }
  }
  function filter(updateURL = true) {
    const terms = normalize(form.elements.q.value).trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      const matches = terms.every(term => searchable.get(card).includes(term)) && fields.every(field => field.name === 'q' || !field.value || card.dataset[field.name] === field.value);
      card.hidden = !matches;
      if (matches) visible++;
    }
    count.textContent = `${visible} of ${cards.length} entries`;
    index.querySelector('.research-empty').hidden = visible !== 0;
    if (updateURL) {
      const url = new URL(location.href);
      for (const field of fields) {
        if (field.value) url.searchParams.set(field.name, field.value);
        else url.searchParams.delete(field.name);
      }
      history.replaceState(null, '', url.pathname + url.search + url.hash);
    }
  }
  function revealAnchor() {
    const target = cards.find(card => '#' + card.id === location.hash);
    if (target?.hidden) {
      form.reset(); filter(); target.scrollIntoView();
    }
  }
  form.hidden = false;
  readURL(); filter(false); revealAnchor();
  form.addEventListener('submit', event => { event.preventDefault(); filter(); });
  form.addEventListener('input', () => filter());
  form.addEventListener('change', () => filter());
  form.addEventListener('reset', () => setTimeout(filter, 0));
  window.addEventListener('popstate', () => { readURL(); filter(false); revealAnchor(); });
  window.addEventListener('hashchange', revealAnchor);
}
