"""Убрать нарисованную статичную луну с дальнего ночного слоя (сессия 7): дублирует движущуюся иконку .celestial.
Круглая маска вокруг обнаруженного диска (мягкий край), заливка = гладкий вертикальный градиент неба (медиана по
самой тёмной узкой полосе колонок, без облаков и звёзд), поэтому в месте луны остаётся чистое небо без шва.
Правит и мастера (out/env/bg/bg_s*_far_night_*_v1.png), и уже экспортированные www/img/v2/bg/*_far_night_*.webp.
Запуск: python3 tools/remove_moon.py [in out]"""
import glob
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

def remove_moon(path, out):
    im = Image.open(path); a = np.array(im.convert("RGB")).astype(float)
    H, W = a.shape[:2]
    lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    region = np.zeros((H, W), bool); region[:int(H * 0.5), :int(W * 0.42)] = True
    # семя: самый яркий пиксель после блюра (блюр гасит одиночные звёзды, у которых нет ярких соседей, луна остаётся ярче)
    blur = ndi.gaussian_filter(lum, 3); seed_lum = np.where(region, blur, -1)
    sy, sx = np.unravel_index(np.argmax(seed_lum), seed_lum.shape)
    mask0 = lum > 0.72 * blur[sy, sx]
    lab, n = ndi.label(mask0); comp = lab == lab[sy, sx]
    ys, xs = np.where(comp)
    if len(xs) < 20: print("  без луны", path); return False
    cy, cx = (ys.min() + ys.max()) / 2, (xs.min() + xs.max()) / 2
    r = max(xs.max() - xs.min(), ys.max() - ys.min()) / 2           # bbox компонента, содержащего семя (не «самый большой», а тот, что реально луна)
    yy, xx = np.mgrid[0:H, 0:W]; d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    R, FEATHER = r * 4.2, r * 1.6
    alpha = np.clip((R - d) / FEATHER, 0, 1)
    # заливка: самая тёмная полоса колонок в половине, противоположной луне (без облаков/звёзд) -> медиана по строкам
    bw = max(40, int(r)); half = slice(0, W // 2) if cx > W / 2 else slice(W // 2, W)
    colmean = lum.copy(); colmean[:, :half.start] = 1e9 if half.start else colmean[:, :half.start]
    prof = ndi.uniform_filter1d(lum[:int(R + cy) if cy + R < H else H].mean(0), bw)
    prof = np.where((np.arange(W) >= half.start) & (np.arange(W) < half.stop), prof, 1e9)
    x0 = max(bw, min(W - bw, int(np.argmin(prof))))
    strip = a[:, x0 - bw // 2:x0 + bw // 2]
    rowfill = np.median(strip, axis=1)                     # (H,3) гладкий вертикальный профиль неба
    rowfill = ndi.gaussian_filter1d(rowfill, 25, axis=0)
    fill = np.broadcast_to(rowfill[:, None, :], a.shape)
    out_a = a * (1 - alpha[..., None]) + fill * alpha[..., None]
    Image.fromarray(out_a.clip(0, 255).astype(np.uint8), "RGB").save(out, **({"lossless": True, "quality": 100, "method": 6} if out.endswith(".webp") else {}))
    print("  убрана луна", path, "center", round(cx), round(cy), "r", round(r), "-> R", round(R), "полоса x0", x0)
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        remove_moon(sys.argv[1], sys.argv[2])
    else:
        for f in sorted(glob.glob("out/env/bg/bg_s*_far_night_*_v1.png")):
            remove_moon(f, f)
        for f in sorted(glob.glob("../www/img/v2/bg/s*_far_night_*.webp")):
            remove_moon(f, f)
