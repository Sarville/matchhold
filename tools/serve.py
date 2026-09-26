#!/usr/bin/env python3
"""Dev-сервер: статика из www/ с проверкой кэша (no-cache). Запуск: python3 tools/serve.py [порт=8080]"""
import functools, http.server, os, sys

class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".webp": "image/webp"}
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "www")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Handler, directory=root)).serve_forever()
