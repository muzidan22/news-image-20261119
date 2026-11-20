"""Poster: 19 November 2026, world news, one image.

A standalone Python 3 renderer. It composes a 1024x1024 poster of the day's
news and writes it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR). Everything is
drawn from scratch: a compact 5x7 glyph table for capitals and digits, pixel
rectangles, rings and discs, and a small PNG encoder. No third-party modules,
no network, no external fonts. Two runs produce identical bytes because every
coordinate, colour and iteration is fixed.

The six reported stories of Thursday, 19 November 2026:
  * leaders of China, Russia and the USA meet in Shenzhen at APEC, first time
    in one trilateral, and issue a joint declaration;
  * the Middle East: a tanker burns near Hormuz, strikes hit Lebanon, missiles
    reach Riyadh;
  * GTA VI sets a record with $2.3 billion of sales;
  * Bangladesh garment workers strike, and Chile and the Philippines sign a
    free-trade pact;
  * Senegal's president decrees the budget after parliament rejects it;
  * El Salvador's Bukele registers for a third presidential run.
"""

import os
import struct
import zlib

W = H = 1024

INK = (12, 17, 28)
CARD = (22, 30, 46)
EDGE = (40, 52, 74)
BRIGHT = (244, 247, 252)
DIM = (158, 170, 190)
PROSE = (214, 222, 235)
CREDIT = (110, 122, 142)
HUES = [
    (94, 156, 255),
    (255, 86, 86),
    (255, 196, 61),
    (61, 214, 160),
    (255, 148, 64),
    (186, 130, 255),
]

CARDS = [
    ("TRILLATERAL FIRST", "diplo",
     "Xi, Putin and Trump meet in Shenzhen at APEC; a joint declaration on nuclear war, oil and UN reform"),
    ("MIDDLE EAST", "war",
     "A tanker burns near the Strait of Hormuz; Israel strikes Hezbollah in Lebanon; Houthi missiles hit Riyadh's PIF Tower"),
    ("BIGGEST LAUNCH EVER", "biz",
     "GTA VI sells over $2.3 billion, the largest video-game launch in history"),
    ("ASIA-PACIFIC", "asia",
     "Bangladesh garment strikes shut 341 factories; the Philippines and Chile sign a free-trade deal"),
    ("AFRICA", "africa",
     "Senegal's president enacts the 2026 budget by decree, seeking a $2.2bn IMF loan"),
    ("AMERICAS", "americas",
     "El Salvador's Bukele files for a third term after term limits were abolished"),
]

# Capitals, digits and the few marks the poster needs, as seven rows of five.
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000",) * 7,
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
}


def rect(pix, x, y, w, h, rgb):
    """Paint a solid rectangle into the RGB byte buffer, clipped to the canvas."""
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    band = bytes(rgb) * (x1 - x0)
    for row in range(y0, y1):
        base = (row * W + x0) * 3
        pix[base:base + (x1 - x0) * 3] = band


def span(text, scale):
    """Width in pixels of a string drawn at the given scale."""
    return len(text) * 6 * scale - scale


def label(pix, x, y, text, scale, rgb):
    """Render capitals at (x, y); return the x just past the last glyph."""
    for glyph in text.upper():
        cells = GLYPHS.get(glyph, GLYPHS["?"])
        for dy, bits in enumerate(cells):
            for dx, on in enumerate(bits):
                if on == "1":
                    rect(pix, x + dx * scale, y + dy * scale, scale, scale, rgb)
        x += 6 * scale
    return x


def ring(pix, cx, cy, outer, thickness, rgb):
    """A circle outline of the given outer radius."""
    lo, hi = outer - thickness, outer
    for dy in range(-hi, hi + 1):
        for dx in range(-hi, hi + 1):
            d2 = dx * dx + dy * dy
            if lo * lo <= d2 <= hi * hi:
                rect(pix, cx + dx, cy + dy, 1, 1, rgb)


def disc(pix, cx, cy, radius, rgb):
    """A filled circle."""
    for dy in range(-radius, radius + 1):
        half = int((radius * radius - dy * dy) ** 0.5)
        rect(pix, cx - half, cy + dy, half * 2 + 1, 1, rgb)


