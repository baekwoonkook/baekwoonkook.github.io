# 백운국 회화 갤러리 (GitHub Pages용)

추상 회화 작품을 보여주는 다중 페이지 갤러리 웹사이트입니다.
GitHub에 올리면 `https://아이디.github.io` 주소로 공개됩니다.

## 페이지 구성
```
baekwoonkook.github.io/
├─ index.html         ← 홈 (히어로 + 대표작 + 전시·소개 티저)
├─ works.html         ← 작품 전체 목록
├─ work.html          ← 작품 상세 (work.html?id=w01 형식)
├─ exhibitions.html   ← 전시 기록
├─ about.html         ← 작가 노트 + 약력(살아온 길)
├─ contact.html       ← 연락처
├─ assets/
│   ├─ data.js        ← ★ 작품·전시·약력 데이터 (여기만 고치면 전 페이지 반영)
│   ├─ style.css      ← 공통 스타일
│   └─ site.js        ← 네비게이션·푸터·라이트박스 공통 동작
├─ images/            ← 작품(w**.jpg)·전시(ex**.jpg) 이미지
└─ README.md
```

## 작품 제목·연도·재료 수정
`assets/data.js`를 메모장으로 열어 `WORKS` 부분을 고치면 됩니다.
```js
{ id:"w01", file:"w01.jpg", t:"Abstract", year:"2020",
  m:"Oil & acrylic on canvas · 90 × 56 cm",
  d:"작품 설명을 여기에 적습니다." },
```
- `t` = 제목, `year` = 연도, `m` = 재료·크기, `d` = 상세 페이지 설명
- `id`, `file` 은 바꾸지 마세요 (상세 페이지·이미지 연결에 쓰입니다)
- 현재 제목(Abstract, Journey …)은 임시이니 실제 제목으로 바꾸세요.

## 작품 추가
1. 새 이미지를 `images/` 폴더에 넣습니다 (긴 변 1600px 정도로 줄이면 빨라요).
2. `assets/data.js` 의 `WORKS` 목록에 한 줄 추가:
   ```js
   { id:"w12", file:"w12.jpg", t:"제목", year:"2025", m:"재료 · 크기", d:"설명" },
   ```

## 이미지를 교체했는데 화면이 안 바뀔 때
브라우저가 옛 이미지를 캐시한 것입니다. `assets/data.js` 맨 위의
`ver` 값(예: `"20260603c"`)의 숫자를 올리면 새 이미지를 강제로 불러옵니다.
(같은 값이 `*.html` 의 `?v=...` 에도 들어 있으니 함께 올려주면 CSS/JS까지 갱신됩니다.)

## GitHub Pages로 공개하기
저장소 이름을 `아이디.github.io` 로 만들고 Public 으로 올리면
1~2분 뒤 `https://아이디.github.io` 에서 보입니다.

## 로컬 미리보기
이 폴더에서:
```
python -m http.server 8765
```
→ 브라우저로 http://localhost:8765

## 휴대폰 홈 화면에 앱처럼 설치 (PWA)
이 사이트는 PWA로 만들어져 홈 화면에 아이콘으로 설치할 수 있습니다.
- **아이폰(Safari)**: 사이트 접속 → 하단 **공유(□↑)** → **홈 화면에 추가**
- **안드로이드(Chrome)**: 사이트 접속 → 우상단 **⋮** → **앱 설치 / 홈 화면에 추가**

관련 파일: `manifest.webmanifest`(앱 정보), `sw.js`(서비스 워커),
`assets/icon-*.png`·`assets/apple-touch-icon.png`(아이콘).
아이콘을 바꾸려면 위 png들을 교체하고 `?v=` 캐시 버전을 올리세요.
