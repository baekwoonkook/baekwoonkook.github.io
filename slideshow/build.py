#!/usr/bin/env python3
"""
메리 스튜어트 낭독 영상 — 줄거리에 맞는 역사화를 시간대별로 넣어
슬라이드형 영상(mp4)을 자동으로 만든다.

두 단계:
  1) 이미지 받기 : 위키미디어 공용(Commons)에서 장면별 역사화를 검색·다운로드
       python slideshow/build.py --fetch
       (받은 그림은 slideshow/img/ 에 저장. 마음에 안 들면 파일을 직접 교체)
  2) 영상 만들기 : 받은 그림 + 오디오를 타임라인에 맞춰 합침
       python slideshow/build.py --render --audio "원본음성.mp3" --out mary-slideshow.mp4

필요 패키지: Pillow, imageio-ffmpeg, requests
  pip install Pillow imageio-ffmpeg requests

※ --fetch 는 commons.wikimedia.org / upload.wikimedia.org 접속이 필요합니다.
  네트워크 허용 목록(allowlist)에 두 호스트를 추가해야 동작합니다.
"""
import argparse
import subprocess
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMG_DIR = HERE / "img"
CACHE = HERE / ".cache"
FONT_URL = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Bold.otf"

# 오디오 총 길이(초) = 11:37.47. 실제 파일에 맞게 --render 시 자동 보정됨.
DEFAULT_DUR = 697.47

# 챕터별 길이 비중(글자 수 기준, build 시 계산된 값)과 그 안에 들어갈 장면들.
# 각 장면: (검색어, 화면 자막)  — 한 챕터 시간은 장면들에 균등 분배된다.
# file= 로 시작하면 위키 공용 파일명을 직접 지정(검색 대신).
CHAPTERS = [
    # (챕터 글자수, [장면들])
    (227, [  # 프롤로그 · 처형 새벽
        ("file=Mary_Stuart_James.jpg", "메리, 스코틀랜드의 여왕 (1542–1587)"),
    ]),
    (321, [  # 1장 · 패전 속에서 태어난 여왕
        ("James V of Scotland portrait", "제임스 5세 — 메리의 아버지 (코르네유 드 리옹)"),
        ("Battle of Solway Moss", "솔웨이 모스 전투, 1542 — 스코틀랜드의 패전"),
        ("Linlithgow Palace engraving", "린리스고 궁 — 메리가 태어난 곳"),
    ]),
    (542, [  # 2장 · 전쟁이 프랑스로 보낸 아이
        ("Battle of Pinkie 1547", "핑키 전투, 1547 — '검은 토요일'"),
        ("Mary Queen of Scots child France", "프랑스 궁정의 어린 메리"),
        ("Francis II France Mary Stuart", "프랑수아 2세와 메리 — 프랑스의 왕비"),
        ("Mary Queen of Scots white mourning Clouet", "흰 상복의 메리 (프랑수아 클루에) — 과부가 되어 귀국"),
    ]),
    (531, [  # 3장 · 사랑이라는 이름의 함정
        ("Henry Stuart Lord Darnley portrait", "단리 경 — 메리의 두 번째 남편"),
        ("Murder of David Rizzio William Allan", "리치오의 살해 (윌리엄 앨런, 1833)"),
        ("Kirk o Field murder Darnley 1567 drawing", "커크 오 필드 — 단리 암살 현장 (1567년 기록화)"),
        ("Mary Queen of Scots Carberry Hill", "카베리 언덕 — 군대 없이 사로잡히다, 1567"),
    ]),
    (766, [  # 4장 · 마지막 패전과 십구 년의 새장
        ("Battle of Langside 1568", "랭사이드 전투, 1568 — 메리의 마지막 전투"),
        ("Mary Queen of Scots Nicholas Hilliard 1578", "유폐 중의 메리 (니컬러스 힐리어드, 1578)"),
        ("Elizabeth I Darnley portrait", "엘리자베스 1세 — 사촌이자 가둔 자"),
        ("Babington plot conspirators engraving", "배빙턴 음모, 1586 — 가로채인 암호 편지"),
        ("Fotheringhay Castle trial Mary", "포더링헤이 성 — 재판과 유죄"),
    ]),
    (615, [  # 5장 · 그날, 1587년 2월 8일
        ("Mary Queen of Scots led to execution Laslett Pott", "처형장으로 가는 메리 (라슬렛 J. 포트, 1871)"),
        ("Execution of Mary Queen of Scots Herdman", "메리의 처형 (로버트 허드먼, 1867)"),
        ("Execution of Mary Queen of Scots 1587", "포더링헤이 성에서의 참수, 1587년 2월 8일"),
    ]),
    (325, [  # 6장 · 끝에서 시작으로
        ("James VI and I king portrait", "제임스 1세 — 두 왕국을 하나로 묶은 아들"),
        ("Mary Queen of Scots tomb Westminster Abbey", "웨스트민스터 사원의 메리 무덤"),
    ]),
]

W, H = 1920, 1080
BG = (11, 11, 12)
GOLD = (201, 162, 39)
INK = (232, 228, 220)


def ensure_font() -> str:
    CACHE.mkdir(exist_ok=True)
    fp = CACHE / "korean.otf"
    if not fp.exists():
        import requests
        print("한글 폰트 다운로드 중...")
        fp.write_bytes(requests.get(FONT_URL, timeout=60).content)
    return str(fp)


def ffmpeg() -> str:
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def flat_scenes():
    """챕터를 펼쳐 (장면검색어, 자막, 시작시각, 길이) 리스트로."""
    total = sum(c for c, _ in CHAPTERS)
    return total


