"""DevDuo — Demo UI proxy.

The crosstalk-mcp relay requires a Bearer token on every request, including
the CORS preflight OPTIONS request, which browsers send without auth headers.
That makes the relay's REST mirror un-callable directly from a static page
in a browser. This tiny proxy sits in front of it: it holds the token
server-side, answers CORS preflights itself, and forwards GET requests to
the relay's /api/channels/... routes.

Usage:
    source ../.venv/bin/activate
    python proxy.py
"""

import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

RELAY_URL = os.environ["RELAY_URL"].rstrip("/")
RELAY_TOKEN = os.environ["RELAY_TOKEN"]
PORT = int(os.environ.get("DEMO_PROXY_PORT", "8092"))


class Handler(BaseHTTPRequestHandler):
    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        if not self.path.startswith("/channels/"):
            self.send_response(404)
            self._cors_headers()
            self.end_headers()
            return
        upstream = f"{RELAY_URL}/api{self.path}"
        req = urllib.request.Request(
            upstream, headers={"Authorization": f"Bearer {RELAY_TOKEN}"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read()
                status = resp.status
        except urllib.error.HTTPError as e:
            body = e.read()
            status = e.code
        self.send_response(status)
        self._cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    print(f"Demo proxy forwarding {('http://localhost:%d' % PORT)} -> {RELAY_URL}/api")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
