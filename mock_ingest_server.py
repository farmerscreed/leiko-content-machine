#!/usr/bin/env python3
"""mock_ingest_server.py — imitates the website's ingest endpoint locally.

  python mock_ingest_server.py                # listens on 127.0.0.1:8787
  $env:LEIKO_INGEST_URL = 'http://127.0.0.1:8787/api/content/ingest'
  python leiko_ingest.py copy/copy_issueN.json out_issueN/

Every rule here mirrors the real endpoint's SHAPE, not its full logic: enough
to rehearse a send end to end — auth, per-card status, soft flags, and the
"HTTP 200 but the card failed" case — without touching the live site.

Test hooks (environment):
  MOCK_STATUS=published   force a status → leiko_ingest must report a
                          CONTRACT BREAK and exit non-zero, not print OK.
"""
import base64, json, os, re
from http.server import BaseHTTPRequestHandler, HTTPServer

from leiko_lint import scan, scan_cuffless

SECRET = os.environ.get("CONTENT_INGEST_SECRET", "")
REQUIRED = ["market", "issue_no", "card_slot", "caption", "image_base64"]


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # consume the body BEFORE any verdict — rejecting a large upload with
        # the request still in flight aborts the client's socket mid-send
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if self.path != "/api/content/ingest":
            return self._send(404, {"ok": False, "error": "no such route"})
        auth = self.headers.get("Authorization", "")
        if SECRET and auth != f"Bearer {SECRET}":
            return self._send(401, {"ok": False, "error": "bad secret"})

        try:
            card = json.loads(raw)
        except Exception:
            return self._send(400, {"ok": False, "error": "bad JSON"})

        missing = [k for k in REQUIRED if not card.get(k)]
        if missing:
            return self._send(200, {"results": [
                {"ok": False, "error": f"missing fields: {missing}"}]})
        try:
            png = base64.b64decode(card["image_base64"])
        except Exception:
            return self._send(200, {"results": [
                {"ok": False, "error": "image_base64 does not decode"}]})

        text = " ".join([card.get("title", ""), card.get("caption", "")]
                        + list((card.get("captions") or {}).values()))
        hits = scan(text)
        flags = (["cuffless-claim: soft-flagged for human review"]
                 if scan_cuffless(text) else [])

        status = "lint_failed" if hits else "needs_review"
        status = os.environ.get("MOCK_STATUS", status)
        slot, market = card["card_slot"], card["market"]
        self._send(200, {"results": [{
            "ok": True, "status": status,
            "id": f"mock-{card['issue_no']}-{slot}-{market}",
            "image_path": f"issue{card['issue_no']}/{market}/{slot}.png",
            "lint_hits": hits, "review_flags": flags,
            "bytes_received": len(png),
        }]})

    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *a):   # quiet; the client prints the story
        pass


if __name__ == "__main__":
    print("mock ingest listening on http://127.0.0.1:8787/api/content/ingest"
          + ("  (auth enforced)" if SECRET else "  (no secret set — auth off)"))
    HTTPServer(("127.0.0.1", 8787), Handler).serve_forever()
