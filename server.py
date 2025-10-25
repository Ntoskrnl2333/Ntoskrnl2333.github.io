from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os
from urllib.parse import unquote

COMMENTS_FILE = "comments.json"
PORT = 80

class CommentHandler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: str, content_type="text/plain; charset=utf-8"):
        body_bytes = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body_bytes)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body_bytes)
        self.wfile.flush()
        self.close_connection = True

    def do_POST(self):
        if self.path == "/comment/push":
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                new_comment = json.loads(body)
            except Exception:
                self._send(400, "Invalid JSON")
                return

            # 读取/初始化文件
            try:
                if os.path.exists(COMMENTS_FILE):
                    with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
                        comments = json.load(f)
                    if not isinstance(comments, list):
                        comments = []
                else:
                    comments = []
            except Exception:
                comments = []

            comments.append(new_comment)
            with open(COMMENTS_FILE, "w", encoding="utf-8") as f:
                json.dump(comments, f, ensure_ascii=False, indent=2)

            self._send(200, json.dumps({"status": "ok"}, ensure_ascii=False), "application/json; charset=utf-8")
        else:
            self._send(404, "Not Found")

    def do_GET(self):
        if self.path == "/comment/list":
            data = "[]"
            if os.path.exists(COMMENTS_FILE):
                with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
                    data = f.read()
            self._send(200, data, "application/json; charset=utf-8")
            return

        # 静态文件处理
        path = unquote(self.path.lstrip("/")) or "index.html"
        if not os.path.exists(path) or not os.path.isfile(path):
            self._send(404, "File not found")
            return

        mime = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
        }.get(os.path.splitext(path)[1].lower(), "application/octet-stream")

        with open(path, "rb") as f:
            data = f.read()
        self._send(200, data, mime)

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), CommentHandler)
    print(f"Server running at http://localhost:{PORT}")
    server.serve_forever()
