from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen
import json

import db

RECOMMENDER_URL = "http://localhost:5001/recommend"


def call_recommender(category):
    request_body = json.dumps({"products": db.products(), "category": category}).encode("utf-8")
    request = Request(
        RECOMMENDER_URL,
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=3) as response:
        return json.loads(response.read().decode("utf-8"))["recommendations"]


class ApiHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        category = query.get("category", [None])[0]

        if parsed.path == "/api/health":
            self.send_json({"status": "ok", "service": "api", "recommender": RECOMMENDER_URL}, 200)
        elif parsed.path == "/api/products":
            self.send_json({"products": db.products(category)}, 200)
        elif parsed.path == "/api/recommendations":
            try:
                self.send_json({"recommendations": call_recommender(category)}, 200)
            except Exception:
                self.send_json({"error": "El servicio de recomendaciones no está disponible."}, 503)
        else:
            self.send_json({"error": "Ruta no encontrada."}, 404)

    def do_POST(self):
        if self.path != "/api/preferences":
            self.send_json({"error": "Ruta no encontrada."}, 404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(size))
            user_id = str(payload.get("user_id", "")).strip()
            product_id = int(payload.get("product_id"))
            if not user_id:
                raise ValueError("user_id es obligatorio.")
            db.save_preference(user_id, product_id)
            self.send_json({"saved": True}, 201)
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, 400)

    def log_message(self, format, *args):
        print(f"[api] {format % args}")

    def send_json(self, payload, status):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


if __name__ == "__main__":
    db.initialize()
    print("API escuchando en http://localhost:5050")
    ThreadingHTTPServer(("localhost", 5050), ApiHandler).serve_forever()
