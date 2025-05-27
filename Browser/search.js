const axios = require('axios');
const cheerio = require('cheerio');
const Store = require('electron-store');
const { URL } = require('url');

const store = new Store();
const indexedPages = store.get('indexedPages', []);

const MAX_DEPTH = 3;
const MAX_PAGES = 200;
const REQUEST_TIMEOUT = 5000;
const CONCURRENT_REQUESTS = 5;

function cleanText(text) {
  return text
    .replace(/\s+/g, ' ')
    .replace(/[^\w\s]/g, '')
    .trim()
    .toLowerCase();
}

function getWordFrequency(text) {
  const words = cleanText(text).split(' ');
  const frequency = {};
  words.forEach(word => {
    if (word.length > 2) {
      frequency[word] = (frequency[word] || 0) + 1;
    }
  });
  return frequency;
}

async function crawlPage(url, depth = 1, visited = new Set()) {
  if (depth > MAX_DEPTH || indexedPages.length >= MAX_PAGES || visited.has(url)) {
    return;
  }

  visited.add(url);

  try {
    const response = await axios.get(url, {
      timeout: REQUEST_TIMEOUT,
      headers: { 'User-Agent': 'SavaBrowser/2.0.0' },
    });

    const $ = cheerio.load(response.data);
    const title = $('title').text() || url;
    const description = $('meta[name="description"]').attr('content') || '';
    const keywords = $('meta[name="keywords"]').attr('content')?.split(',').map(k => k.trim()) || [];
    const headers = $('h1, h2, h3').map((i, el) => $(el).text()).get().join(' ');
    const content = $('body').text().replace(/\s+/g, ' ').trim();

    const wordFrequency = getWordFrequency(content);

    const pageData = {
      url,
      title: cleanText(title),
      description: cleanText(description),
      keywords: keywords.map(k => cleanText(k)),
      headers: cleanText(headers),
      content: cleanText(content),
      wordFrequency,
      lastIndexed: new Date().toISOString(),
    };

    if (!indexedPages.some(page => page.url === url)) {
      indexedPages.push(pageData);
      store.set('indexedPages', indexedPages);
    }

    const links = [];
    $('a').each((i, link) => {
      const href = $(link).attr('href');
      if (href) {
        try {
          const absoluteUrl = new URL(href, url).href;
          if (absoluteUrl.startsWith('http')) {
            links.push(absoluteUrl);
          }
        } catch (e) {
          console.warn(`Nieprawidłowy URL: ${href}`);
        }
      }
    });

    const batch = links.slice(0, 10);
    for (let i = 0; i < batch.length; i += CONCURRENT_REQUESTS) {
      const batchSlice = batch.slice(i, i + CONCURRENT_REQUESTS);
      await Promise.all(batchSlice.map(link => crawlPage(link, depth + 1, visited)));
    }
  } catch (error) {
    console.error(`Błąd indeksowania ${url}:`, error.message);
  }
}

function calculateScore(query, page) {
  const queryWords = cleanText(query).split(' ').filter(word => word.length > 2);
  let score = 0;

  if (page.title.includes(query.toLowerCase())) score += 25;
  if (page.description.includes(query.toLowerCase())) score += 15;
  if (page.headers.includes(query.toLowerCase())) score += 10;
  queryWords.forEach(word => {
    if (page.keywords.some(k => k.includes(word))) score += 8;
    if (page.content.includes(word)) score += 3;
    score += (page.wordFrequency[word] || 0) * 5;
  });

  const daysOld = (new Date() - new Date(page.lastIndexed)) / (1000 * 60 * 60 * 24);
  score -= daysOld * 0.05;

  return score;
}

async function searchWeb(query) {
  const cachedResults = store.get(`searchCache.${query.toLowerCase()}`, []);
  if (cachedResults.length > 0) {
    return cachedResults;
  }

  const results = indexedPages
    .map(page => ({ ...page, score: calculateScore(query, page) }))
    .filter(page => page.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 15);

  store.set(`searchCache.${query.toLowerCase()}`, results);
  return results.map(({ url, title, description, score }) => ({ url, title, description, score }));
}

function clearIndex() {
  store.set('indexedPages', []);
  indexedPages.length = 0;
  store.set('searchCache', {});
  console.log('Indeks i cache wyczyszczone');
}

function getIndexStats() {
  return {
    totalPages: indexedPages.length,
    lastCrawl: indexedPages.length > 0 ? indexedPages[indexedPages.length - 1].lastIndexed : null,
  };
}

module.exports = { searchWeb, crawlPage, clearIndex, getIndexStats };
