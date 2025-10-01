from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse, os


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve /hello
        if self.path == "/hello":
            self._send(200, "Hello!", "text/plain")
        # Serve index.html for /
        elif self.path == "/" and os.path.exists("./index.html"):
            with open("./index.html", "rb") as f:
                self._send(200, f.read(), "text/html", raw=True)
        # Serve form.html for /form.html
        elif self.path == "/form.html" and os.path.exists("./form.html"):
            with open("./form.html", "rb") as f:
                self._send(200, f.read(), "text/html", raw=True)
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/form":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = urllib.parse.parse_qs(body)
            name = data.get("name", [""])[0]
            address = data.get("address", [""])[0]
            response = f"Post Request Successful\nName = {name}\nAddress = {address}\n"
            self._send(200, response, "text/plain")
        else:
            self.send_error(404, "Not Found")

    def _send(self, code, content, ctype, raw=False):
        self.send_response(code)
        self.send_header("Content-type", f"{ctype}; charset=utf-8")
        self.end_headers()
        self.wfile.write(content if raw else content.encode("utf-8"))


if __name__ == "__main__":
    print("Server running at http://localhost:8080")
    HTTPServer(("localhost", 8080), MyHandler).serve_forever()
