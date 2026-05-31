#!/usr/bin/env python3
"""
Matrix Green - Material Design Icon Üretici
ME176C TWRP teması için PNG ikonlar üretir
"""

import struct
import zlib
import math
import os

OUTPUT_DIR = "theme/images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Matrix renk paleti
MATRIX_GREEN    = (0x00, 0xff, 0x41, 0xff)   # #00ff41
MATRIX_DIM      = (0x00, 0xcc, 0x33, 0xff)   # #00cc33
MATRIX_DARK     = (0x00, 0x7a, 0x1f, 0xff)   # #007a1f
BG_DARK         = (0x0d, 0x1a, 0x0d, 0xff)   # #0d1a0d
BG_SURFACE      = (0x11, 0x22, 0x11, 0xff)   # #112211
TRANSPARENT     = (0x00, 0x00, 0x00, 0x00)
WHITE           = (0xff, 0xff, 0xff, 0xff)
BLACK           = (0x00, 0x00, 0x00, 0xff)


def write_png(filename, width, height, pixels):
    """pixels: list of (r,g,b,a) tuples, row by row"""
    def pack_chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    raw_rows = []
    for y in range(height):
        row = b'\x00'  # filter type None
        for x in range(width):
            r, g, b, a = pixels[y * width + x]
            row += bytes([r, g, b, a])
        raw_rows.append(row)

    compressed = zlib.compress(b''.join(raw_rows), 9)

    png  = b'\x89PNG\r\n\x1a\n'
    png += pack_chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    png += pack_chunk(b'IDAT', compressed)
    png += pack_chunk(b'IEND', b'')

    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'wb') as f:
        f.write(png)
    print(f"  ✓ {filename} ({width}x{height})")


def new_canvas(w, h, fill=TRANSPARENT):
    return [fill] * (w * h)


def set_pixel(pixels, w, x, y, color):
    if 0 <= x < w and 0 <= y < len(pixels) // w:
        pixels[y * w + x] = color


def draw_rect(pixels, w, x1, y1, x2, y2, color):
    for y in range(y1, y2):
        for x in range(x1, x2):
            set_pixel(pixels, w, x, y, color)


def draw_circle(pixels, w, cx, cy, r, color, fill=True):
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx*dx + dy*dy)
            if fill:
                if dist <= r:
                    set_pixel(pixels, w, x, y, color)
            else:
                if r - 1 <= dist <= r + 1:
                    set_pixel(pixels, w, x, y, color)


def draw_rounded_rect(pixels, w, x1, y1, x2, y2, r, color):
    # Fill center
    draw_rect(pixels, w, x1 + r, y1, x2 - r, y2, color)
    draw_rect(pixels, w, x1, y1 + r, x2, y2 - r, color)
    # Corners
    for cx, cy in [(x1+r, y1+r), (x2-r-1, y1+r), (x1+r, y2-r-1), (x2-r-1, y2-r-1)]:
        draw_circle(pixels, w, cx, cy, r, color)


