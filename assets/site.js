/* =========================================================================
   백운국 갤러리 · 공통 동작 (네비게이션 / 푸터 / 라이트박스 / 유틸)
   각 페이지에서 data.js 다음에 불러옵니다.
   ========================================================================= */
(function () {
  const V = (typeof SITE !== "undefined" && SITE.ver) || "1";
  // 이미지/에셋 경로에 캐시 무효화 버전을 붙입니다.
  window.imgSrc = (file) => "images/" + file + "?v=" + V;

  const PAGES = [
    { href: "works.html",       label: "WORKS" },
    { href: "exhibitions.html", label: "EXHIBITION" },
    { href: "about.html",       label: "ABOUT" },
    { href: "contact.html",     label: "CONTACT" }
  ];
  const here = (location.pathname.split("/").pop() || "index.html");

  /* ---- 네비게이션 ---- */
  function buildNav() {
    const nav = document.createElement("nav");
    nav.className = "nav";
    const links = PAGES.map(p => {
      const active = (here === p.href) ? " active" : "";
      return `<a class="${active.trim()}" href="${p.href}">${p.label}</a>`;
    }).join("");
    nav.innerHTML =
      `<a class="brand" href="index.html">${SITE.nameEn}<small>${SITE.nameKo} · ${SITE.role}</small></a>
       <button class="burger" aria-label="menu">&#9776;</button>
       <div class="links">${links}</div>`;
    document.body.prepend(nav);
    const burger = nav.querySelector(".burger");
    const linksEl = nav.querySelector(".links");
    burger.addEventListener("click", () => linksEl.classList.toggle("open"));
    linksEl.querySelectorAll("a").forEach(a =>
      a.addEventListener("click", () => linksEl.classList.remove("open")));
  }

  /* ---- 푸터 ---- */
  function buildFooter() {
    const f = document.createElement("footer");
    f.className = "foot";
    const links = [{href:"index.html",label:"HOME"}, ...PAGES]
      .map(p => `<a href="${p.href}">${p.label}</a>`).join("");
    f.innerHTML =
      `<div class="name serif">${SITE.nameEn.split(" ").map(w=>w[0]+w.slice(1).toLowerCase()).join(" ")}</div>
       <div class="nav2">${links}</div>
       <div class="c">© <span class="yr"></span> ${SITE.nameKo}. All rights reserved.</div>`;
    document.body.appendChild(f);
    f.querySelector(".yr").textContent = new Date().getFullYear();
  }

  /* ---- 라이트박스 ---- */
  let LBItems = [], lbCur = 0;
  function ensureLb() {
    if (document.getElementById("lb")) return;
    const lb = document.createElement("div");
    lb.className = "lb"; lb.id = "lb";
    lb.innerHTML =
      `<button class="close" aria-label="close">&times;</button>
       <button class="prev" aria-label="prev">&#8249;</button>
       <img id="lbImg" alt="" />
       <div class="cap"><div class="t" id="lbT"></div><div class="m" id="lbM"></div></div>
       <button class="next" aria-label="next">&#8250;</button>`;
    document.body.appendChild(lb);
    lb.querySelector(".close").onclick = closeLb;
    lb.querySelector(".prev").onclick = e => { e.stopPropagation(); stepLb(-1); };
    lb.querySelector(".next").onclick = e => { e.stopPropagation(); stepLb(1); };
    lb.addEventListener("click", e => { if (e.target === lb) closeLb(); });
    document.addEventListener("keydown", e => {
      if (!lb.classList.contains("open")) return;
      if (e.key === "Escape") closeLb();
      if (e.key === "ArrowLeft") stepLb(-1);
      if (e.key === "ArrowRight") stepLb(1);
    });
  }
  function renderLb() {
    const it = LBItems[lbCur];
    document.getElementById("lbImg").src = imgSrc(it.file);
    document.getElementById("lbT").textContent = it.t || "";
    document.getElementById("lbM").textContent = it.m || "";
    const multi = LBItems.length > 1;
    document.querySelector("#lb .prev").style.display = multi ? "" : "none";
    document.querySelector("#lb .next").style.display = multi ? "" : "none";
  }
  function stepLb(d) {
    lbCur = (lbCur + d + LBItems.length) % LBItems.length;
    renderLb();
  }
  function closeLb() { document.getElementById("lb").classList.remove("open"); }
  // 외부 공개 API
  window.openLightbox = function (items, index) {
    ensureLb();
    LBItems = items; lbCur = index || 0; renderLb();
    document.getElementById("lb").classList.add("open");
  };

  /* ---- 작품 카드 (작품 상세로 연결) ---- */
  window.renderWorks = function (container, list) {
    list.forEach(w => {
      const a = document.createElement("a");
      a.className = "card reveal";
      a.href = "work.html?id=" + encodeURIComponent(w.id);
      const img = new Image();
      img.src = imgSrc(w.file); img.alt = w.t; img.loading = "lazy";
      img.onload = () => img.classList.add("loaded");
      const ov = document.createElement("div"); ov.className = "ov";
      ov.innerHTML = `<div class="t">${w.t}</div><div class="m">${w.year || ""}</div>`;
      a.appendChild(img); a.appendChild(ov);
      container.appendChild(a);
    });
  };

  /* ---- 스크롤 등장 효과 ---- */
  function initReveal() {
    const els = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window) || !els.length) {
      els.forEach(e => e.classList.add("in")); return;
    }
    const io = new IntersectionObserver((ents) => {
      ents.forEach(en => { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { threshold: .12 });
    els.forEach(e => io.observe(e));
  }

  // 페이지 로드 시 공통 요소 구성
  document.addEventListener("DOMContentLoaded", () => {
    buildNav();
    buildFooter();
    if (typeof window.pageInit === "function") window.pageInit();
    initReveal(); // pageInit이 추가한 동적 요소까지 관찰
  });
})();
