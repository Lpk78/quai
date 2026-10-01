/* Minimal service worker: enough to make the app installable and to open on a loading dock with no
   signal. Deliberately small — there is no build-time precache list to keep in step, and nothing here
   needs to understand the application.

   Strategy: network first, falling back to the cache. The operator must never be shown a stale plan
   because a cached response won a race, so the network always gets the first chance. */

const CACHE = "quai-v1";
const SHELL = ["/", "/app", "/manifest.webmanifest", "/icons/icon-192.png", "/icons/icon-512.png"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key))),
    ),
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  // Only GETs are cacheable, and API calls are never served from the cache: a plan is a live answer.
  if (request.method !== "GET" || new URL(request.url).pathname.startsWith("/plan")) return;

  event.respondWith(
    fetch(request)
      .then((response) => {
        const copy = response.clone();
        caches.open(CACHE).then((cache) => cache.put(request, copy));
        return response;
      })
      .catch(() => caches.match(request).then((hit) => hit || caches.match("/"))),
  );
});
