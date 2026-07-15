import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, Tuple
from urllib.parse import urlparse

try:
    from .agent import TOOL_NAMES, route_tool
except ImportError:  # pragma: no cover - supports running the file directly
    from agent import TOOL_NAMES, route_tool


class InteractionHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send_json(204, {})

    def do_GET(self) -> None:  # noqa: N802
        if self.path == '/health':
            self._send_json(200, {'status': 'ok'})
            return
        self._send_json(404, {'detail': 'Not found'})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != '/api/interaction':
            self._send_json(404, {'detail': 'Not found'})
            return

        content_length = int(self.headers.get('Content-Length', '0'))
        raw_body = self.rfile.read(content_length) if content_length else b'{}'
        try:
            payload = json.loads(raw_body.decode('utf-8'))
        except json.JSONDecodeError:
            self._send_json(400, {'detail': 'Invalid JSON payload'})
            return

        submission = payload.get('submission') or {}
        if not isinstance(submission, dict) or not submission:
            self._send_json(400, {'detail': 'Submission payload is required.'})
            return

        reply, suggestions = route_tool(payload.get('tool', 'Summarize from Voice Note'), submission, payload.get('message', ''), payload.get('mode', 'form'))
        self._send_json(200, {'reply': reply, 'tools': TOOL_NAMES, 'suggestions': suggestions})

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _send_json(self, status_code: int, payload: Dict[str, object]) -> None:
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = '127.0.0.1', port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), InteractionHandler)
    print(f'Serving on http://{host}:{port}')
    server.serve_forever()


if __name__ == '__main__':
    run_server()
