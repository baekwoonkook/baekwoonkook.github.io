# 백운국 회화 갤러리 (GitHub Pages용)

추상 회화 작품을 보여주는 갤러리 웹사이트입니다.
그대로 GitHub에 올리면 `https://아이디.github.io` 주소로 공개됩니다.

## 폴더 구성
```
baekwoonkook-gallery/
├─ index.html   ← 갤러리 페이지 (메인)
├─ images/      ← 작품/전시 이미지
│   ├─ w01.jpg ~ w08.jpg   (작품 8점, 웹용으로 최적화됨)
│   └─ ex01.jpg ~ ex03.jpg (전시 사진 3장)
└─ README.md
```
※ images 폴더의 원본 파일(abstract2020… 등)도 그대로 남아 있습니다. 화면에는 w/ex 파일만 쓰입니다.

## 작품 제목·연도·재료 수정
`index.html`을 메모장으로 열어 `WORKS` 부분을 고치면 됩니다.
```js
{ file:"w01.jpg", t:"Abstract", m:"Oil & acrylic on canvas · 90 × 56 cm · 2020" },
```
- `t` = 작품 제목, `m` = 재료·크기·연도 (자유롭게 한글로 써도 됩니다)
- 현재 제목(Abstract, Journey, Lines …)은 제가 임의로 붙인 것이니 실제 제목으로 바꾸세요.

## 작품 추가
1. 새 이미지를 `images/` 폴더에 넣습니다 (가로·세로 1600px 정도로 줄이면 빨라요).
2. `WORKS` 목록에 한 줄 추가:
   ```js
   { file:"w09.jpg", t:"제목", m:"재료 · 크기 · 연도" },
   ```

## GitHub Pages로 공개하기
1. https://github.com 가입 후 로그인
2. 오른쪽 위 **+ → New repository**
3. 저장소 이름을 **`아이디.github.io`** 로 입력
4. **Public** → **Create repository**
5. **uploading an existing file** → `index.html`과 `images` 폴더를 통째로 드래그 → **Commit changes**
6. 1~2분 뒤 `https://아이디.github.io` 접속

## 로컬 미리보기
이 폴더에서:
```
python -m http.server 8765
```
→ 브라우저로 http://localhost:8765
