#!/usr/bin/env python3
"""Сборка под платформу: python3 tools/build_platform.py <yandex|vk|android>
build (r.js) -> dist/<platform>/ ; yandex дополнительно -> dist/matchhold-yandex.zip"""
import os, re, shutil, subprocess, sys, zipfile

PLATFORMS = ('yandex', 'vk', 'android')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JUNK = ('src', 'nodeploy')  # в img/


def main(name):
    if name not in PLATFORMS:
        sys.exit('usage: build_platform.py <%s>' % '|'.join(PLATFORMS))
    os.chdir(ROOT)
    subprocess.check_call(['node', 'tools/r.js', '-o', 'tools/build.js'], stdout=subprocess.DEVNULL)

    out = os.path.join('dist', name)
    shutil.rmtree(out, ignore_errors=True)
    shutil.copytree('build', out, ignore=shutil.ignore_patterns('thumbs.db', 'Thumbs.db', 'build.txt', 'jquery-dev.js'))
    for d in JUNK:
        shutil.rmtree(os.path.join(out, 'img', d), ignore_errors=True)

    plat = os.path.join(out, 'js', 'app', 'platform')
    for f in os.listdir(plat):
        if f != name + '.js':
            os.remove(os.path.join(plat, f))
    if name != 'vk':
        os.remove(os.path.join(out, 'js', 'lib', 'vk-bridge.min.js'))
    if name == 'android':  # WebView (Chromium) играет ogg; вдвое меньше APK
        audio = os.path.join(out, 'audio')
        for f in os.listdir(audio):
            if f.endswith('.mp3'):
                os.remove(os.path.join(audio, f))

    idx = os.path.join(out, 'index.html')
    html = open(idx, encoding='utf-8', newline='').read()
    html = re.sub(r'<div [^>]*nodeploy>[^<]*</div>\s*', '', html)
    html, n = re.subn(r'<head>', '<head>\n\t\t<script>window.G_PLATFORM="%s"</script>' % name, html, count=1)
    assert n == 1, 'no <head> in index.html'
    open(idx, 'w', encoding='utf-8', newline='').write(html)

    if name == 'yandex':
        zp = os.path.join('dist', 'matchhold-yandex.zip')
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
            for base, _, files in os.walk(out):
                for f in files:
                    p = os.path.join(base, f)
                    z.write(p, os.path.relpath(p, out))
        print('%s: %.1f MB' % (zp, os.path.getsize(zp) / 1e6))

    size = sum(os.path.getsize(os.path.join(b, f)) for b, _, fs in os.walk(out) for f in fs)
    print('%s: %.1f MB' % (out, size / 1e6))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '')
