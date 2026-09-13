const CACHE_NAME = 'portupy-shell-v2';
// Assets versionados e imutáveis (o caminho carrega a versão do Pyodide).
// Servi-los cache-first evita rebaixar o runtime pesado (.wasm/.zip) a cada
// reabertura online; só a rede é consultada quando ainda não estão em cache.
// Cada resposta cacheada é conferida contra o sha256 embutido abaixo — o
// script instalado do Service Worker não vive na Cache Storage, então um
// snippet do aluno não consegue trocar o mapa de hashes junto com o arquivo.
const PREFIXO_IMUTAVEL = '/vendor/pyodide/';
/* pyodide-integrity:begin */
const PYODIDE_INTEGRITY = {
  "/vendor/pyodide/v0.26.4/full/pyodide-lock.json": "cd50b49de944c579045e122fe8628b31f9ce446379f032f36c05e273d38766e0",
  "/vendor/pyodide/v0.26.4/full/pyodide.asm.js": "919560652ed3dad3707cb3a394785da1e046fb13dc0defa162058ff230cb7eed",
  "/vendor/pyodide/v0.26.4/full/pyodide.asm.wasm": "b7e66a19427a55010ac3367c1b6c64b893f9826f783412945fdf0c3337f3bc94",
  "/vendor/pyodide/v0.26.4/full/pyodide.js": "c0069107621d5b942a659e737a12e774cc0451feaa2256f475d72e071d844ec7",
  "/vendor/pyodide/v0.26.4/full/python_stdlib.zip": "72894522b791858b9d613ac786b951d8b5094035dcf376313ea24a466810f336"
};
/* pyodide-integrity:end */
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

function chaveIntegridade(pathname) {
  const indice = pathname.indexOf(PREFIXO_IMUTAVEL);
  if (indice === -1) return null;
  return pathname.slice(indice);
}

async function sha256Hex(buffer) {
  const digest = await crypto.subtle.digest('SHA-256', buffer);
  return Array.from(new Uint8Array(digest), (byte) =>
    byte.toString(16).padStart(2, '0')
  ).join('');
}

async function confereIntegridade(response, esperado) {
  const atual = await sha256Hex(await response.clone().arrayBuffer());
  if (atual !== esperado) {
    throw new Error('Falha de integridade do runtime Pyodide.');
  }
  return response;
}

async function respondeComIntegridade(request) {
  const esperado = PYODIDE_INTEGRITY[chaveIntegridade(new URL(request.url).pathname)];
  if (!esperado) {
    return respondeComRedePrimeiro(request);
  }

  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  if (cached) {
    try {
      return await confereIntegridade(cached, esperado);
    } catch (error) {
      await cache.delete(request);
    }
  }

  const response = await fetch(request);
  if (!response.ok) {
    return response;
  }
  const verificado = await confereIntegridade(response, esperado);
  await cache.put(request, verificado.clone());
  return verificado;
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
  const isLocalAsset = url.origin === self.location.origin;
  if (!isLocalAsset) return;

  // Runtime Pyodide é imutável por versão: cache-first com verificação de
  // hash. O restante do shell segue network-first para receber updates.
  if (url.pathname.includes(PREFIXO_IMUTAVEL)) {
    event.respondWith(respondeComIntegridade(event.request));
  } else {
    event.respondWith(respondeComRedePrimeiro(event.request));
  }
});
