/* Progressive enhancement: episodes and audio remain usable without JavaScript. */
const form = document.querySelector('.archive-filters');
if (form) {
  const search = document.querySelector('#episode-search');
  const topic = document.querySelector('#episode-topic');
  const cards = [...document.querySelectorAll('[data-episode]')];
  const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const filter = () => {
    const terms = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    let count = 0;
    for (const card of cards) {
      const matches = terms.every(term => normalize(card.textContent).includes(term)) && (!topic.value || card.dataset.category === topic.value);
      card.hidden = !matches;
      if (matches) count++;
    }
    document.querySelector('#result-count').textContent = `${count} of ${cards.length} episodes and trailers`;
    document.querySelector('#no-results').hidden = count !== 0;
  };
  form.hidden = false;
  form.addEventListener('submit', event => event.preventDefault());
  search.addEventListener('input', filter);
  topic.addEventListener('change', filter);
  form.addEventListener('reset', () => setTimeout(filter, 0));
}
for (const button of document.querySelectorAll('[data-embed]')) {
  button.hidden = false;
  button.addEventListener('click', () => {
    const frame = document.createElement('iframe');
    frame.src = button.dataset.embed;
    siteEvent('load_player', frame.src.includes('spotify.com') ? 'spotify' : 'youtube');
    frame.title = button.dataset.title;
    frame.height = button.dataset.height;
    frame.allow = 'encrypted-media; fullscreen; picture-in-picture';
    frame.allowFullscreen = true;
    frame.tabIndex = 0;
    button.replaceWith(frame);
    frame.focus();
  });
}

/* Local semantic events: no storage, network transport, email addresses or search terms.
   Cloudflare Web Analytics measures visits/performance separately. */
function siteEvent(action, destination) {
  document.dispatchEvent(new CustomEvent('viking:interaction', {
    detail: { action, destination }
  }));
}
document.addEventListener('click', event => {
  const link = event.target.closest('a');
  if (!link) return;
  const url = new URL(link.href, location.href);
  if (url.protocol === 'mailto:') siteEvent('contact', 'email');
  else if (url.hostname === 'open.spotify.com') siteEvent('outbound', 'spotify');
  else if (url.hostname === 'www.youtube.com') siteEvent('outbound', 'youtube');
  else if (url.hostname === 'www.instagram.com') siteEvent('outbound', 'instagram');
});
for (const audio of document.querySelectorAll('audio')) {
  audio.addEventListener('playing', () => siteEvent('audio_play', 'podcast'), { once: true });
  const showError = () => {
    if (audio.parentElement.querySelector('.media-error')) return;
    const message = document.createElement('p');
    message.className = 'media-error';
    message.setAttribute('role', 'status');
    message.textContent = 'The audio could not be loaded here. Try the audio-file or podcast-host link below.';
    audio.after(message);
  };
  audio.addEventListener('error', showError);
  audio.querySelector('source')?.addEventListener('error', showError);
}
