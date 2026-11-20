"""
Sum up 19 November 2026's world news in one image.

Draws a 1024x1024 poster with the day's six defining stories and writes it as
/output/entry.png. Standard library only: no network, no fonts installed, so the
whole poster is drawn from primitives with a hand-written 5x7 bitmap font.

The stories, from the day's wire reports:
  1. First trilateral Xi-Putin-Trump meeting in Shenzhen at APEC.
  2. Middle East flashpoints: tanker hit near the Strait of Hormuz, Israeli
     strikes on Hezbollah in Lebanon, Houthi missiles hit Riyadh's PIF Tower.
  3. GTA VI posts the biggest video-game launch in history, over $2.3 billion.
  4. Asia-Pacific: 341 Bangladesh garment factories shut by strikes; the
     Philippines and Chile sign a free-trade agreement.
  5. Africa: Senegal's president enacts the 2026 budget by decree for an IMF loan.
  6. Americas: El Salvador's Bukele files for a third presidential term.

Run twice and the bytes are identical: every colour and coordinate is a constant.

Outside the grader's container MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

SIZE = 1024

BG = (12, 17, 28)
PANEL = (22, 30, 46)
PANEL_EDGE = (40, 52, 74)
WHITE = (244, 247, 252)
MUTED = (158, 170, 190)
BODY = (214, 222, 235)
FOOT = (110, 122, 142)
ACCENTS = [  # blue, red, gold, green, orange, violet
    (94, 156, 255),
    (255, 86, 86),
    (255, 196, 61),
    (61, 214, 160),
    (255, 148, 64),
    (186, 130, 255),
]

STORIES = [
    ("TRILLATERAL FIRST", "diplo",
     "Xi, Putin & Trump meet in Shenzhen at APEC; joint declaration on nuclear war, oil and UN reform"),
    ("MIDDLE EAST", "war",
     "Tanker ablaze near the Strait of Hormuz; Israel strikes Hezbollah in Lebanon; Houthi missiles hit Riyadh's PIF Tower"),
    ("BIGGEST LAUNCH EVER", "biz",
     "GTA VI sells over $2.3 billion, the largest video-game launch in history"),
    ("ASIA-PACIFIC", "asia",
     "Bangladesh garment strikes shut 341 factories; the Philippines and Chile sign a free-trade deal"),
    ("AFRICA", "africa",
     "Senegal's president enacts the 2026 budget by decree, seeking a $2.2bn IMF loan"),
    ("AMERICAS", "americas",
     "El Salvador's Bukele files for a third term after term limits were abolished"),
]


# ---- a tiny 5x7 bitmap font: A-Z, 0-9 and the punctuation the poster uses ----
GLYPHS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000"] * 7,
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    ";": ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
}


def text_width(text, scale):
    """Pixels a text run occupies, one blank column between glyphs."""
    return len(text) * 6 * scale - scale


def draw_text(canvas, x, y, text, scale, colour):
    """Paint text at (x, y) at the given pixel scale; return the end x."""
    for ch in text.upper():
        glyph = GLYPHS.get(ch, GLYPHS["?"])
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "1":
                    fill_block(canvas, x + col * scale, y + row * scale, scale, scale, colour)
        x += 6 * scale
    return x


def fill_block(canvas, x, y, w, h, colour):
    """Set a rectangle of pixels to one colour, clipped to the canvas."""
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(SIZE, x + w), min(SIZE, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    for py in range(y0, y1):
        start = (py * SIZE + x0) * 3
        canvas[start:start + (x1 - x0) * 3] = bytes(colour) * (x1 - x0)


def wrap(text, scale, max_px):
    """Greedy word wrap at the pixel width the text may take."""
    lines, line = [], ""
    for word in text.split(" "):
        trial = (line + " " + word).strip()
        if text_width(trial, scale) <= max_px:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def circle(canvas, cx, cy, radius, colour, thickness=1):
    """Draw a ring: pixels whose distance from the centre is near the radius."""
    r_out, r_in = radius * radius, (radius - thickness) * (radius - thickness)
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if r_in <= d <= r_out:
                fill_block(canvas, x, y, 1, 1, colour)


def disc(canvas, cx, cy, radius, colour):
    """Draw a filled circle."""
    r2 = radius * radius
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                fill_block(canvas, x, y, 1, 1, colour)


def draw_icon(canvas, kind, cx, cy, colour):
    """A category pictogram: simple primitives that read at 300 px across."""
    if kind == "diplo":
        circle(canvas, cx, cy, 18, colour, 3)
        for dx, dy in ((0, -26), (-23, 16), (23, 16)):
            disc(canvas, cx + dx, cy + dy, 6, colour)
    elif kind == "war":
        for i, (dx, dy) in enumerate(((0, 0), (14, -10), (-14, -10), (10, 12), (-10, 12))):
            disc(canvas, cx + dx, cy + dy, 9 - i // 2, colour)
    elif kind == "biz":
        for i, h in enumerate((14, 24, 34, 44)):
            fill_block(canvas, cx - 24 + i * 14, cy + 22 - h, 9, h, colour)
    elif kind == "asia":
        circle(canvas, cx, cy, 22, colour, 3)
        circle(canvas, cx, cy, 8, colour, 2)
        fill_block(canvas, cx - 22, cy - 1, 44, 3, colour)
    elif kind == "africa":
        disc(canvas, cx - 4, cy - 12, 14, colour)
        disc(canvas, cx + 6, cy + 10, 13, colour)
        disc(canvas, cx - 10, cy + 14, 9, colour)
    else:
        disc(canvas, cx - 8, cy - 14, 13, colour)
        disc(canvas, cx + 6, cy + 12, 15, colour)
        circle(canvas, cx + 14, cy - 18, 5, colour, 2)


def header(canvas):
    """Rule, kicker and title across the top of the poster."""
    fill_block(canvas, 0, 0, SIZE, 8, ACCENTS[0])
    draw_text(canvas, 48, 30, "WORLD NEWS - 19 NOVEMBER 2026", 3, ACCENTS[0])
    draw_text(canvas, 46, 62, "THE DAY IN", 9, WHITE)
    draw_text(canvas, 46, 130, "SIX STORIES", 9, WHITE)
    fill_block(canvas, 48, 202, SIZE - 96, 2, PANEL_EDGE)


def footer(canvas):
    """Small provenance line at the bottom edge, so the date is never cropped."""
    draw_text(canvas, 48, SIZE - 40, "SOURCES: WIRE REPORTS OF 19 NOVEMBER 2026", 2, FOOT)


def panel(canvas, x, y, w, h, index):
    """One story card: colour rail, icon, headline and wrapped body."""
    accent = ACCENTS[index]
    fill_block(canvas, x, y, w, h, PANEL)
    fill_block(canvas, x, y, 8, h, accent)
    fill_block(canvas, x, y, w, 2, PANEL_EDGE)
    fill_block(canvas, x, y + h - 2, w, 2, PANEL_EDGE)
    fill_block(canvas, x + w - 2, y, 2, h, PANEL_EDGE)
    kind = STORIES[index][1]
    draw_icon(canvas, kind, x + 54, y + 54, accent)
    head = STORIES[index][0]
    draw_text(canvas, x + 104, y + 34, head, 3, WHITE)
    body_lines = wrap(STORIES[index][2], 2, w - 52)
    ty = y + 104
    for line in body_lines[:5]:
        draw_text(canvas, x + 26, ty, line, 2, BODY)
        ty += 26


def draw(canvas):
    """Lay the whole poster out: header, six cards, footer."""
    fill_block(canvas, 0, 0, SIZE, SIZE, BG)
    header(canvas)
    margin, gut, top = 48, 18, 218
    cols, rows = 2, 3
    pw = (SIZE - 2 * margin - (cols - 1) * gut) // cols
    ph = (SIZE - top - 74 - (rows - 1) * gut) // rows
    for i in range(len(STORIES)):
        r, c = divmod(i, cols)
        panel(canvas, margin + c * (pw + gut), top + r * (ph + gut), pw, ph, i)
    footer(canvas)


def to_png(canvas):
    """Encode an RGB byte buffer as a PNG: one IDAT, filter 0 on every row."""
    raw = bytearray()
    for y in range(SIZE):
        raw.append(0)
        raw += canvas[y * SIZE * 3:(y + 1) * SIZE * 3]

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    canvas = bytearray(SIZE * SIZE * 3)
    draw(canvas)
    png = to_png(canvas)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as handle:
        handle.write(png)
    print("wrote %s (%d bytes)" % (target, len(png)))


if __name__ == "__main__":
    main()