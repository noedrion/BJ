import os, json
from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3

DB = os.environ.get("DB", "/data/counters.db")

KEYS = ("zg", "zb", "ng", "nb")

def init_db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS counters (id TEXT PRIMARY KEY, val INTEGER DEFAULT 0)")
    for k in KEYS:
        con.execute("INSERT OR IGNORE INTO counters VALUES (?, 0)", (k,))
    con.commit()
    con.close()

def get_counters():
    con = sqlite3.connect(DB)
    rows = dict(con.execute("SELECT id, val FROM counters").fetchall())
    con.close()
    return {k: rows.get(k, 0) for k in KEYS}

def set_counters(data):
    con = sqlite3.connect(DB)
    for k in KEYS:
        if k in data:
            con.execute("UPDATE counters SET val=? WHERE id=?", (int(data[k]), k))
    con.commit()
    con.close()

HERE = os.path.dirname(os.path.abspath(__file__))

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        if self.path == "/api/counters":
            body = json.dumps(get_counters()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(os.path.join(HERE, "index.html"), "rb") as f:
                self.wfile.write(f.read())

    def do_POST(self):
        if self.path == "/api/counters":
            length = int(self.headers.get("Content-Length", 0))
            body   = json.loads(self.rfile.read(length))
            set_counters(body)
            result = json.dumps(get_counters()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(result))
            self.end_headers()
            self.wfile.write(result)

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 3000))
    print(f"Bonne journée → http://localhost:{port}  (DB: {DB})")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
