const axios = require('axios');
const cheerio = require('cheerio');
const Store = require('electron-store');
const { URL } = require('url');
const winston = require('winston'); // Dodajemy bibliotekę do logowania

// Inicjalizacja loggera
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'crawler.log' }),
    new winston.transports.Console(),
  ],
});

const store = new Store();
const indexedPages = store.get('indexedPages', []);
const priorityDomains = store.get('priorityDomains', []); // Lista priorytetowych domen
const priorityKeywords = store.get('priorityKeywords', []); // Lista priorytetowych słów kluczowych

const MAX_DEPTH = 3;
const MAX_PAGES = 200;
const REQUEST_TIMEOUT = 5000;
const CONCURRENT_REQUESTS = 5;
const CACHE_EXPIRY = 24 * 60 * 60 * 1000; // Cache wygasa po 24 godzinach

// Funkcja do czyszczenia tekstu
function cleanText(text) {
  return text
    .replace(/\s+/g, ' ')
    .replace(/[^\w\s]/g, '')
    .trim()
    .toLowerCase();
}

// Funkcja do analizy częstotliwości słów
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

// Funkcja do wykrywania języka strony (prosta heurystyka)
function detectLanguage(text) {
  const languages = {
    en: ['the', 'and', 'is', 'in'],
    pl: ['i', 'oraz', 'jest', 'w'],
    es: ['el', 'y', 'es', 'en'],
  };
  const words = cleanText(text).split(' ').slice(0, 100);
  let maxScore = 0;
  let detectedLang = 'en';

  for (const [lang, keywords] of Object.entries(languages)) {
    const score = words.filter(word => keywords.includes(word)).length;
    if (score > maxScore) {
      maxScore = score;
      detectedLang = lang;
    }
  }
  return detectedLang;
}

// Funkcja do indeksowania strony
async function crawlPage(url, depth = 1, visited = new Set()) {
  if (depth > MAX_DEPTH || indexedPages.length >= MAX_PAGES || visited.has(url)) {
    return;
  }

  visited.add(url);
  logger.info(`Indeksowanie: ${url}, Głębokość: ${depth}`);

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
    const images = $('img').map((i, img) => ({
      src: $(img).attr('src'),
      alt: cleanText($(img).attr('alt') || ''),
    })).get();

    const wordFrequency = getWordFrequency(content);
    const language = detectLanguage(content);

    // Priorytet dla domen i słów kluczowych
    const domain = new URL(url).hostname;
    const isPriorityDomain = priorityDomains.includes(domain);
    const priorityKeywordScore = priorityKeywords.reduce((score, keyword) => {
      return content.includes(keyword.toLowerCase()) ? score + 10 : score;
    }, 0);

    const pageData = {
      url,
      title: cleanText(title),
      description: cleanText(description),
      keywords: keywords.map(k => cleanText(k)),
      headers: cleanText(headers),
      content: cleanText(content),
      images,
      wordFrequency,
      language,
      lastIndexed: new Date().toISOString(),
      priorityScore: isPriorityDomain ? 20 : 0 + priorityKeywordScore,
    };

    if (!indexedPages.some(page => page.url === url)) {
      indexedPages.push(pageData);
      store.set('indexedPages', indexedPages);
      logger.info(`Zaindeksowano: ${url}`);
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
          logger.warn(`Nieprawidłowy URL: ${href}`);
        }
      }
    });

    const batch = links.slice(0, 10);
    for (let i = 0; i < batch.length; i += CONCURRENT_REQUESTS) {
      const batchSlice = batch.slice(i, i + CONCURRENT_REQUESTS);
      await Promise.all(batchSlice.map(link => crawlPage(link, depth + 1, visited)));
    }
  } catch (error) {
    logger.error(`Błąd indeksowania ${url}: ${error.message}`);
  }
}

