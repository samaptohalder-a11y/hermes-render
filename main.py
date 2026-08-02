import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from hermes_agent import AIAgent

# --- Render Free Web Service Health Check ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hermes Agent is live and healthy!")

def start_health_check_server():
    # Render assigns a dynamic port via the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

def run():
    # Start the HTTP server in a background thread for Render
    threading.Thread(target=start_health_check_server, daemon=True).start()

    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY or OPENAI_API_KEY is missing.")
        sys.exit(1)

    print("Initializing Hermes Agent on Render...")

    agent = AIAgent(
        skip_memory=True
    )

    response = agent.run("Hermes Agent is running successfully on Render!")
    print(f"Agent Output: {response}")

if __name__ == "__main__":
    run()