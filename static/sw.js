/**
 * Service Worker for Stock Portfolio Platform PWA
 * Implements caching strategies for offline functionality and performance
 * 
 * Caching Strategy:
 * - Cache-first: Static assets (CSS, JS, images)
 * - Network-first: API responses and dynamic content
 * - Stale-while-revalidate: Navigation requests
 */

const CACHE_VERSION = 'v1';
const CACHE_NAMES = {
  STATIC: `static-${CACHE_VERSION}`,
  DYNAMIC: `dynamic-${CACHE_VERSION}`,
  API: `api-${CACHE_VERSION}`,
  OFFLINE: `offline-${CACHE_VERSION}`
};

// Static assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/dashboard',
  '/static/css/design-system.css',
  '/static/css/components.css',
  '/static/css/pages.css',
  '/static/js/main.js',
  '/static/js/mobile-navigation.js',
  '/static/js/stock-autocomplete.js',
  '/static/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  '/offline'
];

/**
 * Install event: Cache static assets
 */
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAMES.STATIC)
      .then((cache) => {
        console.log('[Service Worker] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
      .catch((error) => {
        console.error('[Service Worker] Install error:', error);
      })
  );
});

/**
 * Activate event: Clean up old caches
 */
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            // Delete old cache versions
            if (!Object.values(CACHE_NAMES).includes(cacheName)) {
              console.log('[Service Worker] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => self.clients.claim())
      .catch((error) => {
        console.error('[Service Worker] Activation error:', error);
      })
  );
});

/**
 * Fetch event: Implement caching strategies
 */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    return;
  }

  // API requests: Network-first strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request));
    return;
  }

  // Navigation requests: Stale-while-revalidate strategy
  if (request.mode === 'navigate') {
    event.respondWith(staleWhileRevalidateStrategy(request));
    return;
  }

  // Static assets: Cache-first strategy
  event.respondWith(cacheFirstStrategy(request));
});

/**
 * Cache-first strategy: Check cache first, fall back to network
 * Used for static assets (CSS, JS, images)
 */
function cacheFirstStrategy(request) {
  return caches.match(request)
    .then((response) => {
      if (response) {
        console.log('[Service Worker] Cache hit:', request.url);
        return response;
      }

      return fetch(request)
        .then((response) => {
          // Don't cache non-successful responses
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }

          // Clone the response
          const responseToCache = response.clone();

          // Cache the response
          caches.open(CACHE_NAMES.STATIC)
            .then((cache) => {
              cache.put(request, responseToCache);
            });

          return response;
        })
        .catch(() => {
          // Return offline page if available
          return caches.match('/offline');
        });
    });
}

/**
 * Network-first strategy: Try network first, fall back to cache
 * Used for API responses and dynamic content
 */
function networkFirstStrategy(request) {
  return fetch(request)
    .then((response) => {
      // Don't cache non-successful responses
      if (!response || response.status !== 200) {
        return response;
      }

      // Clone the response
      const responseToCache = response.clone();

      // Cache the response
      caches.open(CACHE_NAMES.API)
        .then((cache) => {
          cache.put(request, responseToCache);
        });

      return response;
    })
    .catch(() => {
      // Fall back to cache
      return caches.match(request)
        .then((response) => {
          if (response) {
            console.log('[Service Worker] Using cached API response:', request.url);
            return response;
          }

          // Return offline page if no cache available
          return caches.match('/offline');
        });
    });
}

/**
 * Stale-while-revalidate strategy: Return cached response immediately,
 * update cache in background
 * Used for navigation requests
 */
function staleWhileRevalidateStrategy(request) {
  return caches.match(request)
    .then((response) => {
      // Return cached response immediately
      const fetchPromise = fetch(request)
        .then((networkResponse) => {
          // Don't cache non-successful responses
          if (!networkResponse || networkResponse.status !== 200) {
            return networkResponse;
          }

          // Clone and cache the response
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAMES.DYNAMIC)
            .then((cache) => {
              cache.put(request, responseToCache);
            });

          return networkResponse;
        })
        .catch(() => {
          // Network failed, return cached response if available
          return response || caches.match('/offline');
        });

      // Return cached response immediately, or wait for network
      return response || fetchPromise;
    });
}

/**
 * Message event: Handle messages from clients
 */
self.addEventListener('message', (event) => {
  const { type, payload } = event.data;

  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;

    case 'CLEAR_CACHE':
      clearAllCaches();
      break;

    case 'GET_CACHE_SIZE':
      getCacheSize()
        .then((size) => {
          event.ports[0].postMessage({ type: 'CACHE_SIZE', size });
        });
      break;

    default:
      console.log('[Service Worker] Unknown message type:', type);
  }
});

/**
 * Clear all caches
 */
function clearAllCaches() {
  return caches.keys()
    .then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => caches.delete(cacheName))
      );
    })
    .then(() => {
      console.log('[Service Worker] All caches cleared');
    });
}

/**
 * Get total cache size
 */
function getCacheSize() {
  return caches.keys()
    .then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          return caches.open(cacheName)
            .then((cache) => {
              return cache.keys()
                .then((requests) => {
                  return Promise.all(
                    requests.map((request) => {
                      return cache.match(request)
                        .then((response) => {
                          return response.blob().then((blob) => blob.size);
                        });
                    })
                  );
                })
                .then((sizes) => {
                  return sizes.reduce((total, size) => total + size, 0);
                });
            });
        })
      );
    })
    .then((cacheSizes) => {
      return cacheSizes.reduce((total, size) => total + size, 0);
    });
}

console.log('[Service Worker] Loaded');
