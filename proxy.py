from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import json

class ProxyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            token = self.headers.get('Authorization')
            if not token:
                self.send_error(400, "Missing token")
                return

            try:
                if '/richmenu/' in self.path and '/content' in self.path:
                    url = f"https://api-data.line.me{self.path[4:]}"
                else:
                    url = f"https://api.line.me{self.path[4:]}"

                print(f"\n=== REQUEST ===")
                print(f"URL: {url}")
                print(f"Method: GET")
                print(f"Headers: Authorization: Bearer ***[token hidden]***")

                req = urllib.request.Request(url, headers={'Authorization': token})

                try:
                    response = urllib.request.urlopen(req)
                    content = response.read()

                    print(f"\n=== RESPONSE ===")
                    print(f"Status: {response.status}")
                    print(f"Headers: {dict(response.headers)}")
                    if 'content' not in self.path:
                        print(f"Body: {content.decode('utf-8')}")
                    else:
                        print("Body: [Image Binary Data]")

                    self.send_response(200)
                    self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(content)
                except urllib.error.HTTPError as e:
                    error_content = e.read()

                    print(f"\n=== ERROR RESPONSE ===")
                    print(f"Status: {e.code}")
                    print(f"Headers: {dict(e.headers)}")
                    print(f"Error: {error_content.decode('utf-8')}")

                    self.send_response(e.code)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(error_content)

            except Exception as e:
                print(f"\n=== EXCEPTION ===")
                print(f"Error: {str(e)}")
                self.send_error(500, str(e))
        else:
            super().do_GET()

    def do_DELETE(self):
        if self.path.startswith('/api/'):
            token = self.headers.get('Authorization')
            if not token:
                self.send_error(400, "Missing token")
                return

            try:
                url = f"https://api.line.me{self.path[4:]}"
                req = urllib.request.Request(url, method='DELETE', headers={'Authorization': token})

                print(f"\n=== DELETE REQUEST ===")
                print(f"URL: {url}")

                response = urllib.request.urlopen(req)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.read())
            except Exception as e:
                print(f"Delete error: {str(e)}")
                self.send_error(500, str(e))

    def do_POST(self):
        if self.path.startswith('/api/'):
            token = self.headers.get('Authorization')
            content_length = int(self.headers.get('Content-Length', 0))
            content_type = self.headers.get('Content-Type', '')

            if not token:
                self.send_error(400, "Missing token")
                return

            try:
                body = self.rfile.read(content_length)
                if '/content' in self.path:
                    url = f"https://api-data.line.me{self.path[4:]}"
                    boundary = content_type.split('boundary=')[1]
                    start = body.find(b'\r\n\r\n') + 4
                    end = body.rfind(b'\r\n--' + boundary.encode() + b'--')
                    image_data = body[start:end]

                    # ? form-data ???????
                    if b'image/jpeg' in body or b'image/jpg' in body:
                        image_type = 'image/jpeg'
                    elif b'image/png' in body:
                        image_type = 'image/png'
                    else:
                        image_type = 'image/jpeg'  # ??

                    headers = {
                        'Authorization': token,
                        'Content-Type': image_type
                    }
                else:
                    url = f"https://api.line.me{self.path[4:]}"
                    headers = {
                        'Authorization': token,
                        'Content-Type': content_type
                    }
                    image_data = body

                print(f"\n=== POST REQUEST ===")
                print(f"URL: {url}")
                print(f"Content-Type: {headers.get('Content-Type')}")

                req = urllib.request.Request(url, data=image_data, headers=headers, method='POST')
                response = urllib.request.urlopen(req)

                print(f"\n=== RESPONSE ===")
                print(f"Status: {response.status}")

                self.send_response(response.status)
                self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.read())

            except Exception as e:
                print(f"Error: {str(e)}")
                self.send_error(500, str(e))

httpd = HTTPServer(('localhost', 8000), ProxyHandler)
print("Server running on http://localhost:8000")
httpd.serve_forever()
