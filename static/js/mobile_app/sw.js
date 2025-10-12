// Tesla & Starbucks inspired Service Worker for PWA functionality
const CACHE_NAME = 'smart-compressor-manager-v2';
const STATIC_CACHE = 'static-v2';
const DYNAMIC_CACHE = 'dynamic-v2';
const API_CACHE = 'api-v2';

// Tesla App style caching strategy
const CACHE_STRATEGIES = {
  STATIC: 'cache-first',
  DYNAMIC: 'network-first',
  API: 'network-first',
  IMAGES: 'cache-first'
};

// URLs to cache immediately (Tesla App style)
const STATIC_URLS = [
  '/',
  '/mobile_app',
  '/mobile_app/dashboard',
  '/mobile_app/diagnosis',
  '/mobile_app/payments',
  '/mobile_app/notifications',
  '/static/css/mobile_app.css',
  '/static/css/dashboard.css',
  '/static/css/notification_dashboard.css',
  '/static/js/mobile_app.js',
  '/static/js/dashboard.js',
  '/static/js/notification_dashboard.js',
  '/static/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png'
];

// API endpoints to cache (Starbucks App style)
const API_URLS = [
  '/api/analytics/health',
  '/api/dashboard/summary',
  '/api/notifications/history',
  '/api/mobile_app/products',
  '/api/mobile_app/orders'
];

// Install event - Tesla App style installation
self.addEventListener('install', event => {
  console.log('🚀 Service Worker installing...');
  
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(STATIC_CACHE).then(cache => {
        console.log('📦 Caching static assets...');
        return cache.addAll(STATIC_URLS);
      }),
      // Cache API responses
      caches.open(API_CACHE).then(cache => {
        console.log('🌐 Caching API endpoints...');
        return cache.addAll(API_URLS.map(url => new Request(url, { method: 'GET' })));
      })
    ]).then(() => {
      console.log('✅ Service Worker installed successfully');
      return self.skipWaiting();
    })
  );
});

// Activate event - Clean up old caches
self.addEventListener('activate', event => {
  console.log('🔄 Service Worker activating...');
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== STATIC_CACHE && 
              cacheName !== DYNAMIC_CACHE && 
              cacheName !== API_CACHE) {
            console.log('🗑️ Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('✅ Service Worker activated');
      return self.clients.claim();
    })
  );
});

// Fetch event - Advanced caching strategies
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Determine caching strategy based on URL
  let strategy = CACHE_STRATEGIES.DYNAMIC;
  
  if (url.pathname.startsWith('/static/')) {
    strategy = CACHE_STRATEGIES.STATIC;
  } else if (url.pathname.startsWith('/api/')) {
    strategy = CACHE_STRATEGIES.API;
  } else if (url.pathname.match(/\.(jpg|jpeg|png|gif|svg|webp)$/)) {
    strategy = CACHE_STRATEGIES.IMAGES;
  }
  
  event.respondWith(handleRequest(request, strategy));
});

// Tesla App style request handling
async function handleRequest(request, strategy) {
  const url = new URL(request.url);
  
  try {
    switch (strategy) {
      case CACHE_STRATEGIES.STATIC:
        return await cacheFirst(request, STATIC_CACHE);
        
      case CACHE_STRATEGIES.API:
        return await networkFirst(request, API_CACHE);
        
      case CACHE_STRATEGIES.IMAGES:
        return await cacheFirst(request, DYNAMIC_CACHE);
        
      case CACHE_STRATEGIES.DYNAMIC:
      default:
        return await networkFirst(request, DYNAMIC_CACHE);
    }
  } catch (error) {
    console.error('❌ Request failed:', error);
    
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      return await caches.match('/mobile_app') || 
             new Response('Offline - Please check your connection', {
               status: 503,
               statusText: 'Service Unavailable'
             });
    }
    
    // Return cached version if available
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    throw error;
  }
}

// Cache First Strategy (Tesla App style)
async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    console.log('📦 Serving from cache:', request.url);
    return cachedResponse;
  }
  
  console.log('🌐 Fetching from network:', request.url);
  const networkResponse = await fetch(request);
  
  if (networkResponse.ok) {
    cache.put(request, networkResponse.clone());
  }
  
  return networkResponse;
}

// Network First Strategy (Starbucks App style)
async function networkFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  
  try {
    console.log('🌐 Fetching from network:', request.url);
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('📦 Network failed, trying cache:', request.url);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    throw error;
  }
}

// Background Sync for offline data (Starbucks App style)
self.addEventListener('sync', event => {
  console.log('🔄 Background sync triggered:', event.tag);
  
  if (event.tag === 'offline-data-sync') {
    event.waitUntil(syncOfflineData());
  } else if (event.tag === 'notification-sync') {
    event.waitUntil(syncNotifications());
  }
});

