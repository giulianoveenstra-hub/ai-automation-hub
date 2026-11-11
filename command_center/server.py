"""Loopback-only application. Share the same instance using an authenticated SSH tunnel."""
import argparse
import json
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from .model import METHODS, validate
from .storage import Store, Conflict

ROOT = Path(__file__).parent
MAX_BODY = 2_000_000


def make_server(database, port=8765):
    store = Store(database)
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, body, content_type='application/json; charset=utf-8', attachment=None):
            if isinstance(body, (dict,list)):
                body = json.dumps(body, ensure_ascii=False).encode()
            elif isinstance(body, str):
                body = body.encode()
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
            if attachment:
                self.send_header('Content-Disposition', 'attachment; filename="' + attachment + '"')
            self.end_headers()
            self.wfile.write(body)

        def valid_host(self):
            host = self.headers.get('Host','')
            try:
                parsed = urlsplit('http://' + host)
                return parsed.hostname in ('localhost','127.0.0.1') and parsed.username is None and parsed.password is None
            except ValueError:
                return False

        def do_GET(self):
            if not self.valid_host():
                return self.reply(403, {'error':'Nur localhost erlaubt'})
            path = urlsplit(self.path).path
            if path == '/api/workspace':
                return self.reply(200, dict(**store.read(), csrf=token, methods=METHODS))
            if path == '/api/export.json':
                return self.reply(200, store.read(), attachment='arvo-workspace.json')
            if path == '/api/techpack.pdf':
                try:
                    from .pdf_export import export_pdf
                    saved = store.read()
                    pdf = export_pdf(saved['data'], saved['revision'])
                    return self.reply(200, pdf, 'application/pdf', 'ARVO-Tech-Pack-Entwurf.pdf')
                except ImportError:
                    return self.reply(503, {'error':'PDF-Abhängigkeit fehlt: pip install -r command_center/requirements.txt'})
            files = {'/':'index.html','/app.js':'app.js','/style.css':'style.css'}
            if path in files:
                kind = {'/':'text/html; charset=utf-8','/app.js':'text/javascript; charset=utf-8','/style.css':'text/css; charset=utf-8'}[path]
                return self.reply(200, (ROOT/'static'/files[path]).read_bytes(), kind)
            return self.reply(404, {'error':'Nicht gefunden'})

        def do_POST(self):
            if not self.valid_host():
                return self.reply(403, {'error':'Nur localhost erlaubt'})
            origin = self.headers.get('Origin')
            if (origin and origin != 'http://' + self.headers.get('Host')) or not secrets.compare_digest(self.headers.get('X-ARVO-CSRF',''), token):
                return self.reply(403, {'error':'Ungültiger Ursprung oder CSRF-Token; Seite neu laden'})
            if self.path not in ('/api/workspace', '/api/validate'):
                return self.reply(404, {'error':'Nicht gefunden'})
            try:
                if self.headers.get('Content-Type') != 'application/json':
                    raise ValueError('JSON erforderlich')
                length = int(self.headers.get('Content-Length','0'))
                if not 0 < length <= MAX_BODY:
                    raise ValueError('Ungültige Nutzlastgröße')
                payload = json.loads(self.rfile.read(length))
                if self.path == '/api/validate':
                    validate(payload)
                    return self.reply(200, {'valid':True})
                if not isinstance(payload,dict) or set(payload) != {'revision','data'} or type(payload['revision']) is not int:
                    raise ValueError('Revision und Daten erforderlich')
                result = store.save(payload['revision'], payload['data'])
                return self.reply(200, result)
            except Conflict as exc:
                return self.reply(409, {'error':str(exc)})
            except (ValueError,TypeError,KeyError,RecursionError) as exc:
                return self.reply(400, {'error':str(exc)})

        def log_message(self, format, *args):
            # No request headers or private field contents in logs.
            pass
    return ThreadingHTTPServer(('127.0.0.1', port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--data-dir',type=Path,default=ROOT/'private')
    args = parser.parse_args()
    args.data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    server = make_server(args.data_dir/'workspace.sqlite3', args.port)
    print('ARVO Command Center: http://127.0.0.1:' + str(server.server_port), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
