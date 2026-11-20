"""Render the 19 November 2026 world-news summary image (1024x1024) for the make.fun entry.

Built with Pillow from the day's reported events (Wikipedia current events, 2026-11-19):
 - First trilateral Xi/Putin/Trump meeting at the APEC summit in Shenzhen (joint declaration: nuclear war, oil, UN reform)
 - Middle East: Iran war / Strait of Hormuz tanker hit and on fire; Israeli strikes on Hezbollah site in Lebanon;
   Houthi missiles damage Riyadh's PIF Tower
 - Business: GTA VI becomes the biggest video-game launch ever ($2.3bn)
 - Asia: Bangladesh garment-factory strikes; Philippines-Chile sign free trade deal
 - Africa: Senegal's president enacts budget by decree (IMF $2.2bn loan)
 - Americas: Bukele files for a third term in El Salvador

The output must match the committed entry.png byte for byte; run twice to confirm it is deterministic.
Run: python make_image.py entry.png
"""
from PIL import Image, ImageDraw, ImageFont
import sys

S = 1024
BG = (12, 17, 28)
PANEL = (22, 30, 46)
PANEL_EDGE = (40, 52, 74)
WHITE = (244, 247, 252)
MUTED = (158, 170, 190)
ACCENT = {
    "diplo": (94, 156, 255),   # blue
    "war": (255, 86, 86),      # red
    "biz": (255, 196, 61),     # gold
    "asia": (61, 214, 160),    # green
    "africa": (255, 148, 64),  # orange
    "americas": (186, 130, 255),  # violet
}

FONT_DIR = "C:/Windows/Fonts/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def fit(draw, text, f, max_w):
    """Shrink a font until the text fits max_w."""
    size = f.size
    while size > 8:
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
        f = font(f.path.split("/")[-1].split("\\")[-1], size)
    return f


def main(out_path):
    img = Image.new("RGB", (S, S), BG)
    d = ImageDraw.Draw(img)

    # ---- header -----------------------------------------------------------------
    d.rectangle([0, 0, S, 8], fill=(94, 156, 255))
    d.text((48, 34), "WORLD NEWS  ·  19 NOVEMBER 2026", font=font("arialbd.ttf", 25),
           fill=ACCENT["diplo"])
    d.text((48, 68), "THE DAY IN SIX STORIES", font=font("impact.ttf", 62), fill=WHITE)
    d.text((48, 142), "A recap of Thursday 19 November 2026 — conflicts, diplomacy, trade and culture",
           font=font("segoeui.ttf", 22), fill=MUTED)
    d.line([48, 182, S - 48, 182], fill=PANEL_EDGE, width=2)

    # ---- panels -----------------------------------------------------------------
    margin, gut, top = 48, 18, 196
    cols, rows = 2, 3
    pw = (S - 2 * margin - (cols - 1) * gut) // cols
    ph = (S - top - 96 - (rows - 1) * gut) // rows

    stories = [
        ("diplo", "TRILLATERAL FIRST", "Xi, Putin & Trump meet in Shenzhen at APEC — a joint declaration on nuclear war, oil and UN reform"),
        ("war", "MIDDLE EAST", "Tanker burns near the Strait of Hormuz; Israel strikes Hezbollah in Lebanon; Houthi missiles hit Riyadh's PIF Tower"),
        ("biz", "BIGGEST LAUNCH EVER", "GTA VI sells over $2.3 billion, the largest video-game launch in history"),
        ("asia", "ASIA-PACIFIC", "Bangladesh garment strikes shut 341 factories; the Philippines and Chile sign a free-trade deal"),
        ("africa", "AFRICA", "Senegal's president enacts the 2026 budget by decree, seeking a $2.2bn IMF loan"),
        ("americas", "AMERICAS", "El Salvador's Bukele files for a third term after term limits were abolished"),
    ]

    for i, (key, head, body) in enumerate(stories):
        r, c = divmod(i, cols)
        x = margin + c * (pw + gut)
        y = top + r * (ph + gut)
        col = ACCENT[key]
        d.rounded_rectangle([x, y, x + pw, y + ph], radius=16, fill=PANEL, outline=PANEL_EDGE, width=2)
        d.rounded_rectangle([x, y, x + 8, y + ph], radius=4, fill=col)

        # icon: a category-coloured disc with a monogram-free pictogram block
        cx, cy, rad = x + 52, y + 52, 26
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=col, width=4)
        draw_pictogram(d, key, x + 26, y + 26, 52, col)

        d.text((x + 96, y + 22), head, font=fit(d, head, font("arialbd.ttf", 27), pw - 118), fill=WHITE)

        body_font = font("segoeui.ttf", 22)
        # wrap body text into the panel below the header
        words, line, lines = body.split(), "", []
        max_w = pw - 44
        for w in words:
            trial = (line + " " + w).strip()
            if d.textlength(trial, font=body_font) <= max_w:
                line = trial
            else:
                lines.append(line)
                line = w
        lines.append(line)
        ty = y + 92
        for ln in lines[:5]:
            d.text((x + 26, ty), ln, font=body_font, fill=(214, 222, 235))
            ty += 29

    # ---- footer -----------------------------------------------------------------
    d.text((48, S - 74), "Sources: wire reports of 19 Nov 2026  ·  make.fun daily news image",
           font=font("segoeui.ttf", 18), fill=(110, 122, 142))

    img.save(out_path, "PNG", optimize=True)


def draw_pictogram(d, key, x, y, size, col):
    """Small deterministic pictogram inside the icon box."""
    cx, cy = x + size // 2, y + size // 2
    if key == "diplo":
        # three chairs / table: a round table with three dots
        d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=col, width=3)
        for dx, dy in ((0, -20), (-18, 12), (18, 12)):
            d.ellipse([cx + dx - 5, cy + dy - 5, cx + dx + 5, cy + dy + 5], fill=col)
    elif key == "war":
        # explosion flare
        d.polygon([(cx, cy - 22), (cx + 8, cy - 6), (cx + 22, cy), (cx + 8, cy + 6),
                   (cx, cy + 22), (cx - 8, cy + 6), (cx - 22, cy), (cx - 8, cy - 6)], fill=col)
    elif key == "biz":
        # rising bar chart
        for i, h in enumerate((10, 18, 28, 38)):
            d.rectangle([cx - 20 + i * 11, cy + 20 - h, cx - 13 + i * 11, cy + 20], fill=col)
    elif key == "asia":
        # globe with meridian
        d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], outline=col, width=3)
        d.ellipse([cx - 9, cy - 20, cx + 9, cy + 20], outline=col, width=2)
        d.line([cx - 20, cy, cx + 20, cy], fill=col, width=2)
    elif key == "africa":
        # Africa silhouette, approximated
        d.polygon([(cx - 12, cy - 20), (cx + 12, cy - 16), (cx + 18, cy - 2), (cx + 8, cy + 4),
                   (cx + 6, cy + 20), (cx - 4, cy + 14), (cx - 10, cy + 2), (cx - 16, cy - 6)], fill=col)
    else:
        # americas: two continents, north and south
        d.ellipse([cx - 16, cy - 20, cx + 4, cy - 2], fill=col)
        d.polygon([(cx + 2, cy - 2), (cx + 14, cy + 2), (cx + 6, cy + 10), (cx + 4, cy + 22),
                   (cx - 4, cy + 14), (cx - 2, cy + 2)], fill=col)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "entry.png")