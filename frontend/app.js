const form = document.querySelector('#ask-form');
const question = document.querySelector('#question');
const submit = document.querySelector('#submit');
const feedback = document.querySelector('#feedback');
const result = document.querySelector('#result');

question.addEventListener('input', () => {
  document.querySelector('#count').textContent = `${question.value.length} / 1 000`;
});
document.querySelectorAll('[data-question]').forEach(button => {
  button.addEventListener('click', () => {
    question.value = button.dataset.question;
    question.dispatchEvent(new Event('input'));
    question.focus();
  });
});

function renderSources(sources) {
  const list = document.querySelector('#sources');
  list.replaceChildren();
  document.querySelector('#sources-block').hidden = !sources.length;
  sources.forEach(source => {
    const item = document.createElement('li');
    const title = document.createElement('span');
    title.textContent = `${source.title} · ${source.section}${source.page ? ` · page ${source.page}` : ''}`;
    if (source.url && /^https?:\/\//i.test(source.url)) {
      const link = document.createElement('a');
      link.href = source.url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.append(title);
      item.append(link);
    } else item.append(title);
    const details = document.createElement('details');
    const summary = document.createElement('summary');
    summary.textContent = `Voir le passage · ${source.document}`;
    const quote = document.createElement('blockquote');
    quote.textContent = source.text;
    details.append(summary, quote);
    item.append(details);
    list.append(item);
  });
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  if (submit.disabled) return;
  if (!question.value.trim()) {
    feedback.hidden = false;
    feedback.textContent = 'Saisissez une question avant de continuer.';
    question.focus();
    return;
  }
  result.hidden = true;
  feedback.hidden = false;
  feedback.className = 'loading';
  feedback.textContent = 'Recherche des informations pertinentes…';
  submit.disabled = true;
  form.setAttribute('aria-busy', 'true');
  const timer = setTimeout(() => { feedback.textContent = 'Préparation de la réponse…'; }, 1800);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 110000);
  try {
    const response = await fetch('/ask', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: question.value.trim() }), signal: controller.signal,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Le service est indisponible. Veuillez réessayer.');
    document.querySelector('#answer').textContent = data.answer;
    document.querySelector('#disclaimer').textContent = data.disclaimer;
    document.querySelector('#duration').textContent = `${(data.metrics.elapsed_ms / 1000).toFixed(1)} s`;
    renderSources(data.sources);
    feedback.hidden = true;
    result.hidden = false;
    result.focus();
  } catch (error) {
    feedback.textContent = error.name === 'AbortError' ? 'La réponse prend trop de temps. Veuillez réessayer.' : error instanceof TypeError ? 'Connexion au serveur impossible. Vérifiez votre connexion puis réessayez.' : error.message;
  } finally {
    clearTimeout(timer);
    clearTimeout(timeout);
    feedback.className = '';
    submit.disabled = false;
    form.removeAttribute('aria-busy');
  }
});
