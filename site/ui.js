(() => {

const SITE_URL = 'https://haoli-ku.github.io/Hao-Parents-AI-Lecture/';


function absolutiseSiteLinks() {
  try {
    const site = new URL(SITE_URL);
    if (location.origin !== site.origin) return;
    const base = new URL(document.documentElement.dataset.pageDir || '', site);
    const page = new URL(document.documentElement.dataset.pagePath || '', site);
    const absolute = (value) => {
      if (!value) return value;
      if (value.charAt(0) === '#') return page.href + value;
      if (/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(value)) return value;
      return new URL(value, base).href;
    };
    document.querySelectorAll('a[href]').forEach((link) => {
      const raw = link.getAttribute('href');
      const next = absolute(raw);
      if (next !== raw) link.setAttribute('href', next);
    });
    document.querySelectorAll('form[action]').forEach((form) => {
      const raw = form.getAttribute('action');
      const next = absolute(raw);
      if (next !== raw) form.setAttribute('action', next);
    });
  } catch (error) {
    /* Keep the authored relative links when the page is not on the production origin. */
  }
}

absolutiseSiteLinks();
  document.documentElement.classList.add('js');

  const header = document.querySelector('[data-site-header]');
  if (header) {
    const updateHeader = () => header.classList.toggle('is-stuck', window.scrollY > 8);
    updateHeader();
    window.addEventListener('scroll', updateHeader, { passive: true });
  }

  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#siteNav');
  if (toggle && nav) {
    const closeMenu = () => {
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', '打开导航菜单');
    };
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? '关闭导航菜单' : '打开导航菜单');
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeMenu();
    });
    document.addEventListener('click', (event) => {
      if (!nav.classList.contains('is-open')) return;
      if (!nav.contains(event.target) && !toggle.contains(event.target)) closeMenu();
    });
  }

  const tocLinks = [...document.querySelectorAll('.toc-nav a[href^="#step-"]')];
  if (tocLinks.length && 'IntersectionObserver' in window) {
    const targets = new Map();
    tocLinks.forEach((link) => {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) targets.set(target, link);
    });
    const setCurrent = (link) => {
      tocLinks.forEach((item) => {
        const active = item === link;
        item.classList.toggle('is-active', active);
        if (active) item.setAttribute('aria-current', 'true');
        else item.removeAttribute('aria-current');
      });
    };
    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
      if (visible.length) setCurrent(targets.get(visible[0].target));
    }, { rootMargin: '-12% 0px -72% 0px', threshold: 0 });
    targets.forEach((_, target) => observer.observe(target));
  }

  document.querySelectorAll('.prompt').forEach((prompt) => {
    const button = prompt.querySelector('.prompt-copy');
    const code = prompt.querySelector('pre');
    if (!button || !code) return;
    button.addEventListener('click', async () => {
      const text = code.innerText;
      let copied = false;
      try {
        await navigator.clipboard.writeText(text);
        copied = true;
      } catch (error) {
        const area = document.createElement('textarea');
        area.value = text;
        area.setAttribute('readonly', '');
        area.style.position = 'fixed';
        area.style.opacity = '0';
        document.body.append(area);
        area.select();
        try {
          copied = document.execCommand('copy');
        } catch (fallbackError) {
          copied = false;
        }
        area.remove();
      }
      button.textContent = copied ? '已复制' : '请手动选择';
      setTimeout(() => { button.textContent = '复制'; }, 2200);
    });
  });

  document.querySelectorAll('[data-gallery-switch]').forEach((button) => {
    const caption = button.querySelector('[data-gallery-caption]');
    button.addEventListener('click', () => {
      const original = button.classList.toggle('is-original');
      const art = button.closest('.gallery-art');
      button.setAttribute('aria-pressed', String(original));
      if (art) art.classList.toggle('is-original', original);
      if (caption) {
        caption.textContent = button.getAttribute(
          original ? 'data-original-caption' : 'data-vector-caption',
        ) || '';
      }
    });
  });
})();
