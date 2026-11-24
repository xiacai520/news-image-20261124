#!/usr/bin/env python3
"""news-image-20261124 — one 1024x1024 poster summing up the world news of
24 November 2026 in six stories.

Pure Python standard library only. Ships its own PNG encoder (zlib + struct)
and its own hand-drawn 5x7 bitmap font. No third-party packages, no network.
Deterministic: identical bytes on every run.

Run:  python3 main.py        -> writes /output/entry.png
"""

import os
import struct
import zlib

# --------------------------------------------------------------------------
# Canvas
# --------------------------------------------------------------------------

W, H = 1024, 1024

# Palette (my own scheme: ink navy, paper white, six story accents)
INK      = (13, 20, 34)      # deep navy background
PANEL    = (24, 34, 54)      # panel fill
PANEL_LN = (52, 66, 96)      # panel outline
PAPER    = (238, 240, 244)   # main text
MUTED    = (148, 163, 184)   # secondary text
FAINT    = (94, 108, 132)    # source lines
AMBER    = (245, 158, 11)
TEAL     = (45, 212, 191)
RULE     = (45, 212, 191)

ACCENTS = [
    (245, 158, 11),   # 01 amber   - Riyadh
    (239, 68, 68),    # 02 red     - Gaza
    (96, 165, 250),   # 03 blue    - Zaporizhzhia
    (45, 212, 191),   # 04 teal    - Landmines
    (167, 139, 250),  # 05 violet  - Iran rial
    (74, 222, 128),   # 06 green   - Nvidia
]

buf = bytearray(W * H * 3)


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = color


def fill_rect(x, y, w, h, color):
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + w, W), min(y + h, H)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i], buf[i + 1], buf[i + 2] = color


def fill_bg(color):
    for i in range(0, len(buf), 3):
        buf[i], buf[i + 1], buf[i + 2] = color


# --------------------------------------------------------------------------
# Bitmap font — 5x7, drawn by hand for this poster.
# Each glyph is 7 rows of 5 characters ('#' = ink, '.' = empty).
# --------------------------------------------------------------------------

FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': ("..#..", "..#..", ".###.", "..#..", "..#..", "..#..", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    '[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    ']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
}

CHAR_W, CHAR_H = 5, 7
ADVANCE = 6  # glyph advance in font units (5 px glyph + 1 px gap)


def text_width(text, scale):
    return len(text) * ADVANCE * scale - scale


