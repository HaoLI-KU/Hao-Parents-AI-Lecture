(() => {
  const form = document.querySelector('#search-form');
  const input = document.querySelector('#course-query');
  if (!form || !input) return;

  const status = document.querySelector('#search-status');
  const results = document.querySelector('#search-results');
  const empty = document.querySelector('#search-empty');
  const filters = [...document.querySelectorAll('.search-filters [data-route]')];
  const hints = [...document.querySelectorAll('[data-query]')];
  const index = Array.isArray(window.courseSearchIndex) ? window.courseSearchIndex : [];
  let route = 'all';

  const normalise = (text) => String(text || '')
    .normalize('NFKC')
    .toLocaleLowerCase()
    .replace(/\s+/g, ' ')
    .trim();

  const escapeRegExp = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  const statusLabel = (entry) => {
    if (entry.status === 'draft') return '草稿';
    if (entry.status === 'followup') return '后续课';
    return '';
  };

  function excerpt(text, terms) {
    const haystack = normalise(text);
    const hits = terms
      .map((term) => haystack.indexOf(term))
      .filter((position) => position >= 0);
    const start = hits.length ? Math.max(0, Math.min(...hits) - 30) : 0;
    const end = start + 130;
    return (start ? '…' : '') + text.slice(start, end) + (text.length > end ? '…' : '');
  }

  function appendHighlighted(parent, text, terms) {
    if (!terms.length) {
      parent.append(document.createTextNode(text));
      return;
    }
    const pattern = new RegExp('(' + terms.map(escapeRegExp).join('|') + ')', 'gi');
    let last = 0;
    let match;
    while ((match = pattern.exec(text)) !== null) {
      if (match.index > last) {
        parent.append(document.createTextNode(text.slice(last, match.index)));
      }
      const mark = document.createElement('mark');
      mark.textContent = match[0];
      parent.append(mark);
      last = match.index + match[0].length;
      if (!match[0].length) pattern.lastIndex += 1;
    }
    if (last < text.length) {
      parent.append(document.createTextNode(text.slice(last)));
    }
  }

  function render(matches, terms) {
    results.replaceChildren();
    matches.slice(0, 80).forEach(({ entry }) => {
      const item = document.createElement('li');
      item.className = 'search-result';

      const meta = document.createElement('p');
      meta.className = 'search-result-meta';
      const routeChip = document.createElement('span');
      routeChip.className = 'chip';
      routeChip.textContent = entry.routeName;
      meta.append(routeChip);
      if (entry.lesson) {
        const detail = document.createElement('span');
        detail.textContent = `Lesson ${String(entry.lesson).padStart(2, '0')}`;
        meta.append(detail);
      }
      const state = statusLabel(entry);
      if (state) {
        const stateChip = document.createElement('span');
        stateChip.className = 'chip chip-status';
        stateChip.textContent = state;
        meta.append(stateChip);
      }

      const heading = document.createElement('h3');
      heading.className = 'search-result-title';
      const link = document.createElement('a');
      link.href = entry.url;
      appendHighlighted(
        link,
        entry.heading ? `${entry.title} · ${entry.heading}` : entry.title,
        terms,
      );
      heading.append(link);

      const text = document.createElement('p');
      text.className = 'search-result-text';
      appendHighlighted(text, excerpt(entry.text, terms), terms);

      item.append(meta, heading, text);
      results.append(item);
    });
  }

  function updateUrl() {
    const query = input.value.trim();
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (route !== 'all') params.set('route', route);
    const url = location.pathname + (params.toString() ? '?' + params.toString() : '') + location.hash;
    try {
      history.replaceState(null, '', url);
    } catch (error) {
      /* file:// previews may block history updates. */
    }
  }

  function search() {
    const terms = normalise(input.value).split(' ').filter(Boolean);
    const scoped = index.filter((entry) => route === 'all' || entry.route === route);
    results.replaceChildren();
    empty.hidden = true;

    if (!index.length) {
      status.textContent = '搜索索引没有加载，请刷新页面。';
      return;
    }
    if (!terms.length) {
      status.textContent = '输入关键词开始搜索。';
      return;
    }

    const matches = scoped.map((entry) => {
      const title = normalise(entry.title + ' ' + (entry.heading || ''));
      const full = title + ' ' + normalise(entry.text);
      if (!terms.every((term) => full.includes(term))) return null;
      const rank = terms.reduce((score, term) => {
        let value = 0;
        if (title.includes(term)) value += 3;
        if (normalise(entry.text).includes(term)) value += 1;
        return score + value;
      }, 0);
      return { entry, rank };
    }).filter(Boolean).sort((a, b) => b.rank - a.rank);

    status.textContent = matches.length
      ? `找到 ${matches.length} 个段落`
      : '没有找到相关内容。';
    empty.hidden = matches.length !== 0;
    render(matches, terms);
    updateUrl();
  }

  function setRoute(nextRoute) {
    route = nextRoute;
    filters.forEach((button) => {
      const active = button.dataset.route === route;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', String(active));
    });
  }

  const params = new URLSearchParams(location.search);
  input.value = params.get('q') || '';
  const knownRoute = new Set(filters.map((button) => button.dataset.route));
  const initialRoute = params.get('route') || 'all';
  setRoute(knownRoute.has(initialRoute) ? initialRoute : 'all');

  filters.forEach((button) => {
    button.addEventListener('click', () => {
      setRoute(button.dataset.route);
      search();
    });
  });

  hints.forEach((button) => {
    button.addEventListener('click', () => {
      input.value = button.dataset.query;
      search();
      input.focus();
    });
  });

  let timer;
  input.addEventListener('input', () => {
    clearTimeout(timer);
    timer = setTimeout(search, 120);
  });

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    search();
  });

  search();
})();
