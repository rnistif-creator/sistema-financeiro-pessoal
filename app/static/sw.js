// Service Worker para PWA
const CACHE_NAME = 'financeiro-v3-20251106a';
// Página offline minimal (poderíamos criar /offline.html dedicada)
const OFFLINE_URL = '/offline';

// Arquivos essenciais para cache
// Apenas assets estáticos públicos. Evitar cache de páginas autenticadas.
const STATIC_CACHE = [
  '/',
  '/offline',
  '/static/config.js',
  '/static/components.js',
  '/static/components.css'
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
  console.log('[SW] Instalando Service Worker...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Cache aberto');
        return cache.addAll(STATIC_CACHE);
      })
      .then(() => self.skipWaiting())
  );
});

// Ativação do Service Worker
self.addEventListener('activate', (event) => {
  console.log('[SW] Ativando Service Worker...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] Removendo cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Estratégia de cache: Network First, fallback para Cache
self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;
  if (!request.url.startsWith(self.location.origin)) return;

  // Não cachear endpoints de API ou páginas potencialmente sensíveis
  const url = new URL(request.url);
  if (url.pathname.startsWith('/auth') || url.pathname.startsWith('/api')) {
    return; // deixar seguir rede normal
  }

  // Estratégia: cache-first para assets estáticos definidos, network-first para demais
  if (STATIC_CACHE.includes(url.pathname)) {
    event.respondWith(
      caches.match(request).then(cached => {
        if (cached) return cached;
        return fetch(request).then(resp => {
          if (resp && resp.status === 200) {
            const clone = resp.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
          }
          return resp;
        }).catch(() => caches.match(OFFLINE_URL));
      })
    );
  } else {
    event.respondWith(
      fetch(request).catch(() => {
        if (request.mode === 'navigate') {
          return caches.match(OFFLINE_URL);
        }
        return caches.match(request);
      })
    );
  }
});

// Sincronização em background (quando voltar online)
self.addEventListener('sync', (event) => {
  console.log('[SW] Sincronização em background:', event.tag);
  
  if (event.tag === 'sync-lancamentos') {
    event.waitUntil(syncLancamentos());
  }
});

// Função para sincronizar lançamentos salvos offline
async function syncLancamentos() {
  console.log('[SW] Sincronizando lançamentos...');
  // Implementar lógica de sincronização aqui
  // Por exemplo, enviar dados salvos no IndexedDB
}

// Notificações Push (futuro)
self.addEventListener('push', (event) => {
  console.log('[SW] Push recebido:', event);
  
  const options = {
    body: event.data ? event.data.text() : 'Notificação do Sistema Financeiro',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    tag: 'financeiro-notification',
    requireInteraction: false
  };
  
  event.waitUntil(
    self.registration.showNotification('Sistema Financeiro', options)
  );
});

// Click em notificação
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notificação clicada:', event);
  
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow('/dashboard')
  );
});

// Mensagens do cliente
self.addEventListener('message', (event) => {
  console.log('[SW] Mensagem recebida:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