def draw_text(x, y, text, scale, color):
    """Draw text at (x, y); top-left origin. Unknown chars render as space."""
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[' '])
        for r in range(CHAR_H):
            row = glyph[r]
            for c in range(CHAR_W):
                if row[c] == '#':
                    fill_rect(cx + c * scale, y + r * scale, scale, scale, color)
        cx += ADVANCE * scale
    return cx


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width px."""
    unit = ADVANCE * scale
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if len(trial) * unit - scale <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------------------
# PNG encoder — filter 0, zlib level 9, no ancillary chunks (deterministic)
# --------------------------------------------------------------------------

def chunk(ctype, data):
    body = ctype + data
    return struct.pack(">I", len(data)) + body + struct.pack(
        ">I", zlib.crc32(body) & 0xFFFFFFFF)


def encode_png(rgb, w, h):
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", idat) + chunk(b"IEND", b""))


# --------------------------------------------------------------------------
# Content — six verified stories from 24 November 2026
# --------------------------------------------------------------------------

STORIES = [
    {
        "tag": "MIDDLE EAST",
        "title": "Riyadh tower hit again as Houthis blamed",
        "body": ("A projectile hit the PIF Tower in Riyadh's financial "
                 "district, injuring 11. It was the second strike "
                 "on the tower in under a week."),
        "source": "Reuters / AFP",
    },
    {
        "tag": "GAZA",
        "title": "Hamas security chief killed in Gaza strike",
        "body": ("Israeli strikes killed Hamas security chief Naeem Abu "
                 "Nahel and six others in Gaza City, despite a ceasefire "
                 "in place since last year."),
        "source": "AP / AFP",
    },
    {
        "tag": "UKRAINE",
        "title": "Russian strike on Zaporizhzhia kills two",
        "body": ("An overnight Russian attack hit an apartment block in "
                 "Zaporizhzhia, killing two and wounding 40, including "
                 "four children, officials said."),
        "source": "AP",
    },
    {
        "tag": "HUMANITARIAN",
        "title": "Landmine toll hits five-year high",
        "body": ("Mines and leftover ordnance killed or injured 6,929 "
                 "people in 2025, the highest toll since 2020. Civilians "
                 "were 84% of victims."),
        "source": "ICBL / Al Jazeera",
    },
    {
        "tag": "IRAN",
        "title": "Rial hits record low after US sanctions",
        "body": ("The rial fell to a record 2.82m per dollar after the US "
                 "sanctioned 22 firms and eight people in Tehran's "
                 "'shadow banking' network."),
        "source": "Al Arabiya / Gulf Times",
    },
    {
        "tag": "TECH",
        "title": "Nvidia chief apologises, says he is in therapy",
        "body": ("Jensen Huang told staff he made 'some terrible mistakes', "
                 "a day after returning as Nvidia CEO, 11 days after "
                 "resigning."),
        "source": "CNN / WSJ",
    },
]


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------

MARGIN = 36
HEADER_H = 168
FOOTER_H = 58
GAP = 22
PANEL_W = (W - 2 * MARGIN - GAP) // 2
PANEL_H = (H - HEADER_H - FOOTER_H - 2 * GAP) // 3
SPINE = 8
PAD = 20


def draw_header():
    draw_text(MARGIN, 28, "TUESDAY  -  24 NOVEMBER 2026", 2, AMBER)
    draw_text(MARGIN, 56, "THE WORLD IN", 5, PAPER)
    draw_text(MARGIN, 94, "ONE IMAGE", 5, PAPER)
    # teal rule under the header
    fill_rect(MARGIN, HEADER_H - 14, W - 2 * MARGIN, 4, RULE)
    draw_text(MARGIN, HEADER_H - 34, "Six stories that defined the day", 2, MUTED)


def draw_panel(idx, story, x, y):
    accent = ACCENTS[idx]
    fill_rect(x, y, PANEL_W, PANEL_H, PANEL)
    # outline
    fill_rect(x, y, PANEL_W, 2, PANEL_LN)
    fill_rect(x, y + PANEL_H - 2, PANEL_W, 2, PANEL_LN)
    fill_rect(x, y, 2, PANEL_H, PANEL_LN)
    fill_rect(x + PANEL_W - 2, y, 2, PANEL_H, PANEL_LN)
    # colour spine
    fill_rect(x, y, SPINE, PANEL_H, accent)
    # ghost number, top right
    num = "%02d" % (idx + 1)
    draw_text(x + PANEL_W - PAD - text_width(num, 4), y + 14, num, 4, (44, 54, 78))
    # tag
    tx = x + SPINE + PAD
    draw_text(tx, y + 18, story["tag"], 2, accent)
    # title (up to 2 lines, scale 2)
    ty = y + 44
    title_lines = wrap_text(story["title"], PANEL_W - SPINE - 2 * PAD, 2)[:2]
    for line in title_lines:
        draw_text(tx, ty, line, 2, PAPER)
        ty += 22
    # body (up to 5 lines, scale 2, tighter leading)
    by = ty + 10
    body_lines = wrap_text(story["body"], PANEL_W - SPINE - 2 * PAD, 2)[:5]
    for line in body_lines:
        draw_text(tx, by, line, 2, MUTED)
        by += 19
    # source, pinned near the bottom
    draw_text(tx, y + PANEL_H - 26, "Source: " + story["source"], 2, FAINT)


def draw_footer():
    fy = H - FOOTER_H + 8
    draw_text(MARGIN, fy,
              "Sources: Reuters | AP | AFP | CNN | WSJ | ICBL | Al Jazeera",
              2, FAINT)
    draw_text(MARGIN, fy + 24,
              "Built with pure Python (stdlib only)  -  deterministic render",
              2, FAINT)


def main():
    fill_bg(INK)
    draw_header()
    for i, story in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = MARGIN + col * (PANEL_W + GAP)
        y = HEADER_H + row * (PANEL_H + GAP)
        draw_panel(i, story, x, y)
    draw_footer()
    out = "/output/entry.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(encode_png(buf, W, H))
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
