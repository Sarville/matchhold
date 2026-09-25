"""Плитка = плашка + иконка. Использование как модуль: compose(plate_png, icon_png, fill=0.66) -> RGBA 512x512.
Плашка и иконка уже с альфой (out/tiles/keyed). Иконка обрезается по bbox, вписывается в fill от стороны плашки,
центрируется чуть выше центра (2%), под ней лёгкая тень вниз-вправо."""
import numpy as np
from PIL import Image, ImageFilter

def trim(im):
    b = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    return im.crop(b)

def compose(plate, icon, fill=0.66, shadow=0.28, glow=None):
    plate = Image.open(plate).convert("RGBA") if isinstance(plate, str) else plate
    icon = trim(Image.open(icon).convert("RGBA") if isinstance(icon, str) else icon)
    W = plate.width
    face = trim(plate).width  # видимая сторона плашки, не холст
    k = fill * face / max(icon.size)
    icon = icon.resize((round(icon.width * k), round(icon.height * k)), Image.LANCZOS)
    x, y = (W - icon.width) // 2, (W - icon.height) // 2 - round(0.02 * W)
    sh = Image.new("RGBA", plate.size, (0, 0, 0, 0))
    m = icon.getchannel("A").point(lambda v: int(v * shadow))
    sh.paste((40, 25, 10, 255), (x + round(0.012 * W), y + round(0.018 * W)), m)
    sh = sh.filter(ImageFilter.GaussianBlur(W * 0.008))
    out = Image.alpha_composite(plate, sh)
    if glow:  # (rgb, сила 0..1): размытая альфа иконки цветом класса под иконкой (ночью)
        g = Image.new("RGBA", plate.size, (0, 0, 0, 0))
        g.paste(glow[0] + (255,), (x, y), icon.getchannel("A").point(lambda v: int(v * glow[1])))
        g = g.filter(ImageFilter.GaussianBlur(W * 0.035))
        out = Image.alpha_composite(out, g)
    out.alpha_composite(icon, (x, y))
    return out
