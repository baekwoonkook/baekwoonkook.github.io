#!/usr/bin/env python3
"""메리 스튜어트 낭독 영상용 표지 이미지를 생성한다 (1920x1080)."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
GOLD = (201, 162, 39)
GOLD_SOFT = (212, 175, 55)
INK = (232, 228, 220)
SUB = (150, 146, 138)

FONT = "/tmp/fonts/korean.ttf"

# ---------- 배경: 어두운 슬레이트 + 새벽빛 그라데이션 ----------
img = Image.new("RGB", (W, H), (11, 11, 12))
px = img.load()
top = (10, 11, 14)
bot = (26, 20, 16)  # 아래쪽에 옅은 새벽 온기
for y in range(H):
    t = y / H
    r = int(top[0] + (bot[0] - top[0]) * t)
    g = int(top[1] + (bot[1] - top[1]) * t)
    b = int(top[2] + (bot[2] - top[2]) * t)
    for x in range(W):
        px[x, y] = (r, g, b)

# ---------- 새벽 글로우 (하단 중앙 따뜻한 빛) ----------
glow = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(glow)
cx, cy = W // 2, int(H * 0.92)
for rad, val in [(720, 70), (520, 90), (340, 110), (200, 130)]:
    gd.ellipse([cx - rad, cy - rad * 0.6, cx + rad, cy + rad * 0.6], fill=val)
glow = glow.filter(ImageFilter.GaussianBlur(120))
amber = Image.new("RGB", (W, H), (150, 96, 40))
img = Image.composite(amber, img, glow.point(lambda v: int(v * 0.55)))

draw = ImageDraw.Draw(img)

# ---------- 왕관 (가는 금색 라인아트) ----------
def crown(d, cx, cy, w, h, color, width=5):
    half = w / 2
    base_y = cy + h / 2
    band_h = h * 0.28
    # 밑단 띠
    d.rounded_rectangle([cx - half, base_y - band_h, cx + half, base_y],
                        radius=8, outline=color, width=width)
    # 5개 뿔 + 끝 보석
    peaks = [-half, -half/2, 0, half/2, half]
    peak_top = cy - h / 2
    mids = base_y - band_h
    pts = []
    valleys_y = mids - h * 0.10
    pattern = [
        (cx - half, mids),
        (cx - half*0.75, peak_top + h*0.18),
        (cx - half/2, valleys_y),
        (cx - half*0.25, peak_top + h*0.05),
        (cx, valleys_y - h*0.04),
        (cx + half*0.25, peak_top + h*0.05),
        (cx + half/2, valleys_y),
        (cx + half*0.75, peak_top + h*0.18),
        (cx + half, mids),
    ]
    d.line(pattern, fill=color, width=width, joint="curve")
    # 뿔 끝 보석
    for bx, by in [(cx - half*0.75, peak_top + h*0.18),
                   (cx, valleys_y - h*0.04),
                   (cx + half*0.75, peak_top + h*0.18)]:
        r = 9
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=color)
    # 띠 위 작은 보석 점선
    n = 9
    for i in range(n):
        bx = cx - half + (w) * (i + 0.5) / n
        by = base_y - band_h / 2
        r = 4
        d.ellipse([bx - r, by - r, bx + r, by + r], outline=color, width=2)

# 왕관 글로우 레이어
crown_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
cdraw = ImageDraw.Draw(crown_layer)
crown(cdraw, W // 2, int(H * 0.33), 360, 230, GOLD_SOFT + (255,), width=6)
glowc = crown_layer.filter(ImageFilter.GaussianBlur(14))
img.paste(Image.new("RGB", (W, H), GOLD), (0, 0), glowc.split()[3].point(lambda v: int(v * 0.35)))
img.paste(crown_layer, (0, 0), crown_layer)
draw = ImageDraw.Draw(img)

# ---------- 텍스트 ----------
def centered(d, y, text, font, fill):
    bb = d.textbbox((0, 0), text, font=font)
    w = bb[2] - bb[0]
    d.text(((W - w) / 2, y), text, font=font, fill=fill)
    return bb[3] - bb[1]

f_title = ImageFont.truetype(FONT, 96)
f_sub = ImageFont.truetype(FONT, 40)
f_small = ImageFont.truetype(FONT, 34)
f_en = ImageFont.truetype(FONT, 36)

centered(draw, int(H * 0.52), "마지막 아침", f_title, INK)
centered(draw, int(H * 0.52) + 120, "메리, 스코틀랜드의 여왕", ImageFont.truetype(FONT, 56), INK)

# 구분선
ly = int(H * 0.74)
draw.line([(W/2 - 180, ly), (W/2 + 180, ly)], fill=GOLD, width=2)

centered(draw, ly + 26, "Mary, Queen of Scots  ·  1542 – 1587", f_en, GOLD_SOFT)
centered(draw, ly + 90, "1587년 2월 8일, 포더링헤이 성", f_small, SUB)

# ---------- 비네트 ----------
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.rectangle([0, 0, W, H], fill=255)
vd.ellipse([-W*0.25, -H*0.25, W*1.25, H*1.25], fill=0)
vig = vig.filter(ImageFilter.GaussianBlur(200))
black = Image.new("RGB", (W, H), (0, 0, 0))
img = Image.composite(black, img, vig.point(lambda v: int(v * 0.55)))

img.save("assets/mary-cover.png")
print("saved assets/mary-cover.png", img.size)