def icon(pix, kind, cx, cy, rgb):
    """The category pictogram for a card."""
    if kind == "diplo":
        ring(pix, cx, cy, 18, 3, rgb)
        for dx, dy in ((0, -26), (-23, 16), (23, 16)):
            disc(pix, cx + dx, cy + dy, 6, rgb)
    elif kind == "war":
        disc(pix, cx, cy, 9, rgb)
        for dx, dy in ((15, -11), (-15, -11), (11, 13), (-11, 13)):
            disc(pix, cx + dx, cy + dy, 7, rgb)
    elif kind == "biz":
        for i, height in enumerate((14, 24, 34, 44)):
            rect(pix, cx - 24 + i * 14, cy + 22 - height, 9, height, rgb)
    elif kind == "asia":
        ring(pix, cx, cy, 22, 3, rgb)
        ring(pix, cx, cy, 8, 2, rgb)
        rect(pix, cx - 22, cy - 1, 44, 3, rgb)
    elif kind == "africa":
        disc(pix, cx - 4, cy - 12, 14, rgb)
        disc(pix, cx + 6, cy + 10, 13, rgb)
        disc(pix, cx - 10, cy + 14, 9, rgb)
    else:
        disc(pix, cx - 8, cy - 14, 13, rgb)
        disc(pix, cx + 6, cy + 12, 15, rgb)
        ring(pix, cx + 14, cy - 18, 5, 2, rgb)


def wrap(text, scale, limit):
    """Break a sentence into lines that fit the pixel width."""
    lines, current = [], ""
    for word in text.split(" "):
        trial = (current + " " + word).strip()
        if span(trial, scale) <= limit:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def paint_card(pix, x, y, w, h, idx):
    """One story card: hue rail, pictogram, headline, body copy."""
    hue = HUES[idx]
    rect(pix, x, y, w, h, CARD)
    rect(pix, x, y, 8, h, hue)
    rect(pix, x, y, w, 2, EDGE)
    rect(pix, x, y + h - 2, w, 2, EDGE)
    rect(pix, x + w - 2, y, 2, h, EDGE)
    icon(pix, CARDS[idx][1], x + 54, y + 54, hue)
    label(pix, x + 104, y + 34, CARDS[idx][0], 3, BRIGHT)
    heading = y + 104
    for line in wrap(CARDS[idx][2], 2, w - 52)[:5]:
        label(pix, x + 26, heading, line, 2, PROSE)
        heading += 26


def compose(pix):
    """The poster: masthead, a two-column stack of six cards, and a credit."""
    rect(pix, 0, 0, W, H, INK)
    rect(pix, 0, 0, W, 8, HUES[0])
    label(pix, 48, 30, "WORLD NEWS - 19 NOVEMBER 2026", 3, HUES[0])
    label(pix, 46, 62, "THE DAY IN", 9, BRIGHT)
    label(pix, 46, 130, "SIX STORIES", 9, BRIGHT)
    rect(pix, 48, 202, W - 96, 2, EDGE)
    left, gap, top = 48, 18, 218
    card_w = (W - 2 * left - gap) // 2
    card_h = (H - top - 74 - 2 * gap) // 3
    for idx in range(6):
        col, row = idx % 2, idx // 2
        paint_card(pix, left + col * (card_w + gap), top + row * (card_h + gap), card_w, card_h, idx)
    label(pix, 48, H - 40, "SOURCES: WIRE REPORTS OF 19 NOVEMBER 2026", 2, CREDIT)


def png(pix):
    """Wrap the pixel buffer in a PNG: IHDR, one IDAT, IEND, filter 0 rows."""
    scanlines = bytearray()
    for row in range(H):
        scanlines.append(0)
        scanlines += pix[row * W * 3:(row + 1) * W * 3]

    def block(tag, payload):
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    body = zlib.compress(bytes(scanlines), 9)
    return b"\x89PNG\r\n\x1a\n" + block(b"IHDR", header) + block(b"IDAT", body) + block(b"IEND", b"")


def run():
    pix = bytearray(W * H * 3)
    compose(pix)
    data = png(pix)
    place = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(place, exist_ok=True)
    with open(os.path.join(place, "entry.png"), "wb") as handle:
        handle.write(data)
    print("entry.png: %d bytes" % len(data))


if __name__ == "__main__":
    run()