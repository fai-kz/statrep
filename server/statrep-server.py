#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import psycopg2


MASTER_PORT = 0
PATH_GET = ''
PATH_POST = ''

# sed imports config here. DO NOT DELETE OR MODIFY THIS LINE!


AUTOHEAL=True

class Database:

    def __init__(self):
        self.conn = psycopg2.connect(database='systemddb', user='postgres')
        self.conn.autocommit = True
        self.db = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.db.close()
        self.conn.close()

    def log_failed(self, host, unit):
        self.db.execute("INSERT INTO units (host, unit) VALUES (%s, %s)", (host, unit))

    def log_journal(self, host, p, idf, message, t):
        self.db.execute("INSERT INTO journal (host, priority, id, message, ts) VALUES (%s, %s, %s, %s, to_timestamp(%s/1000000.0))", (host, p, idf, message, t))

    def log_hacker(self, address, method):
        self.db.execute("INSERT INTO hackers (address, method) VALUES (%s, %s)", (address, method))

    def get_log(self) -> str:
        s = "<h3>Failed units</h3>\n"
        self.db.execute("SELECT ts::timestamp(0), host, unit FROM units WHERE ts > CURRENT_DATE - INTERVAL '1' DAY ORDER BY ts DESC;")
        res = self.db.fetchall()
        if not res:
            s += "<p>None</p>\n"
        else:
            s += '<table border="1" cellpadding="8"><tr><th>Timestamp</th><th>Host</th><th>Unit</th></tr>\n'
            for r in res:
                s += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>\n"
            s += "</table>\n"

        s += "<h3>Journal events</h3>\n"
        # self.db.execute("SELECT ts::timestamp(0), host, id, message, priority FROM journal WHERE ts > CURRENT_DATE - INTERVAL '3' DAY ORDER BY ts DESC;")
        self.db.execute("SELECT ts::timestamp(0), host, id, message, priority FROM journal ORDER BY ts DESC LIMIT 100;")
        res = self.db.fetchall()
        if not res:
            s += "<p>None</p>\n"
        else:
            s += '<table border="1" cellpadding="6" style="font-size:85%"><tr><th>Timestamp</th><th>Level</th><th>Host</th><th>SYS_ID</th><th>Message</th></tr>\n'
            for r in res:
                if r[4] < 2:
                    style = ' style="color:#FF0000;font-weight:bold"'
                    level = 'alert'
                elif r[4] < 3:
                    style = ' style="color:#FF0000"'
                    level = 'critical'
                else:
                    style = ''
                    level = 'error'
                s += f'<tr{style}><td style="white-space:nowrap;">{r[0]}</td><td>{level}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>\n'
            s += "</table>\n"
        return s




class StatusServer(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if self.path != PATH_GET:
            self.wfile.write(bytes("<html><head>You are not supposed to be here...</head>", "utf-8"))
            return
        with Database() as db:
            response = db.get_log()
        self.wfile.write(response.encode("utf-8"))


    def do_POST(self):
        self.send_response(301)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        if self.path != PATH_POST:
            with Database() as db:
                db.log_hacker(self.client_address[0], f'post: {self.path}')
            return
        if AUTOHEAL:
            self.wfile.write("YES".encode("utf-8"))
        else:
            self.wfile.write("NO".encode("utf-8"))
        data_string = self.rfile.read(int(self.headers['Content-Length']))
        data = json.loads(data_string)
        with Database() as db:
            if "failed" in data:
                for r in data["failed"]:
                    db.log_failed(data["host"], r)
            if "journal" in data:
                for r in data["journal"]:
                    msg = r["MESSAGE"]
                    if isinstance(msg, list):
                        msg = msg[0]
                    ind = msg.find('\n')
                    if ind > 0: msg = msg[:ind]
                    db.log_journal(data["host"], r["PRIORITY"], r["SYSLOG_IDENTIFIER"], msg, r["__REALTIME_TIMESTAMP"])




if __name__ == "__main__":        

    webServer = HTTPServer(("0.0.0.0", MASTER_PORT), StatusServer)

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