def fetch():
    """위키미디어 공용에서 장면별 이미지를 검색·다운로드한다."""
    import requests
    IMG_DIR.mkdir(exist_ok=True)
    API = "https://commons.wikimedia.org/w/api.php"
    FILEPATH = "https://commons.wikimedia.org/wiki/Special:FilePath/"
    headers = {"User-Agent": "MaryStuartSlideshow/1.0 (educational)"}

    n = 0
    for ci, (_, scenes) in enumerate(CHAPTERS):
        for si, (query, caption) in enumerate(scenes):
            n += 1
            out = IMG_DIR / f"{n:02d}.jpg"
            if out.exists():
                print(f"[{n:02d}] 이미 있음: {out.name}")
                continue
            try:
                if query.startswith("file="):
                    fname = query[5:]
                    url = FILEPATH + urllib.parse.quote(fname) + "?width=1600"
                    data = requests.get(url, headers=headers, timeout=60).content
                else:
                    params = {
                        "action": "query", "format": "json",
                        "generator": "search", "gsrsearch": query,
                        "gsrnamespace": "6", "gsrlimit": "1",
                        "prop": "imageinfo", "iiprop": "url", "iiurlwidth": "1600",
                    }
                    r = requests.get(API, params=params, headers=headers, timeout=60).json()
                    pages = r.get("query", {}).get("pages", {})
                    if not pages:
                        print(f"[{n:02d}] 검색 결과 없음: {query}")
                        continue
                    page = next(iter(pages.values()))
                    thumb = page["imageinfo"][0].get("thumburl") or page["imageinfo"][0]["url"]
                    data = requests.get(thumb, headers=headers, timeout=60).content
                    print(f"[{n:02d}] {page.get('title','')}  <- {query}")
                out.write_bytes(data)
            except Exception as e:
                print(f"[{n:02d}] 실패({query}): {e}")
    print(f"\n다운로드 폴더: {IMG_DIR}  — 마음에 안 드는 그림은 같은 번호.jpg로 교체하세요.")


def compose_frame(src: Path, caption: str, font_path: str) -> Path:
    """이미지를 1920x1080 어두운 배경에 맞춰 배치하고 자막을 넣은 프레임 생성."""
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    frame = Image.new("RGB", (W, H), BG)
    if src.exists():
        try:
            im = Image.open(src).convert("RGB")
            im = ImageOps.exif_transpose(im)
            im.thumbnail((W - 160, H - 200), Image.LANCZOS)
            frame.paste(im, ((W - im.width) // 2, (H - 120 - im.height) // 2))
        except Exception as e:
            print(f"  이미지 열기 실패 {src.name}: {e}")
    d = ImageDraw.Draw(frame)
    # 하단 자막 바
    d.rectangle([0, H - 92, W, H], fill=(8, 8, 9))
    d.line([(80, H - 92), (W - 80, H - 92)], fill=GOLD, width=2)
    f = ImageFont.truetype(font_path, 34)
    d.text((90, H - 66), caption, font=f, fill=INK)
    outp = CACHE / f"frame_{src.stem}.png"
    frame.save(outp)
    return outp


def render(audio: str, out: str):
    font_path = ensure_font()
    CACHE.mkdir(exist_ok=True)
    FF = ffmpeg()

    # 실제 오디오 길이 확인
    dur = DEFAULT_DUR
    try:
        import subprocess
        info = subprocess.run([FF, "-i", audio], capture_output=True, text=True).stderr
        for line in info.splitlines():
            if "Duration" in line:
                hms = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = hms.split(":")
                dur = int(h) * 3600 + int(m) * 60 + float(s)
    except Exception:
        pass

    total_chars = sum(c for c, _ in CHAPTERS)
    # 장면별 (프레임경로, 길이) 만들기
    clips = []
    n = 0
    fade = 0.5
    for ci, (cchars, scenes) in enumerate(CHAPTERS):
        chap_dur = dur * cchars / total_chars
        each = chap_dur / len(scenes)
        for query, caption in scenes:
            n += 1
            frame = compose_frame(IMG_DIR / f"{n:02d}.jpg", caption, font_path)
            clip = CACHE / f"clip_{n:02d}.mp4"
            # 각 장면을 페이드 인/아웃 있는 짧은 영상으로
            vf = f"fade=t=in:st=0:d={fade},fade=t=out:st={max(each-fade,0):.2f}:d={fade}"
            subprocess.run([
                FF, "-y", "-loop", "1", "-framerate", "24", "-t", f"{each:.2f}",
                "-i", str(frame), "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-r", "24", str(clip)
            ], check=True, capture_output=True)
            clips.append(clip)

    # concat
    listf = CACHE / "list.txt"
    listf.write_text("".join(f"file '{c}'\n" for c in clips))
    silent = CACHE / "video.mp4"
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", str(listf),
                    "-c", "copy", str(silent)], check=True, capture_output=True)
    # 오디오 입히기
    subprocess.run([FF, "-y", "-i", str(silent), "-i", audio,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True, capture_output=True)
    print(f"\n완료: {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="역사화 이미지 다운로드")
    ap.add_argument("--render", action="store_true", help="영상 합치기")
    ap.add_argument("--audio", default="", help="오디오 mp3 경로")
    ap.add_argument("--out", default="mary-slideshow.mp4")
    args = ap.parse_args()
    if args.fetch:
        fetch()
    if args.render:
        if not args.audio:
            sys.exit("--render 에는 --audio 경로가 필요합니다.")
        render(args.audio, args.out)
    if not args.fetch and not args.render:
        ap.print_help()


if __name__ == "__main__":
    main()
