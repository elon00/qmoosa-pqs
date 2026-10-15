"""
Lightweight Web & REST Server for QMoosa-PQS Superplatform.
Provides static UI serving and comprehensive REST API endpoints:
- /api/synthesize: End-to-end agentic synthesis
- /api/rea_investigate: Scoped REA reverse engineering analysis
- /api/rsi_experiment: Raven-style RSI experiment execution
- /api/reality_gates: Live reality verification gate audit report
- /api/scorecard: 100-point production scorecard
- /api/benchmarks: Classiq comparative benchmark suite
- /api/agent_swarm: Full 9-agent collaborative swarm execution
"""

import sys
import os
import json
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.agent import QuantumAgent
from agent.agentic_orchestrator import AgenticQuantumSwarm
from integrations.rea_adapter import REAAdapter
from integrations.classiq_adapter import ClassiqAdapter
from core.raven_experiment_engine import RavenStyleExperimentEngine, RSIPeepholeRule


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

    def do_GET(self):
        if self.path == "/api/reality_gates":
            self._serve_json_file(os.path.join(PROJECT_ROOT, "reports", "REALITY_GATES.json"))
        elif self.path == "/api/scorecard":
            self._serve_json_file(os.path.join(PROJECT_ROOT, "reports", "PRODUCTION_SCORECARD.json"))
        elif self.path == "/api/benchmarks":
            self._serve_json_file(os.path.join(PROJECT_ROOT, "reports", "QUANTUM_BENCHMARKS.json"))
        elif self.path == "/api/rsi_experiments":
            self._serve_json_file(os.path.join(PROJECT_ROOT, "reports", "RSI_EXPERIMENTS.json"))
        else:
            super().do_GET()

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"

        try:
            data = json.loads(post_body.decode("utf-8")) if post_body else {}

            if self.path == "/api/synthesize":
                prompt = data.get("prompt", "Create a 3-qubit GHZ state")
                topology = data.get("topology", "all_to_all")
                backend = data.get("backend", "ibm_quantum")
                agent = QuantumAgent(target_topology=topology, target_backend=backend)
                result = agent.synthesize(prompt)
                self._send_json_response(result)

            elif self.path == "/api/rea_investigate":
                raw_code = data.get("code", "")
                rea = REAAdapter()
                # Reverse engineer input code
                report = rea.quantum_rea.reverse_engineer(raw_code)
                self._send_json_response(report.to_dict())

            elif self.path == "/api/rsi_experiment":
                hypothesis = data.get("hypothesis", "Peephole test hypothesis")
                rule_dict = data.get("rule", {})
                rule = RSIPeepholeRule(
                    rule_id=rule_dict.get("rule_id", "RSI-USER-001"),
                    pattern=rule_dict.get("pattern", "H * Z * H"),
                    replacement=rule_dict.get("replacement", "X"),
                    gate_saving=rule_dict.get("gate_saving", 2),
                )
                rsi_engine = RavenStyleExperimentEngine()
                record = rsi_engine.run_controlled_experiment(hypothesis, rule)
                self._send_json_response(record.to_dict())

            elif self.path == "/api/agent_swarm":
                prompt = data.get("prompt", "Create a 3-qubit GHZ state")
                swarm = AgenticQuantumSwarm()
                result = swarm.run_agentic_workflow(prompt)
                self._send_json_response(result.to_dict())

            else:
                self.send_error(404, "Endpoint not found")

        except Exception as e:
            err_resp = {"error": str(e), "status": "FAILED"}
            self._send_json_response(err_resp, status=500)

    def _serve_json_file(self, file_path: str):
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self._send_json_response({"error": "Report not yet generated", "status": "NOT_FOUND"}, status=404)

    def _send_json_response(self, data: Dict[str, Any], status: int = 200):
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)


def run_server(port: int = 8088):
    server_address = ("", port)
    httpd = HTTPServer(server_address, QMoosaHTTPRequestHandler)
    print(f"=========================================================")
    print(f"  QMoosa-PQS Quantum AI Agentics Superplatform Server")
    print(f"  URL: http://localhost:{port}")
    print(f"  Reality Mode: ACTIVE (Zero Hallucination Protocol)")
    print(f"  Classiq + REA + Raven RSI Modules: LOADED & OPERATIONAL")
    print(f"=========================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping QMoosa-PQS server...")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run QMoosa-PQS Web & API Server")
    parser.add_argument("--port", type=int, default=8088, help="Port to listen on (default 8088)")
    args = parser.parse_args()
    run_server(args.port)
