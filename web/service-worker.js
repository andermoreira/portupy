const CACHE_NAME = 'transpilador-pt-shell-v1';
const SHELL_ASSETS = [
  './',
  './index.html',
  './style.css',
  './app.js',
  './bundle_pt.js',
  './pyodide-worker.js',
  './service-worker.js'
];
const PYODIDE_PREFIX = '/pyodide/v0.26.4/';

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(SHELL_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => Promise.all(
        cacheNames
          .filter((cacheName) => cacheName !== CACHE_NAME)
          .map((cacheName) => caches.delete(cacheName))
      ))
      .then(() => self.clients.claim())
  );
});

async function respondeComCachePrimeiro(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  if (cached) return cached;

  const response = await fetch(request);
  if (response.ok || response.type === 'opaque') {
    await cache.put(request, response.clone());
  }
  return response;
}

async function respondeComRedePrimeiro(request) {
  const cache = await caches.open(CACHE_NAME);
  try {
    const response = await fetch(request);
    if (response.ok) {
      await cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cached = await cache.match(request);
    if (cached) return cached;
    throw error;
  }
}

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  const isPyodideAsset = (
    url.origin === 'https://cdn.jsdelivr.net' &&
    url.pathname.startsWith(PYODIDE_PREFIX)
  );
  const isLocalAsset = url.origin === self.location.origin;

  if (isPyodideAsset) {
    event.respondWith(respondeComCachePrimeiro(event.request));
  } else if (isLocalAsset) {
    event.respondWith(respondeComRedePrimeiro(event.request));
  }
});
