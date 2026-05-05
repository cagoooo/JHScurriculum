"""
Generate favicon.png / favicon.ico / og-image.png for the JHS curriculum review tool.
Uses a CHALKBOARD palette (dark teal-green + chalk white + amber/yellow accents)
to match the visual identity of the NotebookLM-generated Canva teaching deck.
The document badge shows "中" (中學) drawn in chalky strokes — visually distinct
from the elementary 國小 build (which uses a teal/green ✓ checkmark on white card).

Run: python generate_assets.py
"""
import sys, io, math, os
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from PIL import Image, ImageDraw, ImageFont

FONT_REGULAR = "C:/Windows/Fonts/msjh.ttc"
FONT_BOLD    = "C:/Windows/Fonts/msjhbd.ttc"

# ─── Colors (CHALKBOARD palette — matches Canva teaching deck) ──
C_BOARD    = ( 38,  60,  56)   # #263c38 dark chalkboard (deep teal-green)
C_BOARD_D  = ( 22,  38,  36)   # #162624 darker chalkboard for shadows
C_BOARD_L  = ( 56,  82,  76)   # #38524c lighter teal-green for soft regions
C_CHALK    = (245, 245, 240)   # #f5f5f0 off-white chalk (slightly warm,less harsh than pure white)
C_CHALK_D  = (200, 205, 195)   # #c8cdc3 dimmed chalk for secondary text
C_AMBER    = (255, 193,   7)   # #ffc107 yellow chalk (highlight)
C_ORANGE   = (255, 152,   0)   # #ff9800 orange chalk (badge / accent)
C_ORANGE_D = (230, 119,   0)   # #e67700 dark orange (badge stroke)
C_PINK     = (244, 114, 182)   # #f472b6 pink chalk (secondary accent)
C_BLUE     = (100, 181, 246)   # #64b5f6 blue chalk (links/info)
C_WHITE    = (255, 255, 255)


def font(path, size):
    return ImageFont.truetype(path, size)


# ════════════════════════════════════════════════════════════
# 1. FAVICON  (256×256 → saved as PNG; also exported as ICO)
# ════════════════════════════════════════════════════════════
def make_favicon():
    """
    Chalkboard-style favicon: dark teal-green board + chalky doc lines +
    amber/orange '中' badge. Matches Canva teaching deck visual identity.
    """
    SIZE = 256
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Chalkboard background: rounded square in dark teal-green
    margin = 8
    r = 52
    d.rounded_rectangle([margin, margin, SIZE-margin, SIZE-margin],
                        radius=r, fill=C_BOARD)

    # Subtle wooden-frame inner border (slightly lighter chalkboard tone)
    d.rounded_rectangle([margin+6, margin+6, SIZE-margin-6, SIZE-margin-6],
                        radius=r-6, outline=C_BOARD_L, width=2)

    # Document body — chalky off-white card (translucent feel)
    doc_x, doc_y = 56, 44
    doc_w, doc_h = 148, 190
    d.rounded_rectangle([doc_x, doc_y, doc_x+doc_w, doc_y+doc_h],
                        radius=8, fill=C_CHALK)

    # Folded corner — dimmer chalk tone
    fold = 26
    d.polygon([
        (doc_x+doc_w-fold, doc_y),
        (doc_x+doc_w, doc_y+fold),
        (doc_x+doc_w-fold, doc_y+fold),
    ], fill=C_CHALK_D)

    # "Chalk lines" on document — alternating colored chalk widths
    line_styles = [
        (0.78, C_BOARD),    # main heading line (board color)
        (0.55, C_BOARD_L),  # paragraph
        (0.68, C_BOARD_L),
        (0.42, C_AMBER),    # highlighted bullet (yellow chalk)
        (0.58, C_BOARD_L),
    ]
    lx = doc_x + 16
    for i, (width_pct, col) in enumerate(line_styles):
        ly = doc_y + 32 + i * 26
        lw = int(doc_w * 0.78 * width_pct)
        d.rounded_rectangle([lx, ly, lx+lw, ly+9], radius=4, fill=col)

    # Orange "中" badge — bottom right corner, like a chalk-circled stamp
    badge_cx, badge_cy, badge_r = SIZE - 64, SIZE - 64, 48
    # Outer chalk-circle stroke (slightly rough feel via 2-tone)
    d.ellipse([badge_cx-badge_r, badge_cy-badge_r,
               badge_cx+badge_r, badge_cy+badge_r], fill=C_ORANGE)
    # Inner ring for chalk-stroke depth
    d.ellipse([badge_cx-badge_r+5, badge_cy-badge_r+5,
               badge_cx+badge_r-5, badge_cy+badge_r-5],
              outline=C_ORANGE_D, width=3)
    # "中" — bold chalky white, centered
    f_zhong = font(FONT_BOLD, 60)
    d.text((badge_cx, badge_cy + 2), "中",
           font=f_zhong, fill=C_CHALK, anchor="mm")

    img.save("favicon.png")

    # Multi-size ICO
    ico_sizes = [(16,16),(32,32),(48,48),(64,64),(128,128)]
    icons = [img.resize(s, Image.LANCZOS) for s in ico_sizes]
    icons[0].save("favicon.ico", format="ICO",
                  append_images=icons[1:],
                  sizes=ico_sizes)
    print("✅ favicon.png + favicon.ico saved (chalkboard + orange 中 badge)")


