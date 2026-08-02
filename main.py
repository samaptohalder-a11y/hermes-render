import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    import hermes
    print('Successfully imported hermes')
except Exception as e:
    print(f'Failed hermes: {e}')

try:
    import hermes_agent
    print('Successfully imported hermes_agent')
except Exception as e:
    print(f'Failed hermes_agent: {e}')

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Hermes Agent is live and healthy!')

def start_health_check_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

def run():
    threading.Thread(target=start_health_check_server, daemon=True).start()
    print('Health check server running...')

if __name__ == '__main__':
    run()
