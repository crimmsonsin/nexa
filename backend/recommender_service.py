from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json


def recommend(items, category=None):
    filtered = [item for item in items if not category or category == "Todos" or item["category"] == category]
    return sorted(filtered, key=lambda item: item["score"], reverse=True)[:4]


class RecommenderHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/recommend":
            self.send_json({"error": "Ruta no encontrada."}, 404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(size))
            result = recommend(payload.get("products", []), payload.get("category"))
            self.send_json({"recommendations": result}, 200)
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": f"Solicitud inválida: {error}"}, 400)

    def log_message(self, format, *args):
        print(f"[recommender] {format % args}")

    def send_json(self, payload, status):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print("Servicio recomendador escuchando en http://localhost:5001")
    ThreadingHTTPServer(("localhost", 5001), RecommenderHandler).serve_forever()