// Sync offline data when connection is restored
async function syncOfflineData() {
  try {
    console.log('🔄 Syncing offline data...');
    
    // Get offline data from IndexedDB
    const offlineData = await getOfflineData();
    
    if (offlineData.length > 0) {
      // Sync each offline item
      for (const item of offlineData) {
        try {
          await syncOfflineItem(item);
          await removeOfflineItem(item.id);
        } catch (error) {
          console.error('❌ Failed to sync item:', item.id, error);
        }
      }
      
      console.log('✅ Offline data synced successfully');
    }
  } catch (error) {
    console.error('❌ Offline data sync failed:', error);
  }
}

// Sync notifications
async function syncNotifications() {
  try {
    console.log('🔔 Syncing notifications...');
    
    // Check for new notifications
    const response = await fetch('/api/notifications/unread');
    if (response.ok) {
      const notifications = await response.json();
      
      // Show notifications
      for (const notification of notifications) {
        await showNotification(notification);
      }
    }
  } catch (error) {
    console.error('❌ Notification sync failed:', error);
  }
}

// Push notifications (Tesla App style)
self.addEventListener('push', event => {
  console.log('📱 Push notification received');
  
  const options = {
    body: '새로운 알림이 있습니다',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      url: '/mobile_app/notifications'
    },
    actions: [
      {
        action: 'view',
        title: '확인',
        icon: '/static/icons/checkmark.png'
      },
      {
        action: 'dismiss',
        title: '닫기',
        icon: '/static/icons/close.png'
      }
    ]
  };
  
  if (event.data) {
    try {
      const data = event.data.json();
      options.body = data.body || options.body;
      options.data = { ...options.data, ...data };
    } catch (error) {
      console.error('❌ Failed to parse push data:', error);
    }
  }
  
  event.waitUntil(
    self.registration.showNotification('Smart Compressor Manager', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  console.log('👆 Notification clicked:', event.action);
  
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow(event.notification.data.url || '/mobile_app')
    );
  }
});

// IndexedDB helpers for offline data
async function getOfflineData() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('OfflineData', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(['offlineData'], 'readonly');
      const store = transaction.objectStore('offlineData');
      const getAllRequest = store.getAll();
      
      getAllRequest.onsuccess = () => resolve(getAllRequest.result);
      getAllRequest.onerror = () => reject(getAllRequest.error);
    };
  });
}

async function removeOfflineItem(id) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('OfflineData', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(['offlineData'], 'readwrite');
      const store = transaction.objectStore('offlineData');
      const deleteRequest = store.delete(id);
      
      deleteRequest.onsuccess = () => resolve();
      deleteRequest.onerror = () => reject(deleteRequest.error);
    };
  });
}

async function syncOfflineItem(item) {
  const response = await fetch(item.url, {
    method: item.method,
    headers: item.headers,
    body: item.body
  });
  
  if (!response.ok) {
    throw new Error(`Sync failed: ${response.status}`);
  }
  
  return response;
}

async function showNotification(notification) {
  const options = {
    body: notification.message,
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      url: notification.url || '/mobile_app/notifications',
      id: notification.id
    }
  };
  
  return self.registration.showNotification(notification.title, options);
}

// Periodic background sync (if supported)
self.addEventListener('periodicsync', event => {
  console.log('⏰ Periodic sync triggered:', event.tag);
  
  if (event.tag === 'data-refresh') {
    event.waitUntil(refreshData());
  }
});

async function refreshData() {
  try {
    console.log('🔄 Refreshing data...');
    
    // Refresh critical data
    const endpoints = [
      '/api/dashboard/summary',
      '/api/analytics/health',
      '/api/notifications/unread'
    ];
    
    for (const endpoint of endpoints) {
      try {
        const response = await fetch(endpoint);
        if (response.ok) {
          const cache = await caches.open(API_CACHE);
          await cache.put(endpoint, response.clone());
        }
      } catch (error) {
        console.error('❌ Failed to refresh:', endpoint, error);
      }
    }
    
    console.log('✅ Data refresh completed');
  } catch (error) {
    console.error('❌ Data refresh failed:', error);
  }
}

// Message handling for communication with main thread
self.addEventListener('message', event => {
  console.log('📨 Service Worker message received:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_URLS') {
    event.waitUntil(
      caches.open(DYNAMIC_CACHE)
        .then(cache => cache.addAll(event.data.urls))
    );
  }
  
  if (event.data && event.data.type === 'SYNC_OFFLINE_DATA') {
    event.waitUntil(syncOfflineData());
  }
});

// Error handling
self.addEventListener('error', event => {
  console.error('❌ Service Worker error:', event.error);
});

self.addEventListener('unhandledrejection', event => {
  console.error('❌ Service Worker unhandled promise rejection:', event.reason);
});

console.log('🚀 Smart Compressor Manager Service Worker loaded successfully');