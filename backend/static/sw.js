// CropGuard Offline PWA Service Worker (F10)
const CACHE_NAME = 'cropguard-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/manifest.json',
  '/sample_images/tomato_early_blight.jpg',
  '/sample_images/tomato_late_blight.jpg',
  '/sample_images/tomato_leaf_curl.jpg',
  '/sample_images/tomato_healthy.jpg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      return cachedResponse || fetch(event.request).catch(() => {
        // Return offline fallback if network is unavailable
        if (event.request.mode === 'navigate') {
          return caches.match('/');
        }
      });
    })
  );
});