// Funkcja do obliczania wyniku wyszukiwania
function calculateScore(query, page, filters = {}) {
  const queryWords = cleanText(query).split(' ').filter(word => word.length > 2);
  let score = page.priorityScore || 0;

  if (page.title.includes(query.toLowerCase())) score += 25;
  if (page.description.includes(query.toLowerCase())) score += 15;
  if (page.headers.includes(query.toLowerCase())) score += 10;
  queryWords.forEach(word => {
    if (page.keywords.some(k => k.includes(word))) score += 8;
    if (page.content.includes(word)) score += 3;
    if (page.images.some(img => img.alt.includes(word))) score += 5;
    score += (page.wordFrequency[word] || 0) * 5;
  });

  const daysOld = (new Date() - new Date(page.lastIndexed)) / (1000 * 60 * 60 * 24);
  score -= daysOld * 0.05;

  // Filtrowanie
  if (filters.domain && !new URL(page.url).hostname.includes(filters.domain)) {
    score = 0;
  }
  if (filters.language && page.language !== filters.language) {
    score = 0;
  }
  if (filters.minDate && new Date(page.lastIndexed) < new Date(filters.minDate)) {
    score = 0;
  }

  return score;
}

// Funkcja wyszukiwania
async function searchWeb(query, filters = {}) {
  const cacheKey = `searchCache.${cleanText(query)}`;
  const cachedResults = store.get(cacheKey, []);
  const now = Date.now();

  // Sprawdzanie ważności cache
  if (
    cachedResults.length > 0 &&
    cachedResults[0].cachedAt &&
    now - new Date(cachedResults[0].cachedAt) < CACHE_EXPIRY
  ) {
    logger.info(`Zwrócono wyniki z cache dla zapytania: ${query}`);
    return cachedResults;
  }

  const results = indexedPages
    .map(page => ({ ...page, score: calculateScore(query, page, filters) }))
    .filter(page => page.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 15);

  const formattedResults = results.map(({ url, title, description, score, images, language }) => ({
    url,
    title,
    description,
    score,
    images: images.slice(0, 3), // Ograniczamy liczbę obrazów w wynikach
    language,
    cachedAt: new Date().toISOString(),
  }));

  store.set(cacheKey, formattedResults);
  logger.info(`Wyniki wyszukiwania dla: ${query}, wyników: ${formattedResults.length}`);
  return formattedResults;
}

// Funkcja do zarządzania priorytetami
function setPriorities({ domains = [], keywords = [] }) {
  store.set('priorityDomains', domains);
  store.set('priorityKeywords', keywords);
  logger.info(`Zaktualizowano priorytety: domeny=${domains.length}, słowa kluczowe=${keywords.length}`);
}

// Funkcja do czyszczenia indeksu
function clearIndex() {
  store.set('indexedPages', []);
  indexedPages.length = 0;
  store.set('searchCache', {});
  logger.info('Indeks i cache wyczyszczone');
}

// Funkcja do pobierania statystyk
function getIndexStats() {
  const stats = {
    totalPages: indexedPages.length,
    lastCrawl: indexedPages.length > 0 ? indexedPages[indexedPages.length - 1].lastIndexed : null,
    domains: [...new Set(indexedPages.map(page => new URL(page.url).hostname))].length,
    languages: [...new Set(indexedPages.map(page => page.language))],
  };
  logger.info('Pobrano statystyki indeksu', stats);
  return stats;
}

// Funkcja do integracji z rendererem Electrona
function setupIpcHandlers(ipcMain) {
  ipcMain.handle('search', async (event, query, filters) => {
    return await searchWeb(query, filters);
  });

  ipcMain.handle('crawl', async (event, url) => {
    await crawlPage(url);
    return getIndexStats();
  });

  ipcMain.handle('clearIndex', () => {
    clearIndex();
    return { success: true };
  });

  ipcMain.handle('getStats', () => {
    return getIndexStats();
  });

  ipcMain.handle('setPriorities', (event, priorities) => {
    setPriorities(priorities);
    return { success: true };
  });
}

module.exports = {
  searchWeb,
  crawlPage,
  clearIndex,
  getIndexStats,
  setPriorities,
  setupIpcHandlers,
};
