"""Перегенерирует иконку лаунчера, сплэш и иконку магазина из www/img/v2/emblem.webp.

Запуск из корня репозитория:  python3 android/make_assets.py   (нужен Pillow). Затем пересобрать приложение.
"""
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "android/app/src/main/res"
BG = (238, 220, 178)  # кремовая рамка badge.png; тот же цвет в values/ic_launcher_background.xml и сплэше
STORE_DIR = ROOT / "publish/rustore/icon"

emblem = Image.open(ROOT / "www/img/v2/emblem.webp").convert("RGBA")
emblem = emblem.crop(emblem.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox())


def fit(im, box_w, box_h):
    s = min(box_w / im.width, box_h / im.height)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


def centered(canvas, im):
    canvas.alpha_composite(im, ((canvas.width - im.width) // 2, (canvas.height - im.height) // 2))
    return canvas


def tile(size, scale, radius_k):
    """Квадрат/скруглённый квадрат/круг цвета BG с эмблемой, 4x суперсэмплинг для гладких краёв."""
    t = Image.new("RGBA", (size * 4,) * 2, BG + (255,))
    centered(t, fit(emblem, size * 4 * scale, size * 4 * scale))
    if radius_k is not None:
        mask = Image.new("L", t.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, t.width - 1, t.height - 1), round(t.width * radius_k), fill=255)
        t.putalpha(ImageChops.multiply(t.getchannel("A"), mask))
    return t.resize((size, size), Image.LANCZOS)


# Адаптивная иконка: холст 108dp, арт в центральных 50% (система обрезает до круга ~66dp).
DPI = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
for name, k in DPI.items():
    d = RES / f"mipmap-{name}"
    fg = round(108 * k)
    centered(Image.new("RGBA", (fg,) * 2), fit(emblem, fg * 0.50, fg * 0.50)).save(d / "ic_launcher_foreground.png")
    size = round(48 * k)
    tile(size, 0.78, 0.22).save(d / "ic_launcher.png")
    tile(size, 0.66, 0.5).save(d / "ic_launcher_round.png")

(RES / "values/ic_launcher_background.xml").write_text(
    '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#%02X%02X%02X</color>\n</resources>\n' % BG
)


def splash(w, h):
    s = Image.new("RGBA", (w, h), BG + (255,))
    return centered(s, fit(emblem, min(w, h) * 0.55, min(w, h) * 0.55)).convert("RGB")


PORT = {"mdpi": (320, 480), "hdpi": (480, 800), "xhdpi": (720, 1280), "xxhdpi": (960, 1600), "xxxhdpi": (1280, 1920)}
for name, (w, h) in PORT.items():
    splash(w, h).save(RES / f"drawable-port-{name}/splash.png")
    splash(h, w).save(RES / f"drawable-land-{name}/splash.png")
splash(480, 320).save(RES / "drawable/splash.png")

# Иконка магазина 512x512 (RuStore: PNG). Эмблема исходно 300px — на 512 слегка мягкая; для чёткой нужен арт побольше.
# publish/rustore/icon ведёт папка публикации, поэтому кладём рядом с Android-ассетами.
tile(512, 0.86, None).convert("RGB").save(ROOT / "android/store-icon-512.png")
