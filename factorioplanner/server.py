from http.server import HTTPServer, BaseHTTPRequestHandler
from traceback import format_exc
from urllib import parse

from . import planner


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = parse.urlparse(self.path)
        path = parsed.path
        parameters = parse.parse_qs(parsed.query)

        try:
            result = handle(path, parameters)
            self.send_response(200)
        except BaseException as exc:
            from yattag import Doc
            doc, tag, text = Doc().tagtext()
            with tag("div", klass="error"):
                text(str(exc))
            with tag("pre"):
                text(format_exc())
            result = doc.getvalue()
            self.send_response(503)

        self.end_headers()
        self.wfile.write(result.encode('utf-8'))

def handle(path, parameters):
    if path == '/' or path == '/index.html':
        with open("static/index.html") as fileobj:
            return fileobj.read()
    elif path == '/script.js':
        with open("static/script.js") as fileobj:
            return fileobj.read()
    elif path == '/style.css':
        with open("static/style.css") as fileobj:
            return fileobj.read()
    elif path == '/bootstrap.min.css':
        with open("static/bootstrap.min.css") as fileobj:
            return fileobj.read()
    elif path == '/plan':
        targets = {}
        for item in parameters.get("target", []):
            if ':' in item:
                item, amount = item.split(':', maxsplit=1)
                if not amount.strip():
                    amount = "1"
                targets[item] = float(amount.strip())
            else:
                targets[item] = 1

        return planner.visualize(
            targets,
            parameters.get("recipe", []),
            parameters.get("external", [])
        )
    else:
        raise ValueError("Bad request")

def serve(port):
    HTTPServer(('', port), Handler).serve_forever()