def draw_line(pixels, w, x1, y1, x2, y2, color, thickness=2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    x, y = x1, y1
    while True:
        for tx in range(-thickness//2, thickness//2 + 1):
            for ty in range(-thickness//2, thickness//2 + 1):
                set_pixel(pixels, w, x + tx, y + ty, color)
        if x == x2 and y == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


# ──────────────────────────────────────────────
# 1) ARKA PLAN (background.png) 800x1280
# ──────────────────────────────────────────────
def make_background():
    W, H = 800, 1280
    pixels = new_canvas(W, H, (0x0a, 0x0f, 0x0a, 0xff))

    import random
    random.seed(42)

    # Matrix dijital yağmur — ince yeşil dikey çizgiler
    for col in range(0, W, 20):
        length = random.randint(30, 200)
        start_y = random.randint(0, H - length)
        alpha = random.randint(15, 50)
        for i, y in enumerate(range(start_y, start_y + length)):
            fade = int(alpha * (1 - i / length))
            if fade > 0:
                set_pixel(pixels, W, col, y, (0x00, 0xff, 0x41, fade))

    # Sağ alt köşe — yumuşak parıltı
    for dy in range(160):
        for dx in range(160):
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 150:
                a = int(22 * (1 - dist / 150))
                px = W - 1 - dx
                py = H - 1 - dy
                if 0 <= px < W and 0 <= py < H:
                    cur = pixels[py * W + px]
                    pixels[py * W + px] = (cur[0], min(0xff, cur[1] + a), cur[2], cur[3])

    write_png("background.png", W, H, pixels)


# ──────────────────────────────────────────────
# 2) HEADER ARKA PLAN (header_bg.png) 800x96
# ──────────────────────────────────────────────
def make_header_bg():
    W, H = 800, 96
    pixels = new_canvas(W, H, (0x0f, 0x1f, 0x0f, 0xff))
    # Alt kenarda ince parlak çizgi
    for x in range(W):
        set_pixel(pixels, W, x, H-2, MATRIX_DARK)
        set_pixel(pixels, W, x, H-1, (0x00, 0x40, 0x10, 0xff))
    write_png("header_bg.png", W, H, pixels)


# ──────────────────────────────────────────────
# 3) BUTON (button.png) 376x160 - yuvarlak köşeli
# ──────────────────────────────────────────────
def make_button():
    W, H = 376, 160
    pixels = new_canvas(W, H)
    draw_rounded_rect(pixels, W, 0, 0, W, H, 16, (0x0d, 0x2b, 0x0d, 0xff))
    # İç hafif gradient (üst daha açık)
    for y in range(20, 60):
        alpha = int(18 * (1 - y / 60))
        for x in range(20, W - 20):
            r, g, b, a = pixels[y * W + x]
            pixels[y * W + x] = (r, min(0xff, g + 10), b, a)
    # Kalın kenarlık (4px)
    for x in range(W):
        for t in range(4):
            set_pixel(pixels, W, x, t, MATRIX_DARK)
            set_pixel(pixels, W, x, H-1-t, MATRIX_DARK)
    for y in range(H):
        for t in range(4):
            set_pixel(pixels, W, t, y, MATRIX_DARK)
            set_pixel(pixels, W, W-1-t, y, MATRIX_DARK)
    write_png("button.png", W, H, pixels)


def make_button_sel():
    W, H = 376, 160
    pixels = new_canvas(W, H)
    draw_rounded_rect(pixels, W, 0, 0, W, H, 16, (0x00, 0x35, 0x0f, 0xe8))
    # Neon kenarlık 5px
    for x in range(W):
        for t in range(5):
            set_pixel(pixels, W, x, t, MATRIX_GREEN)
            set_pixel(pixels, W, x, H-1-t, MATRIX_GREEN)
    for y in range(H):
        for t in range(5):
            set_pixel(pixels, W, t, y, MATRIX_GREEN)
            set_pixel(pixels, W, W-1-t, y, MATRIX_GREEN)
    # İç parıltı
    for x in range(5, W-5):
        for t in range(2):
            r, g, b, a = pixels[(5+t) * W + x]
            pixels[(5+t) * W + x] = (0x00, min(0xff, g+40), 0x10, 0x60)
    write_png("button_sel.png", W, H, pixels)


# ──────────────────────────────────────────────
# 5) YEDEKLE İKONU - SD Kart (icon_file.png) 64x64
# ──────────────────────────────────────────────
def make_icon_file():
    W = H = 64
    pixels = new_canvas(W, H)
    # SD kart gövdesi
    draw_rounded_rect(pixels, W, 13, 10, 51, 54, 4, (0x00, 0x77, 0x1e, 0xff))
    # Sol üst köşe kesik
    for y in range(10, 24):
        for x in range(13, 27):
            if (x - 13) + (y - 10) < 14:
                set_pixel(pixels, W, x, y, TRANSPARENT)
    # Pinler (alt kısım)
    for i, x in enumerate([18, 24, 30, 36, 42]):
        draw_rect(pixels, W, x, 38, x+3, 54, (0x00, 0x44, 0x11, 0xff))
        draw_line(pixels, W, x, 38, x, 53, MATRIX_DIM, 1)
    # Üst etiket alanı
    draw_rect(pixels, W, 17, 14, 47, 34, (0x00, 0x44, 0x11, 0xaa))
    draw_line(pixels, W, 17, 14, 47, 14, MATRIX_DIM, 1)
    draw_line(pixels, W, 17, 34, 47, 34, MATRIX_DIM, 1)
    # "SD" yazısı efekti - iki yatay çizgi
    draw_rect(pixels, W, 20, 19, 44, 22, (0x00, 0xcc, 0x44, 0xcc))
    draw_rect(pixels, W, 20, 26, 36, 29, (0x00, 0xcc, 0x44, 0xcc))
    # Kenarlık
    draw_line(pixels, W, 27, 10, 51, 10, MATRIX_GREEN, 2)
    draw_line(pixels, W, 13, 24, 13, 54, MATRIX_GREEN, 2)
    draw_line(pixels, W, 13, 54, 51, 54, MATRIX_GREEN, 2)
    draw_line(pixels, W, 51, 10, 51, 54, MATRIX_GREEN, 2)
    draw_line(pixels, W, 13, 24, 27, 10, MATRIX_GREEN, 2)
    write_png("icon_file.png", W, H, pixels)


# ──────────────────────────────────────────────
# 6) GERİ YÜKLE İKONU - Klasör (icon_folder.png) 64x64
# ──────────────────────────────────────────────
def make_icon_folder():
    W = H = 64
    pixels = new_canvas(W, H)
    draw_rounded_rect(pixels, W, 10, 20, 56, 55, 4, (0x00, 0x55, 0x16, 0xff))
    draw_rounded_rect(pixels, W, 10, 13, 32, 23, 3, (0x00, 0x77, 0x1e, 0xff))
    draw_rounded_rect(pixels, W, 10, 22, 56, 54, 4, (0x00, 0x88, 0x22, 0xff))
    for x in range(14, 52):
        set_pixel(pixels, W, x, 26, (0x00, 0xcc, 0x44, 0x88))
    draw_line(pixels, W, 10, 13, 32, 13, MATRIX_GREEN, 2)
    draw_line(pixels, W, 10, 13, 10, 54, MATRIX_GREEN, 2)
    draw_line(pixels, W, 10, 54, 56, 54, MATRIX_GREEN, 2)
    draw_line(pixels, W, 56, 20, 56, 54, MATRIX_GREEN, 2)
    draw_line(pixels, W, 32, 13, 38, 20, MATRIX_GREEN, 2)
    draw_line(pixels, W, 38, 20, 56, 20, MATRIX_GREEN, 2)
    write_png("icon_folder.png", W, H, pixels)


# ──────────────────────────────────────────────
# YENİ: YÜKLE İKONU - Dosya + aşağı ok (icon_flash.png) 64x64
# ──────────────────────────────────────────────
def make_icon_flash():
    W = H = 64
    pixels = new_canvas(W, H)
    # Dosya gövdesi
    draw_rounded_rect(pixels, W, 10, 6, 46, 54, 3, (0x00, 0x77, 0x1e, 0xff))
    # Köşe kesik
    draw_rect(pixels, W, 34, 6, 46, 18, TRANSPARENT)
    for y in range(12):
        for x in range(12):
            if x + y < 12:
                set_pixel(pixels, W, 34+x, 6+y, (0x00, 0x44, 0x11, 0xff))
    draw_line(pixels, W, 34, 18, 46, 18, MATRIX_GREEN, 2)
    draw_line(pixels, W, 34, 6,  34, 18, MATRIX_GREEN, 2)
    draw_line(pixels, W, 34, 6,  46, 18, MATRIX_GREEN, 2)
    # Aşağı ok (dosya içinde)
    draw_line(pixels, W, 28, 20, 28, 38, MATRIX_GREEN, 3)
    draw_line(pixels, W, 20, 32, 28, 42, MATRIX_GREEN, 3)
    draw_line(pixels, W, 36, 32, 28, 42, MATRIX_GREEN, 3)
    # Alt yatay çizgi
    draw_rect(pixels, W, 16, 44, 40, 48, MATRIX_GREEN)
    # Dış kenarlık
    draw_line(pixels, W, 10, 6,  34, 6,  MATRIX_GREEN, 2)
    draw_line(pixels, W, 10, 6,  10, 54, MATRIX_GREEN, 2)
    draw_line(pixels, W, 10, 54, 46, 54, MATRIX_GREEN, 2)
    draw_line(pixels, W, 46, 18, 46, 54, MATRIX_GREEN, 2)
    # Sağda ok işareti
    draw_line(pixels, W, 50, 28, 58, 36, MATRIX_GREEN, 2)
    draw_line(pixels, W, 50, 44, 58, 36, MATRIX_GREEN, 2)
    write_png("icon_flash.png", W, H, pixels)


# ──────────────────────────────────────────────
# YENİ: SİL İKONU - Çöp kutusu X (icon_wipe.png) 64x64
# ──────────────────────────────────────────────
def make_icon_wipe():
    W = H = 64
    pixels = new_canvas(W, H)
    # Çöp kutusu gövdesi
    draw_rounded_rect(pixels, W, 12, 20, 52, 56, 3, (0x00, 0x77, 0x1e, 0xff))
    # Kapak
    draw_rect(pixels, W, 8, 14, 56, 22, (0x00, 0x88, 0x22, 0xff))
    draw_rounded_rect(pixels, W, 22, 8, 42, 16, 3, (0x00, 0x77, 0x1e, 0xff))
    # X işareti (içinde)
    draw_line(pixels, W, 22, 28, 36, 48, MATRIX_GREEN, 3)
    draw_line(pixels, W, 36, 28, 22, 48, MATRIX_GREEN, 3)
    # Dikey çizgiler
    draw_line(pixels, W, 42, 28, 42, 48, MATRIX_DIM, 2)
    # Kenarlık
    draw_line(pixels, W, 8,  14, 56, 14, MATRIX_GREEN, 2)
    draw_line(pixels, W, 12, 20, 12, 56, MATRIX_GREEN, 2)
    draw_line(pixels, W, 12, 56, 52, 56, MATRIX_GREEN, 2)
    draw_line(pixels, W, 52, 20, 52, 56, MATRIX_GREEN, 2)
    draw_line(pixels, W, 22, 8,  42, 8,  MATRIX_GREEN, 2)
    draw_line(pixels, W, 22, 8,  22, 14, MATRIX_GREEN, 2)
    draw_line(pixels, W, 42, 8,  42, 14, MATRIX_GREEN, 2)
    write_png("icon_wipe.png", W, H, pixels)


# ──────────────────────────────────────────────
# YENİ: AYARLAR İKONU - Dişli (icon_settings.png) 64x64
# ──────────────────────────────────────────────
def make_icon_settings():
    W = H = 64
    pixels = new_canvas(W, H)
    cx, cy, r_out, r_in = 32, 32, 22, 13
    # Dış dişli dişleri (8 adet)
    for i in range(8):
        angle = math.pi * 2 * i / 8
        for da in [-0.22, 0.22]:
            a1, a2 = angle - da, angle + da
            for rr in range(r_out - 2, r_out + 6):
                x = int(cx + rr * math.cos(angle))
                y = int(cy + rr * math.sin(angle))
                if 0 <= x < W and 0 <= y < H:
                    set_pixel(pixels, W, x, y, (0x00, 0x88, 0x22, 0xff))
    # Dış halka
    for angle_deg in range(360):
        a = math.radians(angle_deg)
        for rr in range(r_in + 2, r_out + 1):
            x = int(cx + rr * math.cos(a))
            y = int(cy + rr * math.sin(a))
            set_pixel(pixels, W, x, y, (0x00, 0x88, 0x22, 0xff))
    # Dişler (8 dikdörtgen)
    for i in range(8):
        a = math.pi * 2 * i / 8
        for rr in range(r_out, r_out + 7):
            for da in [-2, -1, 0, 1, 2]:
                x = int(cx + rr * math.cos(a) - da * math.sin(a))
                y = int(cy + rr * math.sin(a) + da * math.cos(a))
                set_pixel(pixels, W, x, y, (0x00, 0x88, 0x22, 0xff))
    # İç delik
    draw_circle(pixels, W, cx, cy, r_in, TRANSPARENT)
    # İç çember kenarlığı
    draw_circle(pixels, W, cx, cy, r_in + 1, MATRIX_GREEN, fill=False)
    draw_circle(pixels, W, cx, cy, r_out + 5, MATRIX_GREEN, fill=False)
    write_png("icon_settings.png", W, H, pixels)


# ──────────────────────────────────────────────
# 7) SD KART İKONU (icon_sdcard.png) 64x64
# ──────────────────────────────────────────────
def make_icon_sdcard():
    W = H = 64
    pixels = new_canvas(W, H)
    # Kart gövdesi (gölge)
    draw_rounded_rect(pixels, W, 14, 11, 51, 54, 4, (0x00, 0x55, 0x16, 0xff))
    # Kart gövdesi
    draw_rounded_rect(pixels, W, 13, 10, 50, 53, 4, (0x00, 0x88, 0x22, 0xff))
    # Sol üst köşe kesik (SD şekli) — üçgen sil
    for y in range(10, 24):
        for x in range(13, 27):
            if (x - 13) + (y - 10) < 14:
                set_pixel(pixels, W, x, y, TRANSPARENT)
    # Kart çentikleri (alt pimler)
    for i, x in enumerate([18, 24, 30, 36, 42]):
        draw_rect(pixels, W, x, 10, x+3, 19, (0x00, 0x44, 0x11, 0xff))
        draw_line(pixels, W, x, 10, x, 18, MATRIX_DIM, 1)
    # Yüzey çizgileri
    draw_rect(pixels, W, 17, 26, 47, 29, (0x00, 0x55, 0x18, 0xff))
    draw_rect(pixels, W, 17, 34, 47, 37, (0x00, 0x55, 0x18, 0xff))
    # Kenarlık
    draw_line(pixels, W, 27, 10, 50, 10, MATRIX_GREEN, 2)
    draw_line(pixels, W, 13, 24, 13, 53, MATRIX_GREEN, 2)
    draw_line(pixels, W, 13, 53, 50, 53, MATRIX_GREEN, 2)
    draw_line(pixels, W, 50, 10, 50, 53, MATRIX_GREEN, 2)
    draw_line(pixels, W, 13, 24, 27, 10, MATRIX_GREEN, 2)
    write_png("icon_sdcard.png", W, H, pixels)


def make_icon_usb():
    W = H = 64
    pixels = new_canvas(W, H)
    # USB sembolü - merkez dikey çizgi
    draw_rect(pixels, W, 30, 10, 34, 50, (0x00, 0x88, 0x22, 0xff))
    # Sol dal
    draw_rect(pixels, W, 16, 24, 30, 27, (0x00, 0x88, 0x22, 0xff))
    draw_circle(pixels, W, 16, 20, 6, (0x00, 0x88, 0x22, 0xff))
    draw_circle(pixels, W, 16, 20, 3, (0x0a, 0x0f, 0x0a, 0xff))
    # Sağ dal
    draw_rect(pixels, W, 34, 32, 48, 35, (0x00, 0x88, 0x22, 0xff))
    draw_rounded_rect(pixels, W, 42, 28, 52, 40, 3, (0x00, 0x88, 0x22, 0xff))
    draw_rounded_rect(pixels, W, 44, 30, 50, 38, 2, (0x0a, 0x0f, 0x0a, 0xff))
    # Alt ok (A tipi konnektör)
    draw_rounded_rect(pixels, W, 24, 46, 40, 56, 3, (0x00, 0x77, 0x1e, 0xff))
    # Kenarlık vurguları
    draw_line(pixels, W, 30, 10, 34, 10, MATRIX_GREEN, 2)
    draw_circle(pixels, W, 16, 20, 6, MATRIX_GREEN, fill=False)
    draw_line(pixels, W, 24, 46, 40, 46, MATRIX_GREEN, 2)
    draw_line(pixels, W, 24, 56, 40, 56, MATRIX_GREEN, 2)
    write_png("icon_usb.png", W, H, pixels)


# ──────────────────────────────────────────────
# 9) İLERLEME ÇUBUĞU (progress_empty / full)
# ──────────────────────────────────────────────
def make_progress():
    W, H = 600, 16
    # Boş
    pixels = new_canvas(W, H, (0x0d, 0x2b, 0x0d, 0xff))
    draw_rounded_rect(pixels, W, 0, 0, W, H, 8, (0x0d, 0x2b, 0x0d, 0xff))
    write_png("progress_empty.png", W, H, pixels)
    # Dolu
    pixels = new_canvas(W, H, TRANSPARENT)
    draw_rounded_rect(pixels, W, 0, 0, W, H, 8, MATRIX_GREEN)
    write_png("progress_full.png", W, H, pixels)


# ──────────────────────────────────────────────
# 10) CHECKBOX (checkbox_true / false) 48x48
# ──────────────────────────────────────────────
def make_checkbox():
    W = H = 48
    # İşaretli
    pixels = new_canvas(W, H)
    draw_rounded_rect(pixels, W, 4, 4, 44, 44, 6, (0x00, 0x88, 0x22, 0xff))
    draw_line(pixels, W, 12, 24, 20, 34, MATRIX_GREEN, 3)
    draw_line(pixels, W, 20, 34, 36, 14, MATRIX_GREEN, 3)
    write_png("checkbox_true.png", W, H, pixels)
    # İşaretsiz
    pixels = new_canvas(W, H)
    for x in range(4, 44):
        for t in range(2):
            set_pixel(pixels, W, x, 4+t, MATRIX_DIM)
            set_pixel(pixels, W, x, 42+t, MATRIX_DIM)
    for y in range(4, 44):
        for t in range(2):
            set_pixel(pixels, W, 4+t, y, MATRIX_DIM)
            set_pixel(pixels, W, 42+t, y, MATRIX_DIM)
    write_png("checkbox_false.png", W, H, pixels)


# ──────────────────────────────────────────────
# 11) TOGGLE (toggle_true / false) 80x40
# ──────────────────────────────────────────────
def make_toggle():
    W, H = 80, 40
    # Açık
    pixels = new_canvas(W, H)
    draw_rounded_rect(pixels, W, 0, 0, W, H, 20, (0x00, 0x66, 0x1a, 0xff))
    draw_circle(pixels, W, 58, 20, 16, MATRIX_GREEN)
    write_png("toggle_true.png", W, H, pixels)
    # Kapalı
    pixels = new_canvas(W, H)
    draw_rounded_rect(pixels, W, 0, 0, W, H, 20, (0x1a, 0x1a, 0x1a, 0xff))
    draw_circle(pixels, W, 22, 20, 16, (0x55, 0x55, 0x55, 0xff))
    write_png("toggle_false.png", W, H, pixels)


# ──────────────────────────────────────────────
# 12) KAYDIRICI (slider) 600x16
# ──────────────────────────────────────────────
def make_slider():
    W, H = 600, 16
    pixels = new_canvas(W, H, TRANSPARENT)
    draw_rounded_rect(pixels, W, 0, 4, W, 12, 4, MATRIX_DIM)
    write_png("slider_used.png", W, H, pixels)

    pixels = new_canvas(W, H, TRANSPARENT)
    draw_rounded_rect(pixels, W, 0, 4, W, 12, 4, (0x1a, 0x2a, 0x1a, 0xff))
    write_png("slider_unused.png", W, H, pixels)

    # Thumb
    S = 40
    pixels = new_canvas(S, S, TRANSPARENT)
    draw_circle(pixels, S, 20, 20, 18, MATRIX_GREEN)
    draw_circle(pixels, S, 20, 20, 10, (0x0d, 0x1a, 0x0d, 0xff))
    write_png("slider_thumb.png", S, S, pixels)


# ──────────────────────────────────────────────
# 13) KLAVYE TUŞU (key_background) 80x80
# ──────────────────────────────────────────────
def make_key_bg():
    W = H = 80
    pixels = new_canvas(W, H)
    draw_rounded_rect(pixels, W, 2, 2, 78, 78, 8, (0x0d, 0x2b, 0x0d, 0xff))
    for x in range(2, 78):
        for t in range(2):
            set_pixel(pixels, W, x, 2+t, MATRIX_DARK)
            set_pixel(pixels, W, x, 76+t, MATRIX_DARK)
    for y in range(2, 78):
        for t in range(2):
            set_pixel(pixels, W, 2+t, y, MATRIX_DARK)
            set_pixel(pixels, W, 76+t, y, MATRIX_DARK)
    write_png("key_background.png", W, H, pixels)

    pixels = new_canvas(W, H)
    draw_rounded_rect(pixels, W, 2, 2, 78, 78, 8, (0x00, 0x44, 0x11, 0xff))
    for x in range(2, 78):
        for t in range(2):
            set_pixel(pixels, W, x, 2+t, MATRIX_GREEN)
            set_pixel(pixels, W, x, 76+t, MATRIX_GREEN)
    for y in range(2, 78):
        for t in range(2):
            set_pixel(pixels, W, 2+t, y, MATRIX_GREEN)
            set_pixel(pixels, W, 76+t, y, MATRIX_GREEN)
    write_png("key_background_sel.png", W, H, pixels)


# ──────────────────────────────────────────────
# 14) YAN ARKA PLAN (background_side.png) 64x1280
# ──────────────────────────────────────────────
def make_bg_side():
    W, H = 64, 1280
    pixels = new_canvas(W, H, (0x0a, 0x0f, 0x0a, 0xff))
    # Sağ kenarda ince çizgi
    for y in range(H):
        set_pixel(pixels, W, W-1, y, (0x00, 0x22, 0x08, 0xff))
    write_png("background_side.png", W, H, pixels)


# ──────────────────────────────────────────────
# ÇALIŞTIR
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("🟢 Matrix Green ikonlar üretiliyor...\n")
    make_background()
    make_header_bg()
    make_button()
    make_button_sel()
    make_icon_file()      # Yedekle - SD kart
    make_icon_folder()    # Geri Yükle - klasör
    make_icon_flash()     # Yükle - dosya+ok
    make_icon_wipe()      # Sil/Format - çöp kutusu
    make_icon_sdcard()    # SD kart (genel)
    make_icon_usb()       # USB Bağla
    make_icon_settings()  # Ayarlar - dişli
    make_progress()
    make_checkbox()
    make_toggle()
    make_slider()
    make_key_bg()
    make_bg_side()
    print(f"\n✅ Tüm ikonlar '{OUTPUT_DIR}/' klasörüne kaydedildi!")
