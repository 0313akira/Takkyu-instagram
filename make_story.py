"""卓球部のインスタストーリー画像（1080x1920）をオーダー表のテキストから作る。

使い方:
    python make_story.py order.txt                  # story.png ができる
    python make_story.py order.txt -b logo.png -o out.png

order.txt の書き方:
    - 空行で区切ったまとまりが、黒い角丸の枠 1 つになる
    - 「#」で始まる行は無視
    - 「○」「〇」「●」は赤い丸（勝ち）、「×」「✕」は青いバツ（負け）として描く
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",  # Mac
    "C:/Windows/Fonts/meiryob.ttc",  # Windows
    "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
]
WIN_MARKS = "○〇●"
LOSE_MARKS = "×✕"


def find_font(path=None):
    for p in ([path] if path else []) + FONT_CANDIDATES:
        if p and Path(p).exists():
            return p
    sys.exit("日本語フォントが見つかりません。--font でフォントファイルを指定してください。")


def read_blocks(text):
    blocks, cur = [], []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("#"):
            continue
        if not line:
            if cur:
                blocks.append(cur)
                cur = []
            continue
        cur.append(line)
    if cur:
        blocks.append(cur)
    return blocks


def make_background(bg_path):
    base = Image.new("RGB", (W, H), (236, 236, 236))
    # 上が明るく下が少し暗いグラデーション
    d = ImageDraw.Draw(base)
    for y in range(H):
        v = int(244 - 22 * y / H)
        d.line([(0, y), (W, y)], fill=(v, v, v))
    if bg_path:
        logo = Image.open(bg_path).convert("RGBA")
        # 画面幅の 90% に収めて中央に薄く置く
        scale = min(W * 0.9 / logo.width, H * 0.6 / logo.height)
        logo = logo.resize((int(logo.width * scale), int(logo.height * scale)), Image.LANCZOS)
        logo = logo.filter(ImageFilter.GaussianBlur(1))
        alpha = logo.getchannel("A").point(lambda a: int(a * 0.35))
        logo.putalpha(alpha)
        base = base.convert("RGBA")
        base.alpha_composite(logo, ((W - logo.width) // 2, (H - logo.height) // 2))
        base = base.convert("RGB")
    return base


def text_width(font, line):
    return sum(font.getlength(ch) for ch in line)


def draw_line(draw, font, line, x, y, size):
    """1 行を描く。勝敗マークだけ色付きの図形にする。"""
    ascent, _ = font.getmetrics()
    for ch in line:
        w = font.getlength(ch)
        if ch in WIN_MARKS:
            r = size * 0.42
            cx, cy = x + w / 2, y + ascent * 0.62
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(230, 0, 18), width=max(4, size // 9))
        elif ch in LOSE_MARKS:
            r = size * 0.36
            cx, cy = x + w / 2, y + ascent * 0.62
            lw = max(4, size // 9)
            draw.line([cx - r, cy - r, cx + r, cy + r], fill=(30, 90, 230), width=lw)
            draw.line([cx - r, cy + r, cx + r, cy - r], fill=(30, 90, 230), width=lw)
        else:
            draw.text((x, y), ch, font=font, fill="white",
                      stroke_width=max(1, size // 40), stroke_fill="white")
        x += w


def render(blocks, font_path, bg_path=None, size=None):
    img = make_background(bg_path)
    draw = ImageDraw.Draw(img)
    max_text_w = W - 2 * 60 - 2 * 40  # 画面余白 60 + 枠の内側余白 40

    # 一番長い行が画面に収まり、全体の高さも収まる文字サイズを探す
    lines_total = sum(len(b) for b in blocks)
    size = size or 96
    while size > 30:
        font = ImageFont.truetype(font_path, size)
        widest = max(text_width(font, l) for b in blocks for l in b)
        total_h = lines_total * size * 1.22 + (len(blocks) - 1) * size * 0.9
        if widest <= max_text_w and total_h <= H * 0.72:
            break
        size -= 2
    font = ImageFont.truetype(font_path, size)

    line_h = int(size * 1.22)
    gap = int(size * 0.9)
    pad_x, pad_y = int(size * 0.35), int(size * 0.18)
    radius = int(size * 0.28)
    total_h = lines_total * line_h + (len(blocks) - 1) * gap
    y = (H - total_h) // 2

    for block in blocks:
        # 行ごとに幅の違う箱をつなげて、写真のような「段々」の枠にする
        for i, line in enumerate(block):
            tw = text_width(font, line)
            x0 = (W - tw) / 2 - pad_x
            x1 = (W + tw) / 2 + pad_x
            ly = y + i * line_h
            top = ly - (pad_y if i == 0 else 0)
            bottom = ly + line_h + (pad_y if i == len(block) - 1 else 0)
            draw.rounded_rectangle([x0, top, x1, bottom], radius=radius, fill="black")
        for line in block:
            tw = text_width(font, line)
            ascent, descent = font.getmetrics()
            ty = y + (line_h - (ascent + descent)) / 2
            draw_line(draw, font, line, (W - tw) / 2, ty, size)
            y += line_h
        y += gap
    return img


def main():
    ap = argparse.ArgumentParser(description="オーダー表からインスタストーリー画像を作る")
    ap.add_argument("order", help="オーダー表のテキストファイル")
    ap.add_argument("-o", "--output", default="story.png")
    ap.add_argument("-b", "--background", help="背景に薄く入れる画像。省略すると北陸大学のロゴ、none でロゴなし")
    ap.add_argument("--font", help="使うフォントファイル")
    ap.add_argument("--size", type=int, help="文字サイズ（省略すると自動）")
    args = ap.parse_args()

    blocks = read_blocks(Path(args.order).read_text(encoding="utf-8"))
    if not blocks:
        sys.exit("オーダー表が空です。")
    bg = args.background
    default_logo = Path(__file__).parent / "assets" / "hokuriku_logo.png"
    if bg is None and default_logo.exists():
        bg = str(default_logo)
    elif bg == "none":
        bg = None
    img = render(blocks, find_font(args.font), bg, args.size)
    img.save(args.output)
    print(f"作成しました: {args.output}")


if __name__ == "__main__":
    main()
