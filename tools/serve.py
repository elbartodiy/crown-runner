#!/usr/bin/env python3
"""Serve the build, and take its picture.

Plain static serving on GET. On POST /shot?name=X the body is a data: URL from the page's own
canvas, saved as a PNG beside the build. Headless Chrome would be the obvious way to get a
1920x1080 frame; it does not come up in this environment, and asking the page to hand over its
own backing store is both simpler and more honest — it is exactly the pixels the cabinet shows.
"""
import base64, os, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(HERE, '.shots')

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)
    def do_POST(self):
        u = urlparse(self.path)
        if u.path != '/shot':
            self.send_error(404); return
        name = (parse_qs(u.query).get('name') or ['frame'])[0]
        name = ''.join(c for c in name if c.isalnum() or c in '-_')
        raw = self.rfile.read(int(self.headers.get('Content-Length', 0))).decode('ascii')
        b64 = raw.split(',', 1)[1] if ',' in raw else raw
        os.makedirs(SHOTS, exist_ok=True)
        dst = os.path.join(SHOTS, name + '.png')
        with open(dst, 'wb') as f:
            f.write(base64.b64decode(b64))
        self.send_response(200); self.send_header('Content-Length', '2')
        self.end_headers(); self.wfile.write(b'ok')
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()
    def log_message(self, *a):
        pass

if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', int(sys.argv[1] if len(sys.argv) > 1 else 8777)), H).serve_forever()
