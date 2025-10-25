from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from urllib.parse import unquote

COMMENTS_FILE = "comments.json"
PORT = 80

class CommentHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/comment/push":
            self.send_error(404, "Not Found")
            return

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            new_comment = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        # 读取原有数据
        if os.path.exists(COMMENTS_FILE):
            try:
                with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
                    comments = json.load(f)
                if not isinstance(comments, list):
                    comments = []
            except Exception:
                comments = []
        else:
            comments = []

        # 追加新评论
        comments.append(new_comment)

        # 写回文件
        with open(COMMENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)

        # 返回成功
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))

    def do_GET(self):
        if self.path == "/comment/list":
            if os.path.exists(COMMENTS_FILE):
                with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
                    data = f.read()
            else:
                data = "[]"
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(data.encode("utf-8"))
        else:
            # 静态文件处理
            path = unquote(self.path.lstrip("/"))
            if path == "":
                path = "index.html"
            if not os.path.exists(path) or not os.path.isfile(path):
                self.send_error(404, "File not found")
                return
            # 根据扩展名设置简单的 MIME 类型
            mime = "text/plain"
            if path.endswith(".html"):
                mime = "text/html; charset=utf-8"
            elif path.endswith(".css"):
                mime = "text/css; charset=utf-8"
            elif path.endswith(".js"):
                mime = "application/javascript; charset=utf-8"
            elif path.endswith(".png"):
                mime = "image/png"
            elif path.endswith(".jpg") or path.endswith(".jpeg"):
                mime = "image/jpeg"

            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.end_headers()
            with open(path, "rb") as f:
                self.wfile.write(f.read())

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), CommentHandler)
    print(f"Server running at http://localhost:{PORT}")
    server.serve_forever()
