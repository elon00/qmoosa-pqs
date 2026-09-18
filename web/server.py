"""
Lightweight Web & REST Server for QMoosa-PQ.
Provides static UI serving and API synthesis endpoints using Python standard library.
"""

import sys
import os
import json
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.agent import QuantumAgent


class QMoosaHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Custom request handler with REST API routing."""

    def __init__(self, *args, **kwargs):
        web_dir = os.path.join(PROJECT_ROOT, "web")
        super().__init__(*args, directory=web_dir, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/synthesize":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len)
            
            try:
                data = json.loads(post_body.decode("utf-8")) if post_body else {}
                prompt = data.get("prompt", "Create a 3-qubit GHZ state")
                topology = data.get("topology", "all_to_all")

                agent = QuantumAgent(target_topology=topology)
                result = agent.synthesize(prompt)

                response_bytes = json.dumps(result).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(response_bytes)))
                self.end_headers()
                self.wfile.write(response_bytes)

            except Exception as e:
                err_resp = json.dumps({"error": str(e), "status": "FAILED"}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(err_resp)))
                self.end_headers()
                self.wfile.write(err_resp)
        else:
            self.send_error(404, "Endpoint not found")


def run_server(port: int = 8088):
    server_address = ("", port)
    httpd = HTTPServer(server_address, QMoosaHTTPRequestHandler)
    print(f"=========================================================")
    print(f"  QMoosa-PQ Autonomous Quantum Engine Server Started")
    print(f"  URL: http://localhost:{port}")
    print(f"  Reality Mode: ACTIVE (Zero Hallucination Protocol)")
    print(f"=========================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping QMoosa-PQ server...")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run QMoosa-PQ Web & API Server")
    parser.add_argument("--port", type=int, default=8088, help="Port to listen on (default 8088)")
    args = parser.parse_args()
    run_server(args.port)
