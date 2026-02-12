from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from nana.brain import NanaBrain
from nana.memory import MemoryStore

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"


class NanaWebHandler(BaseHTTPRequestHandler):
    brain: NanaBrain | None = None
    store: MemoryStore | None = None

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/index.html"}:
            body = (STATIC_DIR / "index.html").read_bytes()
            self._send(200, "text/html; charset=utf-8", body)
            return
        if self.path == "/styles.css":
            self._send(200, "text/css; charset=utf-8", (STATIC_DIR / "styles.css").read_bytes())
            return
        if self.path == "/app.js":
            self._send(200, "application/javascript; charset=utf-8", (STATIC_DIR / "app.js").read_bytes())
            return
        if self.path == "/api/state":
            assert self.store is not None
            payload = json.dumps(self.store.brain_state).encode("utf-8")
            self._send(200, "application/json", payload)
            return
        self._send(404, "text/plain; charset=utf-8", b"Not Found")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/chat":
            self._send(404, "text/plain; charset=utf-8", b"Not Found")
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        data = json.loads(raw.decode("utf-8"))
        message = data.get("message", "")

        assert self.brain is not None
        assert self.store is not None
        reply = self.brain.respond(message)
        self.store.save()

        body = json.dumps({"reply": reply, "now": self.store.now_context()}).encode("utf-8")
        self._send(200, "application/json", body)


def run_web(host: str = "0.0.0.0", port: int = 8080, memory_path: str = "data/memory.json") -> None:
    store = MemoryStore.load(memory_path)
    brain = NanaBrain(store)

    NanaWebHandler.brain = brain
    NanaWebHandler.store = store

    server = ThreadingHTTPServer((host, port), NanaWebHandler)
    print(f"Nana web running at http://{host}:{port}")
    print("Female voice mode: frontend SpeechSynthesis chooses female-preferred voice when available.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        store.save()
        server.server_close()
