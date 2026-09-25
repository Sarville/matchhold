"""Сдвиг левой или правой половины слоя к краю (за границу кадра). Оригинал не трогаем.
Использование: shift_layer.py in.png out.png left|right PX
left: содержимое левой половины уезжает влево на PX (обрезается краем), правая половина не меняется."""
import sys
from PIL import Image

im = Image.open(sys.argv[1]).convert("RGBA"); side = sys.argv[3]; dx = int(sys.argv[4])
W, H = im.size; half = W // 2
out = im.copy()
if side == "left":
    out.paste(Image.new("RGBA", (half, H), (0, 0, 0, 0)), (0, 0))
    out.alpha_composite(im.crop((dx, 0, half, H)), (0, 0))
else:
    out.paste(Image.new("RGBA", (W - half, H), (0, 0, 0, 0)), (half, 0))
    out.alpha_composite(im.crop((half, 0, W - dx, H)), (half + dx, 0))
out.save(sys.argv[2])
