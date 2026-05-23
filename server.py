import os, json
from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3

DB = os.environ.get("DB", "counters.db")

def init_db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS counters (id TEXT PRIMARY KEY, val INTEGER DEFAULT 0)")
    con.execute("INSERT OR IGNORE INTO counters VALUES ('z', 0)")
    con.execute("INSERT OR IGNORE INTO counters VALUES ('n', 0)")
    con.commit()
    con.close()

def get_counters():
    con = sqlite3.connect(DB)
    rows = dict(con.execute("SELECT id, val FROM counters").fetchall())
    con.close()
    return rows

def set_counter(col, val):
    con = sqlite3.connect(DB)
    con.execute("UPDATE counters SET val=? WHERE id=?", (val, col))
    con.commit()
    con.close()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        if self.path == "/api/counters":
            self._json(get_counters())
        else:
            self._file()

    def do_POST(self):
        if self.path == "/api/counters":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            for col in ("z", "n"):
                if col in body:
                    set_counter(col, body[col])
            self._json(get_counters())

    def _json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _file(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        with open("index.html", "rb") as f:
            self.wfile.write(f.read())

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 3000))
    print(f"http://localhost:{port}  (DB: {DB})")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
