const CACHE_NAME = 'transpilador-pt-shell-v2';
const PYODIDE_ASSETS = [
  './vendor/pyodide/v0.26.4/full/pyodide.js',
  './vendor/pyodide/v0.26.4/full/pyodide.asm.js',
  './vendor/pyodide/v0.26.4/full/pyodide.asm.wasm',
  './vendor/pyodide/v0.26.4/full/python_stdlib.zip',
  './vendor/pyodide/v0.26.4/full/pyodide-lock.json'
];
const SHELL_ASSETS = [
  './',
  './index.html',
  './style.css',
  './app.js',
  './bundle_pt.js',
  './pyodide-worker.js',
  './service-worker.js',
  ...PYODIDE_ASSETS
];

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
  const isLocalAsset = url.origin === self.location.origin;

  if (isLocalAsset) {
    event.respondWith(respondeComRedePrimeiro(event.request));
  }
});
