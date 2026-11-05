const searchForm = document.querySelector('.course-search form');
const queryInput = document.querySelector('#course-query');
const statusText = document.querySelector('#search-status');
const results = document.querySelector('#search-results');

function normalise(text) {
    return text.normalize('NFKC').toLocaleLowerCase().replace(/\s+/g, ' ').trim();
}

function excerpt(text, terms) {
    const start = terms.map(term => normalise(text).indexOf(term)).filter(i => i >= 0);
    const offset = start.length ? Math.max(0, Math.min(...start) - 24) : 0;
    return (offset ? '…' : '') + text.slice(offset, offset + 110) +
        (text.length > offset + 110 ? '…' : '');
}

function search() {
    results.replaceChildren();
    const query = normalise(queryInput.value);
    if (!query) {
        statusText.textContent = '';
        return;
    }
    const terms = query.split(' ');
    const matches = window.courseSearchIndex.map(entry => {
        const heading = normalise(entry.title + ' ' + entry.heading);
        const full = heading + ' ' + normalise(entry.text);
        return { entry, full, rank: terms.filter(term => heading.includes(term)).length };
    }).filter(match => terms.every(term => match.full.includes(term)))
        .sort((a, b) => b.rank - a.rank);
    statusText.textContent = matches.length ? `找到 ${matches.length} 个段落` :
        '没有找到相关内容。试试更短的关键词。';
    for (const { entry } of matches) {
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.href = entry.url;
        link.textContent = entry.heading ? entry.title + ' · ' + entry.heading : entry.title;
        const description = document.createElement('p');
        description.textContent = excerpt(entry.text, terms);
        item.append(link, description);
        results.append(item);
    }
}

queryInput.addEventListener('input', search);
searchForm.addEventListener('submit', event => {
    event.preventDefault();
    search();
});
