/* 백운국 갤러리 · 서비스 워커 (홈 화면 설치 + 간단 오프라인 캐시) */
const CACHE = "bwk-v20260604c";
const CORE = [
  "./",
  "./index.html",
  "./works.html",
  "./work.html",
  "./exhibitions.html",
  "./about.html",
  "./contact.html",
  "./assets/style.css?v=20260604c",
  "./assets/data.js?v=20260604c",
  "./assets/site.js?v=20260604c",
  "./assets/icon-192.png?v=20260604c",
  "./assets/icon-512.png?v=20260604c",
  "./manifest.webmanifest"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;

  // 페이지 이동: 네트워크 우선, 실패 시 캐시
  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
        return res;
      }).catch(() => caches.match(req).then((r) => r || caches.match("./index.html")))
    );
    return;
  }

  // 그 외 자원: 캐시 우선, 없으면 네트워크 후 캐시에 저장
  e.respondWith(
    caches.match(req).then((cached) =>
      cached || fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
        return res;
      }).catch(() => cached)
    )
  );
});