# ════════════════════════════════════════════════════════════
# 2. OG IMAGE  (1200×630)
# ════════════════════════════════════════════════════════════
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))


def _composite(base_rgba, overlay_rgba):
    """Alpha-composite overlay onto base, return RGBA result."""
    return Image.alpha_composite(base_rgba, overlay_rgba)


def make_og():
    """
    Chalkboard-style OG image (1200×630): dark teal-green board background,
    white chalk title, amber/orange highlight strokes, hand-drawn feel.
    Matches the Canva teaching deck so social previews look consistent.
    """
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), (*C_BOARD, 255))
    d = ImageDraw.Draw(img)

    # ── Subtle vertical gradient on the board (top brighter, bottom darker) ──
    for y in range(H):
        t = y / H
        color = lerp_color(C_BOARD_L, C_BOARD_D, t * 0.7 + 0.15)
        d.line([(0, y), (W, y)], fill=(*color, 255))

    # ── Add a faint "chalk dust" texture via random soft circles ──
    import random
    random.seed(42)  # deterministic
    dust = Image.new("RGBA", (W, H), (0,0,0,0))
    dod = ImageDraw.Draw(dust)
    for _ in range(120):
        x = random.randint(0, W); y = random.randint(0, H)
        r = random.randint(1, 3)
        a = random.randint(8, 28)
        dod.ellipse([x-r, y-r, x+r, y+r], fill=(*C_CHALK, a))
    img = _composite(img, dust)
    d = ImageDraw.Draw(img)

    # ── Chalk frame (slight rectangle "drawn" border) ──
    frame_inset = 18
    for offset in [0, 2, -1]:  # multi-pass for hand-drawn feel
        d.rectangle([frame_inset+offset, frame_inset+offset,
                     W-frame_inset-offset, H-frame_inset-offset],
                    outline=(*C_CHALK_D, 180), width=1)

    # ── Top-left chalk-pill badge ──
    pill_overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    pod = ImageDraw.Draw(pill_overlay)
    pill_w, pill_h = 360, 44
    pill_x, pill_y = 72, 70
    pod.rounded_rectangle([pill_x, pill_y, pill_x+pill_w, pill_y+pill_h],
                          radius=22, fill=(*C_BOARD_D, 220))
    pod.rounded_rectangle([pill_x, pill_y, pill_x+pill_w, pill_y+pill_h],
                          radius=22, outline=(*C_AMBER, 255), width=2)
    img = _composite(img, pill_overlay)
    d = ImageDraw.Draw(img)
    d.text((pill_x+pill_w//2, pill_y+pill_h//2),
           "桃園市 115 學年度 · 國民中學",
           font=font(FONT_BOLD, 20), fill=(*C_AMBER, 255), anchor="mm")

    # ── Main chalk title (large white) ──
    d.text((72, 165), "課程計畫",
           font=font(FONT_BOLD, 102), fill=(*C_CHALK, 255))
    d.text((72, 275), "AI 審查工具",
           font=font(FONT_BOLD, 102), fill=(*C_CHALK, 255))

    # Yellow chalk underline strokes (3 hand-drawn passes for organic feel)
    underline_overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    uo = ImageDraw.Draw(underline_overlay)
    for off in [(0, 0, 5), (1, 1, 4), (-1, -1, 3)]:
        dx, dy, w = off
        uo.line([(72+dx, 392+dy), (640+dx, 388+dy)],
                fill=(*C_AMBER, 230), width=w)
    img = _composite(img, underline_overlay)
    d = ImageDraw.Draw(img)

    # ── Subtitle (chalky white, slightly dimmer) ──
    d.text((72, 412),
           "上傳 7-9 年級課程計畫 PDF，依國中審查標準自動審查各項次",
           font=font(FONT_REGULAR, 22), fill=(*C_CHALK_D, 255))

    # ── Feature chips (chalk-circled labels) ──
    chips = ["40+ 國中審查項次", "第四學習階段 Ⅳ", "Gemini AI 驅動", "可彈性編輯提示詞"]
    chip_colors = [C_AMBER, C_ORANGE, C_BLUE, C_PINK]
    fw = font(FONT_BOLD, 18)
    chip_overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    cod = ImageDraw.Draw(chip_overlay)
    chip_positions = []
    cx = 72
    for chip, col in zip(chips, chip_colors):
        tw = d.textlength(chip, font=fw)
        pw = int(tw) + 32
        # Filled board-dark base + colored chalk border
        cod.rounded_rectangle([cx, 472, cx+pw, 514], radius=21,
                              fill=(*C_BOARD_D, 230))
        cod.rounded_rectangle([cx, 472, cx+pw, 514], radius=21,
                              outline=(*col, 255), width=2)
        chip_positions.append((cx, pw, chip, col))
        cx += pw + 14
    img = _composite(img, chip_overlay)
    d = ImageDraw.Draw(img)
    for cx, pw, chip, col in chip_positions:
        d.text((cx+pw//2, 493), chip, font=fw, fill=(*col, 255), anchor="mm")

    # ── Right-side: chalk-drawn "doc with 中 badge" illustration ──
    # Chalk doc outline (no fill, just chalk strokes)
    doc_x, doc_y, doc_w, doc_h = 850, 130, 250, 320
    # Chalky paper card - off-white fill
    d.rounded_rectangle([doc_x, doc_y, doc_x+doc_w, doc_y+doc_h],
                        radius=14, fill=(*C_CHALK, 240))
    # Folded corner
    fold = 30
    d.polygon([
        (doc_x+doc_w-fold, doc_y),
        (doc_x+doc_w, doc_y+fold),
        (doc_x+doc_w-fold, doc_y+fold),
    ], fill=(*C_CHALK_D, 240))

    # Doc title bar (board green)
    d.rounded_rectangle([doc_x, doc_y, doc_x+doc_w, doc_y+50],
                        radius=14, fill=(*C_BOARD, 255))
    d.rectangle([doc_x, doc_y+34, doc_x+doc_w, doc_y+50], fill=(*C_BOARD, 255))
    d.text((doc_x+doc_w//2, doc_y+25), "國中課程計畫審查",
           font=font(FONT_BOLD, 19), fill=(*C_AMBER, 255), anchor="mm")

    # Doc content lines (mixed colors like chalk highlights)
    line_styles = [
        (0.78, C_BOARD),
        (0.62, C_BOARD_L),
        (0.70, C_BOARD_L),
        (0.45, C_ORANGE),  # highlighted
        (0.66, C_BOARD_L),
        (0.50, C_BOARD_L),
    ]
    lx = doc_x + 22
    for i, (w_pct, col) in enumerate(line_styles):
        ly = doc_y + 80 + i * 32
        lw = int(doc_w * 0.82 * w_pct)
        d.rounded_rectangle([lx, ly, lx+lw, ly+11], radius=5, fill=(*col, 255))

    # AI 審查 sub-badge (left of card)
    d.rounded_rectangle([doc_x+18, doc_y+doc_h-72,
                         doc_x+92, doc_y+doc_h-46],
                        radius=11, fill=(*C_BLUE, 255))
    d.text((doc_x+55, doc_y+doc_h-59), "AI 審查",
           font=font(FONT_BOLD, 16), fill=(*C_WHITE, 255), anchor="mm")

    # Orange "中" badge — chalky stamp in bottom-right of card
    bx, by, br = doc_x+doc_w-44, doc_y+doc_h-44, 36
    d.ellipse([bx-br, by-br, bx+br, by+br], fill=(*C_ORANGE, 255))
    d.ellipse([bx-br+3, by-br+3, bx+br-3, by+br-3],
              outline=(*C_ORANGE_D, 255), width=2)
    d.text((bx, by+1), "中", font=font(FONT_BOLD, 40),
           fill=(*C_CHALK, 255), anchor="mm")

    # Hand-drawn arrow + sparkle around the doc (chalk decoration)
    sparkle_overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    so = ImageDraw.Draw(sparkle_overlay)
    # Sparkle stars (★) above doc
    for x, y, sz in [(820, 145, 16), (1110, 280, 14), (810, 380, 12)]:
        # 4-point sparkle drawn as 2 thin rectangles
        so.line([(x-sz, y), (x+sz, y)], fill=(*C_AMBER, 220), width=3)
        so.line([(x, y-sz), (x, y+sz)], fill=(*C_AMBER, 220), width=3)
    img = _composite(img, sparkle_overlay)
    d = ImageDraw.Draw(img)

    # ── Bottom: URL (left) + credit (right) ──
    d.text((72, 578), "cagoooo.github.io/JHScurriculum",
           font=font(FONT_REGULAR, 20), fill=(*C_CHALK_D, 255))
    d.text((W-60, 578), "阿凱老師製作",
           font=font(FONT_REGULAR, 20), fill=(*C_CHALK_D, 255), anchor="ra")

    # Flatten to RGB
    final = Image.new("RGB", (W, H), C_BOARD)
    final.paste(img, (0, 0), img)
    final.save("og-image.png", format="PNG", optimize=True)
    print("✅ og-image.png saved (1200×630, chalkboard theme matching Canva deck)")


# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    make_favicon()
    make_og()
    print("🎉 All JHS assets generated!")
