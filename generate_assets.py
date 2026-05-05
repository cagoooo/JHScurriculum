"""
Generate favicon.png / favicon.ico / og-image.png for the JHS curriculum review tool.
Uses an indigo/blue palette to visually distinguish the 國中 build from the
國小 (teal/green) build, and the document badge shows "中" (中學) instead of
the elementary version's checkmark-only motif.

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

# ─── Colors (Indigo / Blue palette for JHS) ───────────────
C_DARK    = (30,  41, 100)   # #1e2964 deep indigo
C_MID     = (49,  68, 168)   # #3144a8 indigo
C_LIGHT   = (96, 118, 220)   # #6076dc lighter indigo
C_ACCENT  = (245, 158,  11)  # #f59e0b amber (instead of green for JHS)
C_AMBER_D = (217, 119,   6)  # #d97706 amber dark
C_WHITE   = (255, 255, 255)
C_PALE    = (224, 230, 255)  # very pale indigo
C_INK     = ( 30,  27,  75)  # text ink


def font(path, size):
    return ImageFont.truetype(path, size)


# ════════════════════════════════════════════════════════════
# 1. FAVICON  (256×256 → saved as PNG; also exported as ICO)
# ════════════════════════════════════════════════════════════
def make_favicon():
    SIZE = 256
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Rounded square background — solid indigo (matches 國小 version's saturation)
    # 不做 gradient overlay,避免把底色洗淡;靠純色塊與綠色國小版做對比
    margin = 8
    r = 52
    d.rounded_rectangle([margin, margin, SIZE-margin, SIZE-margin],
                        radius=r, fill=C_DARK)  # 用 C_DARK (深靛) 而非 C_MID,對比更明顯

    # Document body (white card)
    doc_x, doc_y = 62, 48
    doc_w, doc_h = 148, 190
    d.rounded_rectangle([doc_x, doc_y, doc_x+doc_w, doc_y+doc_h],
                        radius=10, fill=C_WHITE)

    # Folded corner
    fold = 28
    d.polygon([
        (doc_x+doc_w-fold, doc_y),
        (doc_x+doc_w, doc_y+fold),
        (doc_x+doc_w-fold, doc_y+fold),
    ], fill=C_PALE)

    # Text lines on document
    line_color = C_LIGHT
    lx = doc_x + 18
    for i, width_pct in enumerate([0.72, 0.55, 0.68, 0.45]):
        ly = doc_y + 55 + i * 28
        lw = int(doc_w * 0.75 * width_pct)
        d.rounded_rectangle([lx, ly, lx+lw, ly+10], radius=5, fill=line_color)

    # JHS-distinct badge: amber circle with "中" character (junior-high marker)
    badge_cx, badge_cy, badge_r = SIZE - 68, SIZE - 68, 46
    # Amber base
    d.ellipse([badge_cx-badge_r, badge_cy-badge_r,
               badge_cx+badge_r, badge_cy+badge_r], fill=C_ACCENT)
    # Inner ring for depth
    d.ellipse([badge_cx-badge_r+5, badge_cy-badge_r+5,
               badge_cx+badge_r-5, badge_cy+badge_r-5],
              outline=C_AMBER_D, width=3)
    # "中" character — bold white, centered
    f_zhong = font(FONT_BOLD, 56)
    d.text((badge_cx, badge_cy + 2), "中",
           font=f_zhong, fill=C_WHITE, anchor="mm")

    img.save("favicon.png")

    # Multi-size ICO
    ico_sizes = [(16,16),(32,32),(48,48),(64,64),(128,128)]
    icons = [img.resize(s, Image.LANCZOS) for s in ico_sizes]
    icons[0].save("favicon.ico", format="ICO",
                  append_images=icons[1:],
                  sizes=ico_sizes)
    print("✅ favicon.png + favicon.ico saved (JHS indigo + 中 badge)")


# ════════════════════════════════════════════════════════════
# 2. OG IMAGE  (1200×630)
# ════════════════════════════════════════════════════════════
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))


def _composite(base_rgba, overlay_rgba):
    """Alpha-composite overlay onto base, return RGBA result."""
    return Image.alpha_composite(base_rgba, overlay_rgba)


def make_og():
    W, H = 1200, 630
    # Use full RGBA pipeline so translucent pills/chips render correctly
    img = Image.new("RGBA", (W, H), (*C_DARK, 255))
    d = ImageDraw.Draw(img)

    # ── Indigo gradient background (diagonal) ──────────────
    for x in range(W):
        t = x / W
        color = lerp_color(C_DARK, C_MID, t * 0.65)
        d.line([(x, 0), (x, H)], fill=(*color, 255))

    # ── Decorative circles (cooler indigo glow) ────────────
    for cx, cy, cr, alpha in [
        (1050, 160, 240, 22),
        (1050, 160, 170, 30),
        (120,  530,  90, 18),
        (1100, 540,  55, 24),
        ( 880,  60,  70, 16),
    ]:
        overlay = Image.new("RGBA", (W, H), (0,0,0,0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx-cr, cy-cr, cx+cr, cy+cr],
                   fill=(*C_LIGHT, alpha))
        img = _composite(img, overlay)
    d = ImageDraw.Draw(img)

    # ── Document card (right side) ─────────────────────────
    card_x, card_y, card_w, card_h = 820, 140, 270, 340
    # shadow (multiple layered translucent rects for soft edge)
    shadow = Image.new("RGBA", (W, H), (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    for s in range(12, 0, -1):
        sd.rounded_rectangle(
            [card_x+s, card_y+s, card_x+card_w+s, card_y+card_h+s],
            radius=16, fill=(0,0,0, 10))
    img = _composite(img, shadow)
    d = ImageDraw.Draw(img)

    # card body
    d.rounded_rectangle([card_x, card_y, card_x+card_w, card_y+card_h],
                        radius=16, fill=(255,255,255,255))

    # card header bar (indigo)
    d.rounded_rectangle([card_x, card_y, card_x+card_w, card_y+52],
                        radius=16, fill=(*C_MID,255))
    d.rectangle([card_x, card_y+36, card_x+card_w, card_y+52], fill=(*C_MID,255))

    # header text
    fsmall = font(FONT_BOLD, 20)
    d.text((card_x+card_w//2, card_y+26), "國中課程計畫審查",
           font=fsmall, fill=(*C_WHITE,255), anchor="mm")

    # document lines
    lx = card_x + 22
    for i, (w_pct, _) in enumerate([
        (0.78, 200),(0.60, 170),(0.70, 160),
        (0.50, 140),(0.65, 130),(0.45, 110),
    ]):
        ly = card_y + 80 + i * 32
        lw = int(card_w * 0.82 * w_pct)
        gray = int(220 - (1-w_pct)*60)
        d.rounded_rectangle([lx, ly, lx+lw, ly+12],
                            radius=6, fill=(gray, gray, gray, 255))

    # "中" badge on card (replaces green checkmark — visually identifies JHS)
    bx, by, br = card_x+card_w-50, card_y+card_h-50, 38
    d.ellipse([bx-br, by-br, bx+br, by+br], fill=(*C_ACCENT,255))
    d.ellipse([bx-br+3, by-br+3, bx+br-3, by+br-3],
              outline=(*C_AMBER_D,255), width=2)
    d.text((bx, by+1), "中", font=font(FONT_BOLD, 42),
           fill=(*C_WHITE,255), anchor="mm")

    # AI label badge on card (indigo accent)
    d.rounded_rectangle([card_x+16, card_y+card_h-76,
                         card_x+90, card_y+card_h-52],
                        radius=10, fill=(*C_LIGHT,255))
    d.text((card_x+53, card_y+card_h-64), "AI 審查",
           font=font(FONT_BOLD, 16), fill=(*C_WHITE,255), anchor="mm")

    # ── Left-side text ─────────────────────────────────────
    # Badge pill: 桃園市115學年度 · 國民中學
    # Composite onto RGBA so alpha actually shows through
    pill_overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    pod = ImageDraw.Draw(pill_overlay)
    pill_w, pill_h = 330, 40
    pill_x, pill_y = 72, 70
    pod.rounded_rectangle([pill_x, pill_y, pill_x+pill_w, pill_y+pill_h],
                          radius=20, fill=(255,255,255,55))
    pod.rounded_rectangle([pill_x, pill_y, pill_x+pill_w, pill_y+pill_h],
                          radius=20, outline=(255,255,255,150), width=2)
    img = _composite(img, pill_overlay)
    d = ImageDraw.Draw(img)
    d.text((pill_x+pill_w//2, pill_y+pill_h//2),
           "桃園市 115 學年度 · 國民中學",
           font=font(FONT_BOLD, 18), fill=(*C_WHITE,255), anchor="mm")

    # Main title
    d.text((72, 175), "課程計畫",
           font=font(FONT_BOLD, 100), fill=(*C_WHITE,255))
    d.text((72, 280), "AI 審查工具",
           font=font(FONT_BOLD, 100), fill=(*C_WHITE,255))

    # Amber accent line (replaces 國小's green line)
    d.rounded_rectangle([72, 393, 620, 399], radius=3, fill=(*C_ACCENT,255))

    # Subtitle (JHS-specific wording: 七至九年級)
    d.text((72, 416),
           "上傳 7-9 年級課程計畫 PDF，依國中審查標準自動審查各項次",
           font=font(FONT_REGULAR, 22), fill=(*C_WHITE,255))

    # Feature chips (JHS-specific) — composite alpha pills, then draw text
    chip_overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    cod = ImageDraw.Draw(chip_overlay)
    # NOTE: 不放 emoji,因 msjh.ttc 不含 emoji 字型會變成方框 (tofu)
    chips = ["40+ 國中審查項次", "第四學習階段 Ⅳ", "Gemini AI 驅動", "可彈性編輯提示詞"]
    fw = font(FONT_BOLD, 18)
    chip_positions = []  # store (cx, pw) for the text pass
    cx = 72
    for chip in chips:
        tw = d.textlength(chip, font=fw)
        pw = int(tw) + 36
        cod.rounded_rectangle([cx, 470, cx+pw, 514], radius=22,
                              fill=(255,255,255,55))
        cod.rounded_rectangle([cx, 470, cx+pw, 514], radius=22,
                              outline=(255,255,255,150), width=2)
        chip_positions.append((cx, pw, chip))
        cx += pw + 14
    img = _composite(img, chip_overlay)
    d = ImageDraw.Draw(img)
    for cx, pw, chip in chip_positions:
        d.text((cx+pw//2, 492), chip, font=fw,
               fill=(*C_WHITE,255), anchor="mm")

    # URL bottom left
    d.text((72, 578), "cagoooo.github.io/JHScurriculum",
           font=font(FONT_REGULAR, 20), fill=(*C_WHITE,255))

    # Credit bottom right
    d.text((W-60, 578), "阿凱老師製作",
           font=font(FONT_REGULAR, 20), fill=(*C_WHITE,255), anchor="ra")

    # Flatten to RGB for OG image (PNG with alpha works on FB/LINE but RGB is safer)
    final = Image.new("RGB", (W, H), C_DARK)
    final.paste(img, (0, 0), img)
    final.save("og-image.png", format="PNG", optimize=True)
    print("✅ og-image.png saved (1200×630, JHS indigo theme, properly composited)")


# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    make_favicon()
    make_og()
    print("🎉 All JHS assets generated!")
