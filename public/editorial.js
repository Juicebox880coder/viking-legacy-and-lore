/* All posts and links remain readable without JavaScript. Search stays on-device. */
(() => {
  const form = document.querySelector('.editorial-filters');
  if (!form) return;
  const search = document.querySelector('#post-search');
  const category = document.querySelector('#post-category');
  const cards = [...document.querySelectorAll('[data-post]')];
  const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const filter = () => {
    const terms = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    let count = 0;
    for (const card of cards) {
      const match = terms.every(term => normalize(card.textContent).includes(term)) && (!category.value || category.value === card.dataset.category);
      card.hidden = !match;
      if (match) count++;
    }
    document.querySelector('#post-count').textContent = `${count} of ${cards.length} reads`;
    document.querySelector('#post-empty').hidden = count !== 0;
  };
  form.hidden = false;
  form.addEventListener('submit', event => event.preventDefault());
  search.addEventListener('input', filter);
  category.addEventListener('change', filter);
  form.addEventListener('reset', () => setTimeout(filter, 0));
})();
