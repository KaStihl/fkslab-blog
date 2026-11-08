// Floodlight Chairman service worker: makes the game installable and playable offline.
// The page itself is fetched network-first so new versions arrive whenever you're online.
const VERSION = 'fc-v1';
const BASE = '/games/floodlight-chairman/';
const SHELL = [BASE, BASE + 'manifest.webmanifest', BASE + 'icon-192.png', BASE + 'icon-512.png', BASE + 'apple-touch-icon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('fc-') && k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // The game page: network first, fall back to the cached copy offline.
  if (req.mode === 'navigate' && url.pathname.startsWith(BASE)) {
    e.respondWith(fetch(req).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(VERSION).then(c => c.put(BASE, copy)); }
      return res;
    }).catch(() => caches.match(BASE)));
    return;
  }

  // Fonts: serve from cache, refresh in the background.
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(caches.open(VERSION + '-fonts').then(async c => {
      const hit = await c.match(req);
      const net = fetch(req).then(res => { if (res.ok || res.type === 'opaque') c.put(req, res.clone()); return res; }).catch(() => hit);
      return hit || net;
    }));
    return;
  }

  // Icons and manifest: cache first.
  if (url.origin === location.origin && url.pathname.startsWith(BASE)) {
    e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
  }
});
